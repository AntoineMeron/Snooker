# """
# main.py
# -------
# Test visuel ASCII de la table de snooker.
# Utilise GameController comme point d'entrée unique — pas de classe Shot.
#
# Utilisation :
#     python main.py
# """
#
# import sys
# import os
# import time
#
# sys.path.insert(0, os.path.dirname(__file__))
#
# from state.game_controller import GameController
#
# # ─────────────────────────────────────────────
# #  Dimensions de l'affichage ASCII
# # ─────────────────────────────────────────────
# COLS = 28 * 180 // 370 * 2
# ROWS = 28
#
#
# def render(gc: GameController, step: int = 0) -> None:
#     """
#     Affiche la table et les billes dans le terminal en ASCII.
#
#     Symboles :
#         #   bordure/bande
#         P   poche
#         W   blanche   R   rouge
#         Y   jaune     G   verte
#         N   brune     B   bleue
#         M   rose      K   noire
#         .   tapis vide
#     """
#     table = gc.table
#     grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
#
#     def to_col(x: float) -> int:
#         return int(x / table.largeur * (COLS - 2)) + 1
#
#     def to_row(y: float) -> int:
#         return (ROWS - 2) - int(y / table.longueur * (ROWS - 2))
#
#     # Poches
#     for pocket in table.poches:
#         c, r = to_col(pocket.pos[0]), to_row(pocket.pos[1])
#         if 0 <= r < ROWS and 0 <= c < COLS:
#             grid[r][c] = 'P'
#
#     # Billes
#     color_symbol = {
#         'white': 'W', 'red':    'R', 'yellow': 'Y',
#         'green': 'G', 'brown':  'N', 'blue':   'B',
#         'pink':  'M', 'black':  'K',
#     }
#     for ball in table.balls:
#         if not ball.is_potted:
#             c, r = to_col(ball.pos[0]), to_row(ball.pos[1])
#             if 0 <= r < ROWS and 0 <= c < COLS:
#                 grid[r][c] = color_symbol.get(ball.color, '?')
#
#     # Rendu
#     border = '#' * (COLS + 2)
#     os.system('clear' if os.name == 'posix' else 'cls')
#     print(border)
#     for row in grid:
#         print('#' + ''.join(row) + '#')
#     print(border)
#
#     # Stats
#     active  = [b for b in table.balls if not b.is_potted]
#     moving  = [b for b in active if b.is_moving()]
#     p = gc.current_player()
#     print(f"  Step {step:>5}  |  Tour : {p.name:<12}  "
#           f"|  Score : {p.score:>3}  |  Break : {p.current_break:>3}")
#     print(f"  Billes actives : {len(active):>2}  |  En mouvement : {len(moving):>2}"
#           f"  |  État : {gc.state}")
#     print("  W=blanche R=rouge Y=jaune G=verte N=brune B=bleue M=rose K=noire P=poche")
#
#
# def simulate_until_stopped(gc: GameController, render_fn, delay: float = 0.05):
#     """
#     Boucle de simulation : appelle run_frame() jusqu'à l'arrêt complet,
#     en affichant la table toutes les 3 frames.
#     """
#     step = 0
#     while gc.state == 'rolling':
#         gc.run_frame()
#         step += 1
#         if step % 3 == 0:
#             render_fn(gc, step)
#             time.sleep(delay)
#     render_fn(gc, step)
#     return step
#
#
# def main():
#     gc = GameController("Alice", "Bob")
#
#     # ── Affichage initial ──────────────────────────────
#     render(gc, step=0)
#     print("\n  Position initiale — Appuyez sur Entrée pour tirer...")
#     input()
#
#     # ── Tir 1 : Alice vise le triangle de rouges ───────
#     print("  Alice tire (angle=80°, force=60)...")
#     gc.handle_shot(angle_deg=70, force=60)
#     steps = simulate_until_stopped(gc, render)
#
#     print(f"\n  Tir terminé en {steps} steps ({steps/60:.2f}s simulées).")
#     potted = [b.color for b in gc.table.balls if b.is_potted]
#     print(f"  Billes empochées : {potted if potted else 'aucune'}")
#     print(f"  Score Alice : {gc.players[0].score}  |  Score Bob : {gc.players[1].score}")
#     input("\n  Appuyez sur Entrée pour le tir de Bob...")
#
#     # ── Tir 2 : Bob tire à 45° ─────────────────────────
#     print("  Bob tire (angle=45°, force=40)...")
#     gc.handle_shot(angle_deg=45.0, force=40)
#     steps = simulate_until_stopped(gc, render)
#
#     print(f"\n  Tir terminé en {steps} steps ({steps/60:.2f}s simulées).")
#     potted = [b.color for b in gc.table.balls if b.is_potted]
#     print(f"  Billes empochées au total : {potted if potted else 'aucune'}")
#     input("\n  Appuyez sur Entrée pour tester save/load...")
#
#     # ── Sauvegarde / chargement ────────────────────────
#     gc.save_game("save.json")
#     print("  Partie sauvegardée dans save.json")
#
#     gc2 = GameController("Alice", "Bob")
#     gc2.load_game("save.json")
#     print("  Partie rechargée depuis save.json")
#     render(gc2, step=0)
#
#     print("\n  Test ASCII terminé avec succès.")
#
#
# if __name__ == "__main__":
#     main()

import sys
from PyQt5.QtWidgets import QApplication, QInputDialog
from IHM.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    # Demande le nom du joueur 1
    name1, ok1 = QInputDialog.getText(
        None,
        "Snooker",
        "Nom du joueur 1 :"
    )
    if not ok1 or not name1.strip():
        name1 = "Joueur 1"

    # Demande le nom du joueur 2
    name2, ok2 = QInputDialog.getText(
        None,
        "Snooker",
        "Nom du joueur 2 :"
    )
    if not ok2 or not name2.strip():
        name2 = "Joueur 2"
    window = MainWindow(name1,name2)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()