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
from objets.ball import Ball
from objets.table import Tables

class Physique :
    """
    Moteur de simulation pour le snooker.

    faire docstring tu connais
    """

    def __init__(self, table : Tables, dt:float = 1/60)->None:
        self.dt = dt
        self.table = table #attribut car permanent

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

        ball.pos += ball.vit*self.dt

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

        delta = b2.pos - b1.pos
        dist = float(np.linalg.norm(delta))
        min_dist = b1.rayon + b2.rayon

        #1er cas : les billes ne se touchent pas
        if dist==0 or dist >= min_dist: #dist=0 pour éviter la division par 0 en dessous
            return

        normal = delta / dist         # vecteur unitaire de b1 vers b2
        overlap = min_dist - dist     # combien les billes se chevauchent

        # On recule chaque bille de la moitié du chevauchement
        b1.pos -= normal * (overlap / 2)
        b2.pos += normal * (overlap / 2)

        # Échange des vitesses selon l'axe de collision (collision élastique, masses égales)
        v1n = np.dot(b1.vit, normal) #projection de la vitesse
        v2n = np.dot(b2.vit, normal)

        # On n'agit que si les billes se rapprochent encore (évite les doubles résolutions)
        if v1n - v2n <= 0: #cela signifie que les billes s'éloignent car la bille 2 a une vitesse + élevée que la 1
            return

        b1.vit += (v2n - v1n) * normal
        b2.vit += (v1n - v2n) * normal

        #Exemple : b1 arrive en diagonale sur b2 immobile
        # b1 vitesse = [3, 2]
        # normal = [1, 0] (b2 est directement à droite de b1)
        #
        # v1n = dot([3, 2], [1, 0]) = 3  # composante vers b2
        # v2n = dot([0, 0], [1, 0]) = 0  # b2 immobile
        #
        # après collision:
        # b1.vit = [3, 2] + (0 - 3) * [1, 0] = [0, 2]  # perd sa vitesse horizontale
        # b2.vit = [0, 0] + (3 - 0) * [1, 0] = [3, 0]  # repart horizontalement

    def resolve_table_collision(self, ball:Ball)->None:
        """
        Fait rebondir les billes sur le bord de la table

        Le rebond est supposé parfaitement élastique (pas de perte
        d'énergie sur la bande). La bille est repositionnée hors de
        la bande avant d'inverser la composante de vitesse concernée.

        :param ball:
        :return:
        """
        r = ball.rayon
        x, y = ball.pos

        #Côté gauche
        if x - r < 0:
            ball.pos[0] = r
            ball.vit[0] = abs(ball.vit[0]) #on inverse la composante vx pour que la balle reparte avec un angle de 45° avec la normale
        #Si la balle allait vers le côté gauche, vx < 0 donc on inverse bien la composante

        #Côté droit
        elif x + r > self.table.longueur:
            ball.pos[0] = self.table.longueur - r
            ball.vit[0] = -abs(ball.vit[0])

        #En bas
        if y - r < 0:
            ball.pos[1] = r
            ball.vit[1] = abs(ball.vit[1])

        #En haut
        elif y + r > self.table.largeur:
            ball.pos[1] = self.table.largeur - r
            ball.vit[1] = -abs(ball.vit[1])

    def check_pocket(self, ball:Ball)-> None:
        """
        Vérifie si la bille est dans une poche
        :return:
        """
        for pocket in self.table.poches:
            if pocket.contains(ball):
                ball.is_potted = True
                ball.vit = np.zeros(2, dtype=float)
                self.potted_this_step.append(ball)
                break  # une seule poche à la fois suffit

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
