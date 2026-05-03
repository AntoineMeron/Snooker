"""
IHM/main_window.py
------------------
Fenêtre principale du jeu de snooker.
Connecte l'IHM Qt à GameController.
"""

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

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

    def __init__(self,name1:str,name2:str) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.gc = GameController(name1, name2)

        self.table_view = TableView(self.ui.Table, self.gc.table)
        self.table_view.draw()

        self._update_labels()

        self.ui.slider_angle.valueChanged.connect(self._update_label_angle)
        self.ui.slider_force.valueChanged.connect(self._update_label_force)

        self.ui.btn_tirer.clicked.connect(self._tirer)
        self.ui.btn_reset.clicked.connect(self._reset_frame)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_load.clicked.connect(self._load)

        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(16)

    def _game_loop(self) -> None:
        """Appelée 60x/s — avance la physique, redessine, met à jour les labels."""
        self.gc.run_frame()
        angle = self.ui.slider_angle.value()
        force = self.ui.slider_force.value()
        self.table_view.draw(angle_deg=float(angle), force=float(force))
        self._update_labels()

    def _update_labels(self) -> None:
        """Met à jour tous les labels d'information."""
        p1 = self.gc.players[0]
        p2 = self.gc.players[1]
        current = self.gc.current_player()

        # Scores joueurs
        self.ui.label_joueur1_nom.setText(p1.name)
        self.ui.label_joueur1_score.setText(f"Score : {p1.score}")
        self.ui.label_joueur1_break.setText(f"Break : {p1.current_break}")
        self.ui.label_joueur2_nom.setText(p2.name)
        self.ui.label_joueur2_score.setText(f"Score : {p2.score}")
        self.ui.label_joueur2_break.setText(f"Break : {p2.current_break}")

        # Tour et état
        self.ui.label_tour.setText(f"Tour : {current.name}")
        self.ui.label_etat.setText(
            "Billes en mouvement..." if self.gc.state == 'rolling'
            else "En jeu"
        )

        # Prochaine bille à viser
        next_ball = self.gc.rules.next_ball_type
        self.ui.label_next_ball.setText(
            "Viser : Rouge" if next_ball == 'red' else "Viser : Couleur"
        )

        # Joueur courant en gras
        font_bold = QFont()
        font_bold.setBold(True)
        font_normal = QFont()
        font_normal.setBold(False)
        self.ui.label_joueur1_nom.setFont(
            font_bold if self.gc.current_player_index == 0 else font_normal
        )
        self.ui.label_joueur2_nom.setFont(
            font_bold if self.gc.current_player_index == 1 else font_normal
        )

        # Désactiver tirer si billes en mouvement
        self.ui.btn_tirer.setEnabled(self.gc.state == 'aiming')

    def _update_label_angle(self, value: int) -> None:
        """Met à jour le label angle quand le slider change."""
        self.ui.label_angle.setText(f"Angle : {value}°")

    def _update_label_force(self, value: int) -> None:
        """Met à jour le label force quand le slider change."""
        self.ui.label_force.setText(f"Force : {value}")

    def _tirer(self) -> None:
        """Déclenche un tir avec les valeurs courantes des sliders."""
        if self.gc.state != 'aiming':
            return
        angle = float(self.ui.slider_angle.value())
        force = float(self.ui.slider_force.value())
        self.gc.handle_shot(angle_deg=angle, force=force)

    def _reset_frame(self) -> None:
        """Remet toutes les billes en position initiale."""
        self.gc.reset_frame()
        self._update_labels()

    def _save(self) -> None:
        """Sauvegarde la partie dans save.json."""
        self.gc.save_game("save.json")
        self.ui.label_etat.setText("Partie sauvegardée")

    def _load(self) -> None:
        """Charge la partie depuis save.json."""
        try:
            self.gc.load_game("save.json")
            self._update_labels()
            self.ui.label_etat.setText("Partie chargée")
        except FileNotFoundError:
            self.ui.label_etat.setText("Aucune sauvegarde trouvée")