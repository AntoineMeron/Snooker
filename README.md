# Snooker — Projet Informatique FISE28

Simulation complète d'un jeu de snooker en Python avec interface graphique Qt,
moteur physique vectoriel, intelligence artificielle et sauvegarde de partie.

---

## Table des matières

- [Présentation](#présentation)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Lancer le jeu](#lancer-le-jeu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Figures du cahier des charges](#figures-du-cahier-des-charges)
- [Tests unitaires](#tests-unitaires)
- [Sauvegarde](#sauvegarde)
- [Auteurs](#auteurs)

---

## Présentation

Ce projet implémente un jeu de snooker jouable à deux joueurs (humain vs humain
ou humain vs IA) avec :

- Un moteur physique 2D réaliste (collisions, friction, rebonds)
- Les règles officielles du snooker (alternance rouge/couleur, fautes, scores)
- Une interface graphique PyQt5 avec visualisation des trajectoires
- Une IA capable de choisir ses tirs par optimisation
- Une sauvegarde/reprise de partie en JSON

---

## Structure du projet

```
Snooker/
│
├── main.py                  # Point d'entrée — lance l'application Qt
│
├── objets/                  # Objets du monde réel
│   ├── ball.py              # Bille (position, vitesse, couleur, points)
│   ├── table.py             # Table (dimensions, poches, setup des billes)
│   ├── poche.py             # Poche (position, détection d'empochage)
│   └── player.py            # Joueur (nom, score, break)
│
├── moteur/                  # Concepts métier — logique de simulation
│   ├── physique.py          # Moteur physique (collisions, friction, rebonds)
│   └── rules.py             # Moteur de règles (fautes, scores, transitions)
│
├── IA/                      # Intelligence artificielle
│   └── ai_player.py         # AIPlayer — choisit ses tirs par optimisation
│
├── state/                   # Stockage et orchestration
│   ├── game_state.py        # GameState — snapshot de la partie (Memento)
|   ├── shot_config.py       # Vérifie que le tire est valide
│   └── game_controller.py   # GameController — orchestre toutes les classes
│
├── IHM/                     # Interface graphique PyQt5
│   ├── IHM.ui               # Fichier Qt Designer
│   ├── IHM.py               # Généré par pyuic5 (ne pas modifier)
│   ├── main_window.py       # Fenêtre principale — connecte IHM et logique
│   └── table_view.py        # Rendu graphique de la table (QGraphicsScene)
│
├── tests/                   # Tests unitaires
│   ├── test_physics.py      # Tests du moteur physique
│   ├── test_rules.py        # Tests des règles
│   └── test_ball.py         # Tests de la classe Ball
│   
│
├── save.json                # Sauvegarde de partie (généré à l'exécution)
├── .gitignore
└── README.md
```

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Dépendances

```bash
pip install PyQt5 numpy
pip install pyqt5-tools  # pour Qt Designer (optionnel)
```

---

## Lancer le jeu

```bash
cd Snooker
python main.py
```

Au lancement, une boîte de dialogue demande les noms des deux joueurs.
Laissez vide pour utiliser les noms par défaut (`Joueur 1` / `Joueur 2`).

---

## Fonctionnalités

### Jeu

- **Tir à la souris** — cliquez et glissez depuis la bille blanche :
  la direction est opposée au glissement, la force est proportionnelle
  à la distance parcourue
- **Visualisation des trajectoires** — trait blanc pointillé jusqu'au
  premier obstacle, trait jaune pour la bille cible, trait bleu pour
  la blanche après impact, rebond sur les bandes
- **Règles officielles** — alternance rouge/couleur, fautes détectées
  (blanche empochée, mauvaise bille visée), pénalités attribuées à l'adversaire
- **Scores en temps réel** — score, break courant, joueur actif mis en évidence

### Intelligence artificielle

- L'IA analyse toutes les billes valides et calcule le meilleur tir
  par un algorithme d'optimisation (maximisation d'une fonction de score)
- Deux niveaux de difficulté : facile (bruit ajouté à l'angle) et difficile

### Sauvegarde

- **Sauvegarder** — capture l'état complet de la partie dans `save.json`
- **Charger** — reprend la partie exactement là où elle a été sauvegardée
- **Nouvelle frame** — remet toutes les billes en position initiale

---

## Architecture

### Héritage et composition

```
Player
  └── AIPlayer          (héritage)

Table
  ├── Ball × 22         (composition)
  └── Poche × 6         (composition)

GameController
  ├── Table             (agrégation)
  ├── Physique          (agrégation)
  ├── Rules             (agrégation)
  ├── GameState         (agrégation)
  └── Player × 2        (agrégation)
```

### Modules — justification des choix

| Module | Rôle | Justification |
|---|---|---|
| `objets/` | Objets du monde réel | Indépendants de toute logique, réutilisables |
| `moteur/` | Simulation et règles | Séparation physique / règles métier |
| `IA/` | Prise de décision | Isolé pour pouvoir changer d'algorithme |
| `state/` | Cycle de vie de la partie | Séparation orchestration / stockage |
| `IHM/` | Interface graphique | Indépendant du moteur, remplaçable |
| `tests/` | Validation | Isolation complète des tests |

---

## Figures du cahier des charges

### Calcul vectoriel (numpy)

Toutes les opérations physiques utilisent `np.ndarray` :

```python
# Collision bille-bille — moteur/physique.py
delta  = b2.pos - b1.pos                  # vecteur numpy
normal = delta / np.linalg.norm(delta)    # normalisation vectorielle
b1.vit += (v2n - v1n) * normal            # échange de vitesse vectoriel
```

### Algorithme d'optimisation

L'IA évalue tous les tirs candidats et sélectionne le meilleur
par maximisation d'une fonction de score pondérée :

```python
# IA/ai_player.py
score = (w_pot      * prob_empochage
       + w_position * qualite_position
       - w_risque   * risque_faute)
```

### Design Patterns

**Memento** — `GameState` capture un snapshot complet de la partie
et permet la sauvegarde/reprise sans coupler `GameController` au format JSON :

```python
state = GameState.from_game_controller(gc)  # capture
data  = state.to_dict()                     # sérialisation
state = GameState.from_dict(data)           # restauration
```

**Strategy** — `AIPlayer` délègue la sélection du tir à une stratégie
interchangeable selon le niveau de difficulté.

### Fonction récursive (bonus)

`predict_trajectory` dans `moteur/physique.py` simule la trajectoire
d'une bille de façon récursive — chaque appel avance d'un pas de temps
jusqu'à l'arrêt, l'empochage ou la profondeur maximale :

```python
def predict_trajectory(self, ball, table, steps=0,
                       max_steps=200, path=None):
    if path is None:
        path = [ball.pos.copy()]

    # Cas de base : bille arrêtée, empochée ou profondeur max
    if not ball.is_moving():
        return path
    if steps >= max_steps:
        return path
    for pocket in table.poches:
        if pocket.contains(ball):
            return path

    # Pas de temps récursif
    ball.pos = ball.pos + ball.vit * self.dt
    ball.vit = ball.vit * self.table.friction_coef
    self.resolve_table_collision(ball)
    path.append(ball.pos.copy())

    # Appel récursif
    return self.predict_trajectory(ball, table, steps + 1, max_steps, path)
```

---

## Tests unitaires

```bash
cd Snooker
python -m pytest tests/ -v
```

Couverture minimale : 4 méthodes testées, 2 cas par méthode.

| Fichier | Méthodes testées |
|---|---|
| `test_ball.py` | `is_moving`, `reset` |
| `test_physics.py` | `apply_shot`, `resolve_ball_collision`, `resolve_cushion`, `all_stopped` |
| `test_rules.py` | `score_potted`, `detect_foul`, `apply_foul`, `is_frame_over` |
| `test_player.py` | `add_points`, `reset_break` |

---

## Sauvegarde

La sauvegarde utilise le format **JSON** (pas de pickle) pour sa lisibilité
et sa portabilité. Un seul fichier `save.json` est généré à la racine.

**Choix JSON vs SQLite** : la partie est un objet unique lu/écrit en entier —
pas besoin de requêtes. JSON correspond naturellement à la structure des données
et est lisible sans outil externe.

```json
{
  "current_player": 0,
  "state": "aiming",
  "players": [...],
  "balls": [...]
}
```

---

## Auteurs
GALHARRET Ana & MERON Antoine

Projet réalisé dans le cadre du projet informatique FISE28.
