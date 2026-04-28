"""
Tests du moteur physique.
"""

import numpy as np
import pytest
from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique


# ------------------------------------------------------------------
# Fixtures : objets réutilisables dans tous les tests
# ------------------------------------------------------------------

@pytest.fixture
def table():
    """Crée une table vide pour les tests."""
    return Tables()

@pytest.fixture
def physique(table):
    """Crée un moteur physique avec une table vide."""
    return Physique(table=table)

@pytest.fixture
def ball():
    """Crée une bille rouge immobile au centre de la table."""
    return Ball(x=185, y=90, color="red", points=1, ball_id=1)


# ------------------------------------------------------------------
# Tests apply_shot
# ------------------------------------------------------------------

def test_apply_shot_vitesse_max(physique, ball):
    """Force 100 doit donner la vitesse maximale (500 cm/s)."""
    physique.apply_shot(ball, angle_deg=0, force=100)
    speed = float(np.linalg.norm(ball.vit))
    assert abs(speed - 500.0) < 0.01

def test_apply_shot_force_zero(physique, ball):
    """Force 0 doit laisser la bille immobile."""
    physique.apply_shot(ball, angle_deg=0, force=0)
    assert not ball.is_moving()

def test_apply_shot_angle_0(physique, ball):
    """Angle 0° doit envoyer la bille vers la droite (vx > 0, vy ≈ 0)."""
    physique.apply_shot(ball, angle_deg=0, force=50)
    assert ball.vit[0] > 0
    assert abs(ball.vit[1]) < 0.01

def test_apply_shot_angle_90(physique, ball):
    """Angle 90° doit envoyer la bille vers le haut (vy > 0, vx ≈ 0)."""
    physique.apply_shot(ball, angle_deg=90, force=50)
    assert ball.vit[1] > 0
    assert abs(ball.vit[0]) < 0.01


# ------------------------------------------------------------------
# Tests move_ball
# ------------------------------------------------------------------

def test_move_ball_deplace_position(physique, ball):
    """Une bille en mouvement doit changer de position après move_ball."""
    ball.vit = np.array([100.0, 0.0])
    pos_avant = ball.pos.copy()
    physique.move_ball(ball)
    assert ball.pos[0] > pos_avant[0]  # la bille a avancé vers la droite

def test_move_ball_applique_friction(physique, ball):
    """La vitesse doit diminuer après move_ball."""
    ball.vit = np.array([100.0, 0.0])
    vitesse_avant = float(np.linalg.norm(ball.vit))
    physique.move_ball(ball)
    vitesse_apres = float(np.linalg.norm(ball.vit))
    assert vitesse_apres < vitesse_avant

def test_move_ball_arret_si_immobile(physique, ball):
    """Une bille déjà arrêtée doit rester à zéro."""
    ball.vit = np.array([0.0, 0.0])
    pos_avant = ball.pos.copy()
    physique.move_ball(ball)
    assert ball.pos[0] == pos_avant[0]
    assert ball.pos[1] == pos_avant[1]


# ------------------------------------------------------------------
# Tests resolve_ball_collision
# ------------------------------------------------------------------

def test_collision_billes_se_touchent(physique):
    """Deux billes qui se touchent doivent échanger leurs vitesses."""
    b1 = Ball(x=100, y=90, color="white", points=0, ball_id=0)
    b2 = Ball(x=105, y=90, color="red", points=1, ball_id=1)  # dist = 5 = 2*rayon
    b1.vit = np.array([50.0, 0.0])  # b1 fonce vers b2
    b2.vit = np.array([0.0, 0.0])   # b2 immobile
    physique.resolve_ball_collision(b1, b2)
    # b1 doit s'arrêter, b2 doit repartir
    assert b1.vit[0] < 1.0
    assert b2.vit[0] > 0.0

def test_collision_billes_ne_se_touchent_pas(physique):
    """Deux billes éloignées ne doivent pas être affectées."""
    b1 = Ball(x=100, y=90, color="white", points=0, ball_id=0)
    b2 = Ball(x=200, y=90, color="red", points=1, ball_id=1)
    b1.vit = np.array([50.0, 0.0])
    physique.resolve_ball_collision(b1, b2)
    assert b1.vit[0] == 50.0  # vitesse inchangée
    assert b2.vit[0] == 0.0


# ------------------------------------------------------------------
# Tests resolve_table_collision
# ------------------------------------------------------------------

def test_rebond_bande_gauche(physique, table):
    """Une bille contre la bande gauche doit repartir vers la droite."""
    ball = Ball(x=1.0, y=90, color="red", points=1, ball_id=1)  # très proche du bord gauche
    ball.vit = np.array([-50.0, 0.0])  # va vers la gauche
    physique.resolve_table_collision(ball)
    assert ball.vit[0] > 0  # repart vers la droite

def test_rebond_bande_droite(physique, table):
    """Une bille contre la bande droite doit repartir vers la gauche."""
    ball = Ball(x=table.longueur - 1.0, y=90, color="red", points=1, ball_id=1)
    ball.vit = np.array([50.0, 0.0])
    physique.resolve_table_collision(ball)
    assert ball.vit[0] < 0

def test_rebond_bande_basse(physique, table):
    """Une bille contre la bande basse doit repartir vers le haut."""
    ball = Ball(x=185, y=1.0, color="red", points=1, ball_id=1)
    ball.vit = np.array([0.0, -50.0])
    physique.resolve_table_collision(ball)
    assert ball.vit[1] > 0

def test_rebond_bande_haute(physique, table):
    """Une bille contre la bande haute doit repartir vers le bas."""
    ball = Ball(x=185, y=table.largeur - 1.0, color="red", points=1, ball_id=1)
    ball.vit = np.array([0.0, 50.0])
    physique.resolve_table_collision(ball)
    assert ball.vit[1] < 0


# ------------------------------------------------------------------
# Tests all_stopped
# ------------------------------------------------------------------

def test_all_stopped_vrai(physique, table):
    """Toutes les billes immobiles → all_stopped retourne True."""
    b = Ball(x=185, y=90, color="red", points=1, ball_id=1)
    table.add_ball(b)
    assert physique.all_stopped() == True

def test_all_stopped_faux(physique, table):
    """Une bille en mouvement → all_stopped retourne False."""
    b = Ball(x=185, y=90, color="red", points=1, ball_id=1)
    b.vit = np.array([50.0, 0.0])
    table.add_ball(b)
    assert physique.all_stopped() == False