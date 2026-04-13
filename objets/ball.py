"""
Représente une bille de snooker sur la table.
"""

import numpy as np

class Ball:
    """
    Une bille de snooker.
    """
    def __init__(self, x:float, y:float, speed:float, color:str, points:int, ball_id: int)->None:
        self.pos = np.array([x, y], dtype=float)
        self.color = color
        self.speed = speed
        self.points = points
        self.id = ball_id
        self.rayon = 2.625 #en cm
        self.vit: np.ndarray = np.zeros(2, dtype=float)
        self.is_potted = False #est-ce que la bille est empochée

    def is_moving(self)->bool:
        """
        Indique si la bille est en mouvement.

        Returns
        -------
        bool
            True si la vitesse dépasse le seuil minimal.
        """
        return (float(np.linalg.norm(self.vit))) > 0.01

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
            Méthode spéciale qui définit la représentation officielle d’un objet sous forme de chaîne de caractères.
            """
            return (
                f"Ball(id={self.id}, color='{self.color}', "
                f"pos=({self.pos[0]:.1f}, {self.pos[1]:.1f}), "
                f"vel=({self.vel[0]:.2f}, {self.vel[1]:.2f}), "
                f"potted={self.is_potted})"
            )

