"""
ihm/main_window.py
------------------
Fenêtre principale du jeu de snooker.
Connecte l'IHM Qt à GameController.
"""

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

# Fichier généré par pyuic5
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

        # Chargement de l'IHM générée par Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Création du GameController
        self.gc = GameController("Alice", "Bob")

        # Rendu graphique — 'table' est le nom du QGraphicsView dans Qt Designer
        self.table_view = TableView(self.ui.Table, self.gc.table)
        self.table_view.draw()

        # Timer 60 fps
        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(16)  # 16 ms ≈ 60 fps

    # ------------------------------------------------------------------
    # Boucle de jeu
    # ------------------------------------------------------------------

    def _game_loop(self) -> None:
        """
        Appelée 60x par seconde par le QTimer.
        Avance la physique et redessine.
        """
        self.gc.run_frame()
        self.table_view.draw()