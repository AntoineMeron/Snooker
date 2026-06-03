"""
Joueur IA du snooker.
"""

import math
import random
import numpy as np
from objets.player import Player
from objets.ball import Ball
from objets.table import Tables
from moteur.physique import Physique
from moteur.rules import Rules
from state.game_state import GameState
from state.shot_config import ShotConfig


class AIPlayer(Player):
    """
    Joueur contrôlé par l'ordinateur.


    Hérite de Player — possède donc score, current_break, add_points()
    et reset_break(). Ajoute la logique de choix automatique de tir.


    Le principe est le suivant :
       1. Générer des tirs candidats (angles × forces)
       2. Simuler chaque candidat sur un clone de l'état actuel
       3. Évaluer le résultat de chaque simulation
       4. Retourner le meilleur tir


    Attributes
    ----------
    difficulty : str
       Niveau de difficulté : 'easy', 'medium' ou 'hard'.
    randomness : float
       Bruit gaussien sur l'angle du meilleur tir (en degrés).
       Plus élevé = moins précis. Calculé depuis difficulty.
    """

    _RANDOMNESS   = {'easy': 8.0,  'medium': 2.0,  'hard': 0.5}
    _N_CANDIDATES = {'easy':  40,  'medium': 200,  'hard': 200}

    def __init__(self, name: str, difficulty: str = 'medium') -> None:
        super().__init__(name=name, is_ai=True)
        self.difficulty = difficulty
        self.randomness = self._RANDOMNESS.get(difficulty, 5.0)

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    # def choose_shot(self, state: GameState) -> ShotConfig:
    #     """
    #     Choisit le meilleur tir depuis l'état donné.
    #
    #     Parameters
    #     ----------
    #     state : GameState
    #         Photo de la partie au moment du choix.
    #
    #     Returns
    #     -------
    #     ShotConfig
    #         Le tir choisi avec bruit ajouté selon le niveau.
    #     """
    #     candidates = self._get_candidate_shots(state)
    #
    #     best_shot = None
    #     best_score = -float('inf')
    #
    #     for shot in candidates:
    #         score = self._evaluate_shot(shot, state)
    #         if score > best_score:
    #             best_score = score
    #             best_shot = shot
    #
    #     if best_shot is None:
    #         best_shot = ShotConfig(angle_deg=0.0, force=30.0, target_ball_id=-1)
    #
    #     # Ajout du bruit selon le niveau de difficulté
    #     noisy_angle = (best_shot.angle_deg + random.gauss(0, self.randomness)) % 360
    #
    #     return ShotConfig(
    #         angle_deg=noisy_angle,
    #         force=best_shot.force,
    #         target_ball_id=best_shot.target_ball_id,
    #     )

    def choose_shot(self, state: GameState) -> ShotConfig:
        candidates = self._get_candidate_shots(state)
        best_shot = None
        best_score = -float('inf')

        for shot in candidates:
            score = self._evaluate_shot(shot, state)
            if score > best_score:
                best_score = score
                best_shot = shot

        print(f"Meilleur tir : angle={best_shot.angle_deg:.1f}°, "
              f"force={best_shot.force:.1f}, score={best_score:.1f}")

        # Affiche aussi la position de la blanche et de la cible
        white = next(b for b in state.balls_snapshot if b["id"] == 0)
        target = next((b for b in state.balls_snapshot
                       if b["id"] == best_shot.target_ball_id), None)
        if target:
            print(f"Blanche : ({white['x']:.1f}, {white['y']:.1f})")
            print(f"Cible   : ({target['x']:.1f}, {target['y']:.1f})")
            import math
            delta = [target['x'] - white['x'], target['y'] - white['y']]
            angle_exact = math.degrees(math.atan2(delta[1], delta[0])) % 360
            print(f"Angle exact calculé : {angle_exact:.1f}°")

        noisy_angle = (best_shot.angle_deg + random.gauss(0, self.randomness)) % 360
        return ShotConfig(
            angle_deg=noisy_angle,
            force=best_shot.force,
            target_ball_id=best_shot.target_ball_id,
        )

    # ------------------------------------------------------------------
    # Génération des tirs candidats
    # ------------------------------------------------------------------

    # def _get_candidate_shots(self, state: GameState) -> list[ShotConfig]:
    #     """
    #     Génère des tirs candidats en ciblant uniquement les billes
    #     valides selon next_ball_type (rouge ou couleur).
    #
    #     Parameters
    #     ----------
    #     state : GameState
    #         État actuel avec next_ball_type.
    #
    #     Returns
    #     -------
    #     list[ShotConfig]
    #         Tirs candidats à évaluer.
    #     """
    #     candidates = []
    #     n = self._N_CANDIDATES[self.difficulty]
    #
    #     white = next((b for b in state.balls_snapshot if b["id"] == 0), None)
    #     if white is None:
    #         return candidates
    #
    #     white_pos = np.array([white["x"], white["y"]])
    #
    #     next_type = state.next_ball_type
    #     if next_type == 'red':
    #         targets = [
    #             b for b in state.balls_snapshot
    #             if not b["is_potted"] and b["id"] != 0 and b["points"] == 1
    #         ]
    #     else:
    #         targets = [
    #             b for b in state.balls_snapshot
    #             if not b["is_potted"] and b["id"] != 0 and b["points"] > 1
    #         ]
    #
    #     if not targets:
    #         targets = [
    #             b for b in state.balls_snapshot
    #             if not b["is_potted"] and b["id"] != 0
    #         ]
    #
    #     for target in targets:
    #         target_pos = np.array([target["x"], target["y"]])
    #         delta = target_pos - white_pos
    #         dist = float(np.linalg.norm(delta))
    #
    #         if dist < 0.1:
    #             continue
    #
    #         # Angle exact pour toucher la bille cible
    #         exact_angle = math.degrees(math.atan2(delta[1], delta[0])) % 360
    #
    #         n_per_target = max(6, n // max(1, len(targets)))
    #
    #         # ← angle_spread réduit : on reste proche de l'angle exact
    #         angle_spread = 10
    #
    #         for _ in range(n_per_target):
    #             angle_offset = random.uniform(-angle_spread, angle_spread)
    #             angle = (exact_angle + angle_offset) % 360
    #
    #             # Force proportionnelle à la distance, mieux calibrée
    #             base_force = min(90, max(30, dist * 0.4))
    #             force = max(20, min(100, base_force + random.uniform(-5, 5)))
    #
    #             candidates.append(ShotConfig(
    #                 angle_deg=angle,
    #                 force=force,
    #                 target_ball_id=target["id"],
    #             ))
    #
    #         # On ajoute aussi l'angle exact avec plusieurs forces
    #         # pour être sûr qu'au moins un tir parfait est testé
    #         for force in [30, 50, 70, 90]:
    #             candidates.append(ShotConfig(
    #                 angle_deg=exact_angle,
    #                 force=force,
    #                 target_ball_id=target["id"],
    #             ))
    #
    #     return candidates

    def _get_candidate_shots(self, state: GameState) -> list[ShotConfig]:
        candidates = []
        n = self._N_CANDIDATES[self.difficulty]

        white = next((b for b in state.balls_snapshot if b["id"] == 0), None)
        if white is None:
            return candidates

        white_pos = np.array([white["x"], white["y"]])

        # Filtrage selon next_ball_type
        next_type = state.next_ball_type
        if next_type == 'red':
            targets = [b for b in state.balls_snapshot
                       if not b["is_potted"] and b["id"] != 0 and b["points"] == 1]
        else:
            targets = [b for b in state.balls_snapshot
                       if not b["is_potted"] and b["id"] != 0 and b["points"] > 1]

        if not targets:
            targets = [b for b in state.balls_snapshot
                       if not b["is_potted"] and b["id"] != 0]

        if not targets:
            return candidates

        # ── Étape 1 : score chaque bille selon sa jouabilité ──────────────
        # Une bille est "jouable" si :
        #   - elle est proche de la blanche (facile à toucher)
        #   - elle est proche d'une poche (facile à empocher)
        #   - la blanche, la bille et la poche sont bien alignées
        scored_targets = []
        for target in targets:
            target_pos = np.array([target["x"], target["y"]])
            dist_white = float(np.linalg.norm(target_pos - white_pos))

            # Distance minimale à une poche
            best_pocket_score = 0.0
            for pocket in state.pockets_snapshot:
                pocket_pos = np.array([pocket["x"], pocket["y"]])
                dist_pocket = float(np.linalg.norm(target_pos - pocket_pos))

                # Vecteur blanche → bille
                v_wb = target_pos - white_pos
                norm_wb = np.linalg.norm(v_wb)
                # Vecteur bille → poche
                v_bp = pocket_pos - target_pos
                norm_bp = np.linalg.norm(v_bp)

                if norm_wb > 0 and norm_bp > 0:
                    # Alignement : produit scalaire normalisé
                    alignement = float(np.dot(v_wb / norm_wb, v_bp / norm_bp))
                    # Score : alignement bonus, distance malus
                    pocket_score = alignement / (1 + dist_pocket * 0.01)
                    best_pocket_score = max(best_pocket_score, pocket_score)

            # Score global de la bille : proche + bien alignée vers une poche
            ball_score = best_pocket_score / (1 + dist_white * 0.005)
            scored_targets.append((ball_score, target))

        # Trie par score décroissant
        scored_targets.sort(key=lambda x: x[0], reverse=True)

        # ── Étape 2 : concentrer les candidats sur les meilleures billes ──
        # On garde les 3 meilleures billes et on leur donne plus de candidats
        top_targets = scored_targets[:3]
        weights = [3, 2, 1]  # la meilleure bille reçoit 3x plus de candidats

        total_weight = sum(weights[:len(top_targets)])

        for i, (ball_score, target) in enumerate(top_targets):
            target_pos = np.array([target["x"], target["y"]])
            delta = target_pos - white_pos
            dist = float(np.linalg.norm(delta))

            if dist < 0.1:
                continue

            exact_angle = math.degrees(math.atan2(delta[1], delta[0])) % 360

            # Nombre de candidats proportionnel au poids
            n_for_this = (n * weights[i]) // total_weight
            n_for_this = max(8, n_for_this)

            for _ in range(n_for_this):
                angle_offset = random.uniform(-10, 10)
                angle = (exact_angle + angle_offset) % 360
                base_force = min(90, max(30, dist * 0.4))
                force = max(20, min(100, base_force + random.uniform(-5, 5)))
                candidates.append(ShotConfig(
                    angle_deg=angle,
                    force=force,
                    target_ball_id=target["id"],
                ))

            # Angle exact avec plusieurs forces — toujours testé
            for force in [30, 50, 70, 90]:
                candidates.append(ShotConfig(
                    angle_deg=exact_angle,
                    force=force,
                    target_ball_id=target["id"],
                ))

        return candidates

    # ------------------------------------------------------------------
    # Évaluation par simulation
    # ------------------------------------------------------------------

    def _evaluate_shot(self, shot: ShotConfig, state: GameState) -> float:
        """
        Simule le tir sur un clone et retourne un score.

        Barème :
            +10  par bille valide empochée
            +5   bonus si la bille empochée était la bonne (next_ball_type)
            -20  si faute
            -5   si aucune bille empochée
            +1   si la blanche reste sur la table

        Parameters
        ----------
        shot : ShotConfig
            Tir à évaluer.
        state : GameState
            État actuel (cloné, jamais modifié).

        Returns
        -------
        float
            Score du tir.
        """
        if not shot.validate():
            return -float('inf')

        clone = state.clone()
        table, rules = self._build_from_state(clone)
        physique = Physique(table=table)

        white = table.get_ball_id(0)
        if white is None:
            return -float('inf')

        physique.apply_shot(white, shot.angle_deg, shot.force)

        potted_this_shot = []
        for _ in range(500):
            if physique.all_stopped():
                break
            potted_this_shot += physique.step()

        score = 0.0
        white_potted = any(b.id == 0 for b in potted_this_shot)
        foul, _ = rules.detect_foul(potted_this_shot, white_potted)

        if foul:
            score -= 20.0
        elif potted_this_shot:
            score += len(potted_this_shot) * 10.0
            # Bonus si les billes empochées sont bien du bon type
            next_type = state.next_ball_type
            for b in potted_this_shot:
                if b.id != 0:
                    if next_type == 'red' and b.points == 1:
                        score += 5.0
                    elif next_type == 'colour' and b.points > 1:
                        score += 5.0
        else:
            score -= 5.0

        white_after = table.get_ball_id(0)
        if white_after and not white_after.is_potted:
            score += 1.0

        return score

    # ------------------------------------------------------------------
    # Reconstruction depuis GameState
    # ------------------------------------------------------------------

    def _build_from_state(self, state: GameState):
        """
        Reconstruit une Tables et une Rules depuis un GameState cloné.

        Parameters
        ----------
        state : GameState
            Clone de l'état.

        Returns
        -------
        tuple[Tables, Rules]
            Table et règles reconstruites.
        """
        table = Tables()
        table.balls = []

        for b_data in state.balls_snapshot:
            ball = Ball(
                x=b_data["x"],
                y=b_data["y"],
                color=b_data["color"],
                points=b_data["points"],
                ball_id=b_data["id"],
            )
            ball.vit[0] = b_data["vx"]
            ball.vit[1] = b_data["vy"]
            ball.is_potted = b_data["is_potted"]
            table.balls.append(ball)

        rules = Rules()
        rules.next_ball_type = state.next_ball_type
        return table, rules