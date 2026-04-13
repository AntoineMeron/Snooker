"""
Représente une poche de la table de snooker
"""

import numpy as np

class Poche:
    """
    Une poche de la table de snooker

    """

    def __init__(self, position_id:str,x:float,y:float,rayon:float)->None:
        """
        Initialisation de la poche

        Parameters
        ----------
        position_id : str
            Identifiant de la poche.
        x : float
            Position X du centre.
        y : float
            Position Y du centre.
        """
        self.position_id = position_id
        self.pos = np.ndarray([x,y], dtype=float)
        self.rayon = rayon

    def contains(self, ball)->bool:
        """
        Vérifie si le centre d'une bille est dans la poche.

        Parameters
        ----------
        ball : Ball
            La bille à tester.

        Returns
        -------
        bool
            True si la bille est dans le rayon de la poche.
        """
        return float(np.linalg.norm(ball.pos - self.pos)) <= self.rayon

    def distance_to(self, x: float, y: float) -> float:
        """
        Distance entre le centre de la poche et un point.

        Parameters
        ----------
        x : float
            Coordonnée X du point.
        y : float
            Coordonnée Y du point.

        Returns
        -------
        float
            Distance en cm.
        """
        return float(np.linalg.norm(self.pos - np.array([x, y])))

