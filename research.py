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
        if self.players:
            pointer = "--> "
            players = ' | '.join(self.players)
            players = pointer + players
        else:
            players = ""

        return f"{self.name[-1]}. {players}"


class TechTrack:
    """Class for most common similarities between tech track objects."""

    def __init__(self, name):
        self.name = name

    def research(self, old_level, player, choice):
        """Function for going up the chosen research track.

        Args:
            level:  Level object where the player currently is on this track.
            player: Player object.
        """

        # num = Number of the level before going up.
        num = int(old_level.name[-1])

        if num == 4:
            # Check if there isn't already a player on level 5.
            # Error is corrected at runtime so i can ignore this.
            # pylint: disable=no-member
            if self.level5.players:
                raise e.Level5IsFullError

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
                    else:
                        raise e.NoFederationGreenError
            else:
                raise e.NoFederationTokensError
        elif num == 5:
            raise e.NoResearchPossibleError

        player_level_pos = [
            "terraforming",
            "navigation",
            "a_i",
            "gaia_project",
            "economy",
            "science",
        ]
        # Remove player from the current level's list of players.
        old_level.remove(player.faction.name)

        # Add player to the next level on the track's list of players and
        # to the player objects corresponding technology property.
        exec(f"self.level{num + 1}.add(player.faction.name)")
        exec(f"player.{player_level_pos[choice]} = self.level{num + 1}")

        # Check if anything is gained directly after researching.
        level = eval(f"player.{player_level_pos[choice]}")
        if level.when == "direct":
            player.resolve_direct(level.reward)

    def str_ (self, title):
        # From high to low for similarity with the physical game.
        # This function is only called on sublasses so i can ignore this error.
        # pylint: disable=no-member
        output = [
            title,
            str(self.level5),
            str(self.level4),
            str(self.level3),
            str(self.level2),
            str(self.level1),
            str(self.level0)
        ]

        return output


class Terraforming(TechTrack):
    """Technology track for Terraforming."""

    def __init__(self, name):
        TechTrack.__init__(self, name)

        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", 3)
        self.level1 = Level("level1", 3, "direct", "ore2" )
        self.level2 = Level("level2", 2)
        self.level3 = Level("level3", 1)
        self.level4 = Level("level4", 1, "direct", "ore2" )
        self.advanced = False  # This property is set during setup
        # Level 5 reward is a federation which is inserted during setup.
        self.level5 = Level("level5", 1, "direct")


class Navigation(TechTrack):
    """Technology track for Navigation."""

    def __init__(self, name):
        TechTrack.__init__(self, name)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", 1)
        self.level1 = Level("level1", 1, "direct", "qic1")
        self.level2 = Level("level2", 2)
        self.level3 = Level("level3", 2, "direct", "qic1")
        self.level4 = Level("level4", 3)
        self.advanced = False  # This property is set during setup
        # TODO insert lost planet object as level 5 reward
        self.level5 = Level("level5", 4, "direct", "Lost Planet")


class ArtificialIntelligence(TechTrack):
    def __init__(self, name):
        TechTrack.__init__(self, name)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "direct", "qic1")
        self.level2 = Level("level2", False, "direct", "qic1")
        self.level3 = Level("level3", False, "direct", "qic2")
        self.level4 = Level("level4", False, "direct", "qic2")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", False, "direct", "qic4")


class GaiaProject(TechTrack):
    def __init__(self, name):
        TechTrack.__init__(self, name)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", 6, "direct", "gaiaformer1")
        self.level2 = Level("level2", 6, "direct", "powertoken3")
        self.level3 = Level("level3", 4, "direct", "gaiaformer1")
        self.level4 = Level("level4", 3, "direct", "gaiaformer1")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", 3, "direct", ["vp4", "gaiaplanet1"])


class Economy(TechTrack):
    def __init__(self, name):
        TechTrack.__init__(self, name)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "income", ["credits2", "power1"])
        self.level2 = Level("level2", False, "income", ["ore1", "credits2",
                                                        "power2"])
        self.level3 = Level("level3", False, "income", ["ore1", "credits3",
                                                        "power3"])
        self.level4 = Level("level4", False, "income", ["ore2", "credits4",
                                                        "power4"])
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", "False", "direct", ["ore3", "credits6",
                                                          "power6"])


class Science(TechTrack):
    def __init__(self, name):
        TechTrack.__init__(self, name)
        self.standard = False  # This property is set during setup
        self.level0 = Level("level0", )
        self.level1 = Level("level1", False, "income", "knowledge1")
        self.level2 = Level("level2", False, "income", "knowledge2")
        self.level3 = Level("level3", False, "income", "knowledge3")
        self.level4 = Level("level4", False, "income", "knowledge4")
        self.advanced = False  # This property is set during setup
        self.level5 = Level("level5", False, "direct", "knowledge9")


class Research:
    """Research board."""

    def __init__(self):
        # Techonlogy tracks.
        self.terraforming = Terraforming("Terraforming")
        self.navigation = Navigation("Navigation")
        self.a_i = ArtificialIntelligence("Artificial Intelligence")
        self.gaia_project = GaiaProject("Gaia Project")
        self.economy = Economy("Economy")
        self.science = Science("Science")

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

        tech_tracks = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science
        ]

        # Randomly assign standard and advanced tiles a location
        while len(standard) > 3:
            # Pick a random standard technology.
            std_tile = standard.pop(random.randrange(len(standard)))

            # Pick a random advanced technology.
            adv_tile = advanced.pop(random.randrange(len(advanced)))

            # Pick a technology track.
            tech_track = (
                tech_tracks.pop(random.randrange(len(tech_tracks)))
            )

            # Place the standard and advanced tiles on the tech track.
            tech_track.standard = std_tile
            tech_track.advanced = adv_tile
        else:
            # Free standard technology tiles allow you to move up a tech
            # track of your choosing.
            self.free_standard_technology.extend(standard)

    def __str__(self):
        space = " "
        width = "  |  "

        terr = self.terraforming.str_("Terraforming (1):")
        terr_lengths = max([len(text) for text in terr])

        navi = self.navigation.str_("Navigation (2):")
        navi_lengths = max([len(text) for text in navi])

        a_i = self.a_i.str_("Artificial Intellience (3):")
        a_i_lengths = max([len(text) for text in a_i])

        gaia = self.gaia_project.str_("Gaia Project (4):")
        gaia_lengths = max([len(text) for text in gaia])

        eco = self.economy.str_("Economy (5):")
        eco_lengths = max([len(text) for text in eco])

        sci = self.science.str_("Science (6):")
        sci_lengths = max([len(text) for text in sci])

        output = []
        i = 0
        for t, n, a, g, e, s in zip(terr, navi, a_i, gaia, eco, sci):
            output.append(
                f"{t}{space * (terr_lengths - len(terr[i]))}{width}"
                f"{n}{space * (navi_lengths - len(navi[i]))}{width}"
                f"{a}{space * (a_i_lengths - len(a_i[i]))}{width}"
                f"{g}{space * (gaia_lengths - len(gaia[i]))}{width}"
                f"{e}{space * (eco_lengths - len(eco[i]))}{width}"
                f"{s}{space * (sci_lengths - len(sci[i]))}"
            )
            i += 1

        return '\n'.join(output)


if __name__ == "__main__":
    test = Research()
    if eval(f"test.terraforming.level{0}.players"):
        print("player found")
    else:
        print("no player found")

