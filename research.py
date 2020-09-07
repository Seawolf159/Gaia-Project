import random

from technology import StandardTechnology


class Level:
    """One single level on the technology track."""

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
    """Technology track for Terraforming."""

    def __init__(self):
        self.standard = False
        self.level0 = Level(active=3)
        self.level1 = Level(direct=["ore", 2], active=3)
        self.level2 = Level(active=2)
        self.level3 = Level(active=1)
        self.level4 = Level(direct=["ore", 2], active=1)
        self.advanced = False  # TODO insert advanced tile object
        self.level5 = Level(direct=False, active=1)  # TODO insert fed token
                                                     # as direct
        self.federation_token = False


class Navigation:
    """Technology track for Navigation."""

    def __init__(self):
        self.level0 = Level(active=1)
        self.level1 = Level(direct=["qic", 1], active=1)
        self.level2 = Level(active=2)
        self.level3 = Level(direct=["qic", 1], active=2)
        self.level4 = Level(active=3)
        self.advanced = "Advanced tile"  # TODO insert advanced tile object
        self.level5 = Level(direct="Lost Planet", active=5)  # TODO insert Lost planet object


class ArtificialIntelligence:
    pass


class GaiaProject:
    pass


class Economy:
    pass


class Science:
    pass


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
        self.ore_qic = ["direct", "ore1", "qic1"]
        self.knowledge_planet_types = ["direct", "knowledge1"]
        self.structures_worth_more = ["worth4power"]
        self.vp = ["direct", "vp7"]
        self.ore_power = ["income", "ore1", "power1"]
        self.knowledge_credit = ["income", "knowledge1", "credits1"]
        self.mine_on_gaia = ["action mine on gaia", "vp3"]
        self.credits_ = ["income", "credits4"]
        self.special_power = ["special", "power4"]

        # Power and QIC actions.
        self.pq_actions = {x: True for x in range(1, 11)}

        self.basic_tech = {x: True for x in range(1, 10)}

    def randomise_tech_tiles(self):
        standard = [
            self.ore_qic,
            self.knowledge_planet_types,
            self.structures_worth_more,
            self.vp,
            self.ore_power,
            self.knowledge_credit,
            self.mine_on_gaia,
            self.credits_,
            self.special_power
        ]

        advanced = [
            # adv tech tiles
        ]

        tech_tracks = [
            self.terraforming,
            self.navigation,
            self.artificial_intelligence,
            self.gaia_project,
            self.economy,
            self.science
        ]

        # Randomly assign standard and advanced tiles a position
        while standard:
            if len(standard) > 3:
                tile = standard.pop(random.randrange(len(standard)))
                adv_tile = "todo"  # TODO
                tech_track = (
                    tech_tracks.pop(random.randrange(len(tech_tracks)))
                )
                tech_track.standard = tile
                tech_track.advanced = adv_tile
            else:
                tile = standard.pop()
                tile.append("free")


