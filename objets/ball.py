"""
Représente une bille de snooker sur la table.
"""

import numpy as np

class Ball:
    """
    Une bille de snooker
    """
    def __init__(self, x:float, y:float, color:str, points:int, ball_id: int)->None:
        """
        Initialise une bille de snooker.

        Parameters
        ----------
        x : float
            Position X initiale en cm.
        y : float
            Position Y initiale en cm.
        color : str
            Couleur de la bille ('white', 'red', 'yellow', etc.).
        points : int
            Valeur en points de la bille (0 pour la blanche, 1 pour les rouges, 2-7 pour les couleurs).
        ball_id : int
            Identifiant unique de la bille (0 = blanche, 1-15 = rouges, 16-21 = couleurs).
        """
        self.pos = np.array([x, y], dtype=float)
        self.color = color
        #self.speed = speed pas utile il me semble car on a déjà le vecteur vitesse
        self.points = points
        self.id = ball_id
        self.rayon = 3.7    #en cm
        self.vit  = np.zeros(2, dtype=float)
        self.is_potted = False #est-ce que la bille est empochée

    def is_moving(self)->bool:
        """
        Indique si la bille est en mouvement.

        Returns
        -------
        bool
            True si la vitesse dépasse le seuil minimal.
        """
        return (float(np.linalg.norm(self.vit))) > 0.5

    def reset(self,x:float, y:float)->None:
        """
        Replace la bille à une position donnée et l'arrête.

        Parameters
        ----------
        x : float
            Nouvelle position X.
        y : float
            Nouvelle position Y.
        """
        self.pos = np.array([x,y], dtype=float)
        self.vit = np.zeros(2, dtype=float)
        self.is_potted = False

    def __repr__(self) -> str:
        """
        Représentation officielle de la bille sous forme de chaîne de caractères.
        Affiche l'identifiant, la couleur, la position, la vitesse et l'état d'empochage.

        Returns
        -------
        str
            Chaîne décrivant l'état complet de la bille.
        """
        return (
            f"Ball(id={self.id}, color='{self.color}', "
            f"pos=({self.pos[0]:.1f}, {self.pos[1]:.1f}), "
            f"vel=({self.vit[0]:.2f}, {self.vit[1]:.2f}), "
            f"potted={self.is_potted})"
        )

