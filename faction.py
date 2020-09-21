class Faction:
    """General faction board."""

    def __init__(self):
        """Common similarieties between factions.

        Override any of these in the subclasses when needed.
        """

        self.name = False
        self.home_type = False

        # resources
        self.credits = 0
        self.ore = 0
        self.knowledge = 0
        self.qic = 0
        self.gaiaformer = 0

        # For subclasses to fill a list []. For example:
        # ["credits3", "ore1", "knowledge1"]. These are the income the
        # Hadsch Halla will ALWAYS get independent of a structure covering the
        # income.
        self.standard_income = False

        # built structures
        self.mine = 0
        self.mine_income = [1, 1, 0, 1, 1, 1, 1, 1]

        self.trading_station = 0
        self.trading_station_income = [3, 4, 4, 5]

        self.research_lab = 0
        self.research_lab_income = [1, 1, 1]

        self.academy = 0
        self.academy_income = [False, 2]  # True means that it is built
        self.academy_special = [False, "qic1"]  # True means that it is built

        self.planetary_institute = 0
        self.planetary_institute_income = ["power4", "powertoken1"]

        # research jump start
        self.start_research = False

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
            "ore1": ["credits1", "powertoken1"],
            "bowl3": self.move_from_bowl2_to_bowl3
        }

    def move_from_bowl2_to_bowl3(self):
        if self.bowl2 > 1:
            self.bowl2 -= 1
            self.bowl3 += 1

    def count_powertokens(self):
        total = self.bowl1 + self.bowl2 + self.bowl3
        return total

    def planetary_institute_bonus_func(self):
        # For subclasses to override
        raise NotImplementedError


class HadschHalla(Faction):

    def __init__(self):
        Faction.__init__(self)

        self.name = "Hadsch Halla"
        self.home_type = "Oxide"

        # starting resources
        self.credits = 15
        self.ore = 4
        self.knowledge = 3
        self.qic = 1
        self.standard_income = ["credits3", "ore1", "knowledge1"]

        # research jump start
        self.start_research = "economy"

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
            "ore1": ["credits1", "powertoken1"],
            "bowl2tobowl3": self.move_from_bowl2_to_bowl3,

            # planetary institute bonus
            "credits3": "ore1",
            "credits4": ["qic1", "knowledge1"]
        }


def select_faction(faction):
        factions = {
            "hadsch halla": HadschHalla
        }

        return factions[faction]
