import random

import constants as C
from exceptions import PlanetNotFoundError, PlanetAlreadyOwnedError


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

    def income_phase(self):
        # Automa has no income.
        pass

    def gaia_phase(self):
        # Automa doesn't have a gaia phase.
        pass

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
                        self.faction
                    )
                except PlanetNotFoundError:
                    print(
                        f"The automa home world ({self.faction.home_type}) "
                        "doesn't exist inside this sector. Please choose a "
                        "different sector."
                    )
                except PlanetAlreadyOwnedError:
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
        # TODO look at end scoring and see if i need to place a
        # sattelite??
        pass

    def gaia(self):
        pass

    def upgrade(self):
        pass

    def federation(self):
        pass

    def research(self):
        pass

    def pq(self):
        pass

    def special(self):
        pass

    def pass_(self):
        pass


class Taklons:

    def __init__(self):
        self.name = "Taklons"
        self.home_type = "Swamp"
        self.faction_action = ["mine", "pq"]
        self.range = 3
        self.tiebreaker = (
            "TIEBREAKER 3a:\nShortest distance to one of the "
            "human's' planets"
        )
        self.vp = 2

        # TODO automate more
        # self.terraforming = [
        #     ["gaia", "desert", "titanium"],
        #     ["trans-dim", "volcanic", "ice"],
        #     ["oxide", "terra"]
        # ]


def select_faction(faction):
        factions = {
            "taklons": Taklons
        }

        return factions[faction]
