"""
ihm/table_view.py
-----------------
Gère le rendu graphique de la table de snooker
dans le QGraphicsView de Qt Designer.
"""

import math

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt


class TableView:
    """
    Dessine la table, les poches et les billes dans un QGraphicsView.

    Attributes
    ----------
    view : QGraphicsView
        Le widget Qt sur lequel on dessine.
    table : Tables
        La table de snooker avec ses billes et poches.
    scene : QGraphicsScene
        La scène Qt rattachée au view.
    scale_x : float
        Facteur d'échelle cm → pixels sur l'axe X.
    scale_y : float
        Facteur d'échelle cm → pixels sur l'axe Y.
    scale_avg : float
        Moyenne des deux échelles pour les rayons (billes, poches).
    width_px : int
        Largeur du view en pixels.
    height_px : int
        Hauteur du view en pixels.
    """

    # Ajoute cette constante en haut de la classe
    BORDER = 20  # épaisseur du bord marron en pixels

    def __init__(self, graphics_view, table) -> None:
        self.view = graphics_view
        self.table = table

        self.width_px = graphics_view.width()
        self.height_px = graphics_view.height()

        # Le tapis vert est à l'intérieur du bord
        self.tapis_x = self.BORDER
        self.tapis_y = self.BORDER
        self.tapis_w = self.width_px - 2 * self.BORDER
        self.tapis_h = self.height_px - 2 * self.BORDER

        # Échelle basée sur le tapis intérieur uniquement
        self.scale_x = self.tapis_w / table.largeur
        self.scale_y = self.tapis_h / table.longueur
        self.scale_avg = (self.scale_x + self.scale_y) / 2

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.width_px, self.height_px)
        self.view.setScene(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(self.width_px, self.height_px)
        self.view.setSceneRect(0, 0, self.width_px, self.height_px)

    def to_px(self, x_cm, y_cm):
        # Décalé par le bord
        px = self.BORDER + x_cm * self.scale_x
        py = self.height_px - self.BORDER - (y_cm * self.scale_y)
        return px, py

    # ------------------------------------------------------------------
    # Dessin principal
    # ------------------------------------------------------------------

    def draw(self, angle_deg: float = 90.0, force: float = 60.0) -> None:
        """
        Efface et redessine toute la scène.
        À appeler à chaque frame.

        Parameters
        ----------
        angle_deg : float
            Angle courant du slider pour la trajectoire.
        force : float
            Force courante du slider pour la longueur du trait.
        """
        self.scene.clear()
        self._draw_table()
        self._draw_baulk()
        self._draw_pockets()
        self._draw_trajectory(angle_deg, force)
        self._draw_balls()

    # ------------------------------------------------------------------
    # Éléments de la table
    # ------------------------------------------------------------------

    def _draw_table(self) -> None:
        # Bord marron (toute la surface)
        self.scene.addRect(
            0, 0,
            self.width_px, self.height_px,
            QPen(Qt.NoPen),
            QBrush(QColor("#5C3317"))  # marron bois
        )
        # Tapis vert intérieur
        self.scene.addRect(
            self.BORDER, self.BORDER,
            self.tapis_w, self.tapis_h,
            QPen(Qt.NoPen),
            QBrush(QColor("#2d8a2d"))
        )

    def _draw_baulk(self) -> None:
        """Dessine la ligne de baulk et le demi-cercle D."""
        pen_white = QPen(QColor("white"), 1)

        # Position Y de la ligne de baulk en pixels
        baulk_py = self.height_px - (self.table.baulk_line_y * self.scale_y)

        # Centre du demi-cercle en pixels
        cx, cy = self.to_px(
            self.table.baulk_center[0],
            self.table.baulk_center[1]
        )

        # Rayon en pixels (on utilise scale_x car le rayon est horizontal)
        r_px = self.table.baulk_zone_rayon * self.scale_x

        # 1 — Cercle complet
        self.scene.addEllipse(
            cx - r_px, cy - r_px,
            r_px * 2, r_px * 2,
            pen_white,
            QBrush(Qt.transparent)
        )

        # 2 — Masque la moitié haute (au-dessus de la ligne de baulk)
        self.scene.addRect(
            cx - r_px, cy - r_px,
            r_px * 2, r_px,
            QPen(Qt.transparent),
            QBrush(QColor("#2d8a2d"))
        )

        # 3 — Ligne de baulk par-dessus le masque
        self.scene.addLine(0, baulk_py, self.width_px, baulk_py, pen_white)

    def _draw_pockets(self) -> None:
        """Dessine les 6 poches en noir."""
        for pocket in self.table.poches:
            px, py = self.to_px(pocket.pos[0], pocket.pos[1])
            r = pocket.rayon * self.scale_avg *1.5
            self.scene.addEllipse(
                px - r, py - r, r * 2, r * 2,
                QPen(Qt.black),
                QBrush(Qt.black)
            )

    def _draw_balls(self) -> None:
        """Dessine chaque bille active avec sa couleur réelle."""
        colors = {
            'white':  '#FFFFFF',
            'red':    '#CC0000',
            'yellow': '#FFD700',
            'green':  '#00AA00',
            'brown':  '#8B4513',
            'blue':   '#4444FF',
            'pink':   '#FF69B4',
            'black':  '#111111',
        }
        for ball in self.table.get_active_balls():
            px, py = self.to_px(ball.pos[0], ball.pos[1])
            r = ball.rayon * self.scale_avg
            color = QColor(colors.get(ball.color, '#FFFFFF'))
            self.scene.addEllipse(
                px - r, py - r, r * 2, r * 2,
                QPen(Qt.black, 0.5),
                QBrush(color)
            )

    def _draw_trajectory(self, angle_deg: float, force: float) -> None:
        white = self.table.get_ball_id(0)
        if white is None or white.is_potted:
            return

        angle_rad = math.radians(angle_deg)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        x, y = white.pos[0], white.pos[1]
        r = white.rayon

        step = 0.5
        max_dist = 500

        end_x, end_y = x, y
        hit_ball = None
        hit_wall = False

        for _ in range(int(max_dist / step)):
            nx = end_x + dx * step
            ny = end_y + dy * step

            # Bandes
            if nx - r < 0 or nx + r > self.table.largeur:
                hit_wall = True
                break
            if ny - r < 0 or ny + r > self.table.longueur:
                hit_wall = True
                break

            # Collision bille
            for ball in self.table.get_active_balls():
                if ball.id == 0:
                    continue
                dist = math.sqrt((nx - ball.pos[0]) ** 2 + (ny - ball.pos[1]) ** 2)
                if dist <= r + ball.rayon:
                    hit_ball = ball
                    break

            if hit_ball or hit_wall:
                break

            end_x, end_y = nx, ny

        # ── Trait principal blanche ──────────────────
        px_start, py_start = self.to_px(x, y)
        px_end, py_end = self.to_px(end_x, end_y)

        pen_white = QPen(QColor("white"), 1)
        pen_white.setStyle(Qt.DashLine)
        self.scene.addLine(px_start, py_start, px_end, py_end, pen_white)

        # ── Impact sur une bille ─────────────────────
        if hit_ball:
            # Cercle fantôme à la position d'impact
            r_px = r * self.scale_avg
            self.scene.addEllipse(
                px_end - r_px, py_end - r_px,
                r_px * 2, r_px * 2,
                QPen(QColor("white"), 1),
                QBrush(Qt.transparent)
            )

            # Vecteur normal de la blanche vers la bille cible
            nx_vec = hit_ball.pos[0] - end_x
            ny_vec = hit_ball.pos[1] - end_y
            norm = math.sqrt(nx_vec ** 2 + ny_vec ** 2)
            if norm > 0:
                nx_vec /= norm
                ny_vec /= norm

            # Trait direction bille cible (jaune)
            longueur_cible = 40  # cm
            cible_end_x = hit_ball.pos[0] + nx_vec * longueur_cible
            cible_end_y = hit_ball.pos[1] + ny_vec * longueur_cible
            px_c1, py_c1 = self.to_px(hit_ball.pos[0], hit_ball.pos[1])
            px_c2, py_c2 = self.to_px(cible_end_x, cible_end_y)

            pen_yellow = QPen(QColor("yellow"), 1)
            pen_yellow.setStyle(Qt.DashLine)
            self.scene.addLine(px_c1, py_c1, px_c2, py_c2, pen_yellow)

            # Vecteur tangentiel blanche après impact (perpendiculaire au normal)
            # La blanche repart perpendiculairement à l'axe de collision
            tx = -ny_vec  # tangente = perpendiculaire au normal
            ty = nx_vec

            # Produit scalaire pour savoir de quel côté
            dot = dx * tx + dy * ty
            if dot < 0:
                tx, ty = -tx, -ty

            longueur_blanche = 30  # cm
            blanche_end_x = end_x + tx * longueur_blanche
            blanche_end_y = end_y + ty * longueur_blanche
            px_b1, py_b1 = self.to_px(end_x, end_y)
            px_b2, py_b2 = self.to_px(blanche_end_x, blanche_end_y)

            pen_blue = QPen(QColor("#88CCFF"), 1)
            pen_blue.setStyle(Qt.DashLine)
            self.scene.addLine(px_b1, py_b1, px_b2, py_b2, pen_blue)

        # ── Impact sur une bande ─────────────────────
        elif hit_wall:
            r_px = r * self.scale_avg
            self.scene.addEllipse(
                px_end - r_px, py_end - r_px,
                r_px * 2, r_px * 2,
                QPen(QColor("white"), 1),
                QBrush(Qt.transparent)
            )