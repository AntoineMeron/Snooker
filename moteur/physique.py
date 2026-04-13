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

class Physique :
    """
    Moteur de simulation pour le snooker.

    faire docstring tu connais
    """

    def __init__(self, dt:float = 1/60)->None:
        self.dt = dt

