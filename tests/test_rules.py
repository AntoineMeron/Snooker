"""
Tests du moteur de règles.
"""

import pytest
from objets.ball import Ball
from objets.player import Player
from moteur.rules import Rules


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def rules():
    """Crée un moteur de règles en début de frame."""
    return Rules(reds_on_table=15)

@pytest.fixture
def players():
    """Crée deux joueurs pour les tests."""
    return [Player("Alice"), Player("Bob")]

@pytest.fixture
def rouge():
    return Ball(x=0, y=0, color="red", points=1, ball_id=1)

@pytest.fixture
def noire():
    return Ball(x=0, y=0, color="black", points=7, ball_id=7)

@pytest.fixture
def blanche():
    return Ball(x=0, y=0, color="white", points=0, ball_id=0)


# ------------------------------------------------------------------
# Tests score_potted
# ------------------------------------------------------------------

def test_score_rouge(rules, players, rouge):
    """Empocher une rouge doit ajouter 1 point et passer à 'colour'."""
    rules.score_potted(rouge, players, current_idx=0)
    assert players[0].score == 1
    assert rules.next_ball_type == 'colour'
    assert rules.reds_on_table == 14  # une rouge en moins

def test_score_couleur(rules, players, noire):
    """Empocher une couleur doit ajouter ses points et repasser à 'red'."""
    rules.next_ball_type = 'colour'
    rules.score_potted(noire, players, current_idx=0)
    assert players[0].score == 7
    assert rules.next_ball_type == 'red'  # il reste des rouges

def test_score_blanche_ignoree(rules, players, blanche):
    """Empocher la blanche ne doit pas ajouter de points."""
    rules.score_potted(blanche, players, current_idx=0)
    assert players[0].score == 0

def test_score_couleur_fin_de_frame(rules, players, noire):
    """Quand il n'y a plus de rouges, empocher une couleur garde next_ball_type à 'colour'."""
    rules.reds_on_table = 0
    rules.next_ball_type = 'colour'
    rules.score_potted(noire, players, current_idx=0)
    assert rules.next_ball_type == 'colour'  # on reste sur colour


# ------------------------------------------------------------------
# Tests detect_foul
# ------------------------------------------------------------------

def test_detect_foul_blanche_empochee(rules, blanche):
    """Empocher la blanche est toujours une faute."""
    foul = rules.detect_foul([], white_potted=True)
    assert foul != ""

def test_detect_foul_couleur_quand_rouge_attendue(rules, noire):
    """Empocher une couleur quand on devait viser une rouge = faute."""
    rules.next_ball_type = 'red'
    foul = rules.detect_foul([noire], white_potted=False)
    assert foul != ""

def test_detect_foul_rouge_quand_couleur_attendue(rules, rouge):
    """Empocher une rouge quand on devait viser une couleur = faute."""
    rules.next_ball_type = 'colour'
    foul = rules.detect_foul([rouge], white_potted=False)
    assert foul != ""

def test_detect_foul_coup_valide(rules, rouge):
    """Empocher une rouge quand on devait viser une rouge = pas de faute."""
    rules.next_ball_type = 'red'
    foul = rules.detect_foul([rouge], white_potted=False)
    assert foul == ""

def test_detect_foul_rien_empoche(rules):
    """Aucune bille empochée, pas de blanche = pas de faute."""
    foul = rules.detect_foul([], white_potted=False)
    assert foul == ""


# ------------------------------------------------------------------
# Tests apply_foul
# ------------------------------------------------------------------

def test_apply_foul_points_adversaire(rules, players):
    """Une faute doit donner 4 points à l'adversaire."""
    rules.apply_foul("Faute : bille blanche empochée", players, current_idx=0)
    assert players[1].score == 4  # Bob reçoit les points
    assert players[0].score == 0  # Alice ne reçoit rien

def test_apply_foul_in_hand(rules, players):
    """Une faute doit mettre in_hand à True."""
    rules.in_hand = False
    rules.apply_foul("Faute", players, current_idx=0)
    assert rules.in_hand == True

def test_apply_foul_chaine_vide(rules, players):
    """Appeler apply_foul avec une chaîne vide ne doit rien faire."""
    rules.apply_foul("", players, current_idx=0)
    assert players[0].score == 0
    assert players[1].score == 0


# ------------------------------------------------------------------
# Tests is_frame_over
# ------------------------------------------------------------------

def test_frame_pas_terminee(rules):
    """Des billes encore en jeu → frame pas terminée."""
    balls = [
        Ball(x=0, y=0, color="white", points=0, ball_id=0),
        Ball(x=0, y=0, color="red", points=1, ball_id=1),  # pas empochée
    ]
    assert rules.is_frame_over(balls) == False

def test_frame_terminee(rules):
    """Toutes les billes (sauf blanche) empochées → frame terminée."""
    balls = [
        Ball(x=0, y=0, color="white", points=0, ball_id=0),
        Ball(x=0, y=0, color="red", points=1, ball_id=1),
    ]
    balls[1].is_potted = True
    assert rules.is_frame_over(balls) == True

def test_frame_terminee_ignore_blanche(rules):
    """La blanche non empochée ne doit pas empêcher la frame d'être terminée."""
    balls = [
        Ball(x=0, y=0, color="white", points=0, ball_id=0),  # blanche jamais empochée
        Ball(x=0, y=0, color="red", points=1, ball_id=1),
    ]
    balls[1].is_potted = True
    assert rules.is_frame_over(balls) == True

if __name__ == "__main__":
    r = Rules(15)
    p = [Player("Alice"), Player("Bob")]
    rouge = Ball(x=0, y=0, color="red", points=1, ball_id=1)
    noire = Ball(x=0, y=0, color="black", points=7, ball_id=7)
    blanche = Ball(x=0, y=0, color="white", points=0, ball_id=0)

    print("--- score_potted ---")
    r.score_potted(rouge, p, 0)
    print(f"score Alice après rouge : {p[0].score}")          # attendu : 1
    print(f"next_ball_type : {r.next_ball_type}")              # attendu : colour
    print(f"reds_on_table : {r.reds_on_table}")                # attendu : 14

    r2 = Rules(15)
    p2 = [Player("Alice"), Player("Bob")]
    r2.next_ball_type = 'colour'
    r2.score_potted(noire, p2, 0)
    print(f"score Alice après noire : {p2[0].score}")          # attendu : 7
    print(f"next_ball_type : {r2.next_ball_type}")             # attendu : red

    print("\n--- detect_foul ---")
    print(r.detect_foul([], white_potted=True))                # attendu : non vide
    print(r.detect_foul([], white_potted=False))               # attendu : ""
    r3 = Rules(15)
    r3.next_ball_type = 'red'
    print(r3.detect_foul([noire], white_potted=False))         # attendu : non vide
    r3.next_ball_type = 'colour'
    print(r3.detect_foul([rouge], white_potted=False))         # attendu : non vide

    print("\n--- apply_foul ---")
    p3 = [Player("Alice"), Player("Bob")]
    r4 = Rules(15)
    r4.apply_foul("Faute", p3, current_idx=0)
    print(f"score Bob après faute d'Alice : {p3[1].score}")    # attendu : 4
    print(f"in_hand : {r4.in_hand}")                           # attendu : True

    print("\n--- is_frame_over ---")
    balls = [blanche, rouge]
    print(r.is_frame_over(balls))                              # attendu : False
    rouge.is_potted = True
    print(r.is_frame_over(balls))                              # attendu : True