import random

from technology import StandardTechnology, AdvancedTechnology


class Level:
    """One single level on the technology track."""

    def __init__(self, active=False, when=False, reward=False):
        # Like Terraforming cost or Navigation range.
        self.active = active

        self.when = when
        self.reward = reward

        # Players on level.
        self.players = set()

    def __str__(self):
        if self.active:
            active = f"Your ongoing bonus is {self.active} "
        else:
            active = ""

        if self.when:
            if self.when == "income":
                reward_type = "income"
            else:
                reward_type = "direct bonus"

            when = f"Your {reward_type} is {self.reward} "
        else:
            when = ""

        if self.players:
            players = ' | '.join(self.players)
        else:
            players = "No players on here"

        return f"{active}{when}{players}"


class Terraforming:
    """Technology track for Terraforming."""

    def __init__(self):
        self.standard = False
        self.level0 = Level(3)
        self.level1 = Level(3, "direct", "ore2" )
        self.level2 = Level(2)
        self.level3 = Level(1)
        self.level4 = Level(1, "direct", "ore2" )
        self.advanced = False
        self.level5 = Level(1, "direct")  # TODO insert fed token
                                                     # as direct


class Navigation:
    """Technology track for Navigation."""

    def __init__(self):
        self.level0 = Level(1)
        self.level1 = Level(1, "direct", "qic1")
        self.level2 = Level(2)
        self.level3 = Level(2, "direct", "qic1")
        self.level4 = Level(3)
        self.advanced = False
        self.level5 = Level(4, "direct", "Lost Planet")  # TODO insert
                                                         # Lost planet object


class ArtificialIntelligence:
    def __init__(self):
        self.level0 = Level()
        self.level1 = Level(False, "direct", "qic1")
        self.level2 = Level(False, "direct", "qic1")
        self.level3 = Level(False, "direct", "qic2")
        self.level4 = Level(False, "direct", "qic2")
        self.advanced = False
        self.level5 = Level(False, "direct", "qic4")


class GaiaProject:
    def __init__(self):
        self.level0 = Level()
        self.level1 = Level(6, "direct", "gaiaformer")
        self.level2 = Level(6, "direct", "powertoken3")
        self.level3 = Level(4, "direct", "gaiaformer")
        self.level4 = Level(3, "direct", "gaiaformer")
        self.advanced = False
        self.level5 = Level(3, "direct", ["vp4", "gaiaplanet1"])


class Economy:
    def __init__(self):
        self.level0 = Level()
        self.level1 = Level(False, "income", ["credits2", "power1"])
        self.level2 = Level(False, "income", ["ore1", "credits2", "power2"])
        self.level3 = Level(False, "income", ["ore1", "credits3", "power3"])
        self.level4 = Level(False, "income", ["ore2", "credits4", "power4"])
        self.advanced = False
        self.level5 = Level("False", "direct", ["ore3", "credits6", "power6"])


class Science:
    def __init__(self):
        self.level0 = Level()
        self.level1 = Level(False, "income", "knowledge1")
        self.level2 = Level(False, "income", "knowledge2")
        self.level3 = Level(False, "income", "knowledge3")
        self.level4 = Level(False, "income", "knowledge4")
        self.advanced = False
        self.level5 = Level(False, "direct", "knowledge9")


class Research:
    """Research board."""

    def __init__(self):
        # Techonlogy tracks.
        self.terraforming = Terraforming()
        self.navigation = Navigation()
        self.artificial_intelligence = ArtificialIntelligence()
        self.gaia_project = GaiaProject()
        self.economy = Economy()
        self.science = Science()

        # Standard technology tiles
        self.free_standard_technology = []

        # Power and QIC actions.
        self.pq_actions = {x: True for x in range(1, 11)}

        self.basic_tech = {x: True for x in range(1, 10)}

    def randomise_tech_tiles(self):
        standard = [
            StandardTechnology("direct", ["ore1", "qic1"]),
            StandardTechnology("direct", "knowledge1"),
            StandardTechnology("worth4power", False),
            StandardTechnology("direct", "vp7"),
            StandardTechnology("income", ["ore1", "power1"]),
            StandardTechnology("income", ["knowledge1", "credits1"]),
            StandardTechnology("action mine on gaia", "vp3"),
            StandardTechnology("income", ["credits4"]),
            StandardTechnology("special", "power4")
        ]

        advanced = [
            AdvancedTechnology("pass", "federationtokens", "vp3"),
            AdvancedTechnology("live", "research", ["vp2"]),
            AdvancedTechnology(special=True, reward=["qic1", "credits5"]),
            AdvancedTechnology("direct", "mine", "vp2"),
            AdvancedTechnology("pass", "researchlab", "vp3"),
            AdvancedTechnology("direct", "sectors", "ore1"),
            AdvancedTechnology("pass", "different_planets", "vp1"),
            AdvancedTechnology("direct", "gaiaplanet", "vp2"),
            AdvancedTechnology("direct", "trade", "vp4"),
            AdvancedTechnology("direct", "sectors", "vp2"),
            AdvancedTechnology(special=True, reward="ore1"),
            AdvancedTechnology("direct", "federationtokens", "vp5"),
            AdvancedTechnology(special=True, reward="knowledge3"),
            AdvancedTechnology("live", "mine", "vp3"),
            AdvancedTechnology("live", "trade", "vp3"),
        ]

        tech_tracks = [
            self.terraforming,
            self.navigation,
            self.artificial_intelligence,
            self.gaia_project,
            self.economy,
            self.science
        ]

        # Randomly assign standard and advanced tiles a location
        while standard:
            if len(standard) > 3:
                tile = standard.pop(random.randrange(len(standard)))
                adv_tile = advanced.pop(random.randrange(len(advanced)))
                tech_track = (
                    tech_tracks.pop(random.randrange(len(tech_tracks)))
                )
                tech_track.standard = tile
                tech_track.advanced = adv_tile
            else:
                tile = standard.pop()
                self.free_standard_technology.append(tile)

    def __str__(self):
        pass
