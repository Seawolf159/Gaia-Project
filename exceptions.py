"""Module for custom exceptions."""


class NoGaiaFormerError(Exception):
    pass


class NotEnoughPowerTokensError(Exception):
    pass


class BackToActionSelection(Exception):
    pass


class NoFederationTokensError(Exception):
    pass


class NoFederationGreenError(Exception):
    pass


class NoResearchPossibleError(Exception):
    pass


class Level5IsFullError(Exception):
    pass


class InsufficientKnowledgeError(Exception):
    pass


class NotEnoughMinesError(Exception):
    pass


class GoBackToSectorSelection(Exception):
    pass

class NoValidMinePlanetsError(Exception):
    def __init__(self):
        print(
            "There are no valid planets in the sector to build a mine on. "
            "Please choose a different sector."
        )
