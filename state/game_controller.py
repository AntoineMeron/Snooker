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

import json
from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique
from objets.player import Player
from objets.rules import Rules

class GameController:
    """
    Orchestre toutes les classes du jeu.

    Attributes
    ----------
    table : Tables
        La table de jeu avec ses billes et ses poches.
    physique : Physique
        Le moteur physique.
    rules : Rules
        Le moteur de règles.
    players : list[Player]
        Liste des deux joueurs.
    current_player_index : int
        Index du joueur dont c'est le tour (0 ou 1).
    state : str
        État courant du jeu : 'aiming' (joueur vise) ou 'rolling' (billes en mouvement).
    """

    def __init__(self, name1 : str ="Joueur 1", name2 : str = 'Joueur 2')-> None:
        """
        Initialise le contrôleur de jeu.

        Parameters
        ----------
        name1 : str
            Nom du premier joueur.
        name2 : str
            Nom du second joueur.
        """
        self.table = Tables()
        self.physique = Physique(table=self.table)
        self.rules = Rules()

        self.players = [Player(name1), Player(name2)]
        self.current_player_index = 0

        self.state = 'aiming'
        self.table.setup_balls()
        self._potted_this_shot = []

    def current_player(self) -> Player:
        """
        Retourne le joueur dont c'est le tour.
        Raccourci pour éviter d'écrire self.players[self.current_player_index] partout.

        Returns
        -------
        Player
            Le joueur courant.
        """
        return self.players[self.current_player_index]

    def switch_turn(self) -> None:
        """
        Remet le break du joueur courant à zéro, puis passe la main.
        """
        self.current_player().reset_break() #on remet le break du joueur qui prend le tour à 0
        self.current_player_index = 1 - self.current_player_index  # alterne entre 0 et 1
        print(f"Tour du joueur {self.current_player().name}")

    def reset_frame(self) -> None:
        """
        Remet les billes en position de début de frame.
        Remet le score à zéro et redonne la main au joueur 1.
        """
        self.table.balls = []
        self.table.setup_balls()
        self.current_player_index = 0
        self.rules = Rules() #on recrée les règles pour mettre next_ball_type etc à 0

        for player in self.players:
            player.score = 0
            player.reset_break() #on remet les scores et break à 0

        self.state = 'aiming'
        print("Nouvelle frame !")

    def handle_shot(self, angle_deg : float, force : float) -> None:
        """
        Applique un tir sur la bille blanche.
        Refuse le tir si les billes sont encore en mouvement.

        Parameters
        ----------
        angle_deg : float
            Angle du tir en degrés (0° = droite, sens antihoraire).
        force : float
            Force du tir entre 0 et 100.
        """
        if self.state != 'aiming':
            return #on attend que les billes soient à l'arrêt pour viser

        white_ball = self.table.get_ball_id(0)  # la bille blanche a l'id 0
        if white_ball is None:
            return #la bille blanche a été empochée

        self.physique.apply_shot(white_ball, angle_deg, force)
        self.state = 'rolling'  # les billes commencent à bouger
        self._potted_this_shot = []

    def run_frame(self) -> None:
        """
        Avance la simulation d'une frame.

        À appeler à chaque frame de l'interface graphique.
        Tant que des billes bougent, on fait avancer la physique.
        Quand tout s'arrête, on applique les règles puis on passe le tour.
        """
        if self.state != 'rolling':
            return

        potted = self.physique.step()
        self._potted_this_shot += potted #on accumule à chaque frame

        # Quand toutes les billes sont arrêtées, on applique les règles, on peut commencer à viser
        if self.physique.all_stopped():
            self.state = 'aiming'

            # On vérifie si la bille blanche est dans la liste des empochées
            white_potted = any(b.id == 0 for b in self._potted_this_shot)
            foul = self.rules.detect_foul(self._potted_this_shot, white_potted)

            if foul:
                # Faute : les points vont à l'adversaire et on passe le tour
                print(foul)
                self.rules.apply_foul(foul, self.players, self.current_player_index)
                self.switch_turn()
            else:
                # Coup valide : on attribue les points au joueur courant
                for ball in self._potted_this_shot:
                    self.rules.score_potted(ball, self.players, self.current_player_index)

                if self._potted_this_shot:
                    # Le joueur a empoché au moins une bille : il rejoue
                    print(f"{self.current_player().name} rejoue !")
                else:
                    # Aucune bille empochée : on passe le tour
                    self.switch_turn()

            # On vérifie si la frame est terminée
            if self.rules.is_frame_over(self.table.balls):
                print("Frame terminée !")
                print(f"{self.players[0].name} : {self.players[0].score} pts")
                print(f"{self.players[1].name} : {self.players[1].score} pts")

    def save_game(self, filepath: str = "save.json") -> None:
        """
        Sauvegarde l'état de la partie dans un fichier JSON.

        Parameters
        ----------
        filepath : str
            Chemin du fichier de sauvegarde.
        """
        data = {
            "current_player": self.current_player_index,
            "state": self.state,
            "players": [p.get_stats() for p in self.players],
            "rules": {
                "reds_on_table": self.rules.reds_on_table,
                "next_ball_type": self.rules.next_ball_type,
                "free_ball": self.rules.free_ball,
                "in_hand": self.rules.in_hand,
            },
            "balls": [
                {
                    "id": b.id,
                    "x": b.pos[0],
                    "y": b.pos[1],
                    "vx": b.vit[0],
                    "vy": b.vit[1],
                    "is_potted": b.is_potted,
                    "color": b.color,
                    "points": b.points,
                }
                for b in self.table.balls
            ]
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self, filepath: str = "save.json") -> None:
        """
        Charge une partie depuis un fichier JSON.

        Parameters
        ----------
        filepath : str
            Chemin du fichier de sauvegarde.
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        self.current_player_index = data["current_player"]
        self.state = data["state"]

        for i, p_data in enumerate(data["players"]):
            self.players[i].score = p_data["score"]
            self.players[i].current_break = p_data["current_break"]

        self.rules.reds_on_table = data["rules"]["reds_on_table"]
        self.rules.next_ball_type = data["rules"]["next_ball_type"]
        self.rules.free_ball = data["rules"]["free_ball"]
        self.rules.in_hand = data["rules"]["in_hand"]

        self.table.balls = []
        for b_data in data["balls"]:
            ball = Ball(
                x=b_data["x"],
                y=b_data["y"],
                color=b_data["color"],
                points=b_data["points"],
                ball_id=b_data["id"],
            )
            ball.vit[0] = b_data["vx"]
            ball.vit[1] = b_data["vy"]
            ball.is_potted = b_data["is_potted"]
            self.table.balls.append(ball)