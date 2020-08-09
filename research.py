class Level:
    """Handles one single level on the technology track.
    """

    def __init__(self, *, income=False, direct=False, active=False):
        self.income = income
        self.direct = False


class Terraforming:
    """Handles the technology track for Terraforming.
    """

    def __init__(self):
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.level0 = Level(active=3)
        self.level1 = Level(direct=["ore", 2], active=3)
        self.level2 = Level(active=2)
        self.level3 = Level(active=1)
        self.level4 = Level(direct=["ore", 2], active=1)
        self.level5 = Level(direct="Federation token", active=1)  # TODO insert federation token


class Research:
    """Research board.

    This class handles everything that can be found on the research board.
    """
    def __init__(self):
        self.terraforming = Terraforming()


