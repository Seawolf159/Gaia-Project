"""Module for custom exceptions."""


class PlanetAlreadyOwnedError(Exception):
    pass


class PlanetNotFoundError(Exception):
    pass


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
