"""
ihm/table_view.py
-----------------
Gère le rendu graphique de la table de snooker
dans le QGraphicsView de Qt Designer.
"""

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
    scale : float
        Facteur d'échelle cm → pixels.
    width_px : int
        Largeur du view en pixels.
    height_px : int
        Hauteur du view en pixels.
    """

    def __init__(self, graphics_view: QGraphicsView, table) -> None:
        """
        Initialise le rendu graphique.

        Parameters
        ----------
        graphics_view : QGraphicsView
            Le widget nommé 'table' dans Qt Designer.
        table : Tables
            La table de snooker.
        """
        self.view = graphics_view
        self.table = table

        # Dimensions du widget en pixels (fixées dans Qt Designer)
        self.width_px = graphics_view.width()
        self.height_px = graphics_view.height()

        # Échelle : on adapte au widget réel
        self.scale = (self.width_px - 2 * self.PADDING) / self.table.largeur

        # Création et rattachement de la scène
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # ------------------------------------------------------------------
    # Conversion coordonnées
    # ------------------------------------------------------------------

    PADDING = 10  # pixels de marge

    def to_px(self, x_cm: float, y_cm: float) -> tuple:
        px = self.PADDING + x_cm * self.scale
        py = self.height_px - self.PADDING - (y_cm * self.scale)
        return px, py

    # ------------------------------------------------------------------
    # Dessin principal
    # ------------------------------------------------------------------

    def draw(self,angle_deg: float = 90.0, force: float = 60.0) -> None:
        """
        Efface et redessine toute la scène.
        À appeler à chaque frame.
        """
        self.scene.clear()
        self._draw_table()
        self._draw_baulk()
        self._draw_pockets()
        self._draw_trajectory(angle_deg, force)
        self._draw_balls()

    def _draw_trajectory(self,angle_deg: float, force: float) -> None:
        """
        Dessine la trajectoire de la bille blanche.
        """
        import math
        from PyQt5.QtGui import QPen, QColor
        from PyQt5.QtCore import Qt

        white = self.table.get_ball_id(0)
        if white is None or white.is_potted:
            return

        # Longueur du trait proportionnelle à la force (max 150 px)
        longueur_px = (force / 100) * 150

        angle_rad = math.radians(angle_deg)
        px, py = self.to_px(white.pos[0], white.pos[1])

        # Point d'arrivée du trait
        end_px = px + longueur_px * math.cos(angle_rad)
        end_py = py - longueur_px * math.sin(angle_rad)  # Y inversé

        pen = QPen(QColor("white"), 1)
        pen.setStyle(Qt.DashLine)  # trait pointillé
        self.scene.addLine(px, py, end_px, end_py, pen)

    def _draw_table(self) -> None:
        """Dessine le fond vert du tapis."""
        self.scene.addRect(
            self.PADDING, self.PADDING,
            self.width_px - 2 * self.PADDING,
            self.height_px - 2 * self.PADDING,
            QPen(QColor("#1a1a1a"), 3),
            QBrush(QColor("#2d8a2d"))
        )

    def _draw_baulk(self) -> None:
        baulk_py = self.height_px - (self.table.baulk_line_y * self.scale)
        pen_white = QPen(QColor("white"), 1)
        r_px = self.table.baulk_zone_rayon * self.scale
        cx, cy = self.to_px(
            self.table.baulk_center[0],
            self.table.baulk_center[1]
        )

        # 1 — Cercle complet
        self.scene.addEllipse(
            cx - r_px, cy - r_px,
            r_px * 2, r_px * 2,
            pen_white,
            QBrush(Qt.transparent)
        )

        # 2 — Masque la moitié haute
        self.scene.addRect(
            cx - r_px, cy - r_px,
            r_px * 2, r_px,
            QPen(Qt.transparent),
            QBrush(QColor("#2d8a2d"))
        )

        # 3 — Ligne de baulk dessinée EN DERNIER pour passer par-dessus le masque
        self.scene.addLine(0, baulk_py, self.width_px, baulk_py, pen_white)

    def _draw_pockets(self) -> None:
        """Dessine les 6 poches en noir."""
        for pocket in self.table.poches:
            px, py = self.to_px(pocket.pos[0], pocket.pos[1])
            r = pocket.rayon * self.scale
            self.scene.addEllipse(
                px - r, py - r, r * 2, r * 2,
                QPen(Qt.black),
                QBrush(Qt.black)
            )

    def _draw_balls(self) -> None:
        """Dessine chaque bille active avec sa couleur."""
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
            r = ball.rayon * self.scale
            color = QColor(colors.get(ball.color, '#FFFFFF'))
            self.scene.addEllipse(
                px - r, py - r, r * 2, r * 2,
                QPen(Qt.black, 0.5),
                QBrush(color)
            )

