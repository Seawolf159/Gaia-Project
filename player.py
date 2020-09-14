import constants as C
from faction import select_faction


class Player:

    def __init__(self, faction):
        """

        Args
            faction (str): name of a faction
                Options to choose from are:
                hadsch halla,
                TODO name all factions and possibly move the options elsewhere
        """

        self.faction = select_faction(faction.lower())()
        self.score = 10
        self.technology = []
        self.advanced_technology = []
        self.booster = False
        self.empire = []  # List of owned planets

    def income(self):
        pass

    def gaia_phase(self):
        pass

    def action_phase(self):
        faction_name: f"\n{self.faction.name}:\n"
        intro = ("What action do you want to take?\n"
                 "Type the number of your action.\n")
        mine = "1. Build a mine.\n"
        gaia = "2. Start a gaia project.\n"
        upgrade = "3. Upgrade existing structure.\n"
        federation = "4. Form a federation.\n"
        research = "5. Research.\n"
        pq = "6. Power or Q.I.C. (Purple/Green).\n"
        special = "7. Special (Orange).\n"
        pass_ = "8. Pass.\n"
        free = "9. Exchange power for resources .\n"

        options = {
            "1": self.mine,
            "2": self.gaia,
            "3": self.upgrade,
            "4": self.federation,
            "5": self.research,
            "6": self.pq,
            "7": self.special,
            "8": self.pass_,
            "9": self.free
        }

        prompt = (
            f"{faction_name}{intro}{mine}{gaia}{upgrade}"
            f"{federation}{research}{pq}{special}{pass_}{free}--> "
        )

        picking_action = True
        while picking_action:
            action = input(prompt)

            if action in options.keys():
                picking_action = False
            else:
                print("\nPlease type the action's corresponding number.",
                      end="")
        else:
            action()

    def start_mines(self, count):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            f"Where whould you like to place your {count.upper()} "
            "mine?"
        )
        print(f"{faction_name}{question}", end="")

        while True:
            sector = (
                "\nPlease type the number of the sector your chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if sector_choice in C.SECTORS_2P:
                planet = self.locate_planet(sector_choice,
                                            self.faction.home_type.lower())
                if planet:
                    planet.owner = self.faction.home_type
                    planet.structure = "mine"
                    return
                else:
                    print(
                        f"\nYour home world ({self.faction.home_type}) doesn't"
                        " exist inside this sector!", end=""
                    )
            else:
                print("\nPlease only type 1-7", end="")

    def locate_planet(self, sector, ptype):
        """Looking for a planet.

        Args:
            sector (str): Number of the sector where you want to find a planet.
            ptype (str): Specific type of planet that your are looking for.
        """

        if sector == "6" and ptype == "gaia":
            pass
        if sector == "7" and ptype == "trans-dim":
            pass
        # skip center as it's always empty
        for circle in eval(f"self.universe.sector{sector}.hexes[1:]"):
            for hex_ in circle:
                if hasattr(hex_, "type"):
                    if hex_.type.lower() == self.faction.home_type.lower():
                        return hex_
        else:
            return False

    def mine(self):
        pass

    def choose_tile(self):
        # more players TODO only for 2p right now
        while True:
            while True:
                sector = (
                    "Please type the number of the sector your planet "
                    "choice is in.\n--> "
                )
                sector_choice = input(sector).lower()

                if sector_choice in C.SECTORS_2P:
                    break

            while True:
                planet = "Please type the chosen planet type or colour.\n--> "
                planet_choice = input(planet).lower()
                if planet_choice in C.PLANETS:
                    # TODO do something
                    pass
                    # if (
                    #     sector_choice == "6"
                    #     and planet_choice == "trans-dim"
                    # ):
                    #     while True:
                    #         specify = (
                    #             "Please specify wich trans-dimensional planet you "
                    #             "would like to choose. Type n for north and s for "
                    #             "south. The sector arrow points north!"
                    #         )
                    #         specification = input(f"{specify}\n--> ")

                    #         if specification in ["n", "s"]:
                    #             break


                    #     else:
                    #         break





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

    def free(self):
        pass



if __name__ == "__main__":
    test = Player("hadsch halla")
    print(test.faction.home_type)
