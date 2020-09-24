import exceptions as e
import random

from technology import AdvancedTechnology, StandardTechnology


class Level:
    """One single level on the technology track."""

    def __init__(self, name, active=False, when=False, reward=False):
        self.name = name

        # Like Terraforming cost or Navigation range.
        self.active = active

        self.when = when
        self.reward = reward

        # Players on level. List of faction names.
        self.players = []

    def add(self, faction_name):
        self.players.append(faction_name)

    def remove(self, faction_name):
        self.players.remove(faction_name)

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
            pointer = "--> "
            players = ' | '.join(self.players)
            players = pointer + players
        else:
            players = ""

        return f"{active}{when}{players}"


class TechTrack:
    """Class for most common similarities between tech track objects."""

    def __init__(self):
        pass

    def research(self, level, player):
        """Function for going up the chosen research track.

        Args:
            level:  Level object where the player currently is on this track.
            faction_name (str): Player object.
        """

        num = int(level.name[-1])

        if num < 4:
            # Remove player from the current level's list of players.
            level.remove(player.faction.name)

            # Add player to the next level on the track's list of players.
            exec(f"self.level[num + 1].add(faction_name)")
        elif num == 4:
            # Check if the player has any federations.
            if player.federations:
                # If they do, check if there are any green sides left and flip
                # the first one found as i don't think it matters which one is
                # flipped if there are multiple ones. Do inform the player
                # which one was turned around.
                for federation in player.federations:
                    if federation.state == "green":
                        federation.state == "grey"
                        print(
                            f"Your {federation} token has been flipped to "
                            "grey and you have been moved to level 5."
                        )
                        return
                else:
                    raise e.NoFederationGreenError
            else:
                raise e.NoFederationTokensError
        elif num == 5:
            raise e.NoResearchPossibleError


class Terraforming(TechTrack):
    """Technology track for Terraforming."""

    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", 3)
        self.level1 = Level("level1", 3, "direct", "ore2" )
        self.level2 = Level("level2", 2)
        self.level3 = Level("level3", 1)
        self.level4 = Level("level4", 1, "direct", "ore2" )
        self.advanced = False  # This property is set during setup
        # Level 5 reward is a federation which is inserted during setup.
        self.level5 = Level("level5", 1, "direct")

    def __str__(self):
        title = "Terraforming\n"
        output = [title]

        output = [
            title,
            f"5. Terraform cost: 1 ore",
            f"4. Terraform cost: 1 ore | Gain: 2 ore",
            f"3. Terraform cost: 1 ore",
        ]

        # From high to low for similarity with the physical game.
        levels = [
            self.level5,
            self.level4,
            self.level3,
            "Charge 3 power.",
            self.level2,
            self.level1,
            self.level0
        ]
        for i, level in enumerate(reversed(levels)):
            output.append(f"{i}. {level}\n")

        return ''.join(output)


class Navigation(TechTrack):
    """Technology track for Navigation."""

    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", 1)
        self.level1 = Level("level1", 1, "direct", "qic1")
        self.level2 = Level("level2", 2)
        self.level3 = Level("level3", 2, "direct", "qic1")
        self.level4 = Level("level4", 3)
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", 4, "direct", "Lost Planet")  # TODO insert
                                                         # Lost planet object

    def __str__(self):
        title = "Navigation\n"
        output = [title]

        # From high to low for similarity with the physical game.
        levels = [
            self.level5,
            self.level4,
            self.level3,
            "Charge 3 power.",
            self.level2,
            self.level1,
            self.level0
        ]
        for i, level in enumerate(reversed(levels), start=1):
            output.append(f"{i}. {level}\n")

        return ''.join(output)


class ArtificialIntelligence(TechTrack):
    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "direct", "qic1")
        self.level2 = Level("level2", False, "direct", "qic1")
        self.level3 = Level("level3", False, "direct", "qic2")
        self.level4 = Level("level4", False, "direct", "qic2")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", False, "direct", "qic4")

    def __str__(self):
        return f"Terraforming:\n{self.advanced}\n"


class GaiaProject(TechTrack):
    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", 6, "direct", "gaiaformer1")
        self.level2 = Level("level2", 6, "direct", "powertoken3")
        self.level3 = Level("level3", 4, "direct", "gaiaformer1")
        self.level4 = Level("level4", 3, "direct", "gaiaformer1")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", 3, "direct", ["vp4", "gaiaplanet1"])

    def __str__(self):
        return f"GaiaProject:\n{self.advanced}\n"


