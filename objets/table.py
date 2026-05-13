"""
Représente la table de snooker, ses poches, ses billes.
"""

import numpy as np
import math
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
        self.baulk_line_y = longueur* 0.206
        self.baulk_center = np.array([largeur/2,self.baulk_line_y],dtype=float)
        self.baulk_zone_rayon = 29.2 #cm réglementaire

        self.balls = []
        self.poches = self.create_poche()

        self.restitution_coef =0.8
        # Spots réglementaires des couleurs (id_bille : position)
        self.colour_spots = {
            16: np.array([self.largeur / 2 - 18.4, self.baulk_line_y]),  # jaune
            17: np.array([self.largeur / 2 + 18.4, self.baulk_line_y]),  # verte
            18: np.array([self.largeur / 2, self.baulk_line_y]),  # marron
            19: np.array([self.largeur / 2, self.longueur / 2]),  # bleue
            20: np.array([self.largeur / 2, self.longueur * 0.74]),  # rose
            21: np.array([self.largeur / 2, self.longueur * 0.89]),  # noire
        }

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
            Poche("top_left", 0, 0, cor_rayon),
            Poche("top_mid",0, l/2, mid_rayon),
            Poche("top_right",0, l, cor_rayon),
            Poche("bot_left", L, 0, cor_rayon),
            Poche("bot_mid", L, l/2, mid_rayon),
            Poche("bot_right", L, l, cor_rayon),
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
            white.pos = np.array([x, y], dtype=float)
            white.vit = np.zeros(2, dtype=float)
            white.is_potted = False

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
        pt = np.array([x,y],dtype=float)
        dist = float(np.linalg.norm(pt-self.baulk_center))
        return dist <= self.baulk_zone_rayon and y <= self.baulk_line_y

    def setup_balls(self) -> None:
        """
        Place toutes les billes en position de début de frame.
        Bille blanche dans la zone D, rouges en triangle,
        couleurs sur leurs spots.
        """

        self.balls.clear()

        # Bille blanche
        self.balls.append(Ball(self.largeur/2,self.baulk_line_y - 10,"white",0,0))

        # Couleurs sur leurs spots réglementaires
        spots = [
            (16, "yellow", 2,self.largeur / 2 - 18.4,self.baulk_line_y),
            (17, "green", 3,self.largeur/ 2 + 18.4,self.baulk_line_y),
            (18, "brown", 4, self.largeur / 2,self.baulk_line_y),
            (19, "blue", 5, self.largeur / 2, self.longueur / 2),
            (20, "pink", 6, self.largeur/2, self.longueur*0.74),
            (21, "black", 7, self.largeur/2, self.longueur*0.89),
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
        start_y = pink.pos[1] + r * 2
        ball_id = 1
        cx = self.largeur / 2
        for row in range(5):  # rangées : 1, 2, 3, 4, 5 billes
            n_balls = row + 1
            y = start_y + row * row_gap
            # Les billes de la rangée sont centrées horizontalement
            start_x = cx - row * r
            for col in range(n_balls):
                x = start_x + col * r * 2
                self.balls.append(Ball(x, y, "red", 1, ball_id))
                ball_id += 1

    def get_valid_baulk_position(self) -> np.ndarray:
        """
        Retourne une position valide dans la zone D pour replacer la bille blanche.
        Essaie le centre du D en premier, puis cherche une position libre
        en tournant autour du centre si celui-ci est occupé.

        Returns
        -------
        np.ndarray
            Position [x, y] valide dans la zone D.
        """
        # On essaie d'abord le centre du D
        candidate = self.baulk_center.copy()

        active_balls = [b for b in self.balls if not b.is_potted and b.id != 0]

        # On vérifie que la position candidate ne chevauche aucune bille
        for angle_deg in range(0, 360, 15):  # on tourne par pas de 15°
            angle_rad = math.radians(angle_deg)
            valid = True

            for ball in active_balls:
                dist = float(np.linalg.norm(candidate - ball.pos))
                if dist < ball.rayon * 2 + 0.5:  # chevauchement détecté
                    valid = False
                    break

            if valid:
                return candidate

            # On essaie une nouvelle position dans le D
            RAYON = 2.625  # rayon fixe, identique pour toutes les billes
            offset = np.array([
                math.cos(angle_rad) * RAYON * 3,
                math.sin(angle_rad) * RAYON * 3,
            ])
            new_candidate = self.baulk_center + offset

            # On vérifie que la nouvelle position est bien dans le D
            dist_center = float(np.linalg.norm(new_candidate - self.baulk_center))
            if dist_center <= self.baulk_zone_rayon and new_candidate[1] <= self.baulk_line_y:
                candidate = new_candidate

        # En dernier recours, on retourne le centre même si occupé
        return self.baulk_center.copy()

    def replace_colour(self, ball: Ball) -> None:
        """
        Replace une bille couleur sur son spot réglementaire.
        Si le spot est occupé, cherche le spot libre le plus valorisé.

        Parameters
        ----------
        ball : Ball
            La bille couleur à replacer.
        """
        # Ordre de priorité si le spot est occupé : du plus valorisé au moins
        priority_order = [21, 20, 19, 18, 17, 16]  # noire → jaune

        spot = self.colour_spots.get(ball.id)
        if spot is None:
            return  # bille inconnue

        # On vérifie si le spot est libre
        if self._spot_is_free(spot):
            ball.pos = spot.copy()
            ball.vit = np.zeros(2, dtype=float)
            ball.is_potted = False
            return

        # Spot occupé : on cherche le spot libre le plus valorisé
        for bid in priority_order:
            candidate = self.colour_spots[bid]
            if self._spot_is_free(candidate):
                ball.pos = candidate.copy()
                ball.vit = np.zeros(2, dtype=float)
                ball.is_potted = False
                return

        # En dernier recours : on place derrière la noire
        ball.pos = np.array([self.largeur / 2, self.longueur * 0.92])
        ball.vit = np.zeros(2, dtype=float)
        ball.is_potted = False

    def _spot_is_free(self, spot: np.ndarray) -> bool:
        """
        Vérifie si un spot est libre (aucune bille active ne le chevauche).
        """
        for b in self.get_active_balls():
            dist = float(np.linalg.norm(b.pos - spot))
            if dist < b.rayon * 2:
                return False
        return True