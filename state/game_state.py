"""
Représente un instantané complet de l'état du jeu.

Responsabilités :
    - Stocker l'état de la partie à un instant donné
    - Permettre la sérialisation (to_dict / from_dict)
    - Permettre la duplication pour l'IA (clone)
    - Indiquer si la partie est terminée (is_terminal)
"""

import copy
from objets.ball import Ball


class GameState:
    """
    Photo instantanée de la partie.

    Ne contient pas de logique de jeu — elle stocke uniquement
    les données nécessaires pour décrire complètement l'état
    à un instant donné. Utilisée par GameController pour
    sauvegarder/charger, et par AIPlayer pour simuler des tirs.

    Attributes
    ----------
    current_player_idx : int
        Index du joueur dont c'est le tour (0 ou 1).
    frame_number : int
        Numéro de la frame en cours (commence à 1).
    balls_snapshot : list[dict]
        Liste des états de chaque bille (position, vitesse, empochée).
    scores_snapshot : dict
        Scores des deux joueurs au moment du snapshot.
    foul_flag : bool
        True si une faute vient d'être commise.
    phase : str
        Phase du jeu : 'aiming' ou 'rolling'.
    """

    def __init__(
        self,
        current_player_idx: int = 0,
        frame_number: int = 1,
        balls_snapshot: list = None,
        scores_snapshot: dict = None,
        foul_flag: bool = False,
        phase: str = 'aiming',
        next_ball_type:str='red'
    ) -> None:
        """
        Initialise un état de jeu.

        Parameters
        ----------
        current_player_idx : int
            Index du joueur courant.
        frame_number : int
            Numéro de la frame en cours.
        balls_snapshot : list[dict]
            Snapshot des billes. Si None, initialisé à liste vide.
        scores_snapshot : dict
            Snapshot des scores. Si None, initialisé à dict vide.
        foul_flag : bool
            True si une faute vient d'être commise.
        phase : str
            Phase courante : 'aiming' ou 'rolling'.
        """
        self.current_player_idx: int = current_player_idx
        self.frame_number: int = frame_number
        self.balls_snapshot: list = balls_snapshot if balls_snapshot is not None else []
        self.scores_snapshot: dict = scores_snapshot if scores_snapshot is not None else {}
        self.foul_flag: bool = foul_flag
        self.phase: str = phase
        self.next_ball_type= next_ball_type

    # ------------------------------------------------------------------
    # Création d'un snapshot depuis GameController
    # ------------------------------------------------------------------

    @staticmethod
    def from_game_controller(gc) -> "GameState":
        """
        Crée un GameState à partir de l'état actuel du GameController.

        À appeler depuis GameController pour prendre une photo de la partie.

        Parameters
        ----------
        gc : GameController
            Le contrôleur de jeu courant.

        Returns
        -------
        GameState
            Un snapshot complet de la partie.
        """
        balls_snapshot = [
            {
                "id":       b.id,
                "x":        b.pos[0],
                "y":        b.pos[1],
                "vx":       b.vit[0],
                "vy":       b.vit[1],
                "color":    b.color,
                "points":   b.points,
                "is_potted": b.is_potted,
            }
            for b in gc.table.balls
        ]

        scores_snapshot = {
            p.name: {"score": p.score, "current_break": p.current_break}
            for p in gc.players
        }

        return GameState(
            current_player_idx=gc.current_player_index,
            frame_number=1,  # à incrémenter depuis GameController si besoin
            balls_snapshot=balls_snapshot,
            scores_snapshot=scores_snapshot,
            foul_flag=False,
            phase=gc.state,
            next_ball_type=gc.next_ball_type,
        )

    # ------------------------------------------------------------------
    # Sérialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Convertit le GameState en dictionnaire sérialisable (JSON).

        Returns
        -------
        dict
            Représentation complète de l'état sous forme de dictionnaire.
        """
        return {
            "current_player_idx": self.current_player_idx,
            "frame_number":       self.frame_number,
            "balls_snapshot":     self.balls_snapshot,
            "scores_snapshot":    self.scores_snapshot,
            "foul_flag":          self.foul_flag,
            "phase":              self.phase,
            "next_ball_type":     self.next_ball_type,
        }

    @staticmethod
    def from_dict(d: dict) -> "GameState":
        """
        Reconstruit un GameState depuis un dictionnaire (ex: chargé depuis JSON).

        Parameters
        ----------
        d : dict
            Dictionnaire produit par to_dict().

        Returns
        -------
        GameState
            L'état reconstruit.
        """
        return GameState(
            current_player_idx=d["current_player_idx"],
            frame_number=d["frame_number"],
            balls_snapshot=d["balls_snapshot"],
            scores_snapshot=d["scores_snapshot"],
            foul_flag=d["foul_flag"],
            phase=d["phase"],
            next_ball_type=d.get["next_ball_type","red"],
        )

    # ------------------------------------------------------------------
    # Duplication pour l'IA
    # ------------------------------------------------------------------

    def clone(self) -> "GameState":
        """
        Retourne une copie profonde du GameState.

        Utilisé par AIPlayer pour simuler des tirs hypothétiques
        sans modifier l'état réel de la partie.

        Returns
        -------
        GameState
            Une copie indépendante de cet état.
        """
        # copy.deepcopy garantit que les listes et dicts imbriqués
        # sont copiés et non partagés avec l'original
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # Condition de fin
    # ------------------------------------------------------------------

    def is_terminal(self) -> bool:
        """
        Indique si la partie est terminée.

        La partie est terminée quand toutes les billes
        (sauf la blanche) sont empochées.

        Returns
        -------
        bool
            True si la frame est terminée.
        """
        non_white = [b for b in self.balls_snapshot if b["id"] != 0]
        return all(b["is_potted"] for b in non_white)

    def __repr__(self) -> str:
        active = sum(1 for b in self.balls_snapshot if not b["is_potted"] and b["id"] != 0)
        return (
            f"GameState(frame={self.frame_number}, "
            f"player={self.current_player_idx}, "
            f"phase='{self.phase}', "
            f"billes_actives={active}, "
            f"faute={self.foul_flag})"
        )