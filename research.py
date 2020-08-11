import components


class Level:
    """Handles one single level on the technology track.
    """

    def __init__(self, *, active=False, income=False, direct=False):
        self.active = active
        self.income = income
        self.direct = False
        self.markers = set()


class Terraforming:
    """Handles the technology track for Terraforming.
    """

    def __init__(self):
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.current = self.level0 = Level(active=3)
        self.level1 = Level(direct=["ore", 2], active=3)
        self.level2 = Level(active=2)
        self.level3 = Level(active=1)
        self.level4 = Level(direct=["ore", 2], active=1)
        self.level5 = Level(direct="Federation token", active=1)  # TODO insert federation token
    # test

class Navigation:
    """Handles the technology track for Navigation.
    """

    def __init__(self):
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.level0 = Level(active=1)
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


