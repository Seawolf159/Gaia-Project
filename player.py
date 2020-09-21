import exceptions as e
import random

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
        self.standard_technology = []
        self.advanced_technology = []
        self.booster = False  # This property is set during setup
        self.empire = []  # List of owned planets
        self.universe = False  # This property is set during setup

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during
                                              # setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

    def income_phase(self):
        print(f"\nDoing income for {self.faction.name}.")

        # Income from faction board.
        # Store income of type "power" and "powertoken" here to resolve the
        # order later.
        power_order = []

        # First look at the standard income that you are always going to get.
        self.resolve_income(self.faction.standard_income)

        # Second look at income from structures.
        # Ore from mines.
        for i, _ in enumerate(range(self.faction.mine)):
            self.faction.ore += self.faction.mine_income[i]

        # Credits from trading stations.
        for i, _ in enumerate(range(self.faction.trading_station)):
            self.faction.credits += self.faction.trading_station_income[i]

        # Knowledge from research labs.
        for i, _ in enumerate(range(self.faction.research_lab)):
            self.faction.credits += self.faction.research_lab_income[i]

        # Knowledge from academy.
        if self.faction.academy_income[0]:
            self.faction.knowledge += self.faction.academy_income[1]

        # Income from planetary_institute.
        if self.faction.planetary_institute == 1:
            power_order.extend(
                self.resolve_income(self.faction.planetary_institute_income)
            )

        # Third look at income from booster.
        if self.booster.income1:
            power_order.extend(self.resolve_income(self.booster.income1))
        if self.booster.income2:
            power_order.extend(self.resolve_income(self.booster.income2))

        # Fourth look at income from standard technology
        for technology in self.standard_technology:
            if technology.when == "income":
                power_order.extend(self.resolve_income(technology.reward))

        # Fifth look at income from research tracks
        # TODO

        # Sixth look if there is any power/powertoken gain order that needs to
        # be resolved.
        if len(power_order) > 1:
            power = 0
            token = 0
            for gain in power_order:
                if gain.startswith("powertoken"):
                    token += 1
                else:
                    power += 1

            if power > 0 and token > 0:
                # Player needs to decide to gain power or powertokens first
                # Order the list so that it is easier to read as a human.
                power_order.sort()
                while power_order:
                    print("In what order do you want to gain these power "
                        "resources? Please type one number at a time.")
                    for i, to_resolve in enumerate(power_order, start=1):
                        print(f"{i}, {to_resolve}")

                    selection = input("--> ")
                    if selection in [
                        str(num + 1) for num in range(len(to_resolve))
                    ]:
                        if power_order[int(selection) - 1].startswith(
                            "powertoken"
                        ):
                            self.faction.bowl1 += (
                                int(power_order[int(selection) - 1][-1])
                            )
                        else:
                            self.cycle_power(
                                int(power_order[int(selection) - 1][-1])
                            )
                        power_order.pop(int(selection) - 1)
                    else:
                        print("Please only type one of the available numbers.")
                    # TODO If at some point only one kind of power is
                    # remaining, do the remaining income automatically.
            else:
                power_to_cycle = 0
                for resolved in power_order:
                    if resolved.startswith("powertoken"):
                        self.faction.bowl1 += int(resolved[-1])
                    else:
                        power_to_cycle += int(resolved[-1])

                if power_to_cycle:
                    self.cycle_power(power_to_cycle)

        elif len(power_order) == 1:
            if power_order[0].startswith("powertoken"):
                self.faction.bowl1 += int(power_order[0][-1])
            else:
                self.cycle_power(int(power_order[0][-1]))

        print(f"Your resources are now:")
        print(f"Credits: {self.faction.credits}")
        print(f"Ore: {self.faction.ore}")
        print(f"Knowledge: {self.faction.knowledge}")
        print(f"Qic: {self.faction.qic}")
        print(f"Power in bowl 1: {self.faction.bowl1}")
        print(f"Power in bowl 2: {self.faction.bowl2}")
        print(f"Power in bowl 3: {self.faction.bowl3}")

    def resolve_income(self, incomes):
        # If incomes is not a list and therefore a single income, put that
        # single income in a list to not iterate over a string instead. For
        # example if incomes == "ore2" the iteration below would fail so
        # correct it like so incomes = ["ore2"]
        if not isinstance(incomes, list):
            incomes = [incomes]

        power_order = []
        for income in incomes:
            if (
                income.startswith("powertoken")
                or income.startswith("power")
            ):
                power_order.append(income)
            else:
                exec(f"self.faction.{income[:-1]} += int({income[-1]})")

        return power_order

    def cycle_power(self, amount):
        """Amount of total power that will be cycled."""

        while amount:
            if self.faction.bowl1 > 0:
                self.faction.bowl1 -= 1
                self.faction.bowl2 += 1
            elif self.faction.bowl2 > 0:
                self.faction.bowl2 -= 1
                self.faction.bowl3 += 1
            else:
                return
            amount -= 1

    def gaia_phase(self):
        if self.faction.gaia_bowl > 0:
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

        while True:
            action = input(prompt)

            if action in options.keys():
                try:
                    action()
                except e.NoGaiaFormerError:
                    print("You have no available Gaiaformers. Please pick a "
                          "different action.")
                else:
                    return
            else:
                print("Please type the action's corresponding number.")

    def start_mines(self, count, universe):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            f"Where whould you like to place your {count.upper()} "
            "mine?"
        )
        print(f"{faction_name}{question}")

        while True:
            sector = (
                "Please type the number of the sector your chosen planet "
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
                except e.PlanetNotFoundError:
                    print(
                        f"Your home world ({self.faction.home_type}) doesn't "
                        "exist inside this sector! Please choose a different "
                        "sector.")
                except e.PlanetAlreadyOwnedError:
                    print(
                        "This planet is already occupied by you. Please choose"
                        " a different sector."
                    )
                else:
                    planet.owner = self.faction.home_type
                    self.empire.append(planet)
                    self.faction.mine += 1
                    planet.structure = "mine"
                    return
            else:
                # More players TODO make this message dynamic to the board.
                # If playing with more players it would be 1-10 for example.
                print("Please only type 1-7")

    def choose_booster(self, scoring_board):
        faction_name = f"\n{self.faction.name}:\n"
        question = "Which booster would you like to pick?"
        print(f"{faction_name}{question}")

        while True:
            for x, booster in enumerate(scoring_board.boosters, start=1):
                print(f"{x}. {booster}")

            choice = input(f"--> ")

            if choice in (
                [str(num + 1) for num in range(len(scoring_board.boosters))]
            ):
                self.booster = scoring_board.boosters.pop(int(choice) - 1)
                print(f"You chose {self.booster}.")
                return
            else:
                print("Please only type one of the available numbers.")

    def mine(self):
        pass

    def choose_planet(self, universe, ptype=False):
        """Function for choosing a planet on the board.

        Args:
            universe (object): The universe object used in the main GaiaProject
                class.
            ptype (str): The planet type you already know will be chosen.
                If not provided, this function will ask for a planet type.
        """

        # more players TODO only for 2p right now
        while True:
            sector = (
                "Please type the number of the sector your chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if sector_choice in C.SECTORS_2P:
                try:
                    if ptype:
                        planet = universe.locate_planet(
                            sector_choice,
                            ptype,
                            self.faction
                        )
                    else:
                        # TODO Automation, load a list of planets available in
                        # the sector.
                        while True:
                            print("What is the type of the planet you want to "
                                    "build on?")
                            for i, pt in enumerate(C.PLANETS, start=1):
                                print(f"{i}. {pt.capitalize()}")
                            chosen_type = input("--> ")
                            if chosen_type in [
                                str(n + 1) for n in range(len(C.PLANETS))
                            ]:
                                planet = universe.locate_planet(
                                    sector_choice,
                                    chosen_type,
                                    self.faction
                                )
                                break
                            else:
                                print("Please only type one of the available "
                                    "numbers.")
                except e.PlanetNotFoundError:
                    print(
                        f"Your home world ({self.faction.home_type}) doesn't "
                        "exist inside this sector! Please choose a different "
                        "sector.")
                except e.PlanetAlreadyOwnedError:
                    print(
                        "This planet is already occupied. Please choose a "
                        "different sector."
                    )
                else:
                    return planet
            else:
                # More players TODO make this message dynamic to the board.
                # If playing with more players it would be 1-10 for example.
                print("Please only type 1-7")

    def gaia(self, universe):
        # TODO Don't forget to make the gaia phase
        # TODO Automation, load all the trans-dim planets within range and let
        # player choose a number.
        if self.faction.gaiaformer > 0:
            if self.faction.count_powertokens():
                pass
            print("You want to start a Gaia Project.")
            planet = self.choose_planet(universe, "trans-dim")
            planet.owner = self.faction.home_type
            planet.structure = "gaiaformer"
            self.faction.gaiaformer -= 1
        else:
            raise e.NoGaiaFormerError

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
