import random

import constants as C
import exceptions as e


class Automa:

    def __init__(self, faction, difficulty):
        self.faction = select_faction(faction.lower())()
        self.difficulty = difficulty
        self.set_difficulty()

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

    def set_difficulty(self):
        if self.difficulty.lower() == "automalein":
            self.vp = 0
        else:
            self.vp = 10

    def start_mine(self, count, universe, players):
        """Function for placing the initial mines.

        Args:
            count (str): Number of the mine placed.
            universe: The universe object used in the main GaiaProject class.
            players: list of the players in the current game.
        """

        faction_name = f"\nAutoma {self.faction.name}:"
        print(f"{faction_name}")

        # Automa places a mine on a home type that is closest to the center
        # space of the board.
        valid_options = [
            planet for planet in universe.planets.values()
                if planet.type == self.faction.home_type
                    and planet not in self.empire
        ]

        # Figure out what the shortest distance to the center is of all
        # valid options.
        closest_distance = 43 # Abitrarily high so found distance is lower.
        center_x = 8
        center_y = 13
        for planet in valid_options:
            startx = planet.location[0]
            starty = planet.location[1]

            targetx = center_x
            targety = center_y

            distance = universe.distance(startx, starty, targetx, targety)
            if distance < closest_distance:
                closest_distance = distance

                # Can't get lower than 1
                if closest_distance == 1:
                    break

        # Figure out which of the valid_options are closest to the center based
        # on the shortest distance we have just found above.
        temp_options = []
        for planet in valid_options:
            startx = planet.location[0]
            starty = planet.location[1]

            targetx = center_x
            targety = center_y

            distance = universe.distance(startx, starty, targetx, targety)
            if distance == closest_distance:
                temp_options.append(planet)

        valid_options = temp_options[:]

        if len(valid_options) > 1:
            print(
                "There are multiple planets that are equally close to the "
                "center.\nPlease take a random decision card and type the number "
                "of the corresponding direction the arrow of the Directional "
                "Selection is pointing to."
            )

            for i, direct in enumerate(["<--", "-->"], start=1):
                print(f"{i}. {direct}")

            while True:
                direction = input("--> ")
                if not direction in [str(n + 1) for n in range(i)]:
                    print(
                        "! Please type the number of the corresponding "
                        "direction the arrow is pointing to."
                    )
                    continue
                else:
                    break

            if direction == '1':
                reverse = True
            else:
                reverse = False

            for _, selection_planet in sorted(
                universe.planets.items(), reverse=reverse
            ):
                if selection_planet in valid_options:
                    planet = selection_planet
                    break
        else:
            planet = valid_options[0]

        print(
           f"The Automa has built it's {count.upper()} mine on the planet in "
           f"{planet}."
        )
        planet.owner = self.faction.name
        planet.structure = "Mine"
        self.faction.mine_available -= 1
        self.empire.append(planet)

        # Check if the mine was placed within range 2 of an opponent.
        universe.planet_has_neighbours(
            planet, self, players, neighbour_charge=False
        )

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
                print("! Please only type one of the available numbers.")

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

    def income_phase(self):
        # Automa doesn't have an income phase.
        pass

    def gaia_phase(self):
        # Automa doesn't have a gaia phase.
        pass

    def action_phase(self, gp, rnd, choice=False):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.

        TODO:
            Automate drawing automa cards.
            Print summary of available strucures?
        """

        faction_name = f"\n{self.faction.name}:"
        intro = "What action does the Automa choose?"
        mine = "1. Build a mine."
        upgrade = "2. Upgrade an existing structure."
        research = "3. Do research."
        pq = "4. Power or Q.I.C. (Purple/Green) action."
        faction_action = "5. Do a faction action."
        pass_ = "6. Pass."

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine, gp],
            "2": [self.upgrade, gp],
            "3": [self.research, gp.research_board],
            "4": [self.pq, gp.research_board],
            "5": [self.faction.faction_action, gp, self],
            "6": [self.pass_, gp, rnd],
        }

        while True:
            automa_points = f"Automa has {self.vp} victory points."
            prompt = (
                f"{faction_name}\n"
                f"{automa_points}\n"
                f"{intro}\n"
                f"{mine}\n"
                f"{upgrade}\n"
                f"{research}\n"
                f"{pq}\n"
                f"{faction_action}\n"
                f"{pass_}\n"
                "--> "
            )
            if not choice or choice == "0":
                choice = input(prompt)

            if not choice in options.keys():
                print("Please type the action's corresponding number.")
                choice = "0"
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
            except e.NotEnoughMinesError as ex:
                print(ex)
                choice = "2"
                continue
            except e.BackToActionSelection as back:
                # User made a mistake and chose the wrong action for the automa
                choice = back.choice
                continue
            else:
                action_name = action[0].__name__
                if not action_name in ["pass_", "faction_action"]:
                    self.points(action_name)
                return

    def points(self, action):
        # Make action names more user friendly.
        if action == "pq":
            action = "Power/Q.I.C."
        else:
            action = action.capitalize()

        print(
            f"\nHow many points does the Automa score for doing the "
            f"{action} action? Please type the number of points."
        )

        while True:
            points = input("--> ")

            try:
                points = int(points)
            except ValueError:
                print("! Please only type a number.")
            else:
                self.vp += points
                return

    def mine(self, gp, faction_action=False):
        """Place a mine for the Automa.

        Args:
            gp: GaiaProject main game object.
            faction_action: Whether or not this function was called as a result
                of a faction action. False if not, Int if it was. The Int is
                the range the faction action provides.
        """

        # 1. Condition: The Automa has at least one mine in.
        if not self.faction.mine_available:
            raise e.NotEnoughMinesError(
                "! Automa doesn't have any mines left. It will upgrade "
                "instead."
            )

        # 2. Valid Options: Any empty planet (including Trans-dim
        # Planets) within the Automa’s range of a planet the
        # Automa has colonized.
        if faction_action:
            max_range = faction_action
        else:
            print("What is the range of the Automa?")
            while True:
                try:
                    max_range = int(input("--> "))
                except ValueError:
                    print("! Please only type a number.")
                    continue
                else:
                    break

        valid_options = self.mine_valid_options(gp, max_range)

        # After EVERY tiebreaker, check to see if the length of the
        # valid_options list is still bigger than 1. If it IS 1, a planet has
        # been determined.
        if len(valid_options) > 1:
            # 3. Tiebreaker.
            # 3a. Faction action tiebreaker, if built by a faction action.
            if faction_action:
                valid_options = self.faction.mine_tiebreaker(
                    gp, valid_options, self
                )

        if len(valid_options) > 1:
            # 3b. Check if there are end scoring tiles that could be used for
            # breaking ties.
            relevant_tiles = ["sectors", "planet_types", "gaia_planets"]
            end_scoring_flag = False
            for end_scoring in gp.scoring_board.end_scoring:
                if end_scoring.goal in relevant_tiles:
                    end_scoring_flag = True
                    break

            if end_scoring_flag:
                print(
                    "Does the Automa check the final scoring tiles for a "
                    "tiebreaker? Please type the corresponding number."
                )

                print(
                    "1. Top tile\n"
                    "2. Bottom tile\n"
                    "3. Final scoring tiles tile aren't used."
                )
                while True:
                    tile_choice = input("--> ")

                    if not tile_choice in ['1', '2', '3']:
                        print(
                            "! Please only type one of the available numbers."
                        )
                        continue
                    else:
                        break

                if tile_choice != '3':
                    # Start filtering.
                    temp_filter = []
                    for i, tile in enumerate(
                        gp.scoring_board.end_scoring, start=1
                    ):
                        if not i == int(tile_choice):
                            continue

                        if tile.goal in relevant_tiles:
                            if tile.goal == "sectors":
                                # Unique sectors the Automa is in.
                                sectors = {
                                    planet.sector for planet in self.empire
                                }

                                for planet in valid_options:
                                    if not planet.sector in sectors:
                                        temp_filter.append(planet)

                            elif tile.goal == "planet_types":
                                # Unique planet types the Automa owns
                                planet_types = {
                                    planet.type for planet in self.empire
                                }

                                for planet in valid_options:
                                    # Trans-dim counts as Gaia.
                                    if planet.type == "Trans-dim" \
                                            and "Gaia" in planet_types:
                                        continue

                                    if not planet.type in planet_types:
                                        temp_filter.append(planet)

                            elif tile.goal == "gaia_planets":
                                for planet in valid_options:
                                    if planet.type in ["Gaia", "Trans-dim"]:
                                        temp_filter.append(planet)

                    if temp_filter:
                        # If the valid_options got reduced by checking for
                        # end_scoring, make the valid_options the list of
                        # filtered planets.
                        valid_options = temp_filter[:]

        if len(valid_options) > 1:
            # 3c. Planet type requiring the fewest terraforming steps for the
            # Automa’s faction. For this purpose, Gaia Planets require
            # 1 terraforming step and Transdim Planets require 2 steps.
            temp_filter = []
            for tier in range(4):
                for planet in valid_options:
                    if planet.type in self.faction.terraform_tiers[tier]:
                        temp_filter.append(planet)

                # If the current tier produced any results, stop right away
                # because it's about the lowest terraform steps found.
                if temp_filter:
                    valid_options = temp_filter[:]
                    break

        if len(valid_options) > 1:
            # 3d. Planet closest to any of YOUR planets.
            # From the valid_options, find out what the shortest distance
            # to the opponent is.
            closest_distance = self.closest_distance_to_opponent(
                gp, valid_options
            )

            # Find all planets that are closest_distance from the opponent.
            valid_options = self.closest_planets_to_opponent(
                gp, closest_distance, valid_options
            )

        if len(valid_options) > 1:
        # 3e. Directional selection.
            print(
                "\nThere are multiple planets that are equally closest "
                "to you.\nPlease type the number of the corresponding "
                "direction the arrow of the Directional Selection is "
                "pointing to."
            )

            for i, direct in enumerate(["<--", "-->"], start=1):
                print(f"{i}. {direct}")

            while True:
                direction = input("--> ")
                if not direction in [str(n + 1) for n in range(i)]:
                    print(
                        "! Please type the number of the corresponding "
                        "direction the arrow is pointing to."
                    )
                    continue
                else:
                    break

            if direction == '1':
                reverse = True
            else:
                reverse = False

            for _, selection_planet in sorted(
                gp.universe.planets.items(), reverse=reverse
            ):
                if selection_planet in valid_options:
                    valid_options = [selection_planet]
                    break

        planet = valid_options[0]

        print(
            f"The Automa has built a mine on the planet in {planet}.\nDon't "
            "forget to place a satellite if applicable. (The satellite matters"
            " only for the 'Most Satellites' final scoring tile.)"
        )
        planet.owner = self.faction.name
        if planet.type == "Trans-dim":
            planet.type = "Gaia"
        planet.structure = "Mine"
        self.faction.mine_available -= 1
        self.empire.append(planet)
        gp.universe.planet_has_neighbours(planet, self, gp.players)

    def mine_valid_options(self, gp, max_range):
        """Find all planets within max_range of the Automa

        Args:
            gp: GaiaProject main game object.
            max_range (int): Maximum distance the Automa can go.

        Returns:
            A list with all the found planets.
        """

        valid_options = []
        for planet in self.empire:
            start_x = planet.location[0]
            start_y = planet.location[1]
            coords_to_check = self.coords_to_check(
                start_x, start_y, max_range
            )

            for location in coords_to_check:
                # Coordinate is a Space or is outside of the universe.
                if not location in gp.universe.planets:
                    continue

                planet = gp.universe.planets[location]

                # Already found planet.
                if planet in valid_options:
                    continue

                # Planet is already owned.
                if planet.owner:
                    continue
                else:
                    valid_options.append(planet)

        return valid_options

    def coords_to_check(self, start_x, start_y, max_range):
        """
        Provide a list of coordinates that need to be checked
        with a given range.

        Args:
            start_x (int): x coord of Planet
            start_y (int): y coord of Planet
            max_range (int): Maximum distance the Automa can go.

        """
        # Coordinates to check.
        range2 = [
            # First ring.
            (start_x, start_y - 2),
            (start_x - 1, start_y - 1),
            (start_x - 1, start_y + 1),
            (start_x, start_y + 2),
            (start_x + 1, start_y + 1),
            (start_x + 1, start_y - 1),

            # Second ring.
            (start_x, start_y - 4),
            (start_x - 1, start_y - 3),
            (start_x - 2, start_y - 2),
            (start_x - 2, start_y),
            (start_x - 2, start_y + 2),
            (start_x - 1, start_y + 3),
            (start_x, start_y + 4),
            (start_x + 1, start_y + 3),
            (start_x + 2, start_y + 2),
            (start_x + 2, start_y),
            (start_x + 2, start_y - 2),
            (start_x + 1, start_y - 3),
        ]

        range3 = [
            # Third ring.
            (start_x, start_y - 6),
            (start_x - 1, start_y - 5),
            (start_x - 2, start_y - 4),
            (start_x - 3, start_y - 3),
            (start_x - 3, start_y - 1),
            (start_x - 3, start_y + 1),
            (start_x - 3, start_y + 3),
            (start_x - 2, start_y + 4),
            (start_x - 1, start_y + 5),
            (start_x, start_y + 6),
            (start_x + 1, start_y + 5),
            (start_x + 2, start_y + 4),
            (start_x + 3, start_y + 3),
            (start_x + 3, start_y + 1),
            (start_x + 3, start_y - 1),
            (start_x + 3, start_y - 3),
            (start_x + 2, start_y - 4),
            (start_x + 1, start_y - 5),
        ]

        range4 = [
            # Fourth ring.
            (start_x, start_y - 8),
            (start_x - 1, start_y - 7),
            (start_x - 2, start_y - 6),
            (start_x - 3, start_y - 5),
            (start_x - 4, start_y - 4),
            (start_x - 4, start_y - 2),
            (start_x - 4, start_y),
            (start_x - 4, start_y + 2),
            (start_x - 4, start_y + 4),
            (start_x - 3, start_y + 5),
            (start_x - 2, start_y + 6),
            (start_x - 1, start_y + 7),
            (start_x, start_y + 8),
            (start_x + 1, start_y + 7),
            (start_x + 2, start_y + 6),
            (start_x + 3, start_y + 5),
            (start_x + 4, start_y + 4),
            (start_x + 4, start_y + 2),
            (start_x + 4, start_y),
            (start_x + 4, start_y - 2),
            (start_x + 4, start_y - 4),
            (start_x + 3, start_y - 5),
            (start_x + 2, start_y - 6),
            (start_x + 1, start_y - 7),
        ]

        if max_range == 2:
            coords_to_check = range2
        elif max_range == 3:
            coords_to_check = range2 + range3
        else:
            coords_to_check = range2 + range3 + range4

        return coords_to_check

    # Old version
    # def mine(self, gp, faction_action=False):
    #     """Place a mine for the Automa.

    #     Args:
    #         gp: GaiaProject main game object.
    #     """

    #     if not self.faction.mine_available:
    #         raise e.NotEnoughMinesError(
    #             "Automa doesn't have any mines left. It will upgrade "
    #             "instead."
    #         )

    #     question = f"\nWhere does the Automa place its mine?\n"
    #     rules = (
    #         "Valid Options: Any empty planet (including Trans-dim Planets) "
    #         "within the Automa’s range of a planet the Automa has colonized."
    #     )

    #     print(f"{question}{rules}")

    #     planet_chosen = False
    #     if faction_action:
    #         sector = (
    #             "Please type the number of the sector the chosen planet "
    #             "is in.\n--> "
    #         )
    #     else:
    #         sector = (
    #             "Please type the number of the sector the chosen planet "
    #             "is in. Type 8 if you chose the wrong action.\n--> "
    #         )
    #     while True:
    #         sector_choice = input(sector)

    #         if sector_choice == "8":
    #             if faction_action:
    #                 print("! Please only type 1-7")
    #                 continue
    #             else:
    #                 raise e.BackToActionSelection

    #         if not sector_choice in C.SECTORS_2P:
    #             print("! Please only type 1-7")
    #             continue

    #         while True:
    #             try:
    #                 planets = gp.universe.valid_planets(
    #                     self, int(sector_choice), "automa_mine"
    #                 )
    #             except e.NoValidMinePlanetsError:
    #                 break

    #             # If there is only one valid planet, return that planet.
    #             if len(planets) == 1:
    #                 planet = planets[0]
    #                 planet_chosen = True
    #                 break

    #             # If there are multiple valid planets, choose one.
    #             print("Please type your chosen planet's corresponding number.")
    #             for i, pt in enumerate(planets, start=1):
    #                 print(f"{i}. {pt}")
    #             print(f"{i + 1}. Go back to sector selection.")

    #             chosen_planet = input("--> ")
    #             if chosen_planet in [str(n + 1) for n in range(i)]:
    #                 planet = planets[int(chosen_planet) - 1]
    #                 planet_chosen = True
    #                 break
    #             elif chosen_planet == f"{i + 1}":
    #                 break
    #             else:
    #                 print("! Please only type one of the available numbers.")
    #                 continue

    #         if planet_chosen:
    #             break

    #     print(
    #        f"The Automa has built a mine in sector {sector_choice} on the "
    #        f"{planet.type} planet. Don't forget to place a satellite if "
    #        "applicable."
    #     )

    #     planet.owner = self.faction.name
    #     if planet.type == "Trans-dim":
    #         planet.type = "Gaia"
    #     planet.structure = "Mine"
    #     self.faction.mine_available -= 1
    #     self.empire.append(planet)

    #     gp.universe.planet_has_neighbours(planet, self, gp.players)

    def gaia(self, universe):
        # Automa can't do a Gaia Project action.
        pass

    def upgrade(self, gp, faction_action=False):
        # 1. Condition: The Automa can resolve an upgrade.
        # 2. Valid Options: The Automa upgrades structures based on the
        #   following priority list (also shown on the “upgrade” icon).
        #   Move down the list until you reach an upgrade the Automa can
        #   resolve; planets with the necessary structure are valid. Note
        #   that there is no difference between the Automa’s academies.
        #   a. Upgrade a trading station into a planetary institute.
        #   b. Upgrade a mine into a trading station.
        #   c. Upgrade a research lab into an academy.
        #   d. Upgrade a trading station into a research lab.

    	# Check for availability of all the structures.
        trade_available = self.faction.trading_station_available != 0
        institute_available = self.faction.planetary_institute_available != 0
        mine_available = self.faction.mine_available != 0
        research_available = self.faction.research_lab_available != 0
        academy_available = self.faction.academy_available != 0

        # Keep checking for available upgrades until one is found.
        i = 0
        while True:
            if i == 0 and institute_available:
                candidates = list(filter(
                    lambda planet: planet.structure == "Trading Station",
                    self.empire
                ))
                if candidates:
                    structure_upgrade = "Planetary Institute"
                    self.faction.trading_station_available += 1
                    self.faction.planetary_institute_available -= 1
                    break
            elif i == 1 and trade_available:
                candidates = list(filter(
                    lambda planet: planet.structure == "Mine",
                    self.empire
                ))
                if candidates:
                    structure_upgrade = "Trading Station"
                    self.faction.mine_available += 1
                    self.faction.trading_station_available -= 1
                    break
            elif i == 2 and academy_available:
                candidates = list(filter(
                    lambda planet: planet.structure == "Research Lab",
                    self.empire
                ))
                if candidates:
                    structure_upgrade = "Academy"
                    self.faction.research_lab_available += 1
                    self.faction.academy_available -= 1
                    break
            elif i == 3 and research_available:
                candidates = list(filter(
                    lambda planet: planet.structure == "Trading Station",
                    self.empire
                ))
                if candidates:
                    structure_upgrade = "Research Lab"
                    self.faction.trading_station_available += 1
                    self.faction.research_lab_available -= 1
                    break

            if i == 3:
                # If nothing was upgradable, the Automa does nothing.
                if faction_action:
                    print(
                        "\n! No structure can be Upgraded. The Automa skips "
                        "this action."
                    )
                else:
                    print(
                        "\n! No structure can be Upgraded. The Automa does "
                        "nothing this turn. The Automa DOES score points "
                        "though!"
                    )
                return
            else:
                i += 1

        # 3. Tiebreaker:
        #   a. Closest to any of your planets.
        #   b. Directional selection.

        # If the candidate list is only 1 long, there must only be 1 upgradable
        # structure so just upgrade it.
        if len(candidates) == 1:
            planet = candidates[0]

            # Check if the planet is neighbouring the opponent.
            closest_distance = self.closest_distance_to_opponent(
                gp, candidates
            )

        # Look at the tiebreakers for which structure to upgrade.
        else:
            # a. Closest to any of player's planets.
            closest_distance = self.closest_distance_to_opponent(
                gp, candidates
            )

            # Check which planets are equally closest.
            closest_planets = self.closest_planets_to_opponent(
                gp, closest_distance, candidates
            )

            if len(closest_planets) == 1:
                planet = closest_planets[0]

            # If there are multiple closest planets, let the player handle
            # the b. Directional selection tiebreaker.
            else:
                print(
                    "\nThere are multiple planets that are equally closest "
                    "to you.\nPlease type the number of the corresponding "
                    "direction the arrow of the Directional Selection is "
                    "pointing to."
                )

                for i, direct in enumerate(["<--", "-->"], start=1):
                    print(f"{i}. {direct}")

                while True:
                    direction = input("--> ")
                    if not direction in [str(n + 1) for n in range(i)]:
                        print(
                            "! Please type the number of the corresponding "
                            "direction the arrow is pointing to."
                        )
                        continue
                    else:
                        break

                if direction == '1':
                    reverse = True
                else:
                    reverse = False

                for _, selection_planet in sorted(
                    gp.universe.planets.items(), reverse=reverse
                ):
                    if selection_planet in closest_planets:
                        planet = selection_planet
                        break

        print(
            f"The Automa has upgraded Planet: {planet} and placed a "
            f"{structure_upgrade} there."
        )
        planet.structure = structure_upgrade

        # Let opponent charge power.
        if closest_distance < 3:
            gp.universe.planet_has_neighbours(planet, self, gp.players)

    def closest_distance_to_opponent(self, gp, valid_options):
        """Function for determining the closest distance to the opponent.

        Args:
            gp: GaiaProject main game object.
            valid_options: List of valid_options.

        Returns:
            The distance of the closest planet to the opponent.
                (1 is the lowest it can be.)
        """

        closest_distance = 43  # Abitrarily high so found distance is lower.
        for opponent in gp.players:
            if opponent is self:
                continue

            # Check all candidatates what the shortest distance is to the
            # opponent.
            for automa_planet in valid_options:
                for opponent_planet in opponent.empire:
                    startx = automa_planet.location[0]
                    starty = automa_planet.location[1]

                    targetx = opponent_planet.location[0]
                    targety = opponent_planet.location[1]

                    distance = gp.universe.distance(
                        startx, starty, targetx, targety
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        # Can't get lower than 1 so immediately return
                        # TODO faction compatibility. With lantids, distance
                        #   can be 0.
                        if closest_distance == 1:
                            return closest_distance
            return closest_distance

    def closest_planets_to_opponent(self, gp, closest_distance, valid_options):
        """Function for determining the closest planet to the opponent.

        Args:
            gp: GaiaProject main game object.
            closest_distance (Int): The distance that's closest to the
                opponent.
            valid_options: List of valid_options.

        Returns:
            A list of planets that are equally close the the opponent.
        """

        closest_planets = []
        for opponent in gp.players:
            if opponent is self:
                continue

            # Check all valid_options if they are one of the closest to the
            # opponent.
            for automa_planet in valid_options:
                for opponent_planet in opponent.empire:
                    startx = automa_planet.location[0]
                    starty = automa_planet.location[1]

                    targetx = opponent_planet.location[0]
                    targety = opponent_planet.location[1]

                    distance = gp.universe.distance(
                        startx, starty, targetx, targety
                    )
                    if distance == closest_distance:
                        closest_planets.append(automa_planet)
                        break

            return closest_planets

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
                print("! Please only type 1-6")
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
                            "! There is already a player on level 5. The "
                            f"Automa can't research {track.name}. Please "
                            "choose the next technology track."
                        )
                        continue
            elif num == 5:
                print(
                    "! Automa is already at the maximum level of 5. Please "
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

        # Add the level to the Automa object's corresponding research
        # property.
        exec(f"self.{automa_level_pos[choice - 1]} = track.level{num + 1}")

        print(research_board)
        print(f"Automa has researched {track.name}.")

    def pq(self, research_board, faction_action=False):
        # Check if there are any Power/Q.I.C. actions still open
        if not any(research_board.pq_actions.values()):
            print(
                "\n! There are no available Power/Q.I.C. Actions left. "
                "The Automa does nothing this turn. the Automa DOES score "
                "points though!"
            )
            return

        print(
            "\nWhich Power/Q.I.C. Action does the Automa take?"
        )

        if faction_action:
            prompt = (
                "Please type the number of the Numbered Selection (1-5).\n"
                "--> "
            )
        else:
            prompt = (
                "Please type the number of the Numbered Selection (1-5).\n"
                "Type 0 if the Automa does a different Action.\n--> "
            )
        while True:
            number = input(prompt)

            if number == "0":
                if faction_action:
                    continue
                else:
                    raise e.BackToActionSelection
            elif not number in [str(num) for num in range(1, 6)]:
                continue

            number_selection = False
            while True:
                print(
                    "Please type the number of the corresponding direction "
                    "the arrow of the Numbered Selection is pointing to."
                )
                for i, direct in enumerate(["<--", "-->"], start=1):
                    print(f"{i}. {direct}")
                print(f"{i + 1}. Go back to number selection.")

                direction = input("--> ")

                if direction == f"{i + 1}":
                    number_selection = True
                    break
                elif not direction in [str(n + 1) for n in range(i)]:
                    print(
                        "! Please type the number of the corresponding "
                        "direction the arrow is pointing to."
                    )
                    continue
                break
            if number_selection:
                continue
            else:
                break

        context = [
            "Gain 3 Knowledge for 7 Power",
            "Gain 2 Terraforming steps for 5 Power",
            "Gain 2 Ore for 4 Power",
            "Gain 7 Credits for 4 Power",
            "Gain 2 Knowledge for 4 Power",
            "Gain 1 Terraforming step for 3 Power",
            "Gain 2 Power Tokens for 3 Power",
            "Gain a technology tile for 4 Q.I.C",
            "Score one of your Federation Tokens again for 3 Q.I.C",
            "Gain 3 VP and 1 VP for every different planet type for 2 " \
            "Q.I.C."
        ]

        number = int(number)
        if direction == "1":
            i = 10
        else:
            i = 1
        # Keep looking for available actions until the amount of actions
        # checked is equal to the Numbered Selection number.
        while number:
            if research_board.pq_actions[i]:
                number -= 1
                if number == 0:
                    continue
            if direction == "1":
                i -= 1
                if i == 0:
                    i = 10
            else:
                i += 1
                if i == 11:
                    i =1
        else:
            research_board.pq_actions[i] = False

        print(f"The Automa has chosen the {context[i - 1]} Action.")

    def special(self):
        # Automa can't do a Special action.
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
                    print("! Please only type one of the available numbers.")
                    continue

        gp.passed += 1
        self.passed = True
        self.vp += scored_vp
        print(f"The Automa scored {scored_vp} VP for passing.")

        if round_number != 6:
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
    """Class for all faction specific parameters.

    For subclasses to override everything that differs.
    """
    def __init__(self):
        # Common properties of factions.
        self.name = False  # For subclasses to override!
        self.home_type = False  # For subclasses to override!

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
        # Options are (exactly as is): Terraforming, Navigation,
        # Artificial Intelligence, Gaia Project, Economy, Science
        self.start_research = False  # For subclasses to override if applicable

        # The cost of terraforming.
        # Example of Taklons:
        # self.terraform_tiers = {
        #     0: {"Swamp"},
        #     1: {"Gaia", "Desert", "Titanium"},
        #     2: {"Trans-dim", "Volcanic", "Ice"},
        #     3: {"Oxide", "Terra"}
        # }
        self.terraform_tiers = False  # For subclasses to override!

    def faction_action(self):
        # For subclasses to overwrite.
        raise NotImplementedError

    def mine_tiebreaker(self, gp, valid_options, automa):
        """Function for filtering planets based on faction action tiebreaker.

        This functions should be overridden by factions that employ a
        tiebreaker when placing a mine during the faction action.

        Args:
            gp: GaiaProject main game object.
            valid_options: List of planets for this function to filter.
            automa: Automa player object.
        """

        pass


class Taklons(Faction):

    def __init__(self):
        Faction.__init__(self)
        self.name = "Taklons"
        self.home_type = "Swamp"

        self.terraform_tiers = {
            0: {"Swamp"},
            1: {"Gaia", "Desert", "Titanium"},
            2: {"Trans-dim", "Volcanic", "Ice"},
            3: {"Oxide", "Terra"}
        }

    def faction_action(self, gp, automa):
        """Function for doing the Taklons Faction Action.

        Args:
            gp: GaiaProject main game object.
            automa: Automa object.
        """

        print(
            "\nAutoma will do his Faction Action. He will build a Mine with "
            "TIEBREAKER 3a: Shortest distance to one of YOUR planets,\n"
            "followed by a Power/Q.I.C. Action and he will gain 2 "
            "Victory Points."
        )

        try:
            automa.mine(gp, faction_action=3)
        except e.NotEnoughMinesError as ex:
            print(ex)
            automa.upgrade(gp)
        automa.pq(gp.research_board, faction_action=True)
        automa.vp += 2
        print("Automa has gained 2 Victory Points.")

    def mine_tiebreaker(self, gp, valid_options, automa):
        # From the valid_options, find out what the shortest distance
        # to the opponent is.
        closest_distance = automa.closest_distance_to_opponent(
            gp, valid_options
        )

        # Find all planets that are closest_distance from the opponent.
        valid_options = automa.closest_planets_to_opponent(
            gp, closest_distance, valid_options
        )
        return valid_options


def select_faction(faction):
    factions = {
        "taklons": Taklons
    }

    return factions[faction]


if __name__ == "__main__":
    test = Automa("Taklons", "Automa")
    print(type(test.faction).__name__)
