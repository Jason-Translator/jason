"""Point de départ de l'application."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .core import packages
from .ui import theme
from .ui.main_window import FenetrePrincipale

RESSOURCES = theme.RESSOURCES


def autotest() -> int:
    """Vérifie qu'une application empaquetée fonctionne réellement.

    Un exécutable figé peut démarrer sans erreur et pourtant être incapable
    de traduire, si une bibliothèque ou un fichier de données manque à
    l'appel. Impossible de s'en rendre compte de l'extérieur : d'où ce mode,
    lancé par `jason --autotest`, qui exerce le moteur sans ouvrir de fenêtre.

    Le compte rendu est écrit dans `autotest.log`, à côté de l'exécutable :
    sous Windows, une application sans console n'a pas de sortie standard, et
    tout affichage y serait perdu.
    """
    from .core import detect, translator

    lignes: list[str] = []

    def noter(ligne: str) -> None:
        lignes.append(ligne)
        try:
            print(ligne, flush=True)
        except Exception:  # noqa: BLE001 — pas de console : sans importance
            pass

    reussi = False
    try:
        langues = packages.langues_installees()
        noter(f"langues installées : {langues}")
        if len(langues) < 2:
            noter("AUTOTEST INCOMPLET : moins de deux langues installées.")
        else:
            depuis, vers = langues[0], langues[1]
            texte = (
                "Hello, my name is Jason."
                if depuis == "en"
                else "Bonjour, je m'appelle Jason."
            )
            noter(f"traduction {depuis}->{vers} : {translator.traduire(texte, depuis, vers)}")
            noter(f"détection : {detect.detecter(texte, langues)}")
            noter("AUTOTEST RÉUSSI")
            reussi = True
    except Exception as erreur:  # noqa: BLE001
        import traceback

        noter(f"AUTOTEST ÉCHOUÉ : {erreur}")
        noter(traceback.format_exc())

    dossier = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd()
    try:
        (dossier / "autotest.log").write_text("\n".join(lignes), encoding="utf-8")
    except OSError:
        pass

    return 0 if reussi else 1


def main() -> int:
    if "--autotest" in sys.argv:
        return autotest()

    application = QApplication(sys.argv)
    application.setApplicationName("Jason")
    application.setApplicationDisplayName("Jason")
    application.setOrganizationName("Jason")

    # Icône de la fenêtre et de la barre des tâches. Sans elle, le système
    # affiche un carré gris générique.
    application.setWindowIcon(QIcon(str(RESSOURCES / "jason.svg")))

    # Sous Wayland, c'est ce nom qui relie la fenêtre à son entrée de menu
    # (jason.desktop) : sans lui, l'icône ne suit pas dans la barre des tâches.
    application.setDesktopFileName("jason")

    # Thème retenu de la dernière session, ou le sombre au premier
    # lancement — modifiable dans les Paramètres.
    theme.appliquer(theme.theme_choisi())

    fenetre = FenetrePrincipale()
    fenetre.show()

    # Premier lancement : sans au moins deux langues, Jason ne peut rien
    # traduire. On ouvre donc d'emblée les Paramètres, sur l'onglet Langues,
    # plutôt que de laisser l'utilisateur chercher où cliquer.
    if len(packages.langues_installees()) < 2:
        fenetre.ouvrir_parametres()

    return application.exec()


if __name__ == "__main__":
    sys.exit(main())
