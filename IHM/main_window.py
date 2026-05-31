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
from IHM.table_view import TableView, SnookerView
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

    def __init__(self, name1: str = "Joueur 1", name2: str = "Joueur 2",ai:bool = False, difficulty:str = "medium") -> None:

        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.gc = GameController(name1, name2,ai = ai, difficulty= difficulty)

        geo = self.ui.Table.geometry()
        parent = self.ui.Table.parent()
        self.ui.Table.hide()
        snooker_view = SnookerView(parent)
        snooker_view.setGeometry(geo)
        snooker_view.show()
        self.ui.Table = snooker_view

        self.table_view = TableView(self.ui.Table, self.gc.table)

        self._angle = 90.0
        self._force = 50.0

        self.ui.Table.aiming.connect(self._on_aiming)
        self.ui.Table.shot_requested.connect(self._on_shot)

        self.ui.btn_reset.clicked.connect(self._reset_frame)
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_load.clicked.connect(self._load)

        self._update_labels()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(16)


    def _game_loop(self) -> None:
        self.gc.run_frame()
        self.ui.Table.white_pos = self._get_white_px()
        self.table_view.draw(
            angle_deg=self._angle,
            force=self._force,
            state=self.gc.state
        )
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

    def _get_white_px(self):
        """Retourne la position de la blanche en pixels scène."""
        white = self.gc.table.get_ball_id(0)
        if white:
            return self.table_view.to_px(white.pos[0], white.pos[1])
        return None

    def _on_aiming(self, angle: float, force: float) -> None:
        """Met à jour la trajectoire pendant le glissement."""
        if self.gc.state == 'aiming':
            self._angle = angle
            self._force = force

    def _on_shot(self, angle: float, force: float) -> None:
        """Déclenche le tir au relâchement."""
        if self.gc.state == 'aiming':
            self._angle = angle
            self._force = force
            self.gc.handle_shot(angle_deg=angle, force=force)

    def _game_loop(self) -> None:
        self.gc.run_frame()
        # Met à jour la position de la blanche pour le snap
        self.ui.Table.white_pos = self._get_white_px()
        self.table_view.draw(angle_deg=self._angle, force=self._force)
        self._update_labels()