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
            "1": [self.mine, gp.universe, gp.scoring_board],
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

            if not choice in options.keys():
                print("Please type the action's corresponding number.")
                continue

            action = options[choice]
            try:
                if len(action) > 1:
                    # If the action function needs additional arguments, unpack
                    # the arguments from the options list.
                    action[0](*action[1:])
                else:
                    # Otherwise just call the function.
                    action[0]()
            except e.NotEnoughMinesError:
                print(
                    "Automa doesn't have any mines left. It will upgrade "
                    "instead."
                )
                continue
            else:
                return

    def start_mines(self, count, universe):
        faction_name = f"\nAutoma: {self.faction.name}:\n"
        question = f"Where does the automa place its {count.upper()} mine?\n"
        rules = (
            "The automa places it's mine closest to the center on its own "
            f"home type ({self.faction.home_type}). If there is a tie, use "
            "directional selection with a random card."
        )

        print(f"{faction_name}{question}{rules}")

        while True:
            sector = (
                "Please type the number of the sector the chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if not sector_choice in C.SECTORS_2P:
                print("Please only type 1-7")
                continue

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
                continue
            except e.PlanetAlreadyOwnedError:
                print(
                    "This planet is already occupied by the Automa. Please"
                    " choose a different sector."
                )
                continue
            else:
                break

        print(
           f"The Automa has built a mine in sector {sector_choice} on the "
           f"{planet.type} planet."
        )
        planet.owner = self.faction.name
        planet.structure = "mine"
        self.faction.mine_max -= 1
        self.empire.append(planet)

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
                break
            else:
                print("Please only type one of the available numbers.")

        # Instruct player to now shuffle the automa deck.
        print(
            "You must now shuffle the automa deck with the cards your chosen"
            " difficulty requires. Don't forget to rotate the 3 bottom cards "
            "to see when the automa could pass."
        )

        # Allow the player to setup the deck without the game starting yet.
        input(
            "Press enter when you are ready to select your own booster and "
            "begin the game.\n--> "
        )

    def mine(self, universe, scoring_board):
        if not self.faction.mine_max:
            raise e.NotEnoughMinesError

        question = f"\nWhere does the automa place its mine?\n"
        rules = (
            "Valid Options: Any empty planet (including Trans-dim Planets) "
            "within the Automa’s range of a planet the Automa has colonized."
        )

        print(f"{question}{rules}")

        type_chosen = False
        while True:
            sector = (
                "Please type the number of the sector the chosen planet "
                "is in.\n--> "
            )
            sector_choice = input(sector)

            if not sector_choice in C.SECTORS_2P:
                print("Please only type 1-7")
                continue

            # TODO Automation, load a list of planets available in the sector.
            # Ask the user for the planet type.
            while True:
                print(
                    "What is the type of the planet the Automa wants to build "
                    "on?"
                )
                for i, pt in enumerate(C.PLANETS, start=1):
                    print(f"{i}. {pt.capitalize()}")
                print("10. Go back to sector selection")
                chosen_type = input("--> ")
                if chosen_type in [str(n + 1) for n in range(len(C.PLANETS))]:
                    try:
                        planet = universe.locate_planet(
                            sector_choice,
                            C.PLANETS[int(chosen_type) - 1],
                        )
                    except e.PlanetNotFoundError:
                        planet_type = C.PLANETS[int(chosen_type) - 1]
                        print(
                            "The selected planet type "
                           f"({planet_type.capitalize()}) doesn't exist inside"
                           f" this sector! ({sector_choice}) Please choose a "
                            "different planet."
                        )
                        continue
                    except e.PlanetAlreadyOwnedError as error:
                        if error.planet.owner == self.faction.name:
                            owner = "you"
                        else:
                            owner = error.planet.owner
                        print(
                           f"The selected planet type ({error.planet.type}) is"
                           f" already occupied by {owner}. "
                            "Please choose a different planet."
                        )
                        continue
                    except e.BothPlanetsAlreadyOwnedError:
                        planet_type = C.PLANETS[int(chosen_type) - 1] \
                            .capitalize()
                        print(
                           f"Both {planet_type} planets are already occupied. "
                            "Please choose a different sector."
                        )
                        break
                    else:
                        type_chosen = True
                        break
                elif chosen_type == "10":
                    break
                else:
                    print("Please only type one of the available numbers.")
                    continue
            if type_chosen:
                break

        print(
           f"The Automa has built a mine in sector {sector_choice} on the "
           f"{planet.type} planet."
        )
        planet.owner = self.faction.name
        planet.structere = "mine"
        self.faction.mine_max -= 1
        self.empire.append(planet)

        # Check if the end tile with goal "Most Satellites" is active.
        for end in scoring_board.end_scoring:
            if end.goal == "satellites":
                self.sattelites += 1

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

        self.points("Research")

        print(research_board)

    def pq(self):
        pass

    def special(self):
        pass

    def pass_(self):
        pass

    def points(self, action):
        print(
            f"How many points does the Automa score for doing {action}? "
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


class Faction:
    def __init__(self):
        # Common properties of factions.
        self.name = False
        self.home_type = False

        # Structures
        # Total amount of mines available at the start.
        self.mine_max = 8
        # Total amount of trading stations available at the start.
        self.trading_station_max = 4
        # Total amount of research labs available at the start.
        self.research_lab_max = 3
        # Total amount of academies available at the start.
        self.academy_max = 2
        # Total amount of planetary institutes available at the start.
        self.planetary_institute_max = 1

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
