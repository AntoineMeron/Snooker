"""
Tests du moteur de règles.
"""

import unittest
from objets.ball import Ball
from objets.player import Player
from moteur.rules import Rules
from objets.table import Tables


class TestRules(unittest.TestCase):
    """Tests du moteur de règles."""

    def setUp(self):
        """Crée les objets réutilisables avant chaque test."""
        self.rules = Rules(reds_on_table=15)
        self.players = [Player("Alice"), Player("Bob")]
        self.rouge = Ball(x=0, y=0, color="red", points=1, ball_id=1)
        self.noire = Ball(x=0, y=0, color="black", points=7, ball_id=7)
        self.blanche = Ball(x=0, y=0, color="white", points=0, ball_id=0)
        self.tables = Tables()

    # ------------------------------------------------------------------
    # Tests score_potted
    # ------------------------------------------------------------------

    def test_score_rouge(self):
        """Empocher une rouge doit ajouter 1 point et passer à 'colour'."""
        self.rules.score_potted(self.rouge, self.players, current_idx=0,table=self.tables)
        self.assertEqual(self.players[0].score, 1)
        self.assertEqual(self.rules.next_ball_type, 'colour')
        self.assertEqual(self.rules.reds_on_table, 14)

    def test_score_couleur(self):
        """Empocher une couleur doit ajouter ses points et repasser à 'red'."""
        self.rules.next_ball_type = 'colour'
        self.rules.score_potted(self.noire, self.players, current_idx=0,table=self.tables)
        self.assertEqual(self.players[0].score, 7)
        self.assertEqual(self.rules.next_ball_type, 'red')

    def test_score_blanche_ignoree(self):
        """Empocher la blanche ne doit pas ajouter de points."""
        self.rules.score_potted(self.blanche, self.players, current_idx=0,table=self.tables)
        self.assertEqual(self.players[0].score, 0)

    def test_score_couleur_fin_de_frame(self):
        """Sans rouges restantes, next_ball_type doit rester sur 'colour'."""
        self.rules.reds_on_table = 0
        self.rules.next_ball_type = 'colour'
        self.rules.score_potted(self.noire, self.players, current_idx=0,table=self.tables)
        self.assertEqual(self.rules.next_ball_type, 'colour')

    # ------------------------------------------------------------------
    # Tests detect_foul
    # ------------------------------------------------------------------

    def test_detect_foul_blanche_empochee(self):
        """Empocher la blanche est toujours une faute, pénalité 4."""
        foul, penalite = self.rules.detect_foul([], white_potted=True)
        self.assertNotEqual(foul, "")
        self.assertEqual(penalite, 4)

    def test_detect_foul_couleur_quand_rouge_attendue(self):
        """Empocher une couleur quand rouge attendue = faute, pénalité max(4,7)=7."""
        self.rules.next_ball_type = 'red'
        foul, penalite = self.rules.detect_foul([self.noire], white_potted=False)
        self.assertNotEqual(foul, "")
        self.assertEqual(penalite, 7)

    def test_detect_foul_rouge_quand_couleur_attendue(self):
        """Empocher une rouge quand couleur attendue = faute, pénalité 4."""
        self.rules.next_ball_type = 'colour'
        foul, penalite = self.rules.detect_foul([self.rouge], white_potted=False)
        self.assertNotEqual(foul, "")
        self.assertEqual(penalite, 4)

    def test_detect_foul_coup_valide(self):
        """Empocher une rouge quand rouge attendue = pas de faute."""
        self.rules.next_ball_type = 'red'
        foul, penalite = self.rules.detect_foul([self.rouge], white_potted=False)
        self.assertEqual(foul, "")
        self.assertEqual(penalite, 0)

    def test_detect_foul_rien_empoche(self):
        """Aucune bille empochée = pas de faute."""
        foul, penalite = self.rules.detect_foul([], white_potted=False)
        self.assertEqual(foul, "")
        self.assertEqual(penalite, 0)

    def test_detect_foul_noire_penalite_7(self):
        """Empocher la noire par faute donne une pénalité de 7."""
        self.rules.next_ball_type = 'red'
        foul, penalite = self.rules.detect_foul([self.noire], white_potted=False)
        self.assertNotEqual(foul, "")
        self.assertEqual(penalite, 7)

    # ------------------------------------------------------------------
    # Tests apply_foul
    # ------------------------------------------------------------------

    def test_apply_foul_points_adversaire(self):
        """Une faute doit donner 4 points à l'adversaire."""
        self.rules.apply_foul("Faute : bille blanche empochée", 4, self.players, current_idx=0)
        self.assertEqual(self.players[1].score, 4)
        self.assertEqual(self.players[0].score, 0)

    def test_apply_foul_in_hand(self):
        """Une faute doit mettre in_hand à True."""
        self.rules.in_hand = False
        self.rules.apply_foul("Faute", 4, self.players, current_idx=0)
        self.assertTrue(self.rules.in_hand)

    def test_apply_foul_chaine_vide(self):
        """Appeler apply_foul avec une chaîne vide ne doit rien faire."""
        self.rules.apply_foul("", 0, self.players, current_idx=0)
        self.assertEqual(self.players[0].score, 0)
        self.assertEqual(self.players[1].score, 0)

    # ------------------------------------------------------------------
    # Tests is_frame_over
    # ------------------------------------------------------------------

    def test_frame_pas_terminee(self):
        """Des billes encore en jeu → frame pas terminée."""
        balls = [self.blanche, self.rouge]
        self.assertFalse(self.rules.is_frame_over(balls))

    def test_frame_terminee(self):
        """Toutes les billes (sauf blanche) empochées → frame terminée."""
        self.rouge.is_potted = True
        balls = [self.blanche, self.rouge]
        self.assertTrue(self.rules.is_frame_over(balls))

    def test_frame_terminee_ignore_blanche(self):
        """La blanche non empochée ne doit pas empêcher la fin de frame."""
        self.rouge.is_potted = True
        balls = [self.blanche, self.rouge]
        self.assertTrue(self.rules.is_frame_over(balls))


if __name__ == "__main__":
    unittest.main(verbosity=2)