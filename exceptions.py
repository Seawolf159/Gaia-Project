"""Module for custom exceptions."""


class NoGaiaFormerError(Exception):
    pass


class NotEnoughPowerTokensError(Exception):
    pass


class BackToActionSelection(Exception):
    def __init__(self, choice="0"):
        self.choice = choice


class NoFederationTokensError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class NoFederationGreenError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class NoResearchPossibleError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class ResearchError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class Level5IsFullError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


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
