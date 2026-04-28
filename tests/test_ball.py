from objets.ball import Ball
import numpy as np

#Vérifier que les attributs sont bien initialisés (position, couleur, points, rayon, vitesse à zéro, is_potted à False)
def test_ball_init():
    ball = Ball(x=10, y=20, color="red", points=1, ball_id=1)
    assert ball.pos[0] == 10
    assert ball.pos[1] == 20
    assert ball.is_potted == False
    assert ball.rayon == 2.625

#Vérifier que la bille n'est pas en mouvement lorsque sa vitese est nulle
def test_is_moving_false():
    ball = Ball(x=0, y=0, color="red", points=1, ball_id=1)
    assert ball.is_moving() == False

#Vérifier que la bille est en mouvement lorsque sa vitesse est non nulle
def test_is_moving_true():
    ball = Ball(x=0, y=0, color="red", points=1, ball_id=1)
    ball.vit =np.array([3.0, 4.0])
    assert ball.is_moving() == True

#Vérifier que lorsque la vitesse est en dessous d'un certain seuil, on considère la bille arrêtée
def test_is_moving_seuil():
    ball = Ball(x=0, y=0, color="red", points=1, ball_id=1)
    ball.vit = np.array([0.001, 0.0])
    assert ball.is_moving() == False

#Vérifier que le reset est correct
def test_reset():
    ball = Ball(x=0, y=0, color="red", points=1, ball_id=1)
    ball.vit = np.array([3.0, 4.0])
    ball.is_potted = True
    ball.reset(50, 100)
    assert ball.pos[0] == 50
    assert ball.pos[1] == 100
    assert ball.is_moving() == False
    assert ball.is_potted == False

print(test_ball_init())
print(test_is_moving_false())
print(test_is_moving_true())
print(test_is_moving_seuil())
print(test_reset())