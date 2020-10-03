import exceptions as e
import random

import constants as C


class Automa:

    def __init__(self, faction, difficulty="automächtig"):
        self.faction = select_faction(faction.lower())()

        # TODO handle this in a difficulty setup function ??
        if difficulty.lower() == "automalein":
            self.score = 0
        else:
            self.score = 10

        self.booster = False  # This property is set during setup
        self.universe = False  # This property is set during setup

        self.empire = []  # List of owned planets

        # Only matters for the “Most Satellites” final scoring tile.
        self.sattelites = 0

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

    def setup(self, research_board):
        # TODO Set yourself on the proper research level.
        pass

    def income_phase(self):
        # Automa doesn't have an income phase.
        pass

    def gaia_phase(self):
        # Automa doesn't have a gaia phase.
        pass

    def action_phase(self, gp):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject class
        """

        # TODO automate drawing automa cards.
        faction_name = f"\n{self.faction.name}:\n"
        intro = "What action does the Automa choose?\n"
        mine = "1. Build a mine.\n"
        upgrade = "2. Upgrade an existing structure.\n"
        research = "3. Do research.\n"
        pq = "4. Power or Q.I.C (Purple/Green) action.\n"
        faction_action = "5. Do a faction action.\n"
        pass_ = "6. Pass.\n"

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine],
            "2": [self.upgrade],
            "3": [self.research, gp.research_board],
            "4": [self.pq],
            "5": [self.faction.faction_action],
            "6": [self.pass_],
        }

        prompt = (
            f"{faction_name}{intro}{mine}{upgrade}"
            f"{research}{pq}{faction_action}{pass_}--> "
        )

        while True:
            choice = input(prompt)

            if choice in options.keys():
                action = options[choice]
                if len(action) > 1:
                    # If the action function needs additional arguments, unpack
                    # the arguments from the options list.
                    action[0](*action[1:])
                else:
                    # Otherwise just call the function.
                    action[0]()
                return
            else:
                print("Please type the action's corresponding number.")

    def start_mines(self, count, universe):
        faction_name = f"\nAutoma: {self.faction.name}:\n"
        question = f"Where does the automa place its {count.upper()} mine?\n"
        rules = (
            "The automa places it's mines closest to the center. If there "
            "is a tie, use directional selection with a random card."
        )

        print(f"{faction_name}{question}{rules}")

        while True:
            sector = (
                "Please type the number of the sector the chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if sector_choice in C.SECTORS_2P:

                try:
                    planet = universe.locate_planet(
                        sector_choice,
                        self.faction.home_type.lower(),
                    )
                except e.PlanetNotFoundError:
                    print(
                        f"The automa home world ({self.faction.home_type}) "
                        "doesn't exist inside this sector. Please choose a "
                        "different sector."
                    )
                except e.PlanetAlreadyOwnedError:
                    print(
                        "This planet is already occupied by the Automa. Please"
                        " choose a different sector."
                    )
                else:
                    planet.owner = self.faction.home_type
                    planet.structure = "mine"
                    return
            else:
                print("Please only type 1-7")

    def choose_booster(self, scoring_board):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            "Which booster does the automa pick? Please turn a random automa "
            "card and look at the bottom right."
        )
        print(f"{faction_name}{question}")

        while True:
            for x, booster in enumerate(scoring_board.boosters, start=1):
                print(f"{x}. {booster}")

            choice = input(f"--> ")

            if choice in (
                [str(num + 1) for num in range(len(scoring_board.boosters))]
            ):
                self.booster = scoring_board.boosters.pop(int(choice) - 1)
                print(f"Automa chose {self.booster}.")
                return
            else:
                print("Please only type one of the available numbers.")

    def mine(self):
        # TODO Look at end scoring and see if i need to place increase the
        # sattelite counter.
        pass

    def gaia(self, universe):
        # Automa can't do a Gaia Project action.
        pass

    def upgrade(self):
        pass

    def federation(self):
        pass

    def research(self, research_board):
        levels = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science,
        ]

        print("\nOn what research track does the Automa go up?")
        print(research_board)
        options = (
            "Please type the corresponding number:\n"
        )
        while True:
            choice = input(f"{options}--> ")

            if choice in ["1", "2", "3", "4", "5", "6"]:
                choice = int(choice)
                current_level = levels[choice - 1]
                track = research_board.tech_tracks[choice - 1]

                # num = Number of the level before completing the research.
                num = int(current_level.name[-1])
            else:
                print("Please only type 1-6")
                continue

            if num == 4:
                # Automa removes the advanced technology if there still is one.
                if track.advanced:
                    print("Automa has taken the advanced tile.")
                    track.advanced = False
                    return
                else:
                    # Check if there is a player on level 5 when there is no
                    # tile present.
                    next_level = track.level5
                    if next_level.players:
                        print(
                            "There is already a player on level 5. The "
                            f"Automa can't research {track.name}. Please "
                            "choose the next technology track."
                        )
                        continue
            elif num == 5:
                print(
                    "Automa is already at the maximum level of 5. Please "
                    "choose the next technology track."
                )
                continue
            break

        print(f"Automa has researched {track.name}.")

        automa_level_pos = [
            "terraforming",
            "navigation",
            "a_i",
            "gaia_project",
            "economy",
            "science",
        ]

        # Remove automa from the current level's list of players.
        current_level.remove(self.faction.name)

        # Add the Automa to the next level on the level's list of players.
        exec(f"track.level{num + 1}.add(self.faction.name)")

        # Add the level to the Automa object's corresponding technology
        # property.
        exec(f"self.{automa_level_pos[choice - 1]} = track.level{num + 1}")

        print(
            "How many points does the Automa score for doing research? ",
            "Please type the number of points."
        )
        while True:
            points = input("--> ")

            try:
                points = int(points)
            except ValueError:
                print("Please only type a number.")
            else:
                self.score += points
                break
        print(research_board)

    def pq(self):
        pass

    def special(self):
        pass

    def pass_(self):
        pass


class Faction:
    def __init__(self):
        # Common properties of factions.
        self.name = False
        self.home_type = False

        # research jump start
        # Options are:
        # Terraforming, Navigation,
        # Artificial Intelligence, Gaia Project
        # Economy, Science
        self.start_research = False

    def faction_action(self):
        # For subclasses to overwrite.
        raise NotImplementedError


class Taklons(Faction):

    def __init__(self):
        Faction.__init__(self)
        self.name = "Taklons"
        self.home_type = "Swamp"

        # research jump start
        # Options are (exactly as is):
        # Terraforming, Navigation,
        # Artificial Intelligence, Gaia Project
        # Economy, Science
        self.start_research = False

        # TODO automate more
        # self.terraforming = [
        #     ["gaia", "desert", "titanium"],
        #     ["trans-dim", "volcanic", "ice"],
        #     ["oxide", "terra"]
        # ]

    def faction_action(self):
        # TODO create the faction action of the automa
        # faction_action = ["mine", "pq"]
        # range = 3
        # tiebreaker = (
        #     "TIEBREAKER 3a:\nShortest distance to one of the "
        #     "human's' planets"
        # )
        # vp = 2
        pass


def select_faction(faction):
    factions = {
        "taklons": Taklons
    }

    return factions[faction]
