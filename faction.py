class Faction:
    """Faction board."""

    def __init__(self):
        self.home_type = False

        # resources
        self.credits = 0
        self.ore = 0
        self.knowledge = 0
        self.gaia_former = 0

        # structures
        self.mine = 8
        self.mine_income = "ore1"
        self.mine_tiers = [1, 1, 0, 1, 1, 1, 1, 1]

        self.trading_center = 4
        self.trading_center_income = "credits3"
        self.trading_center_tiers = [3, 4, 4, 5]

        self.science_lab = 3
        self.science_lab_income = "knowledge1"
        self.science_lab_tiers = [1, 1, 1]

        self.academy = 2
        self.academy_tiers = [2, "special qic1"]

        self.planetary_institute = 1

        # research jump start
        self.research = False

        # power bowls
        self.bowl1 = 0
        self.bowl2 = 0
        self.bowl3 = 0
        self.gaia_bowl = 0
        self.gaia_to_power = "bowl1"

        # free actions
        self.free_actions = {
            "power1": "credits1",
            "power3": "ore1",
            "power4": ["qic1", "knowledge1"],
            "knowledge1": "credits1",
            "qic1": ["range2", "ore1"],
            "ore1": ["credits1", "powertoken1"]
        }

    def planetary_institute_bonus_func(self):
        # For subclasses to override
        raise NotImplementedError


class HadschHalla(Faction):

    def __init__(self):
        Faction.__init__(self)

        self.home_type = "oxide"

        # resources
        self.credits = 15
        self.ore = 4
        self.knowledge = 3

        # structures
        self.planetary_institute_income = ["power 4", "power token 1"]

        # research jump start
        self.research = "economy"

        # power bowls
        self.bowl1 = 2
        self.bowl2 = 4

    def planetary_institute_bonus_func(self):
        self.free_actions = {
            # standard
            "power1": "credits1",
            "power3": "ore1",
            "power4": ["qic1", "knowledge1"],
            "knowledge1": "credits1",
            "qic": ["range2", "ore1"],
            "ore": ["credits1", "powertoken1"],

            # planetary institute bonus
            "credits3": "ore1",
            "credits4": ["qic1", "knowledge1"]
        }


def select_faction(faction):
        factions = {
            "hadsch halla": HadschHalla
        }

        return factions[faction]
