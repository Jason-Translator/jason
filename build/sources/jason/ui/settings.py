"""Fenêtre Paramètres : gérer ses langues, choisir son thème, lire les crédits.

Tout ce qui n'est pas « écrire à gauche, lire à droite » se range ici, derrière
le bouton rouage de la fenêtre principale — la fenêtre de traduction reste
ainsi vide de tout réglage.

L'onglet Langues est l'unique endroit où l'on gère ses langues : une seule
liste, où chaque ligne porte son action — télécharger celles qui manquent,
supprimer celles qu'on n'utilise plus. C'est aussi l'écran proposé au premier
lancement, quand il n'y a encore rien à traduire.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core import languages, packages
from ..workers import ServiceLangues
from . import theme

# Texte de l'onglet « À propos ». Il vit dans un fichier à part, en Markdown,
# pour se corriger sans toucher au code : modifiez `resources/a-propos.md`,
# rouvrez les Paramètres, le nouveau texte s'affiche. Qt sait rendre le
# Markdown tout seul (titres, gras, listes), aucune visionneuse à écrire.
FICHIER_A_PROPOS = "a-propos.md"

# Affiché seulement si le fichier manque — un paquet mal construit, par
# exemple. Mieux vaut une fenêtre incomplète qu'une fenêtre qui refuse de
# s'ouvrir.
A_PROPOS_DE_SECOURS = "## Jason\n\nUn traducteur qui fonctionne hors ligne."

NOTE_LANGUES = (
    "Chaque langue est téléchargée une seule fois : ensuite, Jason traduit "
    "sans connexion. Supprimer une langue efface ses fichiers de votre "
    "ordinateur ; vous pourrez la réinstaller à tout moment."
)


class FenetreParametres(QDialog):
    """Trois onglets : Langues, Apparence, À propos."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Jason — Paramètres")
        self.setModal(True)
        self.resize(520, 600)

        # La fenêtre principale lit ce drapeau à la fermeture : si des langues
        # ont été ajoutées ou supprimées, ses menus doivent être refaits.
        self.langues_modifiees = False

        self._catalogue: list[str] = []  # langues téléchargeables, une fois le réseau passé
        # File d'attente des installations : le premier code est celui en
        # cours, les suivants patientent. On peut donc lancer plusieurs
        # téléchargements d'affilée sans attendre la fin du précédent.
        self._file: list[str] = []
        self._echecs: list[str] = []  # langues de la file qui n'ont pas abouti

        self._service = ServiceLangues(self)
        self._service.catalogue_pret.connect(self._catalogue_recu)
        self._service.catalogue_echoue.connect(self._catalogue_en_echec)
        self._service.progression.connect(self._afficher_progression)
        self._service.langue_installee.connect(self._langue_installee)
        self._service.installation_finie.connect(self._installation_finie)
        self._service.installation_echouee.connect(self._installation_echouee)
        self._service.installation_annulee.connect(self._installation_annulee)

        colonne = QVBoxLayout(self)
        colonne.setContentsMargins(20, 18, 20, 16)
        colonne.setSpacing(12)

        # Construits avant les onglets : la liste des langues les consulte.
        self._construire_progression()

        onglets = QTabWidget()
        onglets.addTab(self._onglet_langues(), "Langues")
        onglets.addTab(self._onglet_apparence(), "Apparence")
        onglets.addTab(self._onglet_a_propos(), "À propos")
        colonne.addWidget(onglets, stretch=1)

        # Progression et ligne d'état vivent hors des onglets : un
        # téléchargement continue quand on va lire les crédits, et on doit
        # pouvoir le suivre — et l'annuler — depuis n'importe quel onglet.
        colonne.addWidget(self.barre)

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.setObjectName("boutonSecondaire")
        bouton_fermer.setCursor(Qt.CursorShape.PointingHandCursor)
        bouton_fermer.clicked.connect(self.accept)

        barre_basse = QHBoxLayout()
        barre_basse.addWidget(self.etat, stretch=1)
        barre_basse.addWidget(self.bouton_annuler)
        barre_basse.addWidget(self.bouton_reessayer)
        barre_basse.addWidget(bouton_fermer)
        colonne.addLayout(barre_basse)

        self._service.charger_catalogue()

    # ------------------------------------------------------------------ langues

    def _onglet_langues(self) -> QWidget:
        page = QWidget()
        colonne = QVBoxLayout(page)
        colonne.setContentsMargins(4, 12, 4, 4)
        colonne.setSpacing(10)

        note = QLabel(NOTE_LANGUES)
        note.setObjectName("note")
        note.setWordWrap(True)
        colonne.addWidget(note)

        self.liste = QListWidget()
        self.liste.setObjectName("listeLangues")
        # Les lignes ne se sélectionnent pas : toute l'action passe par les
        # boutons qu'elles portent.
        self.liste.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.liste.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        colonne.addWidget(self.liste, stretch=1)

        self._remplir_liste()
        return page

    def _construire_progression(self) -> None:
        """Barre de progression et ligne d'état, communes à toute la fenêtre."""
        self.barre = QProgressBar()
        self.barre.setObjectName("barre")
        self.barre.setTextVisible(False)
        self.barre.hide()

        self.etat = QLabel("Récupération de la liste des langues…")
        self.etat.setObjectName("etat")
        self.etat.setWordWrap(True)

        self.bouton_annuler = QPushButton("Annuler")
        self.bouton_annuler.setObjectName("boutonSecondaire")
        self.bouton_annuler.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_annuler.clicked.connect(self._annuler)
        self.bouton_annuler.hide()

        self.bouton_reessayer = QPushButton("Réessayer")
        self.bouton_reessayer.setObjectName("boutonSecondaire")
        self.bouton_reessayer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bouton_reessayer.clicked.connect(self._reessayer)
        self.bouton_reessayer.hide()

    def _icone(self, nom_base: str) -> QIcon:
        """L'icône adaptée au thème en cours (un fichier par thème)."""
        variante = f"{nom_base}-clair.svg" if theme.theme_choisi() == theme.SOMBRE else f"{nom_base}.svg"
        return QIcon(str(theme.RESSOURCES / variante))

    def _remplir_liste(self) -> None:
        """Reconstruit la liste : langues installées d'abord, puis disponibles."""
        self.liste.clear()

        installees = languages.trier_par_nom(packages.langues_installees())
        disponibles = [
            code
            for code in languages.trier_par_nom(self._catalogue)
            if code not in installees
        ]

        if installees:
            self._ajouter_entete("INSTALLÉES")
            for code in installees:
                self._ajouter_ligne(code, installee=True)
        if disponibles:
            self._ajouter_entete("DISPONIBLES")
            for code in disponibles:
                self._ajouter_ligne(code, installee=False)

    def _ajouter_entete(self, texte: str) -> None:
        etiquette = QLabel(texte)
        etiquette.setObjectName("enteteListe")
        element = QListWidgetItem()
        element.setFlags(Qt.ItemFlag.NoItemFlags)
        # Hauteur fixée à la main : le sizeHint du widget est calculé avant
        # que la feuille de style ne s'applique, et serait trop petit. Elle
        # doit loger le libellé ET les 9 px de marge que la feuille de style
        # donne à chaque élément de la liste, en haut comme en bas.
        element.setSizeHint(QSize(0, 44))
        self.liste.addItem(element)
        self.liste.setItemWidget(element, etiquette)

    def _mention(self, texte: str) -> QLabel:
        """Petit texte gris en bout de ligne, à la place d'un bouton."""
        etiquette = QLabel(texte)
        etiquette.setObjectName("note")
        return etiquette

    def _ajouter_ligne(self, code: str, installee: bool) -> None:
        ligne = QWidget()
        disposition = QHBoxLayout(ligne)
        disposition.setContentsMargins(8, 2, 4, 2)
        disposition.setSpacing(8)

        etiquette = QLabel(languages.nom(code))
        if not installee:
            etiquette.setObjectName("langueDisponible")
        disposition.addWidget(etiquette)
        disposition.addStretch(1)

        if installee and code == packages.PIVOT:
            # Pas de poubelle pour le pivot : sans l'anglais, qui relie les
            # autres langues entre elles, plus rien ne se traduit.
            disposition.addWidget(self._mention("pivot, toujours installé"))
        elif code in self._file:
            # Déjà demandée : on montre où elle en est plutôt qu'un bouton
            # grisé, qui n'expliquerait pas pourquoi il ne répond plus.
            en_cours = code == self._file[0]
            disposition.addWidget(
                self._mention("téléchargement…" if en_cours else "en attente")
            )
        else:
            bouton = QPushButton()
            bouton.setObjectName("boutonLigne")
            bouton.setIconSize(QSize(18, 18))
            bouton.setCursor(Qt.CursorShape.PointingHandCursor)
            # Sans quoi le premier bouton prend le focus à l'ouverture et la
            # liste défile pour l'atteindre, cachant l'en-tête au-dessus.
            bouton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            if installee:
                bouton.setIcon(self._icone("poubelle"))
                bouton.setToolTip("Supprimer cette langue")
                bouton.clicked.connect(lambda _=False, c=code: self._supprimer(c))
                # Supprimer pendant qu'un téléchargement écrit dans le même
                # dossier reviendrait à se tirer dans le pied : on attend.
                bouton.setEnabled(not self._file)
            else:
                bouton.setIcon(self._icone("telecharger"))
                bouton.setToolTip("Télécharger et installer cette langue")
                bouton.clicked.connect(lambda _=False, c=code: self._installer(c))
            disposition.addWidget(bouton)

        element = QListWidgetItem()
        element.setFlags(Qt.ItemFlag.ItemIsEnabled)
        # Même remarque que pour les en-têtes : hauteur fixée à la main.
        element.setSizeHint(QSize(0, 38))
        self.liste.addItem(element)
        self.liste.setItemWidget(element, ligne)

    # ----------------------------------------------------------- catalogue

    @Slot(list)
    def _catalogue_recu(self, codes: list[str]) -> None:
        self._catalogue = codes
        # Ne pas écraser l'avancement d'un téléchargement déjà lancé : le
        # catalogue peut arriver (ou être rechargé) pendant celui-ci.
        if not self._file:
            self.etat.setText("")
        self._remplir_liste()
        self.liste.scrollToTop()

    @Slot(str)
    def _catalogue_en_echec(self, message: str) -> None:
        self.etat.setText(
            "Impossible de récupérer la liste des langues — une connexion "
            "Internet est nécessaire, mais uniquement pour en ajouter."
        )
        self.bouton_reessayer.show()

    @Slot()
    def _reessayer(self) -> None:
        self.bouton_reessayer.hide()
        self.etat.setText("Récupération de la liste des langues…")
        self._service.charger_catalogue()

    # -------------------------------------------------------- installation

    def _installer(self, code: str) -> None:
        """Met une langue dans la file : elle part maintenant, ou à son tour."""
        if code in self._file:
            return
        demarrer = not self._file
        self._file.append(code)
        self._remplir_liste()
        if demarrer:
            self._lancer_prochaine()
        else:
            # Le téléchargement en cours continue : on annonce seulement que
            # la file s'est allongée, sans attendre le prochain palier.
            self.etat.setText(self._texte_etat(self._file[0]))

    def _lancer_prochaine(self) -> None:
        """Lance le téléchargement de la première langue de la file."""
        code = self._file[0]
        self.barre.show()
        self.barre.setRange(0, 100)
        self.barre.setValue(0)
        self.bouton_annuler.setEnabled(True)
        self.bouton_annuler.show()
        self.etat.setText(self._texte_etat(code))
        self._service.installer([code])

    def _texte_etat(self, code: str) -> str:
        """Ligne d'état pendant un téléchargement, file d'attente comprise."""
        # Tournure sans article : « du espagnol » serait fautif, et gérer
        # l'élision (« de l'espagnol », « du français ») pour cinquante
        # langues ne vaut pas la complexité.
        texte = f"Téléchargement : {languages.nom(code)}…"
        restantes = len(self._file) - 1
        if restantes == 1:
            texte += "  (1 langue en attente)"
        elif restantes > 1:
            texte += f"  ({restantes} langues en attente)"
        return texte

    @Slot(str, float)
    def _afficher_progression(self, code: str, fraction: float) -> None:
        if fraction < 0:
            # Taille inconnue : barre animée sans pourcentage, plutôt qu'un
            # chiffre inventé.
            self.barre.setRange(0, 0)
        else:
            self.barre.setRange(0, 100)
            self.barre.setValue(int(fraction * 100))
        self.etat.setText(self._texte_etat(code))

    @Slot(str)
    def _langue_installee(self, code: str) -> None:
        # Une langue de plus est utilisable : la fenêtre principale devra
        # refaire ses menus, même si la file n'est pas encore vide.
        self.langues_modifiees = True

    @Slot()
    def _installation_finie(self) -> None:
        self._passer_a_la_suite()

    @Slot(str, str)
    def _installation_echouee(self, code: str, message: str) -> None:
        # On note l'échec et on continue : une langue qui manque au catalogue
        # ne doit pas emporter avec elle celles qui attendaient derrière.
        self._echecs.append(f"{languages.nom(code)} : {message}")
        self._passer_a_la_suite()

    @Slot()
    def _installation_annulee(self) -> None:
        # Annuler annule tout : n'interrompre que le téléchargement en cours
        # pour enchaîner sur le suivant serait déroutant.
        self._file.clear()
        self._fin_installation()
        self.etat.setText("Installation annulée.")

    def _passer_a_la_suite(self) -> None:
        """Retire la langue traitée et enchaîne, ou termine la file."""
        if self._file:
            self._file.pop(0)
        if self._file:
            self._remplir_liste()
            self._lancer_prochaine()
            return
        self._fin_installation()
        self.etat.setText("  ·  ".join(self._echecs))
        self._echecs.clear()

    def _fin_installation(self) -> None:
        """Remet la fenêtre en état de repos, quelle que soit l'issue."""
        self.barre.hide()
        self.bouton_annuler.hide()
        self._remplir_liste()

    @Slot()
    def _annuler(self) -> None:
        self.etat.setText("Annulation…")
        self.bouton_annuler.setEnabled(False)
        self._service.annuler()

    # --------------------------------------------------------- suppression

    def _supprimer(self, code: str) -> None:
        if self._file:
            return
        reponse = QMessageBox.question(
            self,
            "Supprimer une langue",
            f"Supprimer {languages.nom(code)} ?\n\n"
            "Ses fichiers seront effacés de votre ordinateur. Vous pourrez "
            "la réinstaller à tout moment.",
        )
        if reponse != QMessageBox.StandardButton.Yes:
            return

        # Suppression de fichiers locaux : rapide, mais pas instantanée — le
        # curseur d'attente évite un clic dans le vide pendant l'opération.
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            packages.desinstaller_langue(code)
        finally:
            QApplication.restoreOverrideCursor()

        self.langues_modifiees = True
        self._remplir_liste()

    # ------------------------------------------------------------------ apparence

    def _onglet_apparence(self) -> QWidget:
        page = QWidget()
        colonne = QVBoxLayout(page)
        colonne.setContentsMargins(4, 12, 4, 4)
        colonne.setSpacing(10)

        sombre_actif = theme.theme_choisi() == theme.SOMBRE

        self.choix_sombre = QRadioButton("Sombre")
        self.choix_sombre.setChecked(sombre_actif)
        self.choix_sombre.toggled.connect(self._changer_theme)

        self.choix_clair = QRadioButton("Clair")
        self.choix_clair.setChecked(not sombre_actif)

        colonne.addWidget(self.choix_sombre)
        colonne.addWidget(self.choix_clair)
        colonne.addStretch(1)
        return page

    @Slot(bool)
    def _changer_theme(self, sombre: bool) -> None:
        nom = theme.SOMBRE if sombre else theme.CLAIR
        theme.appliquer(nom)
        theme.enregistrer(nom)  # retrouvé au prochain démarrage
        # Les icônes des lignes portent leur couleur en dur : on refait la
        # liste pour prendre la variante de l'autre thème.
        self._remplir_liste()

    # ------------------------------------------------------------------ à propos

    def _lire_a_propos(self) -> str:
        """Le texte des crédits, relu à chaque ouverture de la fenêtre."""
        fichier = theme.RESSOURCES / FICHIER_A_PROPOS
        try:
            return fichier.read_text(encoding="utf-8")
        except OSError:
            return A_PROPOS_DE_SECOURS

    def _onglet_a_propos(self) -> QWidget:
        texte = QLabel(self._lire_a_propos())
        texte.setObjectName("aPropos")
        texte.setWordWrap(True)
        texte.setTextFormat(Qt.TextFormat.MarkdownText)
        texte.setAlignment(Qt.AlignmentFlag.AlignTop)
        texte.setOpenExternalLinks(False)

        page = QScrollArea()
        page.setObjectName("pageAPropos")
        page.setWidgetResizable(True)
        page.setFrameShape(QScrollArea.Shape.NoFrame)
        page.setWidget(texte)
        return page

    # ------------------------------------------------------------------ fermeture

    def closeEvent(self, event) -> None:  # noqa: N802 (nom imposé par Qt)
        self._service.arreter()
        super().closeEvent(event)

    def reject(self) -> None:
        self._service.arreter()
        super().reject()

    def accept(self) -> None:
        self._service.arreter()
        super().accept()
