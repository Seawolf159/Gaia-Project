"""Module for custom exceptions."""


class PlanetAlreadyOwnedError(Exception):
    pass


class PlanetNotFoundError(Exception):
    pass


class NoGaiaFormerError(Exception):
    pass
