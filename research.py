import components


class Level:
    """One single level on the technology track.
    """

    def __init__(self, level=0, *, active=False, income=False, direct=False):
        self.level = level
        self.active = active
        self.income = income
        self.direct = False
        self.markers = set()


class Terraforming:
    """Technology track for Terraforming.
    """
    # TODO figure out levels
    def __init__(self):
        self.advanced = False  # TODO insert advanced tile object
        self.level0 = Level(0, active=3)
        self.level1 = Level(1, direct=["ore", 2], active=3)
        self.level2 = Level(active=2)
        self.level3 = Level(active=1)
        self.level4 = Level(direct=["ore", 2], active=1)
        self.level5 = Level(direct=False, active=1)  # TODO insert federation token

        self.players = {}  #  TODO fill at start of game?


class Navigation:
    """Technology track for Navigation.
    """

    def __init__(self):
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.level0 = Level(0, active=1)
        self.level1 = Level(direct=["qic", 1], active=1)
        self.level2 = Level(active=2)
        self.level3 = Level(direct=["qic", 1], active=2)
        self.level4 = Level(active=3)
        self.level5 = Level(direct="Lost Planet", active=5)  # TODO insert Lost planet object


class Research:
    """Research board.

    This class handles everything that can be found on the research board.
    """
    def __init__(self):
        self.score = 10
        self.terraforming = Terraforming()
        self.actions = {x: True for x in range(1, 11)}
        self.basic = {x: True for x in range(1, 10)}


