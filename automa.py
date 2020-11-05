import random

import constants as C
import exceptions as e


class Automa:

    def __init__(self, faction, difficulty="automächtig"):
        self.faction = select_faction(faction.lower())()

        # TODO handle this in a difficulty setup function ??
        if difficulty.lower() == "Automalein":
            self.vp = 0
        else:
            self.vp = 10

        self.booster = False  # This property is set during setup
        self.universe = False  # This property is set during setup

        self.empire = []  # List of owned planets

        # Only matters for the “Most Satellites” final scoring tile.
        self.satellites = 0

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

        self.passed = False  # whether or not the automa has passed.

    def setup(self, research_board):
        # TODO Set yourself on the proper research level.
        pass

    def income_phase(self):
        # Automa doesn't have an income phase.
        pass

    def gaia_phase(self):
        # Automa doesn't have a gaia phase.
        pass

    def action_phase(self, gp, rnd):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject class

        TODO:
            Automate drawing automa cards.
            Print summary of available strucures?
        """

        faction_name = f"\n{self.faction.name}:"
        intro = "What action does the Automa choose?\n"
        mine = "1. Build a mine.\n"
        upgrade = "2. Upgrade an existing structure.\n"
        research = "3. Do research.\n"
        pq = "4. Power or Q.I.C. (Purple/Green) action.\n"
        faction_action = "5. Do a faction action.\n"
        pass_ = "6. Pass.\n"

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine, gp.universe, gp.scoring_board, rnd],
            "2": [self.upgrade],
            "3": [self.research, gp.research_board],
            "4": [self.pq],
            "5": [self.faction.faction_action],
            "6": [self.pass_, gp, rnd],
        }

        print(faction_name)
        print(f"Automa has {self.vp} victory points.\n")

        prompt = (
            f"{intro}{mine}{upgrade}"
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
            except e.BackToActionSelection:
                # User made a mistake and chose the wrong action for the automa
                continue
            else:
                action_name = action[0].__name__
                if not action_name == "pass_":
                    self.points(action_name)
                return

    def points(self, action):
        # Make action names more user friendly.
        if action == "pq":
            action = "power/Q.I.C."

        print(
            f"How many points does the Automa score for doing the {action}"
            " action? Please type the number of points."
        )

        while True:
            points = input("--> ")

            try:
                points = int(points)
            except ValueError:
                print("Please only type a number.")
            else:
                self.vp += points
                return

    def start_mine(self, count, universe):
        faction_name = f"\nAutoma: {self.faction.name}:\n"
        question = f"Where does the Automa place its {count.upper()} mine?\n"
        rules = (
            "The Automa places it's mine closest to the center on its own "
            f"home type ({self.faction.home_type}).\nIf there is a tie, use "
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
                planet = universe.valid_planets(
                    self, int(sector_choice), "start_mine")[0]
            except e.NoValidMinePlanetsError:
                continue
            break

        print(
           f"The Automa has built a mine in sector {sector_choice} on the "
           f"{planet.type} planet."
        )
        planet.owner = self.faction.name
        planet.structure = "mine"
        self.faction.mine_available -= 1
        self.empire.append(planet)

    def choose_booster(self, scoring_board):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            "Which booster does the Automa pick? Please turn a random Automa "
            "card and look at the bottom right."
        )
        print(f"{faction_name}{question}")

        for x, booster in enumerate(scoring_board.boosters, start=1):
            print(f"{x}. {booster}")
        while True:

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
            "\nYou must now shuffle the Automa deck with the cards your chosen"
            " difficulty requires.\nShuffle the cards that aren't used and set"
            " them aside for now.\nDon't forget to rotate the 3 bottom cards "
            "perpendicular to the rest of the deck to see when the Automa "
            "could pass."
        )

        # Allow the player to setup the deck without the game starting yet.
        input(
            "Press enter when you are ready to select your own booster and "
            "begin the game.\n--> "
        )

    def mine(self, universe, scoring_board, rnd):
        """Place a mine for the Automa.

        Args:
            universe: Universe object.
            scoring_board: Scoring object.
            rnd: Active Round object.
        """
        if not self.faction.mine_available:
            raise e.NotEnoughMinesError

        question = f"\nWhere does the Automa place its mine?\n"
        rules = (
            "Valid Options: Any empty planet (including Trans-dim Planets) "
            "within the Automa’s range of a planet the Automa has colonized."
        )

        print(f"{question}{rules}")

        planet_chosen = False
        while True:
            sector = (
                "Please type the number of the sector the chosen planet "
                "is in. Type 8 if you chose the wrong action.\n--> "
            )
            sector_choice = input(sector)

            if sector_choice == "8":
                raise e.BackToActionSelection

            if not sector_choice in C.SECTORS_2P:
                print("Please only type 1-7")
                continue

            while True:
                try:
                    planets = universe.valid_planets(
                        self, int(sector_choice), "automa_mine"
                    )
                except e.NoValidMinePlanetsError:
                    break

                # If there is only one valid planet, return that planet.
                if len(planets) == 1:
                    planet = planets[0]
                    planet_chosen = True
                    break

                # If there are multiple valid planets, choose one.
                print("Please type your chosen planet's corresponding number.")
                for i, pt in enumerate(planets, start=1):
                    print(f"{i}. {pt}")
                print(f"{i + 1}. Go back to sector selection.")

                chosen_planet = input("--> ")
                if chosen_planet in [str(n + 1) for n in range(i)]:
                    planet = planets[int(chosen_planet) - 1]
                    planet_chosen = True
                    break
                elif chosen_planet == f"{i + 1}":
                    break
                else:
                    print("Please only type one of the available numbers.")
                    continue

            if planet_chosen:
                break

        # TODO CRITICAL Check if the opponent can charge power.
        print(
           f"The Automa has built a mine in sector {sector_choice} on the "
           f"{planet.type} planet. Don't forget to place a satellite if "
           "applicable."
        )
        planet.owner = self.faction.name
        planet.structere = "mine"
        self.faction.mine_available -= 1
        self.empire.append(planet)

        # Check if the end tile with goal "Most Satellites" is active.
        # for end in scoring_board.end_scoring:
        #     if end.goal == "satellites":
        #         self.satellites += 1

    def gaia(self, universe):
        # Automa can't do a Gaia Project action.
        pass

    def upgrade(self):
        # TODO CRITICAL For every upgrade, check if the opponent can charge
        # power.
        pass

    def federation(self):
        # Automa can't do a Federation action.
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
            "Please type the corresponding number or type 7 if you chose the "
            "wrong action.\n"
        )
        while True:
            choice = input(f"{options}--> ")

            if choice in ["1", "2", "3", "4", "5", "6"]:
                choice = int(choice)
                current_level = levels[choice - 1]
                track = research_board.tech_tracks[choice - 1]

                # num = Number of the level before completing the research.
                num = int(current_level.name[-1])
            elif choice == "7":
                raise e.BackToActionSelection
            else:
                print("Please only type 1-6")
                continue

            if num == 4:
                # Automa removes the advanced technology if there still is one.
                if track.advanced:
                    print(
                        f"Automa has taken the {track.advanced} "
                        "Advanced Technology tile."
                    )
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

        print(research_board)
        print(f"Automa has researched {track.name}.")

    def pq(self):
        pass

    def special(self):
        # Automa can't do a Special action.
        pass

    def faction_action(self):
        pass

    def pass_(self, gp, rnd):
        print("\nThe Automa Passes.")

        # Check what the current round number is.
        round_number = gp.scoring_board.rounds.index(rnd) + 1

        # Give the automa points for the current round.
        if round_number < 4:
            scored_vp = rnd.first_half
        else:
            scored_vp = rnd.second_half

        # Don't pick a new booster when it's the last round.
        if round_number != 6:
            print(
                "Which Booster does the Automa choose? Please choose the "
                "Booster's corresponding number."
            )
            for pos, boost in zip(
                ["1 (Left)", "2 (Middle)", "3 (Right)"],
                gp.scoring_board.boosters
            ):
                print(f"{pos}. {boost}")
            print(
                f"4. You chose the wrong action. Go back to action selection."
            )

            while True:
                booster_choice = input("--> ")
                if booster_choice in [str(n + 1) for n in range(3)]:
                    # Add old booster to the right of the unused boosters.
                    gp.scoring_board.boosters.append(self.booster)

                    # Set own booster to the chosen booster.
                    self.booster = gp.scoring_board.boosters.pop(
                        int(booster_choice) - 1
                    )
                    print(f"Automa chose {self.booster}.")
                    break
                elif booster_choice == "4":
                    raise e.BackToActionSelection
                else:
                    print("Please only type one of the available numbers.")
                    continue

        gp.passed += 1
        self.passed = True
        self.vp += scored_vp
        print(f"The Automa scored {scored_vp} VP for passing.")

        print(
            "\nTake the discard pile, any cards remaining in the deck, the "
            "current action and support cards,\nand the top card of the "
            "set-aside pile and shuffle them together facedown without "
            "looking at them to create a new Automa deck.\nAnd don't forget to"
            " rotate the 3 bottom cards perpendicular to the rest of the deck "
            "to see when the Automa could pass."
        )
        input("Press enter when you are ready to continue.\n--> ")

        # If automa passed first, it starts first next round.
        if gp.passed == 1:
            gp.players.remove(self)
            gp.players.insert(0, self)
            print("Automa starts first next round.")

    def clean_up(self):
        # Automa has no clean up to do.
        pass


class Faction:
    def __init__(self):
        # Common properties of factions.
        self.name = False
        self.home_type = False

        # Structures
        # Total amount of mines available at the start.
        self.mine_available = 8
        # Total amount of trading stations available at the start.
        self.trading_station_available = 4
        # Total amount of research labs available at the start.
        self.research_lab_available = 3
        # Total amount of academies available at the start.
        self.academy_available = 2
        # Total amount of planetary institutes available at the start.
        self.planetary_institute_available = 1

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
