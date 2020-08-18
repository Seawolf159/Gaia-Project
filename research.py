import components


class Level:
    """One single level on the technology track.
    """

    def __init__(self, *, active=False, income=False, direct=False):
        # Like Terraforming cost or Navigation range.
        self.active = active

        self.income = income

        # Anything gained directly when reaching level.
        self.direct = False

        # Players on level.
        self.players = set()

    def __str__(self):
        if self.active:
            active = f"Your ongoing bonus is {self.active} "
        else:
            active = ""

        if self.income:
            income = f"Your income is {self.income} "
        else:
            income = ""

        if self.players:
            players = ' | '.join(self.players)
        else:
            players = "No players on here"

        return f"{active}{income}{players}"


class Terraforming:
    """Technology track for Terraforming.
    """

    def __init__(self):
        self.level0 = Level(active=3)
        self.level1 = Level(direct=["ore", 2], active=3)
        self.level2 = Level(active=2)
        self.level3 = Level(active=1)
        self.level4 = Level(direct=["ore", 2], active=1)
        self.advanced = False  # TODO insert advanced tile object
        self.level5 = Level(direct=False, active=1)  # TODO insert federation token


class Navigation:
    """Technology track for Navigation.
    """

    def __init__(self):
        self.level0 = Level(active=1)
        self.level1 = Level(direct=["qic", 1], active=1)
        self.level2 = Level(active=2)
        self.level3 = Level(direct=["qic", 1], active=2)
        self.level4 = Level(active=3)
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.level5 = Level(direct="Lost Planet", active=5)  # TODO insert Lost planet object


class Research:
    """Research board.

    Everything that can be found on the research board.
    """

    def __init__(self):
        # Techonlogy tracks.
        self.terraforming = Terraforming()
        self.navigation = Navigation()

        # Power and QIC actions.
        self.pq_actions = {x: True for x in range(1, 11)}

        self.basic_tech = {x: True for x in range(1, 10)}


