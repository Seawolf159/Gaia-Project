import constants as C


class Automa:

    def __init__(self, faction, difficulty="automächtig"):
        self.faction = faction

        # TODO handle this in a difficulty setup function ??
        if difficulty.lower() == "automalein":
            self.score = 0
        else:
            self.score = 10

        self.booster = False  # This property is set during setup
        self.universe = False  # This property is set during setup

    def start_mines(self, count):
        faction_name = f"\nAutoma: {self.faction.name}:\n"
        question = f"Where does the automa place its {count.upper()} mine?\n"
        rules = (
            "The automa places it's mines closest to the center. If there "
            "is a tie, use directional selection."
        )

        print(f"{faction_name}{question}{rules}", end="")

        while True:
            sector = (
                "\nPlease type the number of the sector the chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if sector_choice in C.SECTORS_2P:
                # Ignore this error, it will be fixed at runtime
                # pylint: disable=no-member
                planet = self.universe.locate_planet(
                    sector_choice,
                    self.faction.home_type.lower()
                )

                if planet:
                    planet.owner = self.faction.home_type
                    planet.structure = "mine"
                    return
                else:
                    print(
                        f"\nThe automa home world ({self.faction.home_type}) "
                        "doesn't exist inside this sector!", end=""
                    )
            else:
                print("\nPlease only type 1-7", end="")

    def mine(self):
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
