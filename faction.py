class Faction:
    """General faction board."""

    def __init__(self):
        """Common similarieties between factions.

        Override any of these in the subclasses when needed.
        """

        self.name = False
        self.home_type = False

        # resources
        self.credits = 0  # This property is set during setup
        self.credits_max = 30  # Maximum credits possible.
        self.ore = 0  # This property is set during setup
        self.ore_max = 15  # Maximum ore possible.
        self.knowledge = 0  # This property is set during setup
        self.knowledge_max = 15  # Maximum knowledge possible.
        self.qic = 0  # This property is set during setup
        self.gaiaformer = 0  # This property is set during setup

        # For subclasses to fill a list []. For example:
        # ["credits3", "ore1", "knowledge1"]. These are the income the
        # Hadsch Halla will ALWAYS get independent of a structure covering the
        # income.
        self.standard_income = False

        # Structures
        self.mine_built = 0
        # Total amount of mines available at the start.
        self.mine_max = 8
        self.mine_income = [1, 1, 0, 1, 1, 1, 1, 1]

        self.trading_station_built = 0
        # Total amount of trading stations available at the start.
        self.trading_station_max = 4
        self.trading_station_income = [3, 4, 4, 5]

        self.research_lab_built = 0
        # Total amount of research labs available at the start.
        self.research_lab_max = 3
        self.research_lab_income = [1, 1, 1]

        self.academy_built = 0
        # Total amount of academies available at the start.
        self.academy_max = 2

        # True means that it is built.
        self.academy_income = [False, "knowledge2"]
        self.academy_special = [False, "qic1"]

        self.planetary_institute_built = 0
        # Total amount of planetary institutes available at the start.
        self.planetary_institute_max = 1
        self.planetary_institute_income = ["power4", "powertoken1"]

        # research jump start
        # Options are:
        # Terraforming, Navigation,
        # Artificial Intelligence, Gaia Project
        # Economy, Science
        self.start_research = False

        # power bowls
        self.bowl1 = 0
        self.bowl2 = 0
        self.bowl3 = 20
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
            "bowl2tobowl3": self.move_from_bowl2_to_bowl3
        }

    def move_from_gaia_to_bowl(self):
        """Move power from the gaia project bowl to bowl 1."""

        # Raise an exception if this function hasn't been overwritten in the
        # Terrans subclass.
        if self.name == "Terrans":
            raise NotImplementedError(
                "Terran faction needs to override the"
                "Faction.move_from_gaia_to_bowl function."
            )

        while self.gaia_bowl > 0:
            self.gaia_bowl -= 1
            self.bowl1 += 1

    def move_from_bowl2_to_bowl3(self):
        if self.bowl2 > 1:
            self.bowl2 -= 2
            self.bowl3 += 1

    def count_powertokens(self):
        total = self.bowl1 + self.bowl2 + self.bowl3
        return total

    def planetary_institute_bonus_func(self):
        # For subclasses to override
        raise NotImplementedError(
            f"The faction {self.name} needs to override the"
            "Faction.planetary_institute_bonus_func function."
        )


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
        self.start_research = "Economy"

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


class Terrans(Faction):
    pass


def select_faction(faction):
        factions = {
            "hadsch halla": HadschHalla
        }

        return factions[faction]
