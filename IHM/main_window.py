"""
IHM/main_window.py
------------------
Fenêtre principale du jeu de snooker.
Connecte l'IHM Qt à GameController.
"""

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

from IHM.IHM import Ui_MainWindow
from IHM.table_view import TableView
from state.game_controller import GameController


class MainWindow(QMainWindow):
    """
    Fenêtre principale du jeu.

    Attributes
    ----------
    gc : GameController
        L'orchestrateur du jeu.
    table_view : TableView
        Le rendu graphique de la table.
    timer : QTimer
        Timer qui fait tourner la boucle de jeu à 60 fps.
    """

    def __init__(self) -> None:
        """Initialise la fenêtre et connecte tous les composants."""
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Création du GameController
        self.gc = GameController("Alice", "Bob")

        # Rendu graphique
        self.table_view = TableView(self.ui.Table, self.gc.table)
        self.table_view.draw()

        # Initialisation des labels avec les valeurs par défaut des sliders
        self._update_label_angle(self.ui.Angle.value())
        self._update_label_force(self.ui.Force.value())

        # Connexion des sliders
        self.ui.Angle.valueChanged.connect(self._update_label_angle)
        self.ui.Force.valueChanged.connect(self._update_label_force)

        # Connexion du bouton tirer
        self.ui.pushButton.clicked.connect(self._tirer)

        # Timer 60 fps
        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(16)

    # ------------------------------------------------------------------
    # Boucle de jeu
    # ------------------------------------------------------------------

    def _game_loop(self) -> None:
        """
        Appelée 60x par seconde par le QTimer.
        Avance la physique et redessine.
        """
        self.gc.run_frame()
        angle = self.ui.Angle.value()
        force = self.ui.Force.value()
        self.table_view.draw(angle_deg=angle, force=force)

    # ------------------------------------------------------------------
    # Sliders
    # ------------------------------------------------------------------

    def _update_label_angle(self, value: int) -> None:
        """
        Met à jour le label angle quand le slider change.

        Parameters
        ----------
        value : int
            Valeur courante du slider (0-360).
        """
        self.ui.label_angle.setText(f"Angle : {value}°")

    def _update_label_force(self, value: int) -> None:
        """
        Met à jour le label force quand le slider change.

        Parameters
        ----------
        value : int
            Valeur courante du slider (1-100).
        """
        self.ui.label_force.setText(f"Force : {value}")

    # ------------------------------------------------------------------
    # Tir
    # ------------------------------------------------------------------

    def _tirer(self) -> None:
        """
        Déclenche un tir avec les valeurs courantes des sliders.
        Ignoré si les billes sont encore en mouvement.
        """
        if self.gc.state != 'aiming':
            return  # on attend que les billes soient arrêtées

        angle = self.ui.Angle.value()
        force = self.ui.Force.value()
        self.gc.handle_shot(angle_deg=float(angle), force=float(force))