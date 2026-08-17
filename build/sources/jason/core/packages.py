"""Gestion des langues : catalogue, téléchargement, installation.

C'est le seul module qui a besoin d'Internet, et uniquement le temps
d'ajouter une langue. Ensuite, Jason fonctionne hors ligne définitivement.

Ce module raisonne en **langues**, pas en « couples de langues ». Le moteur,
lui, ne connaît que des couples orientés (français → anglais) et passe par
l'anglais pour relier deux autres langues entre elles. Cette mécanique ne
regarde pas l'utilisateur : ici, « ajouter l'espagnol » installe tout ce
qu'il faut pour traduire dans les deux sens.
"""

from __future__ import annotations

import tempfile
import urllib.request
from collections.abc import Callable
from pathlib import Path

import argostranslate.package
import argostranslate.translate

# Langue de relais. Le moteur ne sait pas traduire directement de l'espagnol
# vers l'allemand : il enchaîne espagnol → anglais → allemand. L'anglais est
# donc installé quoi qu'il arrive.
PIVOT = "en"

# Taille de bloc pour le téléchargement. Assez petit pour que la barre de
# progression avance visiblement, assez grand pour ne pas ralentir.
BLOC = 64 * 1024

USER_AGENT = "Jason"

# Quelques modèles publiés au catalogue sont défectueux : ils produisent du
# texte incohérent. On les remplace par une version antérieure, restée
# disponible sur le serveur d'archives officiel, qui fonctionne correctement.
#
# Vérifié le 30/07/2026 :
#   es → en   la version du catalogue (285 Mo) renvoie du charabia
#             (« mainstremainstre… »). La version 1.0 (87 Mo) est correcte.
#
# `scripts/audit_modeles.py` sert à repérer d'autres cas. Si le catalogue est
# corrigé un jour, il suffira de retirer l'entrée correspondante.
MODELES_DE_REMPLACEMENT = {
    ("es", "en"): "https://data.argosopentech.com/argospm/v1/translate-es_en-1_0.argosmodel",
}


class ErreurReseau(Exception):
    """Le catalogue ou un modèle n'a pas pu être téléchargé."""


class Annulation(Exception):
    """L'utilisateur a interrompu l'installation."""


# --------------------------------------------------------------------- catalogue


def rafraichir_catalogue() -> None:
    """Récupère la liste des langues téléchargeables. Nécessite Internet."""
    try:
        argostranslate.package.update_package_index()
    except Exception as erreur:  # noqa: BLE001
        raise ErreurReseau("Impossible de récupérer la liste des langues.") from erreur


def _couples_disponibles() -> set[tuple[str, str]]:
    return {
        (p.from_code, p.to_code)
        for p in argostranslate.package.get_available_packages()
        if p.type == "translate"
    }


def _couples_requis(code: str) -> list[tuple[str, str]]:
    """Couples à installer pour rendre une langue utilisable dans les deux sens."""
    if code == PIVOT:
        return []
    return [(code, PIVOT), (PIVOT, code)]


def langues_installables() -> list[str]:
    """Codes des langues que l'on peut ajouter, d'après le dernier catalogue.

    Une langue n'est retenue que si les deux sens existent : proposer une
    langue qu'on ne pourrait traduire que dans un sens serait déroutant.
    """
    disponibles = _couples_disponibles()
    codes = {code for couple in disponibles for code in couple} - {PIVOT}
    return sorted(
        code for code in codes if all(c in disponibles for c in _couples_requis(code))
    )


def langues_installees() -> list[str]:
    """Codes des langues réellement utilisables hors ligne, dans les deux sens.

    Une langue dont un seul sens est installé n'est pas comptée : la proposer
    reviendrait à laisser l'utilisateur choisir une langue d'arrivée vers
    laquelle Jason ne sait pas traduire.
    """
    installes = {
        (p.from_code, p.to_code)
        for p in argostranslate.package.get_installed_packages()
        if p.type == "translate"
    }
    codes = {code for couple in installes for code in couple}
    return sorted(code for code in codes if _est_complete(code, installes))


def _est_complete(code: str, installes: set[tuple[str, str]]) -> bool:
    """La langue est-elle installée dans les deux sens ?"""
    if code == PIVOT:
        # Le pivot est utilisable dès qu'un aller-retour existe avec une
        # autre langue.
        return any(depuis == PIVOT for depuis, _ in installes) and any(
            vers == PIVOT for _, vers in installes
        )
    return all(couple in installes for couple in _couples_requis(code))


def est_installee(code: str) -> bool:
    return code in langues_installees()


# ------------------------------------------------------------------ installation


