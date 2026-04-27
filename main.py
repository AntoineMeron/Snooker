"""

Test visuel ASCII de la table de Snooker.
Affiche la table dans le terminal avec les billes et
simule les déplacements et collisions sans IHM graphique.

"""

import sys
import os
import time
import numpy as np

from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique

COLS = 80
ROWS = 24

def render(table:Tables,step:int = 0)->None:
    """
    Affiche la table et les billes dans le terminal en ASCII.

    La table réelle (356.9 x 177.8 cm) est mise à l'échelle
    dans une grille COLS x ROWS de caractères.

    """

    grid = [['.' for _ in range(COLS)] for _ in range(ROWS)] #la grille vide

    def to_col(x: float) -> int:
        """Convertit une coordonnée X cm en colonne ASCII."""
        return int(x / table.largeur * (COLS - 2)) + 1

    def to_row(y: float) -> int:
        """Convertit une coordonnée Y cm en ligne ASCII (Y inversé)."""
        return (ROWS - 2) - int(y / table.longueur * (ROWS - 2))

    # Représentation des billes
    color_symbol = {
        'white': 'W',
        'red': 'R',
        'yellow': 'Y',
        'green': 'G',
        'brown': 'N',
        'blue': 'B',
        'pink': 'M',
        'black': 'K',
    }

    for ball in table.get_active_balls():
        c = to_col(ball.pos[0])
        r = to_row(ball.pos[1])
        if 0 <= r < ROWS and 0 <= c < COLS:
            symbol = color_symbol.get(ball.color, '?')
            grid[r][c] = symbol

    # Affichage

    border_h = '#' * (COLS + 2)
    os.system('clear' if os.name == 'posix' else 'cls')

    print(border_h)
    for row in grid:
        print('#' + ''.join(row) + '#')
    print(border_h)

    # Légende et stats
    active = table.get_active_balls()
    moving = [b for b in active if b.is_moving()]
    print(f"  Step {step:>5}  |  Billes actives : {len(active):>2}  "
          f"|  En mouvement : {len(moving):>2}")
    print("  W=blanche  R=rouge  Y=jaune  G=verte  "
          "N=brune  B=bleue  M=rose  K=noire  P=poche")


def main():
    engine = Physique(dt=1/60)
    table = Tables()
    table.setup_balls()