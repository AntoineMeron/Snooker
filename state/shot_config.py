"""
Paramètres d'un tir de snooker.
"""

class ShotConfig:
    """
    Regroupe les paramètres d'un tir.
    Utilisé par AIPlayer pour représenter un tir candidat.

    Attributes
    ----------
    angle_deg : float
        Angle du tir en degrés (0° = droite, sens antihoraire).
    force : float
        Force du tir entre 0 et 100.
    target_ball_id : int
        Identifiant de la bille visée.
    """

    def __init__(self, angle_deg: float, force: float, target_ball_id: int) -> None:
        self.angle_deg = angle_deg
        self.force = force
        self.target_ball_id = target_ball_id

    def validate(self) -> bool:
        """
        Vérifie que les paramètres du tir sont valides.

        Returns
        -------
        bool
            True si le tir est dans les bornes autorisées.
        """
        return 0 <= self.angle_deg <= 360 and 0 < self.force <= 100

    def __repr__(self) -> str:
        return (f"ShotConfig(angle={self.angle_deg:.1f}°, "
                f"force={self.force:.1f}, "
                f"target={self.target_ball_id})")