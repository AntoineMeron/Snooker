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
        Liste des états de chaque bille : position, vitesse,
        couleur, valeur, identifiant et état empoché.
    scores_snapshot : dict
        Scores et breaks des deux joueurs au moment du snapshot.
    foul_flag : bool
        True si une faute vient d'être commise.
    phase : str
        Phase du jeu : 'aiming', 'rolling' ou 'placing'.
    next_ball_type : str
        Type de bille attendu par les règles au prochain tir :
        'red' ou 'colour'.
    pockets_snapshot : list[dict]
        Liste des états des poches de la table, contenant leur
        position et leur rayon.
    """

    def __init__(
        self,
        current_player_idx: int = 0,
        frame_number: int = 1,
        balls_snapshot: list = None,
        scores_snapshot: dict = None,
        foul_flag: bool = False,
        phase: str = 'aiming',
        next_ball_type: str = 'red',
        pockets_snapshot: list = None,
    ) -> None:
        """
        Initialise un état de jeu.

        Parameters
        ----------
        current_player_idx : int
            Index du joueur courant.
        frame_number : int
            Numéro de la frame en cours.
        balls_snapshot : list[dict], optional
            Snapshot des billes. Chaque dictionnaire contient les données
            nécessaires pour reconstruire une bille : identifiant, position,
            vitesse, couleur, valeur et état empoché. Si None, une liste
            vide est créée.
        scores_snapshot : dict, optional
            Snapshot des scores et des breaks des joueurs. Si None,
            un dictionnaire vide est créé.
        foul_flag : bool
            True si une faute vient d'être commise, False sinon.
        phase : str
            Phase courante du jeu, par exemple 'aiming', 'rolling'
            ou 'placing'.
        next_ball_type : str
            Type de bille attendu par les règles au prochain tir :
            'red' ou 'colour'.
        pockets_snapshot : list[dict], optional
            Snapshot des poches de la table, contenant leur position
            et leur rayon. Si None, une liste vide est créée.

        Returns
        -------
        None
        """
        self.current_player_idx: int = current_player_idx
        self.frame_number: int = frame_number
        self.balls_snapshot: list = balls_snapshot if balls_snapshot is not None else []
        self.scores_snapshot: dict = scores_snapshot if scores_snapshot is not None else {}
        self.foul_flag: bool = foul_flag
        self.phase: str = phase
        self.next_ball_type = next_ball_type
        self.pockets_snapshot = pockets_snapshot if pockets_snapshot is not None else []

    # ------------------------------------------------------------------
    # Création d'un snapshot depuis GameController
    # ------------------------------------------------------------------

    @staticmethod
    def from_game_controller(gc) -> "GameState":
        """
        Crée un GameState à partir de l'état actuel du GameController.

        À appeler depuis GameController pour prendre une photo complète
        de la partie. Le snapshot contient les billes, les scores, la phase
        de jeu, le joueur courant, le type de bille attendu par les règles
        et les positions des poches.

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

        pockets_snapshot = [
            {"x": p.pos[0], "y": p.pos[1], "rayon": p.rayon}
            for p in gc.table.poches
        ]

        return GameState(
            current_player_idx=gc.current_player_index,
            frame_number=1,  # à incrémenter depuis GameController si besoin
            balls_snapshot=balls_snapshot,
            scores_snapshot=scores_snapshot,
            foul_flag=False,
            phase=gc.state,
            next_ball_type=gc.rules.next_ball_type,
            pockets_snapshot=pockets_snapshot,
        )

    # ------------------------------------------------------------------
    # Sérialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Convertit le GameState en dictionnaire sérialisable.

        Cette méthode est utilisée pour sauvegarder la partie au format JSON.
        Le dictionnaire retourné contient toutes les informations nécessaires
        pour reconstruire l'état de la partie.

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
            "phase":              self.phase, #rolling ou aiming
            "next_ball_type":     self.next_ball_type,
            "pockets_snapshot": self.pockets_snapshot,
        }

    @staticmethod
    def from_dict(d: dict) -> "GameState":
        """
        Reconstruit un GameState depuis un dictionnaire.

        Cette méthode est utilisée lors du chargement d'une partie sauvegardée.
        Elle effectue l'opération inverse de to_dict().

        Parameters
        ----------
        d : dict
            Dictionnaire produit par to_dict() ou chargé depuis un fichier JSON.

        Returns
        -------
        GameState
            L'état de jeu reconstruit à partir du dictionnaire.
        """
        return GameState(
            current_player_idx=d["current_player_idx"],
            frame_number=d["frame_number"],
            balls_snapshot=d["balls_snapshot"],
            scores_snapshot=d["scores_snapshot"],
            foul_flag=d["foul_flag"],
            phase=d["phase"],
            next_ball_type=d.get("next_ball_type", "red"),
            pockets_snapshot=d.get("pockets_snapshot", []),
        )

    # ------------------------------------------------------------------
    # Duplication pour l'IA
    # ------------------------------------------------------------------

    def clone(self) -> "GameState":
        """
        Retourne une copie profonde du GameState.

        Utilisé par AIPlayer pour simuler des tirs hypothétiques
        sans modifier l'état réel de la partie. Les listes et dictionnaires
        imbriqués sont copiés afin que le clone soit indépendant de l'objet
        original.

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

        La partie est considérée comme terminée lorsque toutes les billes
        sauf la bille blanche sont empochées.

        Returns
        -------
        bool
            True si la frame est terminée, False sinon.
        """
        non_white = [b for b in self.balls_snapshot if b["id"] != 0]
        return all(b["is_potted"] for b in non_white)

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle synthétique du GameState.

        Cette représentation est utile pour le débogage, car elle affiche
        le numéro de frame, le joueur courant, la phase du jeu, le nombre
        de billes encore actives et l'état de faute.

        Returns
        -------
        str
            Représentation lisible de l'état du jeu.
        """
        active = sum(1 for b in self.balls_snapshot if not b["is_potted"] and b["id"] != 0)
        return (
            f"GameState(frame={self.frame_number}, "
            f"player={self.current_player_idx}, "
            f"phase='{self.phase}', "
            f"billes_actives={active}, "
            f"faute={self.foul_flag})"
        )