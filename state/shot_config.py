"""
Paramètres d'un tir de snooker.
"""


class ShotConfig:
    """
    Regroupe les paramètres d'un tir.

    Cette classe est utilisée par AIPlayer pour représenter un tir candidat
    ou le tir finalement choisi. Elle sert uniquement de conteneur de données.

    Attributes
    ----------
    angle_deg : float
        Angle du tir en degrés. 0° correspond à un tir vers la droite,
        et les angles augmentent dans le sens antihoraire.
    force : float
        Force du tir entre 0 et 100.
    target_ball_id : int
        Identifiant de la bille visée.
    """

    def __init__(self, angle_deg: float, force: float, target_ball_id: int) -> None:
        """
        Initialise une configuration de tir.

        Parameters
        ----------
        angle_deg : float
            Angle du tir en degrés. 0° correspond à un tir vers la droite,
            et les angles augmentent dans le sens antihoraire.
        force : float
            Force appliquée au tir. Elle doit être comprise entre 0 et 100.
        target_ball_id : int
            Identifiant de la bille visée par le tir.

        Returns
        -------
        None
        """
        self.angle_deg = angle_deg
        self.force = force
        self.target_ball_id = target_ball_id

    def validate(self) -> bool:
        """
        Vérifie que les paramètres du tir sont valides.

        Un tir est considéré comme valide si l'angle est compris entre
        0 et 360 degrés et si la force est strictement positive et
        inférieure ou égale à 100.

        Returns
        -------
        bool
            True si le tir est dans les bornes autorisées, False sinon.
        """
        return 0 <= self.angle_deg <= 360 and 0 < self.force <= 100

    def __repr__(self) -> str:
        """
        Retourne une représentation textuelle de la configuration de tir.

        Cette représentation est utile pour afficher ou déboguer un tir
        candidat choisi par l'IA.

        Returns
        -------
        str
            Représentation lisible du tir, contenant l'angle, la force
            et l'identifiant de la bille cible.
        """
        return (f"ShotConfig(angle={self.angle_deg:.1f}°, "
                f"force={self.force:.1f}, "
                f"target={self.target_ball_id})")