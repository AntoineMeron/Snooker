"""
Représente un joueur de snooker.
"""


class Player:
    """
    Un joueur de snooker.

    Attributes
    ----------
    name : str
        Nom du joueur.
    score : int
        Score total de la partie.
    current_break : int
        Points marqués lors du break en cours (remis à 0 à chaque changement de tour).
    is_ai : bool
        True si le joueur est contrôlé par l'ordinateur.
    """

    def __init__(self, name: str, is_ai: bool = False) -> None:
        self.name = name
        self.score = 0
        self.current_break = 0
        self.is_ai = is_ai

    def add_points(self, n: int) -> None:
        """
        Ajoute n points au score total et au break en cours.

        Parameters
        ----------
        n : int
            Nombre de points à ajouter.
        """
        self.score += n
        self.current_break += n

    def reset_break(self) -> None:
        """
        Remet le break en cours à zéro.
        À appeler quand le tour du joueur se termine.
        """
        self.current_break = 0

    def get_stats(self) -> dict:
        """
        Retourne les statistiques du joueur sous forme de dictionnaire.

        Returns
        -------
        dict
            Dictionnaire avec le nom, le score et le break en cours.
        """
        return {
            "name": self.name,
            "score": self.score,
            "current_break": self.current_break,
            "is_ai": self.is_ai,
        }

    def __repr__(self) -> str:
        return f"Player(name='{self.name}', score={self.score}, break={self.current_break})"