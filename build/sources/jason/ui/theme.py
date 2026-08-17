"""Thème clair et thème sombre.

Une feuille de style Qt ne connaît pas les variables : écrire deux fichiers
`.qss` serait la solution évidente, mais ils divergeraient dès la première
retouche — une couleur corrigée d'un côté, oubliée de l'autre.

Ici, `style.qss` ne contient aucune couleur en dur : seulement des noms entre
accolades, `{FOND}`, `{ACCENT}`… remplacés au démarrage par les valeurs du
thème choisi. Pour modifier l'apparence, on touche à ce fichier-ci ; pour
modifier la disposition, on touche à `style.qss`. Les deux ne se marchent
jamais dessus.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

RESSOURCES = Path(__file__).parent / "resources"
FEUILLE_DE_STYLE = Path(__file__).parent / "style.qss"

CLAIR = "clair"
SOMBRE = "sombre"

PALETTES: dict[str, dict[str, str]] = {
    CLAIR: {
        # Fonds, du plus reculé au plus proche.
        "FOND": "#f5f6f8",
        "SURFACE": "#ffffff",
        "SURFACE_DOUCE": "#fbfcfd",
        "SURFACE_INACTIVE": "#eceef2",
        # Textes, du plus lisible au plus discret.
        "TEXTE": "#1f2430",
        "TEXTE_DOUX": "#6b7382",
        "TEXTE_MOYEN": "#545c6b",
        "TEXTE_INACTIF": "#9aa2b1",
        # Traits.
        "BORDURE": "#e2e5ea",
        "BORDURE_NETTE": "#d8dce3",
        "BORDURE_SURVOL": "#b9c0cc",
        "BORDURE_INACTIVE": "#e6e9ef",
        # Couleur d'accent, unique dans toute l'application.
        "ACCENT": "#2f6fed",
        "ACCENT_SURVOL": "#245ad4",
        "ACCENT_APPUI": "#1d4cb4",
        "ACCENT_INACTIF": "#dfe3ea",
        "ACCENT_VOILE": "#eef3ff",
        "ACCENT_PALE": "#b6c6e8",
        "SELECTION": "#cfe0ff",
        "SURVOL_DOUX": "#f2f6ff",
        # Icônes dessinées : leur couleur est dans le fichier, on change donc
        # de fichier plutôt que de couleur.
        "CHEVRON": "chevron.svg",
    },
    SOMBRE: {
        # Gris bleutés plutôt que noir pur : moins fatigant, et les ombres
        # portées restent visibles.
        "FOND": "#14161b",
        "SURFACE": "#1d2028",
        "SURFACE_DOUCE": "#191c23",
        "SURFACE_INACTIVE": "#22252d",
        "TEXTE": "#e7e9ee",
        "TEXTE_DOUX": "#98a0af",
        "TEXTE_MOYEN": "#aeb6c4",
        "TEXTE_INACTIF": "#666e7d",
        "BORDURE": "#2b2f39",
        "BORDURE_NETTE": "#343945",
        "BORDURE_SURVOL": "#454b59",
        "BORDURE_INACTIVE": "#262a33",
        # Accent éclairci : le bleu du thème clair devient illisible sur fond
        # sombre, l'œil ne distingue plus le texte blanc qu'il porte.
        "ACCENT": "#4c8dff",
        "ACCENT_SURVOL": "#5f9bff",
        "ACCENT_APPUI": "#3d7ae6",
        "ACCENT_INACTIF": "#2b3038",
        "ACCENT_VOILE": "#1e2a40",
        "ACCENT_PALE": "#31456b",
        "SELECTION": "#2c4a7a",
        "SURVOL_DOUX": "#232833",
        "CHEVRON": "chevron-clair.svg",
    },
}


def _reglages() -> QSettings:
    return QSettings("Jason", "Jason")


def theme_choisi() -> str:
    """Le thème retenu de la dernière session, ou le sombre au premier lancement."""
    enregistre = _reglages().value("theme", "")
    return enregistre if enregistre in PALETTES else SOMBRE


def enregistrer(nom: str) -> None:
    _reglages().setValue("theme", nom)


def feuille_de_style(nom: str) -> str:
    """Construit la feuille de style du thème demandé."""
    if not FEUILLE_DE_STYLE.exists():
        return ""

    style = FEUILLE_DE_STYLE.read_text(encoding="utf-8")

    # Qt résout les `url()` d'une feuille de style par rapport au dossier
    # courant du programme, pas par rapport au fichier .qss : les icônes
    # disparaîtraient selon l'endroit d'où Jason est lancé. D'où le chemin
    # absolu, écrit au démarrage.
    style = style.replace("{RESSOURCES}", RESSOURCES.as_posix())

    for cle, valeur in PALETTES[nom].items():
        style = style.replace("{" + cle + "}", valeur)
    return style


def appliquer(nom: str) -> None:
    """Change le thème de toute l'application, fenêtres déjà ouvertes comprises."""
    application = QApplication.instance()
    if application is not None:
        application.setStyleSheet(feuille_de_style(nom))
