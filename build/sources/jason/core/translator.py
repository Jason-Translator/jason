"""Traduction de texte, hors ligne.

Ce module ne connaît rien de l'interface graphique : on peut l'utiliser
seul, depuis un script ou un test.
"""

from __future__ import annotations

import argostranslate.translate


class ErreurTraduction(Exception):
    """La traduction n'a pas pu être effectuée (langue manquante, etc.)."""


def langues_disponibles() -> list[str]:
    """Codes des langues utilisables hors ligne, d'après les modèles installés."""
    return [langue.code for langue in argostranslate.translate.get_installed_languages()]


def peut_traduire(depuis: str, vers: str) -> bool:
    """Une traduction est-elle possible entre ces deux langues ?

    Vrai aussi lorsque le moteur doit passer par une langue intermédiaire
    (français → anglais → allemand), ce qui est transparent pour l'utilisateur.
    """
    if depuis == vers:
        return True
    langues = {l.code: l for l in argostranslate.translate.get_installed_languages()}
    source, cible = langues.get(depuis), langues.get(vers)
    if source is None or cible is None:
        return False
    return source.get_translation(cible) is not None


def traduire(texte: str, depuis: str, vers: str) -> str:
    """Traduit `texte` de la langue `depuis` vers la langue `vers`.

    Opération coûteuse en calcul : toujours l'appeler depuis un thread de
    travail pour ne pas figer l'interface.
    """
    if not texte.strip():
        return ""
    if depuis == vers:
        return texte

    langues = {l.code: l for l in argostranslate.translate.get_installed_languages()}
    source, cible = langues.get(depuis), langues.get(vers)
    if source is None or cible is None:
        raise ErreurTraduction("Cette langue n'est pas installée.")

    traduction = source.get_translation(cible)
    if traduction is None:
        raise ErreurTraduction("Cette combinaison de langues n'est pas disponible.")

    return traduction.translate(texte)