def installer_langue(
    code: str,
    progression: Callable[[float], None] | None = None,
    annule: Callable[[], bool] | None = None,
) -> None:
    """Télécharge puis installe tout ce qu'il faut pour une langue.

    Opération longue (plusieurs dizaines de méga-octets) : à appeler depuis
    un thread de travail, jamais depuis l'interface.

    Args:
        code: la langue à ajouter, ex. "es".
        progression: appelée avec l'avancement entre 0.0 et 1.0. Reçoit -1.0
            si la taille totale est inconnue (avancement non chiffrable).
        annule: consultée régulièrement ; si elle renvoie True, l'installation
            s'arrête en levant `Annulation`.

    Lève `LookupError` si la langue est absente du catalogue, `ErreurReseau`
    en cas de coupure, `Annulation` si l'utilisateur interrompt.
    """
    paquets = _paquets_pour(code)
    if not paquets:
        raise LookupError(f"La langue « {code} » n'est pas disponible.")

    liens = [_lien(p) for p in paquets]

    # On mesure d'abord le total, sinon impossible d'afficher un pourcentage
    # honnête quand une langue demande plusieurs fichiers.
    tailles = [_taille_distante(lien) for lien in liens]
    total = sum(tailles) if all(tailles) else 0

    # `recus` cumule l'avancement d'un fichier à l'autre, pour que la barre
    # de progression couvre la langue entière et non chaque fichier séparément.
    recus = 0
    for taille, lien in zip(tailles, liens, strict=True):
        chemin = _telecharger(
            lien,
            deja_recus=recus,
            total=total,
            progression=progression,
            annule=annule,
        )
        try:
            argostranslate.package.install_from_path(chemin)
        finally:
            chemin.unlink(missing_ok=True)
        recus += taille

    _oublier_langues_en_memoire()

    if progression is not None:
        progression(1.0)


def _lien(paquet) -> str:
    """Adresse de téléchargement d'un modèle, remplacement compris."""
    couple = (paquet.from_code, paquet.to_code)
    return MODELES_DE_REMPLACEMENT.get(couple, paquet.links[0])


def _paquets_pour(code: str) -> list:
    """Paquets du catalogue à installer pour cette langue (ignore ceux déjà là)."""
    voulus = _couples_requis(code)
    installes = {
        (p.from_code, p.to_code) for p in argostranslate.package.get_installed_packages()
    }
    disponibles = {
        (p.from_code, p.to_code): p
        for p in argostranslate.package.get_available_packages()
        if p.type == "translate"
    }
    return [
        disponibles[couple]
        for couple in voulus
        if couple in disponibles and couple not in installes
    ]


def _taille_distante(url: str) -> int:
    """Taille annoncée par le serveur, ou 0 si elle est inconnue."""
    try:
        requete = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(requete, timeout=15) as reponse:
            return int(reponse.headers.get("Content-Length") or 0)
    except Exception:  # noqa: BLE001
        return 0


def _telecharger(
    url: str,
    deja_recus: int,
    total: int,
    progression: Callable[[float], None] | None,
    annule: Callable[[], bool] | None,
) -> Path:
    """Télécharge un modèle par morceaux, en rendant compte de l'avancement.

    Argos sait télécharger, mais d'un seul bloc et sans rien signaler : la
    fenêtre resterait muette pendant toute l'attente. On lit donc le flux
    nous-mêmes, puis on confie le fichier obtenu à Argos pour l'installation.
    """
    fichier = Path(
        tempfile.NamedTemporaryFile(suffix=".argosmodel", delete=False).name
    )
    recus = deja_recus
    try:
        requete = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(requete, timeout=30) as reponse, fichier.open("wb") as sortie:
            while True:
                if annule is not None and annule():
                    raise Annulation
                bloc = reponse.read(BLOC)
                if not bloc:
                    break
                sortie.write(bloc)
                recus += len(bloc)
                if progression is not None:
                    progression(recus / total if total else -1.0)
    except Annulation:
        fichier.unlink(missing_ok=True)
        raise
    except Exception as erreur:  # noqa: BLE001
        fichier.unlink(missing_ok=True)
        raise ErreurReseau("Le téléchargement a été interrompu.") from erreur
    return fichier


def _oublier_langues_en_memoire() -> None:
    """Fait oublier au moteur les langues qu'il croit installées.

    À appeler après toute installation ou suppression, sans quoi le moteur
    continuerait de travailler sur l'inventaire d'avant : la langue ajoutée
    resterait introuvable, la langue retirée provoquerait une erreur au
    premier essai.

    Deux mémoires à vider, et non une seule :

    - `get_installed_languages` est mise en cache ;
    - `installed_translates` est une liste globale d'Argos Translate qui
      **survit** au vidage de ce cache. Les traductions qu'elle conserve
      retiennent les objets « langue » de l'inventaire précédent. Si on la
      garde, Argos reconstruit son graphe en mélangeant objets neufs et
      objets périmés, et les traductions qui passent par l'anglais ne sont
      plus trouvées **vers** la langue qu'on vient d'installer : après avoir
      ajouté l'espagnol, français → espagnol échouait jusqu'au redémarrage,
      alors qu'espagnol → français fonctionnait.
    """
    argostranslate.translate.get_installed_languages.cache_clear()
    argostranslate.translate.installed_translates.clear()


def desinstaller_langue(code: str) -> None:
    """Supprime les modèles d'une langue, pour libérer de l'espace disque.

    Le pivot n'est jamais retiré : sans lui, plus rien ne se traduit.
    """
    if code == PIVOT:
        return
    for paquet in argostranslate.package.get_installed_packages():
        if (paquet.from_code, paquet.to_code) in _couples_requis(code):
            # `uninstall` est une fonction du module, pas une méthode du
            # paquet : `paquet.uninstall()` n'existe pas.
            argostranslate.package.uninstall(paquet)

    _oublier_langues_en_memoire()
