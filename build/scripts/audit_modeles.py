"""Contrôle la qualité des modèles installés.

Certains modèles publiés en amont sont défectueux : ils renvoient du texte
incohérent, souvent un même fragment répété des centaines de fois. Le défaut
ne se voit pas à l'installation, seulement à l'usage.

Ce script traduit une phrase témoin avec chaque langue installée et signale
les résultats suspects. Il ne télécharge rien.

    python scripts/audit_modeles.py

Les langues signalées ici doivent être ajoutées à MODELES_DE_REMPLACEMENT
dans core/packages.py, avec une version de rechange qui fonctionne.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "sources"))

from jason.core import languages, packages, translator  # noqa: E402

TEMOIN = "Hello, my name is Jason. I live in France and I like reading."


def est_suspect(texte: str) -> str | None:
    """Renvoie la raison de la suspicion, ou None si le texte semble correct."""
    if not texte.strip():
        return "réponse vide"
    if "@@" in texte:
        # Marqueur de découpage interne qui ne devrait jamais ressortir.
        return "marqueurs de découpage visibles"
    if len(texte) > 8 * len(TEMOIN):
        return f"réponse démesurée ({len(texte)} caractères)"
    mots = texte.split()
    if len(mots) > 6 and len(set(mots)) <= len(mots) // 4:
        return "texte répétitif"
    return None


def main() -> int:
    codes = [c for c in packages.langues_installees() if c != packages.PIVOT]
    if not codes:
        print("Aucune langue installée.")
        return 0

    print(f"Contrôle de {len(codes)} langue(s), dans les deux sens.\n")
    problemes = 0

    for code in languages.trier_par_nom(codes):
        nom = languages.nom(code)
        for depuis, vers, source in (
            (packages.PIVOT, code, TEMOIN),
            (code, packages.PIVOT, None),
        ):
            if source is None:
                # On repart de la traduction précédente pour rester réaliste.
                source = translator.traduire(TEMOIN, packages.PIVOT, code)
            try:
                resultat = translator.traduire(source, depuis, vers)
            except translator.ErreurTraduction as erreur:
                print(f"  {nom} ({depuis}→{vers}) : ERREUR — {erreur}")
                problemes += 1
                continue

            raison = est_suspect(resultat)
            if raison:
                print(f"  {nom} ({depuis}→{vers}) : SUSPECT — {raison}")
                print(f"      {resultat[:100]}…")
                problemes += 1
            else:
                print(f"  {nom} ({depuis}→{vers}) : ok — {resultat[:60]}")

    print()
    print("Aucun problème détecté." if not problemes else f"{problemes} problème(s).")
    return 1 if problemes else 0


if __name__ == "__main__":
    sys.exit(main())
