"""
Orchestrateur du jeu de snooker.
N'a pas de logique propre

Responsabilités :
    - Instancier et relier toutes les classes (table, joueurs, physique, règles)
    - Faire avancer la simulation frame par frame
    - Gérer les tours de jeu
    - Appliquer les tirs
    - Sauvegarder / charger une partie
"""

from objects.ball import Ball
from objects.table import Tables
from objects.physique import Physique

class GameController:


    def __init__(self)-> None:
        self.table = Tables()
        self.physique = Physique(table=self.table)

        self.current_player_index = 0
        self.state = 'viser'

        self.table.setup_balls()

    def switch_turn(self) -> None:
        """
        Passe la main au joueur suivant.
        """
        self.current_player_index = 1 - self.current_player_index  # alterne entre 0 et 1
        print(f"Tour du joueur {self.current_player_index + 1}")

    def reset_frame(self) -> None:
        """
        Remet les billes en position de début de frame.
        Remet le score à zéro et redonne la main au joueur 1.
        """
        self.table.balls = []
        self.table.setup_balls()
        self.current_player_index = 0
        self.state = 'viser'
        print("Nouvelle frame !")