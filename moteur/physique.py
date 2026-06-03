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
import copy
from objets.ball import Ball
from objets.table import Tables

_MAX_RECURSION = 200


class Physique:
    """
    Moteur de simulation pour le snooker.

    Gère l'intégralité de la physique du jeu : déplacement des billes,
    frottements du tapis, collisions élastiques bille-bille, rebonds
    sur les bandes avec coefficient de restitution, et détection des empochages.

    Attributes
    ----------
    table : Tables
        La table de snooker sur laquelle la simulation s'exécute.
        Attribut permanent — stocké dans self car utilisé dans toutes les méthodes.
    dt : float
        Pas de temps de la simulation en secondes (défaut : 1/60 pour 60 fps).
    potted_this_step : list[Ball]
        Billes empochées lors du dernier appel à step().
        Réinitialisé à chaque appel de step().
    """

    def __init__(self, table: Tables, dt: float = 1/60) -> None:
        """
        Initialise le moteur physique.

        Parameters
        ----------
        table : Tables
            La table de snooker sur laquelle la simulation s'exécute.
        dt : float
            Pas de temps en secondes. 1/60 par défaut (60 fps).
        """
        self.dt = dt
        self.table = table  # attribut car permanent

    def apply_shot(self, ball: Ball, angle_deg: float, force: float) -> None:
        """
        Applique un tir sur une bille en lui donnant une vitesse initiale.

        La vitesse est décomposée en composantes X et Y selon l'angle.
        La force est une valeur arbitraire entre 0 et 100, convertie
        en cm/s par un facteur d'échelle (force 100 = 500 cm/s).

        Parameters
        ----------
        ball : Ball
            La bille à frapper (généralement la blanche).
        angle_deg : float
            Angle du tir en degrés (0° = droite, sens antihoraire).
        force : float
            Force du tir entre 0 et 100.
        """
        angle_rad = math.radians(angle_deg)
        max_speed = 500  # en cm/s
        speed = (force / 100) * max_speed

        # Décomposition de la vitesse en 2 composantes
        ball.vit = np.array([
            speed * math.cos(angle_rad),
            speed * math.sin(angle_rad),
        ], dtype=float)

    def move_ball(self, ball: Ball) -> None:
        """
        Déplace une bille d'un pas de temps et applique le frottement du tapis.

        Si la bille est sous le seuil de is_moving(), elle est stoppée nettement.
        Le frottement est appliqué par multiplication de la vitesse par
        friction_coef à chaque frame — ce coefficient est donc défini
        par frame et non par seconde.

        Parameters
        ----------
        ball : Ball
            La bille à déplacer.
        """
        if not ball.is_moving():
            ball.vit = np.zeros(2, dtype=float)
            return

        # Intégration d'Euler : nouvelle position = ancienne + vitesse * dt
        ball.pos += ball.vit * self.dt

        # Frottement : on réduit la vitesse à chaque frame via friction_coef
        ball.vit *= self.table.friction_coef

    def resolve_ball_collision(self, b1: Ball, b2: Ball) -> None:
        """
        Résout la collision élastique entre deux billes de même masse.

        La détection se fait par chevauchement des rayons. En cas de collision :
            1. Les billes sont séparées (correction de position).
            2. Les composantes de vitesse sur l'axe normal sont échangées.

        La condition v1n - v2n > 0 garantit qu'on n'agit que si les billes
        se rapprochent encore, évitant les doubles résolutions dues aux
        imprécisions numériques.

        Exemple : b1 arrive en diagonale sur b2 immobile
            b1 vitesse = [3, 2], normal = [1, 0] (b2 à droite de b1)
            v1n = dot([3,2],[1,0]) = 3, v2n = dot([0,0],[1,0]) = 0
            après : b1.vit = [0, 2], b2.vit = [3, 0]

        Parameters
        ----------
        b1 : Ball
            Première bille.
        b2 : Ball
            Deuxième bille.
        """
        delta = b2.pos - b1.pos
        dist = float(np.linalg.norm(delta))
        min_dist = b1.rayon + b2.rayon

        # Pas de collision si les billes ne se touchent pas
        # dist == 0 évite la division par zéro sur la ligne normale
        if dist == 0 or dist >= min_dist:
            return

        normal = delta / dist         # vecteur unitaire de b1 vers b2
        overlap = min_dist - dist     # combien les billes se chevauchent

        # On recule chaque bille de la moitié du chevauchement
        b1.pos -= normal * (overlap / 2)
        b2.pos += normal * (overlap / 2)

        # Échange des vitesses selon l'axe de collision (collision élastique, masses égales)
        v1n = np.dot(b1.vit, normal)  # projection de la vitesse de b1 sur l'axe normal
        v2n = np.dot(b2.vit, normal)  # projection de la vitesse de b2 sur l'axe normal

        # On n'agit que si les billes se rapprochent encore (évite les doubles résolutions)
        if v1n - v2n <= 0:
            return

        b1.vit += (v2n - v1n) * normal
        b2.vit += (v1n - v2n) * normal

    def resolve_table_collision(self, ball: Ball) -> None:
        """
        Fait rebondir une bille sur les quatre bandes de la table.

        La bille est repositionnée hors de la bande avant d'inverser
        la composante de vitesse concernée. Le rebond n'est pas parfaitement
        élastique : la vitesse est multipliée par restitution_coef (0.8)
        pour simuler la perte d'énergie réelle sur les coussins.

        Parameters
        ----------
        ball : Ball
            La bille à tester et repositionner si nécessaire.
        """
        r = ball.rayon
        x, y = ball.pos
        k = self.table.restitution_coef

        # Bande gauche : si vx < 0, on force vx > 0 (repart vers la droite)
        if x - r < 0:
            ball.pos[0] = r
            ball.vit[0] = abs(ball.vit[0]) * k

        # Bande droite : si vx > 0, on force vx < 0 (repart vers la gauche)
        elif x + r > self.table.largeur:
            ball.pos[0] = self.table.largeur - r
            ball.vit[0] = -abs(ball.vit[0]) * k

        # Bande basse : si vy < 0, on force vy > 0 (repart vers le haut)
        if y - r < 0:
            ball.pos[1] = r
            ball.vit[1] = abs(ball.vit[1]) * k

        # Bande haute : si vy > 0, on force vy < 0 (repart vers le bas)
        elif y + r > self.table.longueur:
            ball.pos[1] = self.table.longueur - r
            ball.vit[1] = -abs(ball.vit[1]) * k

    def check_pocket(self, ball: Ball) -> None:
        """
        Vérifie si une bille est tombée dans une poche.

        Si le centre de la bille se trouve dans le rayon d'une poche,
        la bille est marquée comme empochée, sa vitesse est annulée,
        et elle est ajoutée à potted_this_step.
        On s'arrête à la première poche trouvée (break).

        Parameters
        ----------
        ball : Ball
            La bille à tester.
        """
        for pocket in self.table.poches:
            if pocket.contains(ball):
                ball.is_potted = True
                ball.vit = np.zeros(2, dtype=float)
                self.potted_this_step.append(ball)
                break  # une seule poche à la fois suffit

    def step(self) -> list[Ball]:
        """
        Avance la simulation d'un pas de temps complet.

        Ordre des opérations à chaque step :
            1. Déplacement et frottement de chaque bille active.
            2. Résolution des collisions bille-bille (chaque paire une fois).
            3. Vérification des empochages.
            4. Résolution des collisions bille-bande.

        Returns
        -------
        list[Ball]
            Liste des billes empochées durant ce pas de temps.
        """
        self.potted_this_step = []
        active = self.table.get_active_balls()  # on ignore les billes déjà empochées

        for ball in active:
            self.move_ball(ball)

        # Collisions entre billes — i < j évite les doublons
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                self.resolve_ball_collision(active[i], active[j])

        # Empochages puis rebonds sur les bandes
        for ball in active:
            self.check_pocket(ball)
            self.resolve_table_collision(ball)

        return self.potted_this_step

    def all_stopped(self) -> bool:
        """
        Indique si toutes les billes actives sont immobiles.

        Utilise is_moving() défini dans Ball, qui compare la norme
        de la vitesse à un seuil minimal (0.5 cm/s).

        Returns
        -------
        bool
            True si aucune bille active n'est en mouvement.
        """
        return all(not ball.is_moving() for ball in self.table.get_active_balls())

    def predict_trajectory(self, ball: Ball, table: Tables, steps: int = 0,
                           max_steps: int = _MAX_RECURSION,
                           path: list = None) -> list[np.ndarray]:
        """
        Prédit la trajectoire d'une bille par simulation récursive.

        Chaque appel récursif simule un pas de temps, applique le frottement
        et les rebonds sur les bandes, puis ajoute la position courante
        à l'accumulateur path.

        La récursion s'arrête quand :
            - La bille est immobile (vitesse sous le seuil)
            - La profondeur maximale est atteinte (max_steps)
            - La bille entre dans une poche

        À l'appel initial, ne pas passer steps ni path —
        ils sont initialisés automatiquement.

        Parameters
        ----------
        ball : Ball
            Bille dont on prédit la trajectoire. Utiliser une copie
            pour ne pas modifier la bille réelle.
        table : Tables
            La table (pour les bandes et les poches).
        steps : int
            Compteur de récursion courant. Ne pas passer à l'appel initial.
        max_steps : int
            Profondeur maximale de récursion (défaut : 200).
        path : list[np.ndarray] or None
            Accumulateur de positions. Ne pas passer à l'appel initial.

        Returns
        -------
        list[np.ndarray]
            Liste de vecteurs position [x, y] le long de la trajectoire prédite.
        """
        if path is None:
            path = [ball.pos.copy()]

        # Cas d'arrêt 1 : bille immobile
        if not ball.is_moving():
            return path

        # Cas d'arrêt 2 : profondeur maximale atteinte
        if steps >= max_steps:
            return path

        # Cas d'arrêt 3 : bille empochée
        for pocket in self.table.poches:
            if pocket.contains(ball):
                return path

        ball.pos = ball.pos + ball.vit * self.dt
        ball.vit = ball.vit * self.table.friction_coef

        # Arrêt net sous le seuil
        if float(np.linalg.norm(ball.vit)) < 0.5:
            ball.vit = np.zeros(2, dtype=float)

        # Rebonds sur les bandes
        self.resolve_table_collision(ball)

        path.append(ball.pos.copy())

        # Appel récursif
        return self.predict_trajectory(ball, table, steps + 1, max_steps, path)