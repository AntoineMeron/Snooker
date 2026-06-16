"""
Tests de la classe Ball.
"""

import unittest
import numpy as np
from objets.ball import Ball


class TestBall(unittest.TestCase):
    """Tests de la classe Ball."""

    def setUp(self):
        """Crée une bille rouge immobile avant chaque test."""
        self.ball = Ball(x=0, y=0, color="red", points=1, ball_id=1)

    def test_ball_init(self):
        """Les attributs doivent être correctement initialisés."""
        ball = Ball(x=10, y=20, color="red", points=1, ball_id=1)
        self.assertEqual(ball.pos[0], 10)
        self.assertEqual(ball.pos[1], 20)
        self.assertFalse(ball.is_potted)
        self.assertEqual(ball.rayon, 3.7)

    def test_is_moving_false(self):
        """Une bille à vitesse nulle ne doit pas être en mouvement."""
        self.assertFalse(self.ball.is_moving())

    def test_is_moving_true(self):
        """Une bille avec une vitesse non nulle doit être en mouvement."""
        self.ball.vit = np.array([3.0, 4.0])
        self.assertTrue(self.ball.is_moving())

    def test_is_moving_seuil(self):
        """Une vitesse sous le seuil doit être considérée comme arrêtée."""
        self.ball.vit = np.array([0.001, 0.0])
        self.assertFalse(self.ball.is_moving())

    def test_reset(self):
        """Après reset, position, vitesse et is_potted doivent être réinitialisés."""
        self.ball.vit = np.array([3.0, 4.0])
        self.ball.is_potted = True
        self.ball.reset(50, 100)
        self.assertEqual(self.ball.pos[0], 50)
        self.assertEqual(self.ball.pos[1], 100)
        self.assertFalse(self.ball.is_moving())
        self.assertFalse(self.ball.is_potted)


if __name__ == "__main__":
    unittest.main(verbosity=2)