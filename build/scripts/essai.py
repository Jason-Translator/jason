"""Petit outil de vérification en console, sans interface graphique.

Sert à s'assurer que le moteur de traduction fonctionne avant de brancher
la fenêtre par-dessus.

    python scripts/essai.py --langues
    python scripts/essai.py --catalogue
    python scripts/essai.py --installer fr
    python scripts/essai.py fr en "Bonjour le monde"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "sources"))

from jason.core import languages, packages, translator  # noqa: E402


def main() -> int:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if args[0] == "--langues":
        codes = translator.langues_disponibles()
        if not codes:
            print("Aucune langue installée. Essayez : --installer fr en")
            return 0
        print("Langues installées :")
        for code in languages.trier_par_nom(codes):
            print(f"  {languages.nom(code)} ({code})")
        return 0

    if args[0] == "--catalogue":
        print("Récupération du catalogue…")
        packages.rafraichir_catalogue()
        for code in packages.langues_installables():
            etat = "installée" if packages.est_installee(code) else ""
            print(f"  {languages.nom(code)} ({code}) {etat}")
        return 0

    if args[0] == "--installer":
        code = args[1]
        print("Récupération du catalogue…")
        packages.rafraichir_catalogue()
        print(f"Installation : {languages.nom(code)}…")
        packages.installer_langue(
            code, progression=lambda f: print(f"\r  {f * 100:5.1f} %", end="", flush=True)
        )
        print("\nTerminé.")
        return 0

    depuis, vers, texte = args[0], args[1], " ".join(args[2:])
    try:
        print(translator.traduire(texte, depuis, vers))
    except translator.ErreurTraduction as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
