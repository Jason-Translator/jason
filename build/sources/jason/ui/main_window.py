"""La fenêtre principale : deux zones de texte et deux menus de langues.

Tout ce que l'utilisateur doit comprendre en un coup d'œil : j'écris à
gauche, je lis à droite. Rien à configurer, rien à valider.
"""

from __future__ import annotations

from PySide6.QtCore import QLocale, QSize, Qt, QTimer, Slot
from PySide6.QtGui import QGuiApplication, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core import languages, packages, translator
from ..workers import ServiceTraduction
from . import theme
from .settings import FenetreParametres

# Délai d'attente après la dernière frappe avant de lancer la traduction.
# Trop court, on traduit des phrases à moitié écrites ; trop long, l'app
# paraît lente. 400 ms correspond à une courte pause dans la frappe.
DELAI_FRAPPE_MS = 400

MESSAGE_REPOS = "Hors ligne — vos textes ne quittent jamais votre ordinateur."
DETECTION_AUTO = "Détecter la langue"


class FenetrePrincipale(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jason")
        self.resize(940, 580)
        self.setMinimumSize(680, 420)

        # Dernière langue reconnue automatiquement, retenue pour l'inversion.
        self._langue_detectee = ""

        self._theme = theme.theme_choisi()

        self._service = ServiceTraduction(self)
        self._service.resultat.connect(self._afficher_traduction)
        self._service.erreur.connect(self._afficher_erreur)

        # Déclenche la traduction une fois la frappe retombée.
        self._minuteur = QTimer(self)
        self._minuteur.setSingleShot(True)
        self._minuteur.setInterval(DELAI_FRAPPE_MS)
        self._minuteur.timeout.connect(self._traduire)

        self._construire()
        self._remplir_langues()

    # ------------------------------------------------------------------ mise en place

    def _construire(self) -> None:
        central = QWidget()
        colonne = QVBoxLayout(central)
        colonne.setContentsMargins(20, 18, 20, 14)
        colonne.setSpacing(14)

        colonne.addLayout(self._barre_langues())
        colonne.addWidget(self._zones_de_texte(), stretch=1)
        colonne.addLayout(self._barre_basse())

        self.setCentralWidget(central)

        raccourci_copie = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        raccourci_copie.activated.connect(self._copier)

    def _barre_langues(self) -> QHBoxLayout:
        barre = QHBoxLayout()
        barre.setSpacing(10)

        self.choix_source = QComboBox()
        self.choix_source.setObjectName("choixLangue")
        self.choix_source.currentIndexChanged.connect(self._traduire)

        self.bouton_echange = QPushButton("⇄")
        self.bouton_echange.setObjectName("boutonEchange")
        self.bouton_echange.setToolTip("Inverser les deux langues")
        self.bouton_echange.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_echange.clicked.connect(self._echanger_langues)

        self.choix_cible = QComboBox()
        self.choix_cible.setObjectName("choixLangue")
        self.choix_cible.currentIndexChanged.connect(self._traduire)

        barre.addWidget(self.choix_source, stretch=1)
        barre.addWidget(self.bouton_echange)
        barre.addWidget(self.choix_cible, stretch=1)
        return barre

    def _zones_de_texte(self) -> QSplitter:
        self.saisie = QTextEdit()
        self.saisie.setObjectName("saisie")
        self.saisie.setPlaceholderText("Écrivez ou collez votre texte ici…")
        self.saisie.setAcceptRichText(False)  # un copier-coller ne doit pas
        self.saisie.textChanged.connect(self._sur_frappe)  # importer une mise en forme

        self.resultat = QTextEdit()
        self.resultat.setObjectName("resultat")
        self.resultat.setReadOnly(True)
        self.resultat.setPlaceholderText("La traduction apparaîtra ici.")

        separateur = QSplitter(Qt.Orientation.Horizontal)
        separateur.addWidget(self.saisie)
        separateur.addWidget(self.resultat)
        separateur.setSizes([1, 1])
        separateur.setChildrenCollapsible(False)
        separateur.setHandleWidth(14)
        return separateur

    def _barre_basse(self) -> QHBoxLayout:
        barre = QHBoxLayout()

        self.etat = QLabel(MESSAGE_REPOS)
        self.etat.setObjectName("etat")

        self.bouton_parametres = QPushButton()
        self.bouton_parametres.setObjectName("boutonIcone")
        self.bouton_parametres.setIconSize(QSize(18, 18))
        self.bouton_parametres.setToolTip("Paramètres")
        self.bouton_parametres.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_parametres.clicked.connect(self.ouvrir_parametres)

        self.bouton_copier = QPushButton()
        self.bouton_copier.setObjectName("boutonCopier")
        self.bouton_copier.setIconSize(QSize(18, 18))
        self.bouton_copier.setToolTip("Copier la traduction (Ctrl+Shift+C)")
        self.bouton_copier.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_copier.setEnabled(False)
        self.bouton_copier.clicked.connect(self._copier)

        self._rafraichir_icones()

        barre.addWidget(self.etat, stretch=1)
        barre.addWidget(self.bouton_parametres)
        barre.addWidget(self.bouton_copier)
        return barre

    @Slot()
    def ouvrir_parametres(self) -> None:
        """Ouvre les Paramètres, puis prend en compte ce qui y a changé."""
        fenetre = FenetreParametres(self)
        fenetre.exec()

        # Le thème a pu changer dans l'onglet Apparence : les icônes de cette
        # fenêtre doivent suivre (la feuille de style, elle, suit déjà toute
        # seule, appliquée à l'application entière).
        self._theme = theme.theme_choisi()
        self._rafraichir_icones()

        if fenetre.langues_modifiees:
            self._reactiver()
            self._remplir_langues()
            self._traduire()

    def _reactiver(self) -> None:
        """Sort du mode « aucune langue » après une première installation."""
        self.saisie.setEnabled(True)
        self.bouton_echange.setEnabled(True)
        self.saisie.setPlaceholderText("Écrivez ou collez votre texte ici…")
        self.etat.setText(MESSAGE_REPOS)

    def _remplir_langues(self) -> None:
        """Remplit les menus avec les langues réellement installées.

        On s'appuie sur l'inventaire des modèles plutôt que sur le moteur :
        celui-ci connaît aussi les langues à moitié installées, qu'on ne veut
        pas proposer.
        """
        codes = languages.trier_par_nom(packages.langues_installees())

        for menu in (self.choix_source, self.choix_cible):
            menu.blockSignals(True)
            menu.clear()
            if menu is self.choix_source:
                # En tête de liste, et sélectionné par défaut : dans le doute,
                # l'utilisateur n'a rien à choisir. La donnée vide signale au
                # service qu'il doit reconnaître la langue lui-même.
                menu.addItem(DETECTION_AUTO, userData="")
            for code in codes:
                menu.addItem(languages.nom(code), userData=code)
            menu.blockSignals(False)

        if len(codes) < 2:
            self._passer_en_mode_sans_langue()
            return

        # Source : reconnaissance automatique, pour n'avoir rien à régler.
        # Cible : la langue du système, celle vers laquelle on traduit le
        # plus souvent quand on ne comprend pas un texte.
        self.choix_source.blockSignals(True)
        self.choix_source.setCurrentIndex(0)
        self.choix_source.blockSignals(False)
        self._choisir(self.choix_cible, QLocale.system().name().split("_")[0], repli=0)

    def _passer_en_mode_sans_langue(self) -> None:
        """Aucune traduction possible : on le dit clairement, sans jargon."""
        self.saisie.setEnabled(False)
        self.bouton_echange.setEnabled(False)
        # Court volontairement : QTextEdit ne renvoie pas ce texte à la ligne
        # et le tronquerait. L'explication complète va dans la ligne d'état.
        self.saisie.setPlaceholderText("Aucune langue installée.")
        self.etat.setText("Ajoutez au moins deux langues pour commencer à traduire.")

    def _choisir(self, menu: QComboBox, code: str, repli: int) -> None:
        """Sélectionne une langue par son code, ou l'entrée `repli` à défaut."""
        index = menu.findData(code)
        menu.blockSignals(True)
        menu.setCurrentIndex(index if index >= 0 else repli)
        menu.blockSignals(False)

    # ------------------------------------------------------------------ traduction

    @Slot()
    def _sur_frappe(self) -> None:
        # Chaque frappe repousse l'échéance : on ne traduit qu'une fois la
        # phrase posée, pas à chaque lettre.
        self._minuteur.start()

    @Slot()
    def _traduire(self) -> None:
        self._minuteur.stop()
        texte = self.saisie.toPlainText()
        depuis = self.choix_source.currentData()
        vers = self.choix_cible.currentData()

        if not texte.strip() or depuis is None or vers is None:
            self.resultat.clear()
            self.bouton_copier.setEnabled(False)
            self.etat.setText(MESSAGE_REPOS)
            return

        # En reconnaissance automatique (`depuis` vide), on ne peut pas savoir
        # d'avance si la traduction sera possible : c'est le service qui
        # tranchera, une fois la langue identifiée.
        if depuis and not translator.peut_traduire(depuis, vers):
            self.resultat.clear()
            self.bouton_copier.setEnabled(False)
            self.etat.setText(
                f"La traduction de {languages.nom(depuis)} vers "
                f"{languages.nom(vers)} n'est pas encore installée."
            )
            return

        self.etat.setText("Traduction en cours…")
        self._service.demander(texte, depuis, vers)

    def _cible_de_repli(self, depuis: str) -> str | None:
        """Langue d'arrivée à utiliser quand la cible actuelle est la langue
        du texte saisi.

        Par ordre de préférence : l'anglais, que l'on cherche le plus souvent
        à obtenir ; puis la langue du système, celle que l'utilisateur
        comprend ; puis n'importe quelle autre langue installée. Sans cet
        ordre, un texte anglais serait traduit vers la première langue venue.
        """
        codes = [
            self.choix_cible.itemData(rang) for rang in range(self.choix_cible.count())
        ]
        autres = [code for code in codes if code and code != depuis]
        if not autres:
            return None

        for prefere in ("en", QLocale.system().name().split("_")[0]):
            if prefere in autres:
                return prefere
        return autres[0]

    @Slot(str, str)
    def _afficher_traduction(self, texte: str, depuis: str) -> None:
        # Reconnaissance automatique tombée sur la langue d'arrivée : le texte
        # ressort identique et Jason paraît ne rien faire. On bascule vers une
        # autre langue, comme le ferait n'importe quel traducteur en ligne.
        if self.choix_source.currentData() == "" and depuis == self.choix_cible.currentData():
            repli = self._cible_de_repli(depuis)
            if repli is not None:
                self._choisir(self.choix_cible, repli, repli=0)
                self._langue_detectee = depuis
                self._traduire()
                return

        self.resultat.setPlainText(texte)
        self.bouton_copier.setEnabled(bool(texte))
        self._langue_detectee = depuis

        if self.choix_source.currentData() == "":
            # On dit quelle langue a été reconnue : sinon, en cas d'erreur de
            # reconnaissance, l'utilisateur n'a aucun moyen de comprendre
            # pourquoi la traduction est incohérente.
            self.etat.setText(f"Langue reconnue : {languages.nom(depuis)}")
        else:
            self.etat.setText(MESSAGE_REPOS)

    @Slot(str)
    def _afficher_erreur(self, message: str) -> None:
        self.resultat.clear()
        self.bouton_copier.setEnabled(False)
        self.etat.setText(message)

    # ------------------------------------------------------------------ actions

    @Slot()
    def _echanger_langues(self) -> None:
        source = self.choix_source.currentData()
        cible = self.choix_cible.currentData()

        # En reconnaissance automatique, on inverse à partir de la langue
        # effectivement reconnue ; sans traduction encore faite, il n'y a
        # rien à inverser.
        if source == "":
            if not self._langue_detectee:
                return
            source = self._langue_detectee

        self._choisir(self.choix_source, cible, repli=0)
        self._choisir(self.choix_cible, source, repli=0)

        # On échange aussi les textes : c'est ce à quoi l'utilisateur
        # s'attend quand il veut « répondre » dans l'autre langue.
        traduction = self.resultat.toPlainText()
        if traduction:
            self.saisie.blockSignals(True)
            self.saisie.setPlainText(traduction)
            self.saisie.blockSignals(False)

        self._traduire()

    @Slot()
    def _copier(self) -> None:
        texte = self.resultat.toPlainText()
        if not texte:
            return
        QGuiApplication.clipboard().setText(texte)
        self.etat.setText("Traduction copiée.")
        QTimer.singleShot(2000, lambda: self.etat.setText(MESSAGE_REPOS))

    def _rafraichir_icones(self) -> None:
        """Choisit les fichiers d'icônes adaptés au thème en cours.

        Les dessins portent leur couleur en dur : un trait sombre disparaît
        sur fond sombre, d'où un fichier par thème (même motif que le chevron
        des menus). L'icône de copie, posée sur le bouton d'accent bleu, est
        blanche dans les deux thèmes.
        """
        rouage = "rouage-clair.svg" if self._theme == theme.SOMBRE else "rouage.svg"
        self.bouton_parametres.setIcon(QIcon(str(theme.RESSOURCES / rouage)))
        self.bouton_copier.setIcon(QIcon(str(theme.RESSOURCES / "copier-blanc.svg")))

    def closeEvent(self, event) -> None:  # noqa: N802 (nom imposé par Qt)
        self._service.arreter()
        super().closeEvent(event)
