class Faction:
    """Faction boards"""

    def __init__(self):
        self.home_type = False

        # resources
        self.credits = 0
        self.ore = 0
        self.knowledge = 0
        self.gaia_former = 0

        # structures
        self.mine = 8
        self.trading_center = 5
        self.science_lab = 3
        self.academy = 2
        self.planetary_institute = 1

        # research jump start
        self.research = False

        # Power bowls
        self.bowl1 = 0
        self.bowl2 = 0
        self.bowl3 = 0
        self.gaia_bowl = 0
        self.gaia_to_power = "bowl1"