class Economy(TechTrack):
    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "income", ["credits2", "power1"])
        self.level2 = Level("level2", False, "income", ["ore1", "credits2", "power2"])
        self.level3 = Level("level3", False, "income", ["ore1", "credits3", "power3"])
        self.level4 = Level("level4", False, "income", ["ore2", "credits4", "power4"])
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", "False", "direct", ["ore3", "credits6", "power6"])

    def __str__(self):
        return f"Economy:\n{self.advanced}\n"


class Science(TechTrack):
    def __init__(self):
        TechTrack.__init__(self)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "income", "knowledge1")
        self.level2 = Level("level2", False, "income", "knowledge2")
        self.level3 = Level("level3", False, "income", "knowledge3")
        self.level4 = Level("level4", False, "income", "knowledge4")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", False, "direct", "knowledge9")

    def __str__(self):
        return f"Science:\n{self.advanced}\n"


class Research:
    """Research board."""

    def __init__(self):
        # Techonlogy tracks.
        self.terraforming = Terraforming()
        self.navigation = Navigation()
        self.a_i = ArtificialIntelligence()
        self.gaia_project = GaiaProject()
        self.economy = Economy()
        self.science = Science()

        # List for easier selection in other functions.
        self.tech_tracks = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science
        ]

        # Standard technology tiles
        self.free_standard_technology = []

        # Power and QIC actions.
        self.pq_actions = {x: True for x in range(1, 11)}

        self.basic_tech = {x: True for x in range(1, 10)}

    def randomise_tech_tiles(self):
        standard = [
            StandardTechnology("TECqic.png", "direct", ["ore1", "qic1"]),
            StandardTechnology("TECtyp.png", "direct", "knowledge1"),
            StandardTechnology("TECpia.png", "worth4power", False),
            StandardTechnology("TECvps.png", "direct", "vp7"),
            StandardTechnology("TECore.png", "income", ["ore1", "power1"]),
            StandardTechnology("TECknw.png", "income", ["knowledge1",
                                                        "credits1"]),
            StandardTechnology("TECgai.png", "action mine on gaia", "vp3"),
            StandardTechnology("TECcre.png", "income", "credits4"),
            StandardTechnology("TECpow.png", "special", "power4")
        ]

        advanced = [
            AdvancedTechnology(
                "ADVfedP.png", "pass", "federationtokens", "vp3"
            ),
            AdvancedTechnology("ADVstp.png", "live", "research", ["vp2"]),
            AdvancedTechnology(
                "ADVqic.png", "special", reward=["qic1", "credits5"]
            ),
            AdvancedTechnology("ADVminV.png", "direct", "mine", "vp2"),
            AdvancedTechnology("ADVlab.png", "pass", "researchlab", "vp3"),
            AdvancedTechnology("ADVsecO.png", "direct", "sectors", "ore1"),
            AdvancedTechnology(
                "ADVtyp.png", "pass", "different_planets", "vp1"),
            AdvancedTechnology("ADVgai.png", "direct", "gaiaplanet", "vp2"
            ),
            AdvancedTechnology("ADVtrsV.png", "direct", "trade", "vp4"),
            AdvancedTechnology("ADVsecV.png", "direct", "sectors", "vp2"),
            AdvancedTechnology("ADVore.png", "special", reward="ore3"),
            AdvancedTechnology(
                "ADVfedV.png", "direct", "federationtokens", "vp5"
            ),
            AdvancedTechnology("ADVknw.png", "special", reward="knowledge3"),
            AdvancedTechnology("ADVminB.png", "live", "mine", "vp3"),
            AdvancedTechnology("ADVtrsB.png", "live", "trade", "vp3"),
        ]


        # Randomly assign standard and advanced tiles a location
        while len(standard) > 3:
            # Pick a random standard technology.
            std_tile = standard.pop(random.randrange(len(standard)))

            # Pick a random advanced technology.
            adv_tile = advanced.pop(random.randrange(len(advanced)))

            # Pick a technology track.
            tech_track = (
                self.tech_tracks.pop(random.randrange(len(self.tech_tracks)))
            )

            # Place the standard and advanced tiles on the tech track.
            tech_track.standard = std_tile
            tech_track.advanced = adv_tile
        else:
            # Free standard technology tiles allow you to move up a tech
            # track of your choosing.
            self.free_standard_technology.extend(standard)

    def __str__(self):
        return (
            "Research tracks:\n"
            f"{str(self.terraforming)}\n"
            f"{str(self.navigation)}\n"
            f"{str(self.a_i)}\n"
            f"{str(self.gaia_project)}\n"
            f"{str(self.economy)}\n"
            f"{str(self.science)}\n"
        )
