"""Le pont entre l'interface et le moteur de traduction.

Traduire prend du temps (de quelques dixièmes de seconde à plusieurs
secondes). Fait dans le thread de la fenêtre, ce calcul figerait l'affichage :
plus de curseur, plus de clic, et sur certains systèmes un message
« l'application ne répond pas ». C'est pourquoi tout passe ici.

L'interface n'appelle jamais le moteur directement : elle demande une
traduction à `ServiceTraduction`, puis reçoit le résultat par un signal.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from .core import detect, packages, translator

# Délai laissé à un thread pour s'arrêter de lui-même à la fermeture.
DELAI_ARRET_MS = 1500


def _arreter_thread(thread: QThread) -> None:
    """Arrête un thread de travail sans faire planter l'application.

    `quit()` demande à la boucle d'événements du thread de se terminer, mais
    n'interrompt pas un calcul déjà commencé : une traduction ou une
    décompression en cours va jusqu'au bout. Si l'utilisateur ferme la fenêtre
    à ce moment-là, Qt détruit un thread encore actif et **abandonne le
    processus** (SIGABRT) — l'application semble planter à la fermeture.

    On laisse donc un court délai, puis on force l'arrêt. Forcer est brutal,
    mais on quitte de toute façon : rien n'est écrit sur le disque à ce
    moment, et mieux vaut un arrêt forcé qu'un plantage visible.
    """
    thread.quit()
    if thread.wait(DELAI_ARRET_MS):
        return
    thread.terminate()
    thread.wait()


class _Ouvrier(QObject):
    """Exécute les traductions, dans son propre thread.

    Chaque demande porte un numéro : il permet au service d'ignorer les
    réponses devenues inutiles (voir `ServiceTraduction`).
    """

    fini = Signal(int, str, str)  # numéro, traduction, langue source retenue
    echoue = Signal(int, str)

    @Slot(int, str, str, str)
    def traduire(self, numero: int, texte: str, depuis: str, vers: str) -> None:
        try:
            if not depuis:
                # Reconnaissance automatique demandée. On ne cherche que
                # parmi les langues installées : le reste serait intraduisible.
                depuis = detect.detecter(texte, packages.langues_installees())
                if depuis is None:
                    self.echoue.emit(
                        numero,
                        "Impossible de reconnaître la langue. Choisissez-la vous-même.",
                    )
                    return
            self.fini.emit(numero, translator.traduire(texte, depuis, vers), depuis)
        except translator.ErreurTraduction as erreur:
            self.echoue.emit(numero, str(erreur))
        except Exception:  # noqa: BLE001
            # Un imprévu du moteur ne doit jamais faire disparaître la fenêtre.
            self.echoue.emit(numero, "La traduction a échoué.")


class ServiceTraduction(QObject):
    """Façade utilisée par l'interface.

    Deux garanties :

    - le calcul n'a jamais lieu dans le thread de la fenêtre ;
    - seule la réponse à la *dernière* demande est transmise. Quand on tape
      au clavier, les demandes s'enchaînent plus vite que les traductions ne
      se terminent ; sans ce filtre, une vieille réponse pourrait s'afficher
      après une plus récente et le texte affiché ne correspondrait plus à ce
      que l'utilisateur a écrit.
    """

    resultat = Signal(str, str)  # traduction, langue source retenue
    erreur = Signal(str)
    _demande = Signal(int, str, str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._numero = 0
        self._attendu = 0

        self._thread = QThread()
        self._ouvrier = _Ouvrier()
        self._ouvrier.moveToThread(self._thread)

        self._demande.connect(self._ouvrier.traduire)
        self._ouvrier.fini.connect(self._sur_fini)
        self._ouvrier.echoue.connect(self._sur_echec)
        self._thread.start()

    def demander(self, texte: str, depuis: str, vers: str) -> None:
        """Demande une traduction. Retourne immédiatement.

        `depuis` vide signifie « reconnaître la langue automatiquement ».
        """
        self._numero += 1
        self._attendu = self._numero
        self._demande.emit(self._numero, texte, depuis, vers)

    def arreter(self) -> None:
        """Arrête le thread. À appeler à la fermeture de la fenêtre."""
        _arreter_thread(self._thread)

    @Slot(int, str, str)
    def _sur_fini(self, numero: int, texte: str, depuis: str) -> None:
        if numero == self._attendu:
            self.resultat.emit(texte, depuis)

    @Slot(int, str)
    def _sur_echec(self, numero: int, message: str) -> None:
        if numero == self._attendu:
            self.erreur.emit(message)


class _OuvrierLangues(QObject):
    """Télécharge le catalogue et installe les langues, dans son propre thread."""

    catalogue_pret = Signal(list)
    catalogue_echoue = Signal(str)
    progression = Signal(str, float)  # code de la langue, avancement 0→1 (-1 si inconnu)
    langue_installee = Signal(str)
    installation_finie = Signal()
    installation_echouee = Signal(str, str)  # code, message
    installation_annulee = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._annule = False

    def annuler(self) -> None:
        """Appelable depuis le thread de la fenêtre : simple drapeau."""
        self._annule = True

    @Slot()
    def charger_catalogue(self) -> None:
        self._annule = False
        try:
            packages.rafraichir_catalogue()
            self.catalogue_pret.emit(packages.langues_installables())
        except packages.ErreurReseau as erreur:
            self.catalogue_echoue.emit(str(erreur))

    @Slot(list)
    def installer(self, codes: list[str]) -> None:
        self._annule = False
        for code in codes:
            try:
                packages.installer_langue(
                    code,
                    progression=lambda fraction, code=code: self.progression.emit(
                        code, fraction
                    ),
                    annule=lambda: self._annule,
                )
                self.langue_installee.emit(code)
            except packages.Annulation:
                self.installation_annulee.emit()
                return
            except (packages.ErreurReseau, LookupError) as erreur:
                self.installation_echouee.emit(code, str(erreur))
                return
            except Exception:  # noqa: BLE001
                self.installation_echouee.emit(code, "L'installation a échoué.")
                return
        self.installation_finie.emit()


class ServiceLangues(QObject):
    """Façade pour tout ce qui touche à l'ajout de langues.

    Comme la traduction, ces opérations sont longues (réseau, décompression)
    et doivent rester hors du thread de la fenêtre.
    """

    catalogue_pret = Signal(list)
    catalogue_echoue = Signal(str)
    progression = Signal(str, float)
    langue_installee = Signal(str)
    installation_finie = Signal()
    installation_echouee = Signal(str, str)
    installation_annulee = Signal()

    _demande_catalogue = Signal()
    _demande_installation = Signal(list)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread = QThread()
        self._ouvrier = _OuvrierLangues()
        self._ouvrier.moveToThread(self._thread)

        self._demande_catalogue.connect(self._ouvrier.charger_catalogue)
        self._demande_installation.connect(self._ouvrier.installer)

        for nom in (
            "catalogue_pret",
            "catalogue_echoue",
            "progression",
            "langue_installee",
            "installation_finie",
            "installation_echouee",
            "installation_annulee",
        ):
            getattr(self._ouvrier, nom).connect(getattr(self, nom).emit)

        self._thread.start()

    def charger_catalogue(self) -> None:
        self._demande_catalogue.emit()

    def installer(self, codes: list[str]) -> None:
        self._demande_installation.emit(codes)

    def annuler(self) -> None:
        # Volontairement appelé directement et non par signal : un signal
        # attendrait la fin du téléchargement en cours pour être traité,
        # donc le bouton « Annuler » ne répondrait pas.
        self._ouvrier.annuler()

    def arreter(self) -> None:
        # On demande d'abord l'annulation : le téléchargement s'interrompt
        # entre deux blocs, donc presque immédiatement.
        self._ouvrier.annuler()
        _arreter_thread(self._thread)
