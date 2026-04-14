"""
Moteur physique du snooker.

Responsabilités :
    - Déplacer les billes à chaque pas de temps (dt)
    - Appliquer les frottements
    - Modéliser les collisions sur les billes et les bandes
    - Appliquer un tir

"""

import math
import numpy as np
from objects.ball import Ball
from objects.table import Tables

class Physique :
    """
    Moteur de simulation pour le snooker.

    faire docstring tu connais
    """

    def __init__(self, dt:float = 1/60)->None:
        self.dt = dt

    def apply_shot(self, ball : Ball, angle_deg : float, force : float)-> None :
        """
        Applique un tir sur la bille blanche

        Parameters
        ----------
        ball : Ball
            La bille à frapper (la blanche).
        angle_deg : float
            Angle en degrés.
        force : float
            Force du tir entre 0 et 100, valeur arbitraire

        """

        #déf force arbitraire + voir valeur de max_speed

        angle_rad = math.radians(angle_deg)
        max_speed = 500 #en cm/s
        speed = (force/100)*max_speed

        #Décomposition de la vitesse en 2 composantes
        ball.vit = np.array([
            speed * math.cos(angle_rad),
            speed * math.sin(angle_rad),
        ], dtype=float)


    def move_ball(self, ball:Ball)->None:
        """
        Déplace une bille et applique le frottement du tapis
        """
        if not ball.is_moving():
            ball.vit=np.zeros(2, dtype=float)
            return

        ball.pos *= ball.vit*self.dt

        #On réduit la vitesse à chaque dt avec le coef de friction
        ball.vit *= self.table.friction_coef ** self.dt #permet que le ralentissement soit le même quelque soit le dt choisi, sinon, la bille freinera 2 fois moins vite en mettant dt=1/30 au lieu de dt= 1/60
        #VOIR AVEC ANTOINE COMMENT ON VOIT FRICTION_COEF

    def resolve_ball_collision(self, b1 : Ball, b2 : Ball)-> None:
        """
        Gère la collision entre 2 billes
        :param b1:
        :param b2:
        :return:
        """

        delta = b1.pos - b2.pos
        dist = float(np.linalg.norm(delta))
        min_dist = b1.rayon + b2.rayon

        #1er cas : les billes ne se touchent pas
        if dist==0 or dist >= min_dist: #dist=0 pour éviter la division par 0 en dessous
            return
        #A FINIR



    def resolve_table_collision(self, ball:Ball)->None:
        """
        Fait rebondir les billes sur le bord de la table
        :param ball:
        :return:
        """
        r = ball.rayon()

        #A FAIRE

        #Côté gauche

        #Côté droit

        #En bas

        #En haut


    def check_pocket(self):
        """
        Vérifie si la bille est dans une poche
        :return:
        """
        #A FAIRE


    def step(self) -> list[Ball]:
        """
        Avance la simulation d'un pas de temps

        """
        self.potted_this_step = []
        active = self.table.get_active_balls() #on ignore les billes déjà empochées

        for ball in active :
            self.move_ball(ball)

        #Collisions entre billes
        for i in range(len(active)):
            for j in range(i+1,len(active)):
                self.resolve_ball_collision(active[i], active[j])

        #Collisions avec la table
        for ball in active :
            self.resolve_table_collision(ball)
            self.check_pocket(ball)

        return self.potted_this_step
