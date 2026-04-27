"""
Moteur de règles du snooker.

Responsabilités :
    - Valider les tirs
    - Détecter les fautes
    - Appliquer les pénalités
    - Gérer les transitions de tour
    - Vérifier la fin de frame
    - Attribuer les points
"""

from objets.ball import Ball
from objets.player import Player

class RuleEngine:
    """
    Applique les règles officielles du snooker.

    Au snooker, le joueur doit alterner entre billes rouges et couleurs.
    Tant qu'il reste des rouges, il doit viser une rouge, puis une couleur,
    puis une rouge, etc. Quand toutes les rouges sont empochées, il doit
    empocher les couleurs dans l'ordre croissant de points.

    Attributes
    ----------
    reds_on_table : int
        Nombre de billes rouges encore en jeu.
    next_ball_type : str
        Type de bille que le joueur doit viser : 'red' ou 'colour'.
    free_ball : bool
        True si le joueur bénéficie d'une bille libre après une faute adverse.
    in_hand : bool
        True si la bille blanche est en main (après une faute ou un début de frame).
    """

    def __init__(self, reds_on_table: int = 15) -> None:
        """
        Initialise le moteur de règles.

        Parameters
        ----------
        reds_on_table : int
            Nombre de rouges en début de frame (15 par défaut).
        """
        self.reds_on_table: int = reds_on_table
        self.next_ball_type: str = 'red'   # on commence toujours par viser une rouge
        self.free_ball: bool = False
        self.in_hand: bool = True          # début de frame : bille blanche en main

    def score_potted(self, ball: Ball, players: list[Player], current_idx: int) -> None:
        """
        Attribue les points d'une bille empochée au joueur courant,
        si l'empochage est valide selon les règles.

        Une rouge empochée vaut 1 pt et fait passer à 'colour'.
        Une couleur empochée vaut ses points et repasse à 'red'
        (sauf si toutes les rouges sont parties, auquel cas on reste sur 'colour').

        Parameters
        ----------
        ball : Ball
            La bille empochée.
        players : list[Player]
            Liste des deux joueurs.
        current_idx : int
            Index du joueur courant dans la liste.
        """
        # Bille blanche empochée = faute, pas de points
        if ball.id == 0:
            return

        player = players[current_idx]

        if ball.points == 1:
            # C'est une rouge
            player.add_points(1)
            self.reds_on_table -= 1 #il y a une boule rouge en moins sur la table
            self.next_ball_type = 'colour'  # prochain coup : viser une couleur

        else:
            # C'est une couleur
            player.add_points(ball.points)
            if self.reds_on_table > 0:
                self.next_ball_type = 'red'  # il reste des rouges : on revient aux rouges
            # sinon on reste sur 'colour' pour empocher les couleurs dans l'ordre


    def validate_shot(self, potted_balls: list[Ball]) -> bool:
        """
        Vérifie si les billes empochées correspondent à ce qui était attendu.

        Parameters
        ----------
        potted_balls : list[Ball]
            Liste des billes empochées lors du coup.

        Returns
        -------
        bool
            True si le coup est valide.
        """
        if not potted_balls:
            return True  # aucune bille empochée : coup raté mais pas forcément une faute

        for ball in potted_balls:
            if ball.id == 0:
                return False  # bille blanche empochée = toujours une faute
            if self.next_ball_type == 'red' and ball.points != 1:
                return False  # on devait viser une rouge et on a empoché une couleur
            if self.next_ball_type == 'colour' and ball.points == 1:
                return False  # on devait viser une couleur et on a empoché une rouge

        return True

    def detect_foul(self, potted_balls: list[Ball], white_potted: bool) -> str:
        """
        Détecte le type de faute commise, s'il y en a une.

        Parameters
        ----------
        potted_balls : list[Ball]
            Billes empochées lors du coup.
        white_potted : bool
            True si la bille blanche a été empochée.

        Returns
        -------
        str
            Description de la faute, ou chaîne vide si pas de faute.
        """
        if white_potted:
            return "Faute : bille blanche empochée"

        for ball in potted_balls:
            if self.next_ball_type == 'red' and ball.points != 1:
                return f"Faute : devait viser une rouge, a empoché {ball.color}"
            if self.next_ball_type == 'colour' and ball.points == 1:
                return "Faute : devait viser une couleur, a empoché une rouge"

        return ""  # pas de faute

    #ON PEUT PAS FUSIONNER VALIDATE_SHOT ET DETECT_FOUL ?

    def apply_foul(self, foul: str, players: list[Player], current_idx: int) -> None:
        """
        Applique la pénalité d'une faute à l'adversaire du joueur courant.

        Au snooker, une faute donne des points à l'adversaire.
        La pénalité minimale est 4 points.

        Parameters
        ----------
        foul : str
            Description de la faute (retournée par detect_foul).
        players : list[Player]
            Liste des deux joueurs.
        current_idx : int
            Index du joueur qui a commis la faute.
        """
        if not foul:
            return

        adversaire_idx = 1 - current_idx
        penalite = 4  # pénalité minimale au snooker

        players[adversaire_idx].add_points(penalite)
        self.in_hand = True  # l'adversaire récupère la bille en main
        print(f"Faute ! +{penalite} pts pour {players[adversaire_idx].name}")


    def next_turn(self, players: list[Player], current_idx: int) -> int:
        """
        Prépare le passage au tour suivant.
        Remet le break du joueur courant à zéro et retourne l'index du joueur suivant.

        Parameters
        ----------
        players : list[Player]
            Liste des deux joueurs.
        current_idx : int
            Index du joueur courant.

        Returns
        -------
        int
            Index du joueur suivant (0 ou 1).
        """
        players[current_idx].reset_break()
        next_idx = 1 - current_idx
        print(f"Tour de {players[next_idx].name}")
        return next_idx

    #FONCTION DEJA ECRITE DANS GAME_CONTROLLER NON ?

    def is_frame_over(self, balls: list[Ball]) -> bool:
        """
        Vérifie si la frame est terminée.

        La frame se termine quand toutes les billes (sauf la blanche) sont empochées.

        Parameters
        ----------
        balls : list[Ball]
            Liste de toutes les billes de la table.

        Returns
        -------
        bool
            True si la frame est terminée.
        """
        # On ignore la bille blanche (id=0)
        return all(b.is_potted for b in balls if b.id != 0)