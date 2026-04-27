"""
Représente la table de snooker, ses poches, ses billes.
"""

import numpy as np
from objets.ball import Ball
from objets.poche import Poche

class Tables:
    """
    Table de snooker réglementaire.

    Dimensions intérieures réglementaires :
        - longueur : 370 cm
        - largeur  : 180 cm

    Le repère (0, 0) est le coin inférieur gauche du tapis.
    """

    def __init__(self,largeur:float = 180, longueur:float = 370 )->None:
        """
        Initialise la table avec ses dimensions et crée les 6 poches.

        Parameters
        ----------
        largeur : float
            La largeur de la table
        longueur : float
            La longueur de la table
        """
        self.largeur = largeur
        self.longueur = longueur

        #Physique du tapis
        self.friction_coef = 0.985

        #Zone de baulk
        self.baulk_line_x = longueur * 0.206
        self.baulk_center = np.darray([self.baulk_line_x, largeur/2],dtype=float)
        self.baulk_zone_rayon = 29.2 #cm réglementaire

        self.balls = []
        self.poches = self.create_poche()

    def create_poche(self) -> list:
        """
        Crée les 6 poches aux positions réglementaires.

        Returns
        -------
        list
            Liste ordonnée des 6 poches.
        """
        l,L = self.longueur, self.largeur
        mid_rayon = 4.0 # les poches du milieu un peu plus petites
        cor_rayon = 4.5
        return [
            Poche("top_left", 0, L, cor_rayon),
            Poche("top_mid", l / 2, L, mid_rayon),
            Poche("top_right", l, L, cor_rayon),
            Poche("bot_left", 0, 0, cor_rayon),
            Poche("bot_mid", l / 2, 0, mid_rayon),
            Poche("bot_right", l, 0, cor_rayon),
        ]

    def add_ball(self,ball:Ball)->None:
        """
        Ajoute une bille sur la table
        """
        self.balls.append(ball)

    def get_ball_id(self,ball_id:int)->int:
        """
        Retourne la bille avec l'identifiant de la bille.

        Parameters
        ----------
        ball_id : int
            Identifiant de la bille recherchée.
        """
        for ball in self.balls:
            if ball.id == ball_id:
                return ball
        return None

    def get_active_balls(self)->list:
        """
        Retourne la liste des billes sur la table non empochées.
        """
        return [b for b in self.balls if not b.is_potted]

    def count_red(self)->int:
        """
        Compte le nombre de billes rouge encore en jeu
        """
        return sum(1 for b in self.balls if b.points == 1 and not b.is_potted)

    def place_white_ball(self,x:float,y:float)->None:
        """
        Place la bille blanche à la position donnée.

        Parameters
        ----------
        x : float
            Position X souhaitée.
        y : float
            Position Y souhaitée.
        """
        white = self.get_ball_id(0)
        if white:
            white.reset(x,y)

    def in_baulk_zone(self,x:float,y:float)->bool:
        """
        Vérifie si un point est dans le demi-cercle D

        Parameters
        ----------
        x : float
            Coordonnée X du point
        y : float
            Coordonnée Y du point

        Returns
        -------
        boolean
            True si le point est dans la zone
        """
        pt = np.darray([x,y],dtype=float)
        dist = np.linalg.norm(pt-self.baulk_center)
        return dist <= self.baulk_zone_rayon and x <= self.baulk_line_x

    def setup_balls(self) -> None:
        """
        Place toutes les billes en position de début de frame.
        Bille blanche dans la zone D, rouges en triangle,
        couleurs sur leurs spots.
        """

        self.balls.clear()

        # Bille blanche
        self.balls.append(Ball(0, "white", 0, self.baulk_line_x - 10, self.longueur / 2))

        # Couleurs sur leurs spots réglementaires
        spots = [
            (16, "yellow", 2, self.baulk_line_x, self.longueur / 2 - 18.4),
            (17, "green", 3, self.baulk_line_x, self.longueur / 2 + 18.4),
            (18, "brown", 4, self.baulk_line_x, self.longueur / 2),
            (19, "blue", 5, self.largeur / 2, self.longueur / 2),
            (20, "pink", 6, self.largeur * 0.74, self.longueur / 2),
            (21, "black", 7, self.largeur * 0.89, self.longueur / 2),
        ]
        for bid, col, pts, x, y in spots:
            self.balls.append(Ball(x,y,col,pts,bid))

        # Triangle de 15 rouges
        self._place_reds_triangle()

    def _place_reds_triangle(self) -> None:
        """Place les 15 billes rouges en triangle derrière la pink."""

        pink = self.get_ball_id(20)
        if pink is None:
            return

        r = 2.625
        row_gap = r * 2  # espacement horizontal entre rangées
        start_x = pink.pos[0] + r * 2 + 1.0
        ball_id = 1

        for row in range(5):  # 5 rangées : 1,2,3,4,5 billes
            n_balls = row + 1
            start_y = self.longueur / 2 - row * r
            for col in range(n_balls):
                x = start_x + row * row_gap
                y = start_y + col * r * 2
                self.balls.append(Ball(x,y,"red", 1, ball_id))
                ball_id += 1