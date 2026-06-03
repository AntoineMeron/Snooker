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
import numpy as np
from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique
from objets.player import Player
from moteur.rules import Rules
from state.game_state import GameState
from IA.ai_player import AIPlayer


class GameController:
    """
    Orchestre toutes les classes du jeu.

    Cette classe sert de point central entre la table, le moteur physique,
    les règles, les joueurs et l'interface. Elle ne contient pas directement
    la logique détaillée de la physique ou des règles, mais coordonne leur
    utilisation pendant la partie.

    Attributes
    ----------
    table : Tables
        La table de jeu avec ses billes et ses poches.
    physique : Physique
        Le moteur physique utilisé pour déplacer les billes, gérer les
        collisions et détecter les empochages.
    rules : Rules
        Le moteur de règles utilisé pour détecter les fautes, attribuer
        les points et gérer la progression de la frame.
    players : list[Player]
        Liste des deux joueurs de la partie. Le second joueur peut être
        une IA si l'option est activée.
    current_player_index : int
        Index du joueur dont c'est le tour, 0 ou 1.
    state : str
        État courant du jeu : 'aiming' lorsque le joueur vise,
        'rolling' lorsque les billes sont en mouvement ou 'placing'
        lorsque la bille blanche doit être replacée.
    _potted_this_shot : list
        Liste des billes empochées pendant le tir courant.
    """

    def __init__(self, name1: str = "Joueur 1", name2: str = 'Joueur 2', ai: bool = False, difficulty: str = 'medium') -> None:
        """
        Initialise le contrôleur de jeu.

        Crée la table, le moteur physique, les règles, les joueurs,
        initialise les billes et place le jeu dans l'état de visée.

        Parameters
        ----------
        name1 : str
            Nom du joueur 1, qui est toujours un joueur humain.
        name2 : str
            Nom du joueur 2.
        ai : bool
            Si True, le joueur 2 est une intelligence artificielle.
            Sinon, le joueur 2 est un joueur humain.
        difficulty : str
            Niveau de difficulté de l'IA si le joueur 2 est contrôlé
            automatiquement. Les valeurs possibles sont 'easy',
            'medium' ou 'hard'.

        Returns
        -------
        None
        """
        self.table = Tables()
        self.physique = Physique(table=self.table)
        self.rules = Rules()
        self.current_player_index = 0

        self.state = 'aiming'
        self.table.setup_balls()
        self._potted_this_shot = []

        if ai:
            self.players = [Player(name1), AIPlayer(name2, difficulty=difficulty)]
        else:
            self.players = [Player(name1), Player(name2)]

    def current_player(self) -> Player:
        """
        Retourne le joueur dont c'est actuellement le tour.

        Cette méthode sert de raccourci pour éviter d'écrire
        self.players[self.current_player_index] à plusieurs endroits
        dans le code.

        Returns
        -------
        Player
            Le joueur courant.
        """
        return self.players[self.current_player_index]

    def switch_turn(self) -> None:
        """
        Passe la main à l'autre joueur.

        Le break du joueur courant est remis à zéro, puis l'index du
        joueur courant est inversé afin d'alterner entre les deux joueurs.

        Returns
        -------
        None
        """
        self.current_player().reset_break() #on remet le break du joueur qui prend le tour à 0
        self.current_player_index = 1 - self.current_player_index  # alterne entre 0 et 1
        print(f"Tour du joueur {self.current_player().name}")

    def reset_frame(self) -> None:
        """
        Réinitialise entièrement la frame en cours.

        Les billes sont replacées dans leur position de départ, les scores
        et les breaks sont remis à zéro, les règles sont recréées et la main
        est redonnée au joueur 1.

        Returns
        -------
        None
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

    def handle_shot(self, angle_deg: float, force: float) -> None:
        """
        Applique un tir sur la bille blanche.

        Le tir est refusé si le jeu n'est pas dans l'état 'aiming',
        c'est-à-dire si les billes sont encore en mouvement ou si la
        bille blanche doit être replacée. Si la bille blanche existe,
        le tir est transmis au moteur physique et l'état du jeu passe
        à 'rolling'.

        Parameters
        ----------
        angle_deg : float
            Angle du tir en degrés. 0° correspond à un tir vers la droite,
            et les angles augmentent dans le sens antihoraire.
        force : float
            Force du tir, comprise entre 0 et 100.

        Returns
        -------
        None
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

        Cette méthode est appelée régulièrement par l'interface graphique.
        Elle gère les actions automatiques de l'IA, applique la physique
        lorsque les billes sont en mouvement, accumule les billes empochées,
        puis applique les règles lorsque toutes les billes sont arrêtées.

        Si c'est le tour d'une IA et que le jeu attend un tir, un snapshot
        de l'état courant est créé et transmis à l'IA afin qu'elle choisisse
        automatiquement un tir. Si une faute est détectée, les points de
        pénalité sont appliqués et le tour passe à l'autre joueur.

        Returns
        -------
        None
        """
        # ── Bloc IA 1 : placement de la blanche ──────────────────────────
        # Si l'IA doit replacer la blanche dans le D, elle choisit
        # automatiquement la meilleure position libre
        if self.state == 'placing' and self.current_player().is_ai:
            pos = self.table.get_valid_baulk_position()
            self.place_white_ball(pos[0], pos[1])
            # place_white_ball repasse state = 'aiming' si la position est valide
            return

        # ── Bloc IA 2 : choix et exécution du tir ────────────────────────
        # Si c'est le tour de l'IA et que le jeu attend un tir,
        # on génère automatiquement le meilleur tir possible
        if self.state == 'aiming' and self.current_player().is_ai:
            state_snapshot = GameState.from_game_controller(self)
            shot = self.current_player().choose_shot(state_snapshot)
            self.handle_shot(shot.angle_deg, shot.force)
            return  # handle_shot passe state en 'rolling', on reviendra au prochain appel

        if self.state != 'rolling':
            return

        potted = self.physique.step()
        self._potted_this_shot += potted #on accumule à chaque frame

        # Quand toutes les billes sont arrêtées, on applique les règles, on peut commencer à viser
        if self.physique.all_stopped():
            self.state = 'aiming'

            white_potted = any(b.id == 0 for b in self._potted_this_shot)
            foul, penalite = self.rules.detect_foul(self._potted_this_shot, white_potted)

            if foul:
                print(foul)
                self.rules.apply_foul(foul, penalite, self.players, self.current_player_index)
                self.switch_turn()

                # Si la blanche a été empochée, on la replace dans le D  ← ajout
                if white_potted:
                    self.state = 'placing'
                    pos = self.table.get_valid_baulk_position()
                    self.place_white_ball(pos[0], pos[1])

            else:
                for ball in self._potted_this_shot:
                    self.rules.score_potted(ball, self.players, self.current_player_index, self.table)

                if self._potted_this_shot:
                    print(f"{self.current_player().name} rejoue !")
                else:
                    self.switch_turn()

            if self.rules.is_frame_over(self.table.balls):
                print("Frame terminée !")
                print(f"{self.players[0].name} : {self.players[0].score} pts")
                print(f"{self.players[1].name} : {self.players[1].score} pts")

    def save_game(self, filepath: str = "save.json") -> None:
        """
        Sauvegarde l'état courant de la partie dans un fichier JSON.

        La méthode crée d'abord un GameState à partir du GameController,
        puis convertit ce snapshot en dictionnaire sérialisable avant
        de l'écrire dans le fichier indiqué.

        Parameters
        ----------
        filepath : str
            Chemin du fichier de sauvegarde. Par défaut, la sauvegarde
            est écrite dans le fichier "save.json".

        Returns
        -------
        None
        """
        state = GameState.from_game_controller(self)  # on prend une photo
        data = state.to_dict()  # on la convertit en dict
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self, filepath: str = "save.json") -> None:
        """
        Charge une partie depuis un fichier JSON.

        Le fichier est lu, transformé en GameState, puis les informations
        du snapshot sont appliquées au GameController : joueur courant,
        phase de jeu, scores, breaks et état des billes.

        Parameters
        ----------
        filepath : str
            Chemin du fichier de sauvegarde à charger. Par défaut,
            le fichier utilisé est "save.json".

        Returns
        -------
        None
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        state = GameState.from_dict(data)  # on reconstruit le GameState

        # On applique le GameState sur le GameController
        self.current_player_index = state.current_player_idx
        self.state = state.phase

        for p_name, p_data in state.scores_snapshot.items():
            player = next(p for p in self.players if p.name == p_name)
            player.score = p_data["score"]
            player.current_break = p_data["current_break"]

        self.table.balls = []
        for b_data in state.balls_snapshot:
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

    def place_white_ball(self, x: float, y: float) -> bool:
        """
        Place la bille blanche à la position choisie.

        La position est acceptée uniquement si le jeu est dans l'état
        'placing', si la position est dans la zone de baulk et si elle
        ne provoque pas de chevauchement avec une autre bille active.
        Si la position est valide, la bille blanche est placée et le jeu
        repasse en état 'aiming'.

        Parameters
        ----------
        x : float
            Position X souhaitée pour la bille blanche.
        y : float
            Position Y souhaitée pour la bille blanche.

        Returns
        -------
        bool
            True si la position a été acceptée et que la bille blanche
            a été replacée, False sinon.
        """
        if self.state != 'placing':
            return False

        # Vérification 1 : position dans la zone D
        if not self.table.in_baulk_zone(x, y):
            print("Position hors de la zone D !")
            return False

        # Vérification 2 : pas de chevauchement avec une autre bille
        white = self.table.get_ball_id(0)
        for ball in self.table.get_active_balls():
            if ball.id == 0:
                continue
            dist = float(np.linalg.norm(np.array([x, y]) - ball.pos))
            if dist < white.rayon + ball.rayon:
                print("Position occupée par une autre bille !")
                return False

        # Position valide : on place la blanche et on repasse en mode visée
        self.table.place_white_ball(x, y)
        self.state = 'aiming'
        self.rules.in_hand = False
        return True