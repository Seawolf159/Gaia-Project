from math import ceil

import constants as C
import exceptions as e
from faction import select_faction
from technology import AdvancedTechnology, StandardTechnology


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
        self.covered_standard_technology = []
        self.advanced_technology = []

        # This property is set during setup and when passing.
        self.booster = False

        self.empire = []  # List of owned planets
        self.federations = []  # List of federation tokens

        # List of trans-dim planets undergoing a gaia project.
        self.gaia_forming = []

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

        self.passed = False  # Wether or not the player has passed.

        # TODO CRITICAL remove when game is done.
        # Initiate testing parameters
        self.faction._testing()

    def start_mine(self, count, universe):
        faction_name = f"\n{self.faction.name}:\n"
        question = (
            f"Where whould you like to place your {count.upper()} "
            "mine?"
        )
        print(f"{faction_name}{question}")

        planet = self.choose_planet(universe, "start_mine")

        print(
            f"You have built a mine in sector {planet.sector} on the "
            f"{planet.type} planet."
        )
        planet.owner = self.faction.name
        planet.structure = "Mine"
        self.faction.mine_built += 1
        self.empire.append(planet)

    def choose_booster(self, scoring_board):
        faction_name = f"\n{self.faction.name}:\n"
        question = "Which booster would you like to pick?"
        print(f"{faction_name}{question}")

        for x, booster in enumerate(scoring_board.boosters, start=1):
            print(f"{x}. {booster}")
        while True:
            choice = input(f"--> ")

            if choice in (
                [str(num + 1) for num in range(len(scoring_board.boosters))]
            ):
                self.booster = scoring_board.boosters.pop(int(choice) - 1)
                print(f"You chose {self.booster}.")
                return
            else:
                print("Please only type one of the available numbers.")

    def resolve_gain(self, gains, reason=""):
        """Function for resolving all resources that are gained.

        Args:
            gains (list): List of resources that are directly gained. Format:
                ["credits3", "vp2", "knowledge1"]
            reason (str): String specifying why something was gained.
                f"{reason} you have gained...."
        """

        # If gains is not a list and therefore a single income, put that
        # single income in a list to not iterate over a string instead. For
        # example if gains == "ore2" the iteration below would fail so
        # correct it like so: gains = ["ore2"]
        if not isinstance(gains, list):
            gains = [gains]

        power_order = []

        text = " you have gained "
        if not reason:
            text = "You have gained "

        # Add up all of the types of income. "knowledge, vp, powertoken" etc.
        # and add them at the same time.
        types_of_gain = {}
        for gain in gains:
            if gain.startswith("power"):
                power_order.append(gain)
                print(f"{reason}{text}{gain[-1]} {gain[:-1]}.")
            elif gain.startswith("vp"):
                # Had to do this because if a double digit integer was rewarded
                # like vp12 for example, it would break my [-1] functionality.
                if not "vp" in types_of_gain:
                    types_of_gain["vp"] = int(gain.lstrip("vp"))
                else:
                    types_of_gain["vp"] += int(gain.lstrip("vp"))
            elif not gain[:-1] in types_of_gain:
                types_of_gain[gain[:-1]] = int(gain[-1])
            else:
                types_of_gain[gain[:-1]] += int(gain[-1])

        for added_up_gain, amount in types_of_gain.items():
            if added_up_gain == "vp":
                exec(f"self.{added_up_gain} += {amount}")
            else:
                # Check if adding the Credits, Ore or Knowledge, doesn't make
                # the player go over the limit.
                if added_up_gain == "credits":
                    if self.faction.credits \
                            + amount > self.faction.credits_max:
                        if self.faction.credits > self.faction.credits_max:
                            continue
                        amount = 0
                elif added_up_gain == "ore":
                    if self.faction.ore + amount > self.faction.ore_max:
                        if self.faction.ore > self.faction.ore_max:
                            continue
                        amount = 0
                elif added_up_gain == "knowledge":
                    if self.faction.knowledge + amount \
                            > self.faction.knowledge_max:
                        if self.faction.knowledge > self.faction.knowledge_max:
                            continue
                        amount = 0
                exec(f"self.faction.{added_up_gain} += {amount}")
            if not amount == 0:
                print(f"{reason}{text}{amount} {added_up_gain}.")

        if power_order:
            self.resolve_power_order(power_order)

    def resolve_power_order(self, power_order):
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

                        # Check if there is only one type of power left. If
                        # there is, just resolve the rest automatically.
                        power = 0
                        token = 0
                        for gain in power_order:
                            if gain.startswith("powertoken"):
                                token += 1
                            else:
                                power += 1
                        if power == 0 or token == 0:
                            while power_order:
                                power_to_cycle = 0
                                for resolved in power_order:
                                    if resolved.startswith("powertoken"):
                                        self.faction.bowl1 += int(resolved[-1])
                                    else:
                                        power_to_cycle += int(resolved[-1])

                                if power_to_cycle:
                                    self.charge_power(power_to_cycle)
                                power_order.pop()
                    else:
                        print("Please only type one of the available numbers.")
                        continue
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

        print(f"You have spent {amount} power.")

    def income_phase(self):
        # TODO Never allow more than the maximium allowed of a resource.
        # TODO get all income into one list and than call the self.resolve_gain
        # function.
        # For example: max credits is 30, max ore is 15
        print(f"\nDoing income for {self.faction.name}.")

        # Income from faction board.
        # Store income of type "power" and "powertoken" here to resolve the
        # order later.

        total_income = []
        # First look at the standard income that you are always going to get.
        total_income.extend(self.faction.standard_income)
        # Second look at income from structures.
        # Ore from mines.
        ore = 0
        for i, _ in enumerate(range(self.faction.mine_built)):
            ore += self.faction.mine_income[i]
        total_income.append(f"ore{ore}")

        # Credits from trading stations.
        credits_ = 0
        for i, _ in enumerate(range(self.faction.trading_station_built)):
            credits_ += self.faction.trading_station_income[i]
        total_income.append(f"credits{credits_}")

        # Knowledge from research labs.
        knowledge_rl = 0
        for i, _ in enumerate(range(self.faction.research_lab_built)):
            knowledge_rl += self.faction.research_lab_income[i]
        total_income.append(f"knowledge{knowledge_rl}")

        # Knowledge from academy.
        knowledge_a = 0
        if self.faction.academy_income[0]:
            knowledge_a += self.faction.academy_income[1]
        total_income.append(f"knowledge{knowledge_a}")

        # Income from planetary_institute.
        if self.faction.planetary_institute_built == 1:
            total_income.extend(self.faction.planetary_institute_income)

        # Third look at income from booster.
        if self.booster.income1:
            total_income.append(self.booster.income1)
        if self.booster.income2:
            total_income.append(self.booster.income2)

        # Fourth look at income from standard technology
        for technology in self.standard_technology:
            if technology.when == "income":
                if isinstance(technology.reward, list):
                    total_income.extend(technology.reward)
                else:
                    total_income.append(technology.reward)

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
                if isinstance(level.reward, list):
                    total_income.extend(level.reward)
                else:
                    total_income.append(level.reward)

        self.resolve_gain(total_income)

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

    def action_phase(self, gp, rnd, choice=False):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject class.
            rnd: Active Round object.

        TODO:
            Find consistency in iterating over all the options of something
            or not printing all the options with every loop.
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
        free = "9. Exchange power for resources. (Free action)"

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine, gp.universe, rnd],
            "2": [self.gaia, gp.universe],
            "3": [self.upgrade, gp, rnd],
            "4": [self.federation, gp, rnd],
            "5": [self.research, gp.research_board, rnd, gp.universe],
            "6": [self.pq, gp, rnd],
            "7": [self.special],
            "8": [self.pass_, gp, rnd],
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
            f"{federation}{research}{pq}{special}{pass_}{free}"
        )

        # Prompt repeat is set when an exception was raised somewhere and the
        # user got back to action selection.
        prompt_repeat = False
        print(prompt)

        while True:
            if prompt_repeat and choice == "0":
                print(prompt)

            if not choice or choice == "0":
                choice = input("--> ")

            if not choice in options.keys():
                print("Please type the action's corresponding number.")
                choice = "0"
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
                prompt_repeat = True
                choice = "0"
                continue
            except e.NotEnoughPowerTokensError:
                print(
                    "You don't have enough power tokens to do this "
                    "action. Please pick a different action."
                )
                prompt_repeat = True
                choice = "0"
                continue
            except e.BackToActionSelection as back:
                # User chose to pick another action or wasn't able to pay for
                # some costs.
                choice = back.choice
                prompt_repeat = True
                continue
            except e.InsufficientKnowledgeError:
                print(
                    "You don't have enough knowledge to research. You "
                    f"currently have {self.faction.knowledge} knowledge. "
                    "Please choose a different action."
                )
                prompt_repeat = True
                choice = "0"
                continue
            else:
                return

    def mine(self, universe, rnd, terraform_steps=False, action="mine"):
        # TODO how to deal with power charging??
        # TODO Some tech tiles give some points on building a mine same with
        # round tiles.

        # Check if the player has any mines left.
        if self.faction.mine_built == self.faction.mine_max:
            print(
                "You don't have any more mines left to build. Please choose a "
                "different action."
            )
            raise e.BackToActionSelection

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
                        "planet and you don't have enough Q.I.C. "
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
                    QIC = "Q.I.C."
                else:
                    QIC = "Q.I.C.'s"
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

            if planet.type == "Gaia":
                # TODO faction compatibility this function doesn't work for the
                # gleens faction as they pay ore to build on gaia planets
                qic_storage = self.faction.qic
                if pay_range_qic:
                    qic_storage -= pay_range_qic

                if not qic_storage > 0:
                    print(
                        "You don't have a Q.I.C. to build on a Gaia planet. "
                        "Please choose a different type of planet."
                    )
                    continue

                if qic_storage == 1:
                    QIC = "Q.I.C."
                else:
                    QIC = "Q.I.C.'s"
                print(
                    "To build a mine on this planet, you need to pay 1 Q.I.C. "
                   f"You now have {qic_storage} {QIC}. Use a Q.I.C.? (Y/N)"
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
                    reason = "Because of the round"
                    self.resolve_gain(f"vp{rnd.vp}", reason)

                # Check if the player has the standard tech tile that grants
                # points for building a mine on a gaia planet type.
                if self.standard_technology:
                    for tile in self.standard_technology:
                        if tile.when == "action mine on gaia":
                            reason = "Because of a standard technology tile"
                            self.resolve_gain(tile.reward, reason)

            elif planet.type == "Trans-dim":
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
                # difficulty == amount of total terraform steps needed.
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
                if rnd.goal == "terraforming":
                    reason = "Because of the round"
                    self.resolve_gain(f"vp{rnd.vp * difficulty}", reason)
            break

        print(
            f"You have built a mine in sector {planet.sector} on the "
            f"{planet.type} planet."
        )

        # Check if the current round awards points for building a mine.
        if rnd.goal == "mine":
            reason = "Because of the round"
            self.resolve_gain(f"vp{rnd.vp}", reason)

        # Check if the player has the advanced tech tile that grants points for
        # building a mine.
        if self.advanced_technology:
            for tile in self.advanced_technology:
                if tile.when == "live" and tile.effect == "mine":
                    reason = "Because of an advanced technology tile"
                    self.resolve_gain(tile.reward, reason)

        # Apply the various payment options.
        if pay_range_qic:
            self.faction.qic -= pay_range_qic
        if pay_gaia_qic:
            self.faction.qic -= 1
        if pay_terraform_ore:
            # Error is corrected at runtime so i can ignore this.
            # pylint: disable=no-member
            self.faction.ore -= self.terraforming.active \
                * (difficulty - terraform_steps)

        planet.owner = self.faction.name
        planet.structure = "Mine"
        self.faction.credits -= 2
        self.faction.ore -= 1
        self.faction.mine_built += 1
        self.empire.append(planet)

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

        sector = (
            "Please type the number of the sector your chosen planet "
            f"is in. {back_to_action}\n--> "
        )
        while True:
            sector_choice = input(sector)

            if sector_choice == "8" and not action == "start_mine":
                raise e.BackToActionSelection

            if not sector_choice in C.SECTORS_2P:
                # More players TODO make this message dynamic to the board.
                # If playing with more players it would be 1-10 for example.
                print(f"Please only type {choose_range}.")
                continue

            # Choose a planet.
            try:
                planets = universe.valid_planets(
                    self, int(sector_choice), action
                )
            except e.NoValidMinePlanetsError:
                continue

            # If there is only one valid planet, return that planet.
            if len(planets) == 1:
                return planets[0]

            # If there are multiple valid planets, choose one.
            print("Please type your chosen planet's corresponding number.")
            for i, pt in enumerate(planets, start=1):
                print(f"{i}. {pt}")
            print(f"{i + 1}. Go back to sector selection.")

            while True:
                chosen_planet = input("--> ")
                if chosen_planet in [str(n + 1) for n in range(i)]:
                    planet = planets[int(chosen_planet) - 1]
                    return planet
                elif chosen_planet == f"{i + 1}":
                    break
                else:
                    print("Please only type one of the available numbers.")
                    continue

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
                        "planet and you don't have enough Q.I.C. "
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
                    QIC = "Q.I.C."
                else:
                    QIC = "Q.I.C.'s"
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
            f"{planet.sector} on the {planet.type} planet."
        )

        # Apply paying for range if applicable.
        if pay_range_qic:
            self.faction.qic -= pay_range_qic

        planet.owner = self.faction.name
        planet.structure = "gaiaformer"
        self.gaia_forming.append(planet)
        self.faction.gaiaformer -= 1

    def resolve_technology_tile(self, research_board, rnd, universe, pq=False):
        available = []
        for track in research_board.tech_tracks:
            # Check for available standard technology tiles connected to a
            # technology track.
            if track.standard not in (
                self.standard_technology
                or self.covered_standard_technology
            ):
                available.append(track.standard)

            # TODO MINOR filter out the advanced tiles if the player has no
            # federation tokens with the green side up left. ??
            # Check if the player is able to go for any advanced technology
            # tiles.
            if (
                self.faction.name in track.level4.players
                or self.faction.name in track.level5.players
            ):
                available.append(track.advanced)

        # Check for available standard technology tiles unconnected to a
        # technology track.
        for tile in research_board.free_standard_technology:
            if tile not in (
                self.standard_technology
                or self.covered_standard_technology
            ):
                available.append(tile)

        # Ask the player which of the available tiles they want to pick.
        print(
            "You may now select a technology tile. Please type one of the "
            "numbers."
        )
        abort = "Choose a different structure."
        if pq:
            abort = "Choose a different Power/ Q.I.C. action."
        choose_another = False
        while True:
            for i, tile in enumerate(available, start=1):
                print(f"{i}. {tile}")
            print(f"{i + 1}. {abort}")

            chosen_tile = input("--> ")
            if chosen_tile in [str(n + 1) for n in range(i)]:
                selected_tile = available[int(chosen_tile) - 1]
            elif chosen_tile == f"{i + 1}":
                if pq:
                    raise e.BackToActionSelection("6")
                else:
                    raise e.BackToActionSelection("3")
            else:
                print("Please only type one of the available numbers.")
                continue

            if isinstance(selected_tile, AdvancedTechnology):
                # Check that the player has any standard technology available.
                if not self.standard_technology:
                    print(
                        "To take an advanced technology, you need to have a "
                        "standard technology available to place your advanced "
                        "technology tile on. Please choose a different tile."
                    )
                    continue

                # Check if the player has a federation token with the green
                # side up.
                if not "green" in [fed.state for fed in self.federations]:
                    print(
                        "You need a federation token with the green side up "
                        "to take an Advanced Technology tile. Please choose a "
                        "different tile."
                    )
                    continue

                # TODO MINOR if only one standard technology is available,
                #   use that immediately??
                # Player must choose which standard technology tile to cover up
                # with the advanced technology tile.
                print(
                    "Which standard technology do you wish to cover up? "
                    "You will no longer receive any rewards from it!"
                )
                for i, tile in enumerate(self.standard_technology, start=1):
                    print(f"{i}. {tile}")
                print(f"{i + 1}. Choose a different technology tile.")

                while True:
                    chosen_std_tile = input("--> ")
                    if chosen_std_tile in [str(n + 1) for n in range(i)]:
                        selected_std_tile = (
                            self.standard_technology[int(chosen_std_tile) - 1]
                        )
                        break
                    elif chosen_std_tile == f"{i + 1}":
                        # Return to the main while loop to choose a different
                        # technology tile.
                        choose_another = True
                        break
                    else:
                        print("Please only type one of the available numbers.")
                        continue
            else:
                # Player has chosen a standard technology tile.
                print(f"You have chosen: {selected_tile}.")

            # Player wants to choose a different technology tile.
            if choose_another:
                continue

            action_selection = False
            # Go up a research track after having chosen a tile.
            if isinstance(selected_tile, AdvancedTechnology):
                try:
                    self.research(research_board, rnd, universe, True)
                except e.BackToActionSelection:
                    # Player changed his/her mind. Go back up to pick another
                    # tile.
                    action_selection = True
                except e.ResearchError as ex:
                    print(ex)
                finally:
                    # TODO MINOR If player types a wrong number during
                    # research track selection, he can't undo that. This
                    # includes the possibility that the player chooses a track
                    # he can't go up on by mistake or by necessity because he
                    # is unable to go up on any of the tracks.
                    if not action_selection:
                        # If the call to self.research doesn't encounter the
                        # BackToActionSelection exception, that means the
                        # player has chosen a track to go up on, so we can add
                        # the standard tile to the Player object. We do this
                        # whether or not a ResearchError was encountered,
                        # because if a player can't go up on the corresponding
                        # research track, the player can still get the advanced
                        # technology tile.
                        self.advanced_technology.append(selected_tile)
                        self.covered_standard_technology.append(
                            selected_std_tile
                        )
                        self.standard_technology.remove(selected_std_tile)

                        print(
                            f"You have chosen {selected_std_tile} and covered "
                            f"it with {selected_tile}."
                        )

                        # Check if the tile rewards anything right away.
                        if selected_tile.when == "direct":
                            selected_tile.resolve_effect(self)
                        return
            else:
                # Look if the chosen standard tile is under any of the
                # research tracks.
                for i, track in enumerate(research_board.tech_tracks, start=1):
                    if selected_tile is track.standard:
                        track_num = str(i)
                        break

                else:
                    # If the tile isn't under any research tracks it must be a
                    # standard tile that allows the user to go up any track
                    # they like.
                    track_num = False

                try:
                    self.research(research_board, rnd, universe, track_num)
                except e.BackToActionSelection:
                    # Player changed his/her mind. Go back up to pick another
                    # tile.
                    action_selection = True
                except e.ResearchError as ex:
                    # TODO Minor. If the player chose a standard tile that lays
                    # directly under a research track and the player can't
                    # go up on that track, ask the player if that is really
                    # what he/she wants to do as it is possible to take a tile
                    # under a research track the player isn't able to go up on.
                    print(ex)
                finally:
                    if not action_selection:
                        # If the call to self.research doesn't encounter the
                        # BackToActionSelection exception, that means the
                        # player has chosen a track to go up on, so we can add
                        # the standard tile to the Player object. We do this
                        # whether or not a ResearchError was encountered,
                        # because if a player can't go up on the corresponding
                        # research track, the player can still get the standard
                        # technology tile.
                        self.standard_technology.append(
                            available[int(chosen_tile) - 1]
                        )

                        # Check if the tile awards anything right away.
                        if selected_tile.when == "direct":
                            selected_tile.resolve_effect(self)
                        return

    def upgrade(self, gp, rnd):
        """Upgrade a built structure to another structure.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.

        TODO:
            Show how much money was spent?? Do this with a function ?? Consider
            this for all actions.
        """

        print("\nYou want to upgrade a structure.")

        print(
            "Please select the planet with the structure you want to "
            "upgrade."
        )
        # TODO filter out the planets with structures that can't be upgraded
        # anymore (Academy, Planetary Institute)?? And upgrades you can't
        # afford?
        # TODO Show the cost of upgrading/current resources??
        # TODO more players CRITICAL For every upgrade, check if the opponent
        # can charge power.
        planets = [
            planet for planet in self.empire if planet.type != "Lost Planet"
        ]
        # Sort on sector and then on planet num.
        planets.sort(key=lambda planet: (planet.sector, planet.num))
        for i, planet in enumerate(planets, start=1):
            print(
                f"{i}. Sector: {planet.sector} "
                f"| Structure: {planet.structure} "
                f"| Type: {planet.type} "
                f"| Number: {planet.num}"
            )
        print(f"{i + 1}. Go back to action selection.")

        # Choose a planet
        while True:
            chosen_planet = input(f"--> ")
            if chosen_planet in [str(n + 1) for n in range(i)]:
                planet_to_upgrade = self.empire[int(chosen_planet) - 1]
                break
            elif chosen_planet == f"{i + 1}":
                raise e.BackToActionSelection
            else:
                print("Please only type one of the available numbers.")
                continue

        upgrade_options = {
            "Mine": "Trading Station",
            "Trading Station": ["Planetary Institute", "Research Lab"],
            "Research Lab": "Academy"
        }

        if planet_to_upgrade.structure == "Mine":
            old = "Mine"

            # Check if the player has any Trading Stations left.
            if (
                self.faction.trading_station_built
                    == self.faction.trading_station_max
            ):
                print(
                    "You have already built all your trading stations. "
                    "Please choose a different structure to upgrade."
                )
                raise e.BackToActionSelection("3")

            # TODO faction compatibility, does this work with lantids??
            # Check if the player is a neighbour with another player. A
            # neighbour is within range 2 of the player.
            if gp.universe.planet_has_neighbours(
                planet_to_upgrade, self, gp.players
            ):
                credit_cost = 3
            else:
                credit_cost = 6

            # Check if the player has enough credits or ore to upgrade this
            # structure.
            if self.faction.credits < credit_cost or self.faction.ore < 2:
                print(
                    "You don't have enough credits or ore to upgrade this "
                    "Mine into a Trading Station. Please choose a different "
                    "structure."
                )
                raise e.BackToActionSelection("3")

            self.faction.credits -= credit_cost
            self.faction.ore -= 2
            planet_to_upgrade.structure = upgrade_options["Mine"]
            self.faction.mine_built -= 1
            self.faction.trading_station_built += 1
            new = "Trading Station"

            # Check if the player has the advanced tech tile that grants
            # points for upgrading to a trading station.
            if self.advanced_technology:
                for tile in self.advanced_technology:
                    if tile.when == "live" and tile.effect == "trade":
                        reason = "Because of an advanced technology tile"
                        self.resolve_gain(tile.reward, reason)

            # Check if the current round awards points for upgrading to a
            # Trading Station.
            if rnd.goal == "trade":
                reason = "Because of the round"
                self.resolve_gain(f"vp{rnd.vp}", reason)

        # TODO faction compatibility this fails with the Bescods faction which
        # has the academy and planetary institure swapped.
        # If the chosen planet has a trading station, let the player choose
        # what to upgrade to.
        elif planet_to_upgrade.structure == "Trading Station":
            old = "Trading Station"
            # Ask the player to upgrade to a Planetary Institute or a Research
            # Lab.
            print("Please select an available structure to upgrade to.")
            for i, structure in enumerate(
                upgrade_options["Trading Station"], start=1
            ):
                print(f"{i}. {structure}")
            print(f"{i + 1}. Choose a different structure.")

            while True:
                chosen_structure = input("--> ")
                if chosen_structure in [str(n + 1) for n in range(i)]:
                    new_structure = upgrade_options["Trading Station"] \
                        [int(chosen_structure) - 1]
                    break
                elif chosen_structure == f"{i + 1}":
                    raise e.BackToActionSelection("3")
                else:
                    print("Please only type one of the available numbers.")
                    continue

            if new_structure == "Planetary Institute":
                # Check if the planetary institute is not placed yet.
                if (
                    self.faction.planetary_institute_built
                        == self.faction.planetary_institute_max
                ):
                    print(
                        "You have already built your Planetary Institute. "
                        "Please choose a different structure to upgrade to."
                    )
                    raise e.BackToActionSelection("3")

                # Check if the player has enough credits or ore to upgrade this
                # structure into a Planetary Institute.
                if self.faction.credits < 6 or self.faction.ore < 4:
                    print(
                        "You don't have enough credits or ore to upgrade this "
                        "Trading Station into a Planetary Institute. "
                        "Please choose a different structure."
                    )
                    raise e.BackToActionSelection("3")

                # TODO CRITICAL get points if the current round gives points
                # for upgrading to Planetary Institute.

                self.faction.credits -= 6
                self.faction.ore -= 4
                planet_to_upgrade.structure = (
                    upgrade_options["Trading Station"][0]
                )
                self.faction.trading_station_built -= 1
                self.faction.planetary_institute_built += 1
                new = "Planetary Institute"

                # TODO make sure this works with all the implemented factions.
                # The planetary institute bonus now becomes available:
                self.faction.planetary_institute_bonus_func()

            elif new_structure == "Research Lab":
                # Check if there are research labs left.
                if (
                    self.faction.research_lab_built
                        == self.faction.research_lab_max
                ):
                    print(
                        "You have already built all of your Research labs. "
                        "Please choose a different structure to upgrade to."
                    )
                    raise e.BackToActionSelection("3")

                # Check if the player has enough credits or ore to upgrade this
                # structure into a Research Lab.
                if self.faction.credits < 5 or self.faction.ore < 3:
                    print(
                        "You don't have enough credits or ore to upgrade this "
                        "Trading Station into a Research Lab. "
                        "Please choose a different structure."
                    )
                    raise e.BackToActionSelection("3")

                # Only if below doesn't raise any exceptions will the player
                # pay for the structure.
                self.resolve_technology_tile(
                    gp.research_board, rnd, gp.universe
                )

                self.faction.credits -= 5
                self.faction.ore -= 3
                planet_to_upgrade.structure = (
                    upgrade_options["Trading Station"][1]
                )
                self.faction.trading_station_built -= 1
                self.faction.research_lab_built += 1
                new = "Research Lab"


        elif planet_to_upgrade.structure == "Research Lab":
            old = "Research Lab"

            # Check if the player has any academy's left.
            if (
                self.faction.academy_built
                    == self.faction.academy_max
            ):
                print(
                    "You have already built all of your Academy's. "
                    "Please choose a different structure to upgrade to."
                )
                raise e.BackToActionSelection("3")

            # Check if the player has enough credits or ore to upgrade this
            # structure.
            if self.faction.credits < 6 or self.faction.ore < 6:
                print(
                    "You don't have enough credits or ore to upgrade this "
                    "Research Lab. Please choose a different structure."
                )
                raise e.BackToActionSelection("3")

            # If more than one Academy is available, let the player choose
            # which one to build.
            if not self.faction.academy_built:
                print("Please choose which Academy you would like to build.")
                for i, side in enumerate(["Left", "Right"], start=1):
                    print(f"{i}. {side}")
                print(f"{i + 1}. Choose a different structure to upgrade.")

                while True:
                    chosen_side = input("--> ")
                    if chosen_side in [str(n + 1) for n in range(i)]:
                        if chosen_side == "1":
                            chosen_academy = self.faction.academy_income
                        elif chosen_side == "2":
                            chosen_academy = self.faction.academy_special
                        break

                    elif chosen_side == f"{i + 1}":
                        raise e.BackToActionSelection("3")
                    else:
                        print("Please only type one of the available numbers.")
                        continue

            elif not self.faction.academy_income[0]:
                chosen_academy = self.faction.academy_income
            elif not self.faction.academy_special[0]:
                chosen_academy = self.faction.academy_special

            # Only if below doesn't raise any exceptions will the player pay
            # for the structure.
            self.resolve_technology_tile(gp.research_board, rnd, gp.universe)

            # TODO CRITICAL get points if the current round gives points for
            # upgrading to academy.

            # Set the built property of the chosen academy to true.
            chosen_academy[0] = True
            self.faction.credits -= 6
            self.faction.ore -= 6
            planet_to_upgrade.structure = upgrade_options["Research Lab"]
            self.faction.research_lab_built -= 1
            self.faction.academy_built += 1
            new = "Academy"

        else:
            # A Planetary Institute and an Academy can't be upgraded
            a_an = "an"
            structure = planet_to_upgrade.structure
            if structure == "Planetary Institute":
                a_an = "a"
            print(
                f"You can't upgrade {a_an} {structure}. "
                "Please choose a different structure."
            )
            raise e.BackToActionSelection("3")
        print(
            f"You have upgraded your {old} on the {planet_to_upgrade.type} "
            f"planet in sector {planet_to_upgrade.sector} to a {new}."
        )

    def federation(self, gp, rnd):
        # TODO SOMEDAY this function only gives a federation tile now.
        #   It doesn't set the federation property of planets and doesn't place
        #   satellites.
        print("\nPlease choose which Federation tile you want.")

        # TODO MOST STRUCTURES IN FEDERATIONS end scoring tile must be done
        # manually right now as well as MOST SATELLITES.
        print(
            "Use your own judgement when forming a federation as this is not "
            "yet implemented."
        )
        print(
            "Please type your chosen Federation token's corresponding number."
        )

        # Get all the available federation tokens.
        available_tokens = []
        for token in gp.federation_tokens:
            if token.count > 0:
                available_tokens.append(token)

        for i, fed in enumerate(available_tokens, start=1):
            print(f"{i}. {fed}")
        print(f"{i + 1}. Go back to action selection.")

        while True:
            fed_token = input("--> ")
            if fed_token in [str(n + 1) for n in range(i)]:
                chosen_fed_token = available_tokens[int(fed_token) - 1]
                break
            elif fed_token == f"{i + 1}":
                raise e.BackToActionSelection
            else:
                print("Please only type one of the available numbers.")
                continue

        if rnd.goal == "fedtoken":
            reason = "Because of the round"
            self.resolve_gain(f"vp{rnd.vp}", reason)

        self.federations.append(chosen_fed_token)
        chosen_fed_token.count -= 1
        self.resolve_gain(
            chosen_fed_token.reward,
            "Because of the Federation token"
        )

    def research(self, research_board, rnd, universe, tech_tile=False):
        """Function for doing the Research action.

        Args:
            research_board: Research object
            rnd: Active Round object
            tech_tile: Whether or not the player can research because they have
                taken a technology tile. If they are able to research because
                of a technology tile, this argument will be a string with the
                corresponding research track number if the chosen technology
                tile is under one of the research tracks. The researchable
                track is fixed in that case.
                "0" == Terraforming track
                "1" == Navigation track
                "2" == Artificial Intelligence track
                "3" == Gaia Project track
                "4" == Economy track
                "5" == Science track
                tech_tile is True when the player can go up any track they
                like, in which case this function will ask them which track
                they want to go up on.
                tech_tile is False if the player took the research action.
        """

        # Check if the player has enough knowledge to research.
        # Researching costs 4 knowledge.
        if not self.faction.knowledge > 3 and not tech_tile:
            raise e.InsufficientKnowledgeError

        levels = [
            self.terraforming,
            self.navigation,
            self.a_i,
            self.gaia_project,
            self.economy,
            self.science,
        ]

        if not isinstance(tech_tile, str):
            print("\nOn what research track do you want to go up?")
            print(research_board)

        options = (
            "Please type the corresponding number or type 7 if you changed "
            "your mind:\n"
        )
        while True:
            if not isinstance(tech_tile, str):
                track_choice = input(f"{options}--> ")
            else:
                track_choice = tech_tile

            if not track_choice in ["1", "2", "3", "4", "5", "6"]:
                if track_choice == "7":
                    raise e.BackToActionSelection
                print("Please only type 1-7")
                continue

            track_choice = int(track_choice)
            current_level = levels[track_choice - 1]
            try:
                research_board.tech_tracks[track_choice - 1] \
                    .research(
                        current_level, self, track_choice - 1, universe, rnd
                    )
            except e.NoFederationTokensError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "You have no federation tokens so you can't advance "
                        "on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.NoFederationGreenError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "You have no federation token with the green side "
                        "up left so you can't advance on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.NoResearchPossibleError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "You are already at the maximum level of 5 so you "
                        "can't advance on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.Level5IsFullError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "Another player is already on level 5. Only one "
                        "person can go to level 5 so you can't advance on the"
                        f" {research_board.tech_tracks[track_choice - 1].name}"
                        " track."
                    )
                print(ex)
                continue
            else:
                break

        if not tech_tile:
            # Pay research cost.
            self.faction.knowledge -= 4
        print(research_board)
        print(
            f"You have researched "
            f"{research_board.tech_tracks[track_choice - 1].name}."
        )

        # Check if the current round awards points for researching.
        if rnd.goal == "research":
            reason = "Because of the round"
            self.resolve_gain(f"vp{rnd.vp}", reason)

        # Check if the player has the advanced tech tile that grants points for
        # doing research.
        if self.advanced_technology:
            for tile in self.advanced_technology:
                if tile.when == "live" and tile.effect == "research":
                    reason = "Because of an advanced technology tile"
                    self.resolve_gain(tile.reward, reason)

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
                "You don't have enough Q.I.C.'s to do this action. "
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
            Perhaps make the power/qic cost text summary more readable.
            Show which actions are still available this round??
        """

        intro = (
            "\nYou want to take a power or Q.I.C. action. Type the number of "
            "your action.\n"
        )
        power = "Power actions:\n"
        knowledge3 = "1. Gain 3 knowledge for 7 power.\n"
        terraform2 = "2. Gain 2 terraforming steps for 5 power.\n"
        ore2 = "3. Gain 2 ore for 4 power.\n"
        credits7 = "4. Gain 7 credits for 4 power.\n"
        knowledge2 = "5. Gain 2 knowledge for 4 power.\n"
        terraform1 = "6. Gain 1 terraforming step for 3 power.\n"
        powertoken2 = "7. Gain 2 powertokens for 3 power.\n"
        qic = "Q.I.C. actions:\n"
        tech_tile = "8. Gain a technology tile.\n"
        score_fed_token = "9. Score one of your federation tokens again.\n"
        vp_for_ptypes = (
            "10. Gain 3 vp and 1 vp for every different planet type.\n"
        )
        cancel = "11. Go back to action selection."

        print(
            f"{intro}{power}{knowledge3}{terraform2}{ore2}{credits7}"
            f"{knowledge2}{terraform1}{powertoken2}{qic}{tech_tile}"
            f"{score_fed_token}{vp_for_ptypes}{cancel}"
        )

        while True:
            action = input("--> ")

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
                self.resolve_gain("knowledge3")

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
                self.resolve_gain("ore2")

            elif action == "4":
                # Gain 7 credits for 4 ore.

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(4)
                self.resolve_gain("credits7")

            elif action == "5":
                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.use_power(4)
                self.resolve_gain("knowledge2")

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
                self.resolve_gain("powertokens2")

            elif action == "8":
                # Gain a technology tile for 4 qic's.

                if not self.enough_qic(4):
                    continue

                # Only if below doesn't raise any exceptions will the player
                # pay for the action.
                self.resolve_technology_tile(
                    gp.research_board, rnd, gp.universe, pq=True
                )

                gp.research_board.pq_actions[int(action)] = False
                self.faction.qic -= 4

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

                chosen = False
                while True:
                    chosen_token = input("--> ")
                    if chosen_token in [str(n + 1) for n in range(i)]:
                        chosen = True
                        break
                    elif chosen_token == f"{i + 1}":
                        break
                    else:
                        print("Please only type one of the available numbers.")
                        continue

                if not chosen:
                    continue

                # TODO CRITICAL test that this resolves federation tokens
                #   correctly.
                self.resolve_gain(
                    self.federations[int(chosen_token) - 1].reward,
                    "Because of the Federation token"
                )
                self.faction.qic -= 3

            elif action == "10":
                # Gain 3 vp immediately and 1 point for every unique planet
                # type that you own.

                if not self.enough_qic(2):
                    continue

                types = len({planet.type for planet in self.empire})

                self.resolve_gain(f"vp{3 + types}")
                self.faction.qic -= 2

            return

    def special(self):
        # TODO academy special
        # TODO booster special
        # TODO technology special
        pass

    def pass_(self, gp, rnd):
        # TODO MINOR allow player to go back to action selection in case of a
        #   miss click and the player doesn't want to pass yet??

        print("\nYou Pass.")

        # Check what the current round number is.
        round_number = gp.scoring_board.rounds.index(rnd) + 1

        # Keep a reference to the old booster for scoring passing points if
        # applicable.
        old_booster = self.booster
        # Don't pick a new booster when it's the last round.
        if round_number != 6:
            print("Which booster would you like to pick?")
            while True:
                for i, booster in enumerate(
                    gp.scoring_board.boosters, start=1
                ):
                    print(f"{i}. {booster}")

                booster_choice = input(f"--> ")
                if booster_choice in [str(n + 1) for n in range(3)]:
                    gp.scoring_board.boosters.append(self.booster)
                    self.booster = gp.scoring_board.boosters.pop(
                        int(booster_choice) - 1
                    )
                    print(f"You chose {self.booster}.")
                    break
                else:
                    print("Please only type one of the available numbers.")
                    continue

        gp.passed += 1
        self.passed = True

        # TODO CRITICAL check if points are rewarded by the booster for passing

        #   Check if the player has any advanced technology tiles that awards
        #   points when passing.
        for adv_tile in self.advanced_technology:
            if adv_tile.when == "pass":
                adv_tile.resolve_effect(self)

        # TODO More players. This only works for 2 players right now.
        #   If starting player order is [1, 2, 3, 4] and if player 3 if first
        #   to pass than [3, 1, 2, 4] the player order is messed up.
        # TODO MINOR instead of "You" make it faction.name starts first...??
        # If player passed first, he/she starts first next round.
        if gp.passed == 1:
            gp.players.remove(self)
            gp.players.insert(0, self)
            print("You start first next round.")

    def free(self):
        pass


if __name__ == "__main__":
    test = Player("hadsch halla")
    print(test.faction.home_type)
