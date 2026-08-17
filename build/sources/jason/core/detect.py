"""Reconnaissance automatique de la langue d'un texte.

Entièrement hors ligne, comme le reste de Jason.

La reconnaissance est volontairement limitée aux langues installées : c'est
la seule chose que l'utilisateur puisse ensuite traduire, et restreindre le
choix améliore nettement la fiabilité sur les textes courts.
"""

from __future__ import annotations

from functools import lru_cache

from lingua import IsoCode639_1, LanguageDetectorBuilder

# Nombre minimum de langues pour que la question « laquelle ? » ait un sens.
MINIMUM_LANGUES = 2

# Écart minimal entre la langue la mieux placée et la suivante. En dessous,
# on considère que le texte est ambigu et on préfère l'avouer.
#
# Exemple réel : « Hola, me llamo Jason. » donne espagnol 0,38 contre anglais
# 0,42 — le prénom anglais suffit à faire pencher la balance. Trancher au plus
# fort produirait une traduction incohérente sans que l'utilisateur comprenne
# pourquoi ; mieux vaut lui demander de choisir la langue.
MARGE_MINIMALE = 0.15


def _connue(code: str) -> IsoCode639_1 | None:
    """Convertit un code de langue en code reconnu par le détecteur.

    Certaines langues du catalogue n'existent pas côté détection (« zt »,
    le chinois traditionnel, par exemple) : on les ignore plutôt que de
    refuser de détecter quoi que ce soit.
    """
    return getattr(IsoCode639_1, code.upper(), None)


@lru_cache(maxsize=4)
def _detecteur(codes: tuple[str, ...]):
    """Construit un détecteur pour un jeu de langues donné.

    La construction charge des modèles et coûte du temps : on la garde en
    mémoire, et elle n'est refaite que si la liste des langues change.
    """
    connus = [c for c in (_connue(code) for code in codes) if c is not None]
    if len(connus) < MINIMUM_LANGUES:
        return None
    return LanguageDetectorBuilder.from_iso_codes_639_1(*connus).build()


def detecter(texte: str, langues_possibles: list[str]) -> str | None:
    """Reconnaît la langue de `texte` parmi `langues_possibles`.

    Renvoie le code de la langue, ou None si le texte est trop court ou trop
    ambigu pour se prononcer. Dans ce cas, mieux vaut demander à
    l'utilisateur que de traduire depuis une langue devinée au hasard.

    Opération pouvant charger des modèles au premier appel : à exécuter dans
    un thread de travail.
    """
    if not texte.strip():
        return None

    detecteur = _detecteur(tuple(sorted(langues_possibles)))
    if detecteur is None:
        # Une seule langue installée : inutile de deviner.
        return langues_possibles[0] if langues_possibles else None

    scores = detecteur.compute_language_confidence_values(texte)
    if not scores:
        return None

    meilleur = scores[0]
    suivant = scores[1].value if len(scores) > 1 else 0.0
    if meilleur.value - suivant < MARGE_MINIMALE:
        return None

    code = meilleur.language.iso_code_639_1.name.lower()
    # Le détecteur peut nommer une langue que Jason ne sait pas traduire.
    return code if code in langues_possibles else None
