import random
from math import ceil

import constants as C
import exceptions as e
from faction import select_faction


class Player:

    def __init__(self, faction):
        """

        Args
            faction (str): name of a faction
                Options to choose from are:
                hadsch halla,
                TODO name all factions and possibly move the options elsewhere

        TODO:
            Implement charging power when opponents builds near me.
            Make every action choice possible to return to the action selection
                menu in case of accidentally choosing the wrong action or
                changing ones mind.
            Don't forget to look at boosters/technology for additional points
            for some actions.
            Find consistency in QIC qic or Q.I.C. or whatever.
            Boosters not completely finished yet.
        """

        self.faction = select_faction(faction.lower())()
        self.vp = 10
        self.standard_technology = []
        self.advanced_technology = []

        # This property is set during setup and when passing.
        self.booster = False

        self.empire = []  # List of owned planets
        self.federations = []  # List of federation tokens

        # List of trans-dim planets undergoing a gaia project.
        self.gaia_forming = []

        self.universe = False  # This property is set during setup

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

        self.passed = False  # Wether or not the player has passed.

    def start_mine(self, count, universe):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            f"Where whould you like to place your {count.upper()} "
            "mine?"
        )
        print(f"{faction_name}{question}")

        planet = self.choose_planet(universe, "start_mine")

        print(
            f"You have built a mine in sector {planet.sector[-1]} on the "
            f"{planet.type} planet."
        )
        planet.owner = self.faction.name
        planet.structure = "mine"
        self.faction.mine_built += 1
        self.faction.mine_max -= 1
        self.empire.append(planet)

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

    def income_phase(self):
        # TODO print everything that is gained from income?
        # TODO Never allow more than the maximium allowed of a resource.
        # For example: max credits is 30, max ore is 15
        print(f"\nDoing income for {self.faction.name}.")

        # Income from faction board.
        # Store income of type "power" and "powertoken" here to resolve the
        # order later.
        power_order = []

        # First look at the standard income that you are always going to get.
        self.resolve_income(self.faction.standard_income)

        # Second look at income from structures.
        # Ore from mines.
        for i, _ in enumerate(range(self.faction.mine_built)):
            self.faction.ore += self.faction.mine_income[i]

        # Credits from trading stations.
        for i, _ in enumerate(range(self.faction.trading_station_built)):
            self.faction.credits += self.faction.trading_station_income[i]

        # Knowledge from research labs.
        for i, _ in enumerate(range(self.faction.research_lab_built)):
            self.faction.credits += self.faction.research_lab_income[i]

        # Knowledge from academy.
        if self.faction.academy_income[0]:
            self.faction.knowledge += self.faction.academy_income[1]

        # Income from planetary_institute.
        if self.faction.planetary_institute_built == 1:
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
        levels = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science,
        ]

        for level in levels:
            # Error is corrected at runtime so i can ignore this.
            # pylint: disable=no-member
            if level.when == "income":
                power_order.extend(self.resolve_income(level.reward))

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
                    print(
                        "In what order do you want to gain these power "
                        "resources? Please type one number at a time."
                    )
                    for i, to_resolve in enumerate(power_order, start=1):
                        print(f"{i}. {to_resolve[:-1]} x{to_resolve[-1]}")

                    selection = input("--> ")
                    if selection in [
                        str(num + 1) for num in range(len(power_order))
                    ]:
                        if power_order[int(selection) - 1].startswith(
                            "powertoken"
                        ):
                            self.faction.bowl1 += (
                                int(power_order[int(selection) - 1][-1])
                            )
                        else:
                            self.charge_power(
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
                    self.charge_power(power_to_cycle)

        elif len(power_order) == 1:
            if power_order[0].startswith("powertoken"):
                self.faction.bowl1 += int(power_order[0][-1])
            else:
                self.charge_power(int(power_order[0][-1]))

    def resolve_income(self, incomes):
        """Give a player the resources gained from income.

        Args:
            incomes (list): A list with the income to be resolved. Format:
                ["credits3", "ore1", "knowledge1"].

        Returns:
            A list with all the power and power tokens gained where the order
            of gaining them still needs to be resolved if any power or
            powertokens were gained.

        TODO:
            Print everything gained like with power?
        """

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

    def charge_power(self, amount):
        """Amount of total power that will be cycled.

        Args:
            amount (int): Number of the power to be cycled.
        """

        charged = 0
        while amount:
            if self.faction.bowl1 > 0:
                self.faction.bowl1 -= 1
                self.faction.bowl2 += 1
            elif self.faction.bowl2 > 0:
                self.faction.bowl2 -= 1
                self.faction.bowl3 += 1
            else:
                break
            amount -= 1
            charged += 1
        print(f"{charged} Power has been charged.")

    def use_power(self, amount):
        for _ in range(amount):
            self.faction.bowl3 -= 1
            self.faction.bowl1 += 1

        print(f"You have used {amount} power.")

    def resolve_direct(self, rewards):
        if not isinstance(rewards, list):
            rewards = [rewards]

        for reward in rewards:
            if reward.startswith("powertoken"):
                self.faction.bowl1 += int(reward[-1])
            else:
                exec(f"self.faction.{reward[:-1]} += int({reward[-1]})")
            print(f"You have gained {reward[-1]} {reward[:-1]}.")

    def gaia_phase(self):
        # TODO untested function
        # TODO Faction incompatibility. Might not work with faction Itars,
        # Bal Tak's
        if self.faction.gaia_bowl > 0:
            self.faction.move_from_gaia_to_bowl()

            while self.gaia_forming:
                # Set the type property of the trans-dimensional planet to Gaia
                # as the gaia project is now completed.
                self.gaia_forming.pop().type = "Gaia"

            print("Your Trans-dimensional planets are now Gaia planets.")
            print(f"Power in gaia bowl: {self.faction.gaia_bowl}")
            print(f"Power in bowl 1: {self.faction.bowl1}")
            print(f"Power in bowl 2: {self.faction.bowl2}")
            print(f"Power in bowl 3: {self.faction.bowl3}")

    def action_phase(self, gp, rnd):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject class.
            rnd: Active Round object.

        TODO:
            Find consistency in iterating over all the options of something
            or not printing all the options again.
        """

        faction_name = f"\n{self.faction.name}:"
        intro = ("\nWhat action do you want to take?\n"
                 "Type the number of your action.\n")
        mine = "1. Build a mine.\n"
        gaia = "2. Start a gaia project.\n"
        upgrade = "3. Upgrade an existing structure.\n"
        federation = "4. Form a federation.\n"
        research = "5. Do research.\n"
        pq = "6. Power or Q.I.C (Purple/Green) action.\n"
        special = "7. Do a special (Orange) action.\n"
        pass_ = "8. Pass.\n"
        free = "9. Exchange power for resources. (Free action)\n"

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine, gp.universe, rnd],
            "2": [self.gaia, gp.universe],
            "3": [self.upgrade],
            "4": [self.federation],
            "5": [self.research, gp.research_board],
            "6": [self.pq, gp, rnd],
            "7": [self.special],
            "8": [self.pass_, gp],
            "9": [self.free]
        }

        print(faction_name)
        # Summary of resources
        print("Your resources are:")
        print(f"Victory points: {self.vp}")
        print(f"Credits: {self.faction.credits}")
        print(f"Ore: {self.faction.ore}")
        print(f"Knowledge: {self.faction.knowledge}")
        print(f"Qic: {self.faction.qic}")
        print(f"Gaia formers: {self.faction.gaiaformer}")
        print(f"Power in bowl 1: {self.faction.bowl1}")
        print(f"Power in bowl 2: {self.faction.bowl2}")
        print(f"Power in bowl 3: {self.faction.bowl3}")

        prompt = (
            f"{intro}{mine}{gaia}{upgrade}"
            f"{federation}{research}{pq}{special}{pass_}{free}--> "
        )

        while True:
            choice = input(prompt)

            if not choice in options.keys():
                print("Please type the action's corresponding number.")
                continue

            try:
                action = options[choice]
                if len(action) > 1:
                    # If the action function needs additional arguments,
                    # unpack the arguments from the options list.
                    action[0](*action[1:])
                else:
                    # Otherwise just call the function.
                    action[0]()
            except e.NoGaiaFormerError:
                print(
                    "You have no available Gaiaformers. Please pick a "
                    "different action."
                )
                continue
            except e.NotEnoughPowerTokensError:
                print(
                    "You don't have enough power tokens to do this "
                    "action. Please pick a different action."
                )
                continue
            except e.BackToActionSelection:
                # User chose to pick another action or wasn't able to pay for
                # some costs.
                continue
            except e.InsufficientKnowledgeError:
                print(
                    "You don't have enough knowledge to research. You "
                   f"currently have {self.faction.knowledge} knowledge. "
                    "Please choose a different action."
                )
                continue
            else:
                return

    def choose_planet(self, universe, action):
        """Function for choosing a planet on the board.

        Args:
            universe: The universe object used in the main GaiaProject class.
            action (str): The action that you are calling this function from.

        TODO:
            This function doesn't work with the lantids function when building
            a mine since it won't show planets that are owned by opponents.
        """

        # more players TODO only for 2p right now
        back_to_action = "Type 8 if you want to choose a different action."
        choose_range = "1-8"
        if action == "start_mine":
            back_to_action = ""
            choose_range = "1-7"
        while True:
            sector = (
                "Please type the number of the sector your chosen planet "
                f"is in. {back_to_action}\n--> "
            )
            sector_choice = input(sector)

            if sector_choice == "8" and not action == "start_mine":
                raise e.BackToActionSelection

            if not sector_choice in C.SECTORS_2P:
                # More players TODO make this message dynamic to the board.
                # If playing with more players it would be 1-10 for example.
                print(f"Please only type {choose_range}.")
                continue

            # Choose a planet.
            while True:
                try:
                    planets = universe.valid_planets(
                        self, int(sector_choice), action
                    )
                except e.NoValidMinePlanetsError:
                    break

                # If there is only one valid planet, return that planet.
                if len(planets) == 1:
                    return planets[0]

                # If there are multiple valid planets, choose one.
                print("Please type your chosen planet's corresponding number.")
                for i, pt in enumerate(planets, start=1):
                    print(f"{i}. {pt}")
                print(f"{i + 1}. Go back to sector selection.")

                chosen_planet = input("--> ")
                if chosen_planet in [str(n + 1) for n in range(i)]:
                    planet = planets[int(chosen_planet) - 1]
                    return planet
                elif chosen_planet == f"{i + 1}":
                    break
                else:
                    print("Please only type one of the available numbers.")
                    continue

    def mine(self, universe, rnd, terraform_steps=False, action="mine"):
        # TODO how to deal with power charging??
        # TODO Some tech tiles give some points on building a mine same with
        # round tiles.

        # Check if the player has enough resources to pay for the mine.
        if not self.faction.credits >= 2 and not self.faction.ore >= 1:
            print(
                f"You don't have enough credits ({self.faction.credits}) "
                f"or ore ({self.faction.ore}) to build a mine. Building a mine"
                " costs 2 credits and 1 ore."
            )
            raise e.BackToActionSelection

        print("\nOn what planet do you want to build a mine?")
        while True:
            # Payment flags
            pay_range_qic = False
            pay_gaia_qic = False
            pay_terraform_ore = False

            planet = self.choose_planet(universe, action)

            # If this function was called from the pq action function, check
            # if a planet that needs terraforming was actually chosen.
            # I think you MUST place on a planet that can be terraformed, but
            # i am not sure. For now it will be like this.
            if (
                terraform_steps
                and planet.type == self.faction.home_type
                and not planet.type in C.home_types
            ):
                print(
                    "When you gain terraform steps, you MUST build a mine on "
                    "a planet that has to be terraformed. Please choose a "
                    "different planet type."
                )
                continue

            # Check if the player is within range of the target planet.
            not_enough_range = False
            all_distances = []
            for owned_planet in self.empire:
                startx = owned_planet.location[0]
                starty = owned_planet.location[1]

                targetx = planet.location[0]
                targety = planet.location[1]

                distance = universe.distance(startx, starty, targetx, targety)
                all_distances.append(distance)

                # If the distance of the planet to one of the players planets
                # is ever smaller or equal to the amount of range the player
                # has, the planet is close enough.
                # Error is corrected at runtime so i can ignore this.
                # pylint: disable=no-member
                if distance <= self.navigation.active:
                    break
            else:
                distance = min(all_distances)
                not_enough_range = True

            if not_enough_range:
                # Error is corrected at runtime so i can ignore this.
                # pylint: disable=no-member
                extra_range_needed = distance - self.navigation.active
                qic_needed = ceil(extra_range_needed / 2)

                # Check if player has the required amount of qic needed to
                # increase the range enough.
                if qic_needed > self.faction.qic:
                    print(
                        "You don't have enough range "
                       f"({self.navigation.active}) to build on your chosen "
                        "planet and you don't have enough QIC "
                       f"({self.faction.qic}) to increase your range."
                    )
                    continue

                # Check if the player is building on a gaia planet and if
                # he/she has enough qic to increase the range AND pay a qic for
                # building on a gaia planet type.
                if planet.type == "Gaia" and not self.faction.qic > qic_needed:
                    print(
                       f"You don't have enough QIC ({self.faction.qic}) to "
                       "increase your range AND build on a gaia planet. "
                       "Please choose a different planet."
                    )
                    continue

                if qic_needed == 1:
                    QIC = "QIC"
                else:
                    QIC = "QIC's"
                print(
                    "Your nearest planet is not within range of your chosen "
                   f"planet. Do you want to spend {qic_needed} {QIC} to "
                    "increase your range? (Y/N)"
                )

                dont_increase_range = False
                while True:
                    increase_range = input("--> ").lower()

                    if not increase_range in ['y', 'n']:
                        print("Please type Y for yes or N for no.")
                        continue
                    elif increase_range == "n":
                        dont_increase_range = True
                        break
                    else:
                        break

                if dont_increase_range:
                    continue

                # Player wants to pay QIC.
                pay_range_qic = qic_needed

            if planet.type in ["Gaia"]:
                # TODO faction compatibility this function doesn't work for the
                # gleens faction as they pay ore to build on gaia planets
                qic_storage = self.faction.qic
                if pay_range_qic:
                    qic_storage -= pay_range_qic

                if not qic_storage > 0:
                    print(
                        "You don't have a QIC to build on a Gaia planet. "
                        "Please choose a different type of planet."
                    )
                    continue

                if qic_storage == 1:
                    QIC = "QIC"
                else:
                    QIC = "QIC's"
                print(
                    "To build a mine on this planet, you need to pay 1 QIC. "
                   f"You now have {qic_storage} {QIC}. Use a QIC? (Y/N)"
                )

                choose_another_planet = False
                while True:
                    pay_qic = input("--> ").lower()

                    if not pay_qic in ['y', 'n']:
                        print("Please type Y for yes or N for no.")
                        continue
                    elif pay_qic == "n":
                        choose_another_planet = True
                        break
                    else:
                        break

                if choose_another_planet:
                    continue

                # Player wants to pay QIC.
                pay_gaia_qic = True

                # Check if the current round awards points for building a mine
                # on a Gaia planet.
                if rnd.goal == "gaiamine":
                    self.resolve_direct(f"vp{rnd.vp}")
                    print(
                        f"Because of the round you have gained {rnd.vp} "
                        "victory points."
                    )

            elif planet.type in ["Trans-dim"]:
                print(
                    "To build a mine on this planet, you first need turn this "
                    "planet into a Gaia planet with the Gaia Project action. "
                    "Please choose a different type of planet."
                )
                continue

            # Check if the player needs to first terraform the planet.
            elif self.faction.home_type != planet.type:
                start = C.home_types.index(self.faction.home_type)
                target = planet.type
                i = start + 1
                # difficulty == amount of terraform steps.
                difficulty = 0
                for difficulty in range(1, 4):
                    if i > 6:
                        i = 0
                    if C.home_types[start - difficulty] == target \
                        or C.home_types[i] == target:
                        break
                    i += 1

                # If the player got enough terraform_steps already
                # without paying ore for them, he/she doesn't have to pay
                # anything so go straight to building the mine.
                free_terraform = False
                if terraform_steps:
                    total = difficulty - terraform_steps
                    if total < 1:
                        free_terraform = True

                choose_another_planet = False
                if not free_terraform:
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    terraform_cost = (
                        self.terraforming.active
                        * (difficulty - terraform_steps)
                    )
                    # self.faction.ore - 1 to check if the terraform cost can
                    # be payed in addition to the ore cost of the mine.
                    if self.faction.ore - 1 < terraform_cost:
                        print(
                            "You don't have enough ore to pay the "
                            "terraforming cost needed to terraform this planet"
                            f" ({terraform_cost} ore). "
                            "Please choose a different type of planet."
                        )
                        continue

                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    print(
                        "To build a mine on this planet, you need to terraform"
                        f" it first. Terraforming will cost {terraform_cost} "
                        f"ore. You now have {self.faction.ore} ore. Do you "
                        f"want to pay {terraform_cost} ore? (Y/N)"
                    )

                    while True:
                        pay_terraform_cost = input("--> ").lower()

                        if not pay_terraform_cost in ['y', 'n']:
                            print("Please type Y for yes or N for no.")
                            continue
                        elif pay_terraform_cost == "n":
                            choose_another_planet = True
                            break
                        else:
                            # Player wants to pay terraforming cost.
                            # TODO check if the ore is now not reduced when
                            # terraforming is free.
                            pay_terraform_ore = True
                            break

                if choose_another_planet:
                    continue


                # Check if the current round awards points for terraforming.
                # TODO check if i get 2 terraform steps, but i only use 1, that
                # it only gives me points for the 1 step if points are awarded
                # that round.
                if rnd.goal == "terraforming":
                    self.resolve_direct(f"vp{rnd.vp * difficulty}")
                    print(
                        "Because of the round you have gained "
                        f"{rnd.vp * difficulty} victory points."
                    )
            break

        print(
            f"You have built a mine in sector {planet.sector[-1]} on the "
            f"{planet.type} planet."
        )
        # Apply the various payment options.
        if pay_range_qic:
            self.faction.qic -= pay_range_qic
        if pay_gaia_qic:
            self.faction.qic -= 1
        if pay_terraform_ore:
            # Error is corrected at runtime so i can ignore this.
            # pylint: disable=no-member
            self.faction.ore -= (difficulty - terraform_steps) \
                * self.terraforming.active

        planet.owner = self.faction.name
        planet.structure = "mine"
        self.faction.credits -= 2
        self.faction.ore -= 1
        self.faction.mine_built += 1
        self.faction.mine_max -= 1
        self.empire.append(planet)

    def gaia(self, universe):
        # Check if the player has an available gaiaformer.
        if not self.faction.gaiaformer > 0:
            raise e.NoGaiaFormerError

        # Error is corrected at runtime so i can ignore this.
        # pylint: disable=no-member
        # Check if the player has enough powertokens to do a gaia project.
        if not self.faction.count_powertokens() >= self.gaia_project.active:
            raise e.NotEnoughPowerTokensError

        print("\nYou want to start a Gaia Project.")
        while True:
            # Payment flag
            pay_range_qic = False

            planet = self.choose_planet(universe, "gaia")

            # Check if the player is within range of the target planet.
            not_enough_range = False
            all_distances = []
            for owned_planet in self.empire:
                startx = owned_planet.location[0]
                starty = owned_planet.location[1]

                targetx = planet.location[0]
                targety = planet.location[1]

                distance = universe.distance(startx, starty, targetx, targety)
                all_distances.append(distance)

                # If the distance of the planet to one of the players planets
                # is ever smaller or equal to the amount of range the player
                # has, the planet is close enough.
                # Error is corrected at runtime so i can ignore this.
                # pylint: disable=no-member
                if distance <= self.navigation.active:
                    break
            else:
                distance = min(all_distances)
                not_enough_range = True

            if not_enough_range:
                # Error is corrected at runtime so i can ignore this.
                # pylint: disable=no-member
                extra_range_needed = distance - self.navigation.active
                qic_needed = ceil(extra_range_needed / 2)

                # Check if player has the required amount of qic needed to
                # increase the range enough.
                if qic_needed > self.faction.qic:
                    print(
                        "You don't have enough range "
                        f"({self.navigation.active}) to build on your chosen "
                        "planet and you don't have enough QIC "
                        f"({self.faction.qic}) to increase your range."
                    )
                    continue

                # TODO Untested!!!!
                # Check if the player is building on a gaia planet and if
                # he/she has enough qic to increase the range AND pay a qic for
                # building on a gaia planet type.
                if planet.type == "Gaia" and not self.faction.qic > qic_needed:
                    print(
                        f"You don't have enough QIC ({self.faction.qic}) to "
                        "increase your range AND build on a gaia planet. "
                        "Please choose a different planet."
                    )
                    continue

                if qic_needed == 1:
                    QIC = "QIC"
                else:
                    QIC = "QIC's"
                print(
                    "Your nearest planet is not within range of your chosen "
                    f"planet. Do you want to spend {qic_needed} {QIC} to "
                    "increase your range? (Y/N)"
                )

                dont_increase_range = False
                while True:
                    increase_range = input("--> ").lower()

                    if not increase_range in ['y', 'n']:
                        print("Please type Y for yes or N for no.")
                        continue
                    elif increase_range == "n":
                        dont_increase_range = True
                        break
                    else:
                        break

                if dont_increase_range:
                    continue

                # Player wants to pay QIC.
                pay_range_qic = qic_needed
            break

        # Deduct the power and put it in the gaia_bowl
        for _ in range(self.gaia_project.active):
            # Prioritise taking from the lowest bowl as i don't see why
            # it would ever be better to not do that.
            if self.faction.bowl1 > 0:
                self.faction.bowl1 -= 1
                self.faction.gaia_bowl += 1
            elif self.faction.bowl2 > 0:
                self.faction.bowl2 -= 1
                self.faction.gaia_bowl += 1
            elif self.faction.bowl3 > 0:
                self.faction.bowl3 -= 1
                self.faction.gaia_bowl += 1

        print(
            f"You have started a gaia project in sector "
            f"{planet.sector[-1]} on the {planet.type} planet."
        )

        # Apply paying for range if applicable.
        if pay_range_qic:
            self.faction.qic -= pay_range_qic

        planet.owner = self.faction.name
        planet.structure = "gaiaformer"
        self.gaia_forming.append(planet)
        self.faction.gaiaformer -= 1

    def upgrade(self):
        # TODO Check if the current round awards points for upgrading to
        # trading center.
        pass

    def federation(self):
        pass

    def research(self, research_board):
        # Check if the player has enough knowledge to research.
        # Researching costs 4 knowledge.
        if not self.faction.knowledge > 3:
            raise e.InsufficientKnowledgeError

        levels = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science,
        ]

        print("\nOn what research track do you want to go up?")
        print(research_board)
        options = (
            "Please type the corresponding number or type 7 if you changed "
            "your mind:\n"
        )
        while True:
            answer = input(f"{options}--> ")

            if not answer in ["1", "2", "3", "4", "5", "6"]:
                if answer == "7":
                    raise e.BackToActionSelection
                print("Please only type 1-7")
                continue

            answer = int(answer)
            current_level = levels[answer - 1]
            try:
                research_board.tech_tracks[answer - 1] \
                    .research(current_level, self, answer - 1)
            except e.NoFederationTokensError:
                print(
                    "You have no federation tokens. You can't go up on this "
                    "track. Please choose another."
                )
                continue
            except e.NoFederationGreenError:
                print(
                    "You have no federation token with the green side up left."
                    " You can't go up on this track. Please choose another."
                )
                continue
            except e.NoResearchPossibleError:
                print(
                    "You are already at the maximum level of 5. Please choose "
                    "a different track."
                )
            except e.Level5IsFullError:
                print(
                    "Another player is already on level 5. Only one person can"
                    " go to level 5. Please choose a different track."
                )
                continue
            else:
                print(
                    f"You have researched "
                    f"{research_board.tech_tracks[answer - 1].name}."
                )
                self.faction.knowledge -= 4
                print(research_board)
                return

    def enough_power(self, amount):
        # Check if there is enough power in bowl 3.
        if not self.faction.bowl3 >= amount:
            print(
                "You don't have enough power to do this action. "
                "Please choose a different action."
            )
            return False
        return True

    def enough_qic(self, amount):
        # Check the player has enough qic's
        if not self.faction.qic >= amount:
            print(
                "You don't have enough qic's to do this action. "
                "Please choose a different action."
            )
            return False
        return True

    def pq_availabe(self, research_board, num):
        # Check if the action is still available.
        if not research_board.pq_actions[num]:
            print(
                "This power action is already used this round. "
                "Please choose a different action."
            )
            return False
        return True


    def pq(self, gp, rnd):
        """Power and Qic action function.

        Args:
            gp: GaiaProject class.
            rnd: Active Round object.

        TODO:
            Perhaps make the power/qic cost more readable.
        """

        intro = (
            "\nYou want to take a power or qic action. Type the number of "
            "your action."
        )
        power = "Power:\n"
        knowledge3 = "1. Gain 3 knowledge for 7 power.\n"
        terraform2 = "2. Gain 2 terraforming steps for 5 power.\n"
        ore2 = "3. Gain 2 ore for 4 power.\n"
        credits7 = "4. Gain 7 credits for 4 power.\n"
        knowledge2 = "5. Gain 2 knowledge for 4 power.\n"
        terraform1 = "6. Gain 1 terraforming step for 3 power.\n"
        powertoken2 = "7. Gain 2 powertokens for 3 power.\n"
        qic = "Qic:\n"
        tech_tile = "8. Gain a tech tile.\n"
        score_fed_token = "9. Score one of your federation tokens again.\n"
        vp_for_ptypes = (
            "10. Gain 3 vp and 1 vp for every different planet type.\n"
        )
        cancel = "11. Pick a different action.\n"

        print(f"{intro}")

        while True:
            action = input(
                f"{power}{knowledge3}{terraform2}{ore2}{credits7}"
                f"{knowledge2}{terraform1}{powertoken2}{qic}{tech_tile}"
                f"{score_fed_token}{vp_for_ptypes}{cancel}--> "
            )

            if action == "11":
                raise e.BackToActionSelection
            elif not action in [str(act) for act in range(1, 11)]:
                print("Please type the action's corresponding number.")
                continue

            # Check if the action is available
            if not self.pq_availabe(gp.research_board, int(action)):
                continue

            if action == "1":
                # Gain 3 knowledge for 7 power.

                if not self.enough_power(7):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(7)
                self.resolve_direct("knowledge3")

            elif action == "2":
                # Gain 2 terraforming steps for 5 power and build a mine.

                if not self.enough_power(5):
                    continue

                try:
                    self.mine(gp.universe, rnd, 2, "pq")
                except e.BackToActionSelection:
                    # Players want to do a different pq action.
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(5)

            elif action == "3":
                # Gain 2 ore for 4 power.

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(4)
                self.resolve_direct("ore2")

            elif action == "4":
                # Gain 7 credits for 4 ore.

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(4)
                self.resolve_direct("credits7")

            elif action == "5":
                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(4)
                self.resolve_direct("knowledge2")

            elif action == "6":
                # Gain 1 terraforming step for 3 power and build a mine.

                if not self.enough_power(3):
                    continue

                try:
                    self.mine(gp.universe, rnd, 2, "pq")
                except e.BackToActionSelection:
                    # Player want to do a different pq action.
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(3)

            elif action == "7":
                # Gain 2 powertokens for 3 power.

                if not self.enough_power(3):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(3)
                self.resolve_direct("powertokens2")

            elif action == "8":
                # TODO need to implement technology tile gain.
                # Gain a technology tile for 4 qic's.

                if not self.enough_qic(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                # TODO pay qic

            elif action == "9":
                # Re-score a federation token in the players possession.

                if not self.enough_qic(3):
                    continue

                if not self.federations:
                    print(
                        "You don't have any federation tiles to score again. "
                        "Please choose a different action."
                    )
                    continue

                print(
                    "Please type the number of the federation token you "
                    "would like to score again."
                )
                for i, token in enumerate(self.federations, start=1):
                    print(f"{i}. {token}")
                print(f"{i + 1}. Go back to action selection.")

                while True:
                    chosen_token = input("--> ")
                    if not chosen_token in [str(n + 1) for n in range(i)]:
                        print("Please only type one of the available numbers.")
                    elif chosen_token == f"{i + 1}":
                        break

                # TODO test that this resolves federation tokens correctly.
                self.resolve_direct(self.federations[int(chosen_token) - 1])
                # TODO pay qic

            elif action == "10":
                # Gain 3 vp and 1 point for every unique planet type that you
                # own.

                if not self.enough_qic(2):
                    continue

                types = len({planet.type for planet in self.empire})

                self.resolve_direct(f"vp{3 + types}")
                # TODO pay qic

            return

    def special(self):
        pass

    def pass_(self, gp):
        # TODO if it is the last round, you don't have to pick a booster
        gp.passed += 1
        self.passed = True
        print("You Pass.")
        return

        # TODO FINAL Wait with this for now
        if self.booster.vp:
            # TODO Make every booster it's own class to handle the vp gain when
            # passing? Do the same for researchh tiles??
            pass


        print("Which booster would you like to pick?")
        while True:
            for x, booster in enumerate(gp.scoring_board.boosters, start=1):
                print(f"{x}. {booster}")

            choice = input(f"--> ")

            if choice in (
                [str(num + 1) for num in range(len(gp.scoring_board.boosters))]
            ):
                self.booster = gp.scoring_board.boosters.pop(int(choice) - 1)
                print(f"You chose {self.booster}.")
                return
            else:
                print("Please only type one of the available numbers.")

    def free(self):
        pass


if __name__ == "__main__":
    test = Player("hadsch halla")
    print(test.faction.home_type)
