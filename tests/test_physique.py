"""
Tests du moteur physique.
"""

import unittest
import numpy as np
from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique


class TestPhysique(unittest.TestCase):
    """Tests du moteur physique."""

    def setUp(self):
        """
        Crée les objets réutilisables avant chaque test.
        """
        self.table = Tables()
        self.physique = Physique(table=self.table)
        self.ball = Ball(x=185, y=90, color="red", points=1, ball_id=1)

    # ------------------------------------------------------------------
    # Tests apply_shot
    # ------------------------------------------------------------------

    def test_apply_shot_vitesse_max(self):
        """Force 100 doit donner la vitesse maximale (500 cm/s)."""
        self.physique.apply_shot(self.ball, angle_deg=0, force=100)
        speed = float(np.linalg.norm(self.ball.vit))
        self.assertAlmostEqual(speed, 500.0, places=1)

    def test_apply_shot_force_zero(self):
        """Force 0 doit laisser la bille immobile."""
        self.physique.apply_shot(self.ball, angle_deg=0, force=0)
        self.assertFalse(self.ball.is_moving())

    def test_apply_shot_angle_0(self):
        """Angle 0° doit envoyer la bille vers la droite."""
        self.physique.apply_shot(self.ball, angle_deg=0, force=50)
        self.assertGreater(self.ball.vit[0], 0)
        self.assertAlmostEqual(self.ball.vit[1], 0, places=1)

    def test_apply_shot_angle_90(self):
        """Angle 90° doit envoyer la bille vers le haut."""
        self.physique.apply_shot(self.ball, angle_deg=90, force=50)
        self.assertGreater(self.ball.vit[1], 0)
        self.assertAlmostEqual(self.ball.vit[0], 0, places=1)

    # ------------------------------------------------------------------
    # Tests move_ball
    # ------------------------------------------------------------------

    def test_move_ball_deplace_position(self):
        """Une bille en mouvement doit changer de position."""
        self.ball.vit = np.array([100.0, 0.0])
        pos_avant = self.ball.pos[0]
        self.physique.move_ball(self.ball)
        self.assertGreater(self.ball.pos[0], pos_avant)

    def test_move_ball_applique_friction(self):
        """La vitesse doit diminuer après move_ball."""
        self.ball.vit = np.array([100.0, 0.0])
        vitesse_avant = float(np.linalg.norm(self.ball.vit))
        self.physique.move_ball(self.ball)
        vitesse_apres = float(np.linalg.norm(self.ball.vit))
        self.assertLess(vitesse_apres, vitesse_avant)

    def test_move_ball_arret_si_immobile(self):
        """Une bille déjà arrêtée doit rester immobile."""
        self.ball.vit = np.array([0.0, 0.0])
        pos_avant = self.ball.pos.copy()
        self.physique.move_ball(self.ball)
        self.assertEqual(self.ball.pos[0], pos_avant[0])
        self.assertEqual(self.ball.pos[1], pos_avant[1])

    # ------------------------------------------------------------------
    # Tests resolve_ball_collision
    # ------------------------------------------------------------------

    def test_collision_billes_se_touchent(self):
        """Deux billes qui se touchent doivent échanger leurs vitesses."""
        b1 = Ball(x=100, y=90, color="white", points=0, ball_id=0)
        b2 = Ball(x=105, y=90, color="red", points=1, ball_id=1)
        b1.vit = np.array([50.0, 0.0])
        b2.vit = np.array([0.0, 0.0])
        self.physique.resolve_ball_collision(b1, b2)
        self.assertLess(b1.vit[0], 1.0)
        self.assertGreater(b2.vit[0], 0.0)

    def test_collision_billes_ne_se_touchent_pas(self):
        """Deux billes éloignées ne doivent pas être affectées."""
        b1 = Ball(x=100, y=90, color="white", points=0, ball_id=0)
        b2 = Ball(x=200, y=90, color="red", points=1, ball_id=1)
        b1.vit = np.array([50.0, 0.0])
        self.physique.resolve_ball_collision(b1, b2)
        self.assertEqual(b1.vit[0], 50.0)
        self.assertEqual(b2.vit[0], 0.0)

    # ------------------------------------------------------------------
    # Tests resolve_table_collision
    # ------------------------------------------------------------------

    def test_rebond_bande_gauche(self):
        """Une bille contre la bande gauche doit repartir vers la droite."""
        ball = Ball(x=1.0, y=90, color="red", points=1, ball_id=1)
        ball.vit = np.array([-50.0, 0.0])
        self.physique.resolve_table_collision(ball)
        self.assertGreater(ball.vit[0], 0)

    def test_rebond_bande_droite(self):
        """Une bille contre la bande droite doit repartir vers la gauche."""
        ball = Ball(x=self.table.largeur - 1.0, y=90, color="red", points=1, ball_id=1)
        ball.vit = np.array([50.0, 0.0])
        self.physique.resolve_table_collision(ball)
        self.assertLess(ball.vit[0], 0)

    def test_rebond_bande_basse(self):
        """Une bille contre la bande basse doit repartir vers le haut."""
        ball = Ball(x=185, y=1.0, color="red", points=1, ball_id=1)
        ball.vit = np.array([0.0, -50.0])
        self.physique.resolve_table_collision(ball)
        self.assertGreater(ball.vit[1], 0)

    def test_rebond_bande_haute(self):
        """Une bille contre la bande haute doit repartir vers le bas."""
        ball = Ball(x=185, y=self.table.longueur - 1.0, color="red", points=1, ball_id=1)
        ball.vit = np.array([0.0, 50.0])
        self.physique.resolve_table_collision(ball)
        self.assertLess(ball.vit[1], 0)

    # ------------------------------------------------------------------
    # Tests all_stopped
    # ------------------------------------------------------------------

    def test_all_stopped_vrai(self):
        """Toutes les billes immobiles → all_stopped retourne True."""
        self.table.add_ball(self.ball)
        self.assertTrue(self.physique.all_stopped())

    def test_all_stopped_faux(self):
        """Une bille en mouvement → all_stopped retourne False."""
        self.ball.vit = np.array([50.0, 0.0])
        self.table.add_ball(self.ball)
        self.assertFalse(self.physique.all_stopped())


if __name__ == "__main__":
    unittest.main(verbosity=2)