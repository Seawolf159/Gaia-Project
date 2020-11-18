import re
from math import ceil

import constants as C
import exceptions as e
from faction import select_faction
from scoring import Booster
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
            Make every action print something like ACTION NAME:??
        """

        self.faction = select_faction(faction.lower())()
        self.vp = 10
        self.standard_technology = []
        self.covered_standard_technology = []
        self.advanced_technology = []

        # This property is set during setup and when passing.
        self.booster = False

        # whether the player owns the lost planet.
        self.lost_planet = False
        self.empire = []  # List of owned planets
        self.federations = []  # List of federation tokens
        self.satellites = 0  # Amount fo satellites placed.

        # List of trans-dim planets undergoing a gaia project.
        self.gaia_forming = []

        # Research levels
        self.terraforming = False  # This property is set during setup
        self.navigation = False  # This property is set during setup
        self.a_i = False  # This property is set during setup
        self.gaia_project = False  # This property is set during setup
        self.economy = False  # This property is set during setup
        self.science = False  # This property is set during setup

        self.passed = False  # whether or not the player has passed.

        # List with all the free action the player has taken. This is used to
        # undo the free actions if the player decides that he doesn't want /
        # can't do an action after all and not doing an action is not allowed
        # when taking free actions.
        # append lists with the cost first and what was gained second.
        # For example: self.free_action.append(["power1", "credits1"])
        self.free_actions = []

        # TESTING parameters.
        # Initiate testing parameters
        self.faction._testing()

    def start_mine(self, count, universe, players):
        """Function for placing the initial mines.

        Args:
            count (int): Number of the mine placed.
            universe: The universe object used in the main GaiaProject class.
            players: list of the players in the current game.
        """

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

        # Check if the mine was placed within range 2 of an opponent.
        universe.planet_has_neighbours(
            planet, self, players, neighbour_charge=False
        )

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
                print("! Please only type one of the available numbers.")

    def income_phase(self):
        print(f"\nDoing income for {self.faction.name}.")

        # Collect the income from all the different sources.
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

        # Take all the income and give it to the player.
        self.resolve_gain(total_income, income_phase=True)

    def resolve_gain(self, gains, reason="", income_phase=False):
        """Function for resolving all resources that are gained.

        Args:
            gains (list): List of resources that are directly gained. Format:
                ["credits3", "vp2", "knowledge1"]
            reason (str): String specifying why something was gained.
                f"{reason} you have gained...."
        """

        # If gains is not a list and therefore a single gain, put that
        # single gain in a list to not iterate over a string instead. For
        # example if gains == "ore2" the iteration below would fail so
        # correct it like so: gains = ["ore2"]
        if not isinstance(gains, list):
            gains = [gains]

        # If different types of power are gained (power and power tokens),
        # allow the player to choose in which order he/she would like to
        # receive it.
        power_order = []

        text = " you have gained "
        if not reason:
            text = "You have gained "

        # Add up all of the types of income. "knowledge, vp, powertoken" etc.
        # and add them at the same time to keep the output clean.
        types_of_gain = {}
        pattern = re.compile(r"(\D+)(\d+)")
        for gain in gains:
            split_up = pattern.search(gain)
            cost_type = split_up.group(1)
            amount = int(split_up.group(2))

            if cost_type.startswith("power"):
                power_order.append(gain)

            if not cost_type in types_of_gain:
                types_of_gain[cost_type] = int(amount)
            else:
                types_of_gain[cost_type] += int(amount)

        for added_up_gain, amount in types_of_gain.items():
            capped = False
            limited = False
            # Check if adding the Credits, Ore or Knowledge, doesn't make
            # the player go over the limit.
            if added_up_gain == "credits":
                if self.faction.credits >= self.faction.credits_max:
                    capped = True

                if self.faction.credits \
                        + amount > self.faction.credits_max:
                    new_amount = self.faction.credits_max \
                        - self.faction.credits
                    limited = True

            elif added_up_gain == "ore":
                if self.faction.ore >= self.faction.ore_max:
                    capped = True

                if self.faction.ore + amount > self.faction.ore_max:
                    new_amount = self.faction.ore_max - self.faction.ore
                    limited = True

            elif added_up_gain == "knowledge":
                if self.faction.knowledge >= self.faction.knowledge_max:
                    capped = True

                if self.faction.knowledge + amount \
                        > self.faction.knowledge_max:
                    new_amount = self.faction.knowledge_max \
                        - self.faction.knowledge
                    limited = True

            # Stuff for making the output prettier.
            if added_up_gain == "powertoken":
                resource = "Power Token"
            elif added_up_gain == "vp":
                resource = "Victory Point"
            elif added_up_gain == "qic":
                resource = "Q.I.C."
            else:
                resource = added_up_gain.capitalize()

            if amount > 1 and added_up_gain == "powertoken" \
                    or added_up_gain == "vp":
                pretty_print_resource = f"{resource}s"
            elif amount == 1 and added_up_gain == "credits":
                pretty_print_resource = f"{resource[:-1]}"
            else:
                pretty_print_resource = resource

            # Gain the resources
            if capped:
                maximum_of_resource = eval(f"self.faction.{added_up_gain}_max")
                print(
                    f"! {reason}{text}{amount} "
                    f"{pretty_print_resource}, but no "
                    f"{pretty_print_resource} could be added because "
                    "you are already at the maximum of "
                    f"{maximum_of_resource}."
                )
                if income_phase:
                    continue
                else:
                    return False
            elif added_up_gain == "vp":
                exec(f"self.{added_up_gain} += {amount}")
            else:
                if not added_up_gain.startswith("power"):
                    # If the player will be going over the max, add until the
                    # players resource is full.
                    if limited:
                        exec(f"self.faction.{added_up_gain} += {new_amount}")
                    else:
                        exec(f"self.faction.{added_up_gain} += {amount}")

            if limited:
                print(
                    f"!+ {reason}{text}{amount} {pretty_print_resource}, "
                    f"but only {new_amount} could be added."
                )
            else:
                print(f"+ {reason}{text}{amount} {pretty_print_resource}.")

        if power_order:
            self.resolve_power_order(power_order)

    def resolve_cost(self, cost):
        """Subtract the cost of stuff.

        Args:
            cost (str): 1 cost to be payed by the player. Looks like:
                "power1", "vp2", "knowledge4"

        Returns:
            True: If the player was able to pay.
            False: If the player was unable to pay.
        """

        pattern = r"(\D+)(\d+)"
        split_up = re.search(pattern, cost)
        cost_type = split_up.group(1)
        amount = int(split_up.group(2))

        if cost_type == "power":
            # Check if the player has enough power to spend.
            if self.faction.bowl3 >= amount:
                for _ in range(amount):
                    self.faction.bowl3 -= 1
                    self.faction.bowl1 += 1
            else:
                return False
        elif cost_type == "powertoken":
            if not self.faction.count_powertokens() >= amount:
                return False
            for _ in range(amount):
                # Prioritise taking from the lowest bowl as i don't see why it
                # would ever be better to not do that.
                if self.faction.bowl1 > 0:
                    self.faction.bowl1 -= 1
                elif self.faction.bowl2 > 0:
                    self.faction.bowl2 -= 1
                elif self.faction.bowl3 > 0:
                    self.faction.bowl3 -= 1
        elif cost_type == "vp":
            if not self.vp >= amount:
                return False
            exec(f"self.{cost_type} -= {amount}")
        else:
            if not eval(f"self.faction.{cost_type}") >= amount:
                return False
            exec(f"self.faction.{cost_type} -= {amount}")

        # Stuff for making the output prettier.
        if cost_type == "powertoken":
            resource = "Power Token"
        elif cost_type == "vp":
            resource = "Victory Point"
        elif cost_type == "qic":
            resource = "Q.I.C."
        else:
            resource = cost_type.capitalize()

        if amount > 1 and cost_type == "powertoken" \
                or cost_type == "vp":
            pretty_print_cost_type = f"{resource}s"
        elif amount == 1 and cost_type == "credits":
            pretty_print_cost_type = f"{resource[:-1]}"
        else:
            pretty_print_cost_type = resource

        print(f"- You have spent {amount} {pretty_print_cost_type}.")
        return True

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
                        pow_text = f"{i}. {to_resolve[:-1]} x{to_resolve[-1]}"

                        # Fill the string from the left with spaces until
                        # it's as long as the longest string in the row
                        # (in this case i chose 17 to hopefully be the longest
                        # string). To line up both columns and add 7 spaces
                        # between columns.
                        filler = (
                            lambda text_left: " " * (17 - len(text_left) + 7)
                        )

                        # Display the power in the players power bowls on the
                        # right side.
                        if i < 4:
                            bowl = eval(f"self.faction.bowl{i}")
                            bowl_text = f"Power in bowl {i}: {bowl}"
                            print(f"{pow_text}{filler(pow_text)}{bowl_text}")
                        else:
                            print(f"{pow_text}")

                    # If there were only 2 power gains to order, bowl 3 was
                    # never printed, so do that here if needed.
                    if i < 3:
                        bowl = self.faction.bowl3
                        bowl_text = f"Power in bowl 3: {bowl}"
                        print(f"{filler('')}{bowl_text}")
                        selection = input("--> ")
                    else:
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
                        print(
                            "! Please only type one of the available numbers."
                        )
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

        if amount == 0:
            print(f"+ {charged} Power has been charged.")
        elif charged == 0:
            print("! No Power could be charged.")
        else:
            print(f"!+ Only {charged} power could be charged.")

    def gaia_phase(self):
        # TODO Faction incompatibility. Might not work with faction Itars,
        # Bal Tak's
        if self.faction.gaia_bowl > 0:
            self.faction.move_from_gaia_to_bowl()

            while self.gaia_forming:
                # Set the type property of the trans-dimensional planet to Gaia
                # as the gaia project is now completed.
                self.gaia_forming.pop().type = "Gaia"

            print(
                "\nGaia phase:\nYour Trans-dimensional planets are now Gaia "
                "planets."
            )
            # Error is corrected at runtime so i can ignore this.
            # pylint: disable=no-member
            print(
                f"{self.gaia_project.active} Power has been returned to you."
            )

    def action_phase(self, gp, rnd, choice=False):
        """Functions for delegating to action functions.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.
        """

        # Summary of actions
        faction_name = f"\n{self.faction.name}:"
        intro_1 = "What action do you want to take?"
        intro_2 = "Type the number of your action."
        mine = "1. Build a Mine."
        gaia = "2. Start a Gaia Project."
        upgrade = "3. Upgrade an existing structure."
        federation = "4. Form a federation."
        research = "5. Do research."
        pq = "6. Power or Q.I.C (Purple/Green) action."
        special = "7. Do a Special (Orange) action."
        pass_ = "8. Pass."
        free = "9. Free action (exchange resources)."

        # Value is a list with the function and the arguments it needs.
        options = {
            "1": [self.mine, gp, rnd],
            "2": [self.gaia, gp.universe],
            "3": [self.upgrade, gp, rnd],
            "4": [self.federation, gp, rnd],
            "5": [self.research, gp.research_board, rnd, gp],
            "6": [self.pq, gp, rnd],
            "7": [self.special, gp.universe, rnd],
            "8": [self.pass_, gp, rnd],
            "9": [self.free]
        }

        while True:
            # Summary of resources
            resources = "Your resources are:"
            vp = f"Victory points: {self.vp}"
            credits_ = f"Credits: {self.faction.credits}"
            ore = f"Ore: {self.faction.ore}"
            knowledge = f"Knowledge: {self.faction.knowledge}"
            qic = f"Q.I.C.: {self.faction.qic}"
            g_formers = f"Gaiaformers: {self.faction.gaiaformer}"
            power_1 = f"Power in bowl 1: {self.faction.bowl1}"
            power_2 = f"Power in bowl 2: {self.faction.bowl2}"
            power_3 = f"Power in bowl 3: {self.faction.bowl3}"
            gaia_bowl = f"Power in Gaia bowl: {self.faction.gaia_bowl}"

            # Fill the string from the left with spaces until it's as long as
            # the longest string in the row (in this case the free variable is
            # the longest string). To line up both columns and add 7 spaces
            # between columns.
            filler = lambda text_left: " " * (len(free) - len(text_left) + 7)

            prompt = (
                f"{faction_name}{filler(faction_name.strip())}{resources}\n"
                f"{intro_1}{filler(intro_1)}{vp}\n"
                f"{intro_2}{filler(intro_2)}{credits_}\n"
                f"{mine}{filler(mine)}{ore}\n"
                f"{gaia}{filler(gaia)}{knowledge}\n"
                f"{upgrade}{filler(upgrade)}{qic}\n"
                f"{federation}{filler(federation)}{g_formers}\n"
                f"{research}{filler(research)}{power_1}\n"
                f"{pq}{filler(pq)}{power_2}\n"
                f"{special}{filler(special)}{power_3}\n"
                f"{pass_}{filler(pass_)}{gaia_bowl}\n"
                f"{free}"
            )
            print(prompt)

            if not choice or choice == "0":
                choice = input("--> ")

            if not choice in options.keys():
                print("Please type the action's corresponding number.")
                choice = "0"
                continue

            action = options[choice]
            try:
                if len(action) > 1:
                    # If the action function needs additional arguments,
                    # unpack the arguments from the options list.
                    action[0](*action[1:])
                else:
                    # Otherwise just call the function.
                    action[0]()
            except (
                e.NotEnoughPowerTokensError,
                e.NoGaiaFormerError,
                e.InsufficientKnowledgeError
            ) as ex:
                print(ex)
                choice = "0"
                continue
            except e.BackToActionSelection as back:
                # User chose to pick another action or wasn't able to pay for
                # some costs.
                choice = back.choice
                continue
            else:
                # If the player used free actions, reset the list.
                if self.free_actions:
                    self.free_actions.clear()
                return

    def undo_free(self):
        # TODO minor print the totals only and not everything individually??

        pattern = re.compile(r"(\D+)(\d+)")

        # Totals are put into this dictionary for printing the totals prettier.
        summary = []
        while self.free_actions:
            action = self.free_actions.pop()

            cost_match = pattern.match(action[0])
            cost = cost_match.group(1)
            cost_amount = int(cost_match.group(2))

            exchange_match = pattern.match(action[1])
            exchange = exchange_match.group(1)
            exchange_amount = int(exchange_match.group(2))

            if cost == "discard":
                self.faction.bowl2 += 2
                self.faction.bowl3 -= 1
                summary.append([
                    "+ You have re-gained 2 Power in Bowl 2",
                    "- You have lost 1 Power from Bowl 3"
                ])
            else:
                if cost == "power":
                    self.faction.bowl3 += cost_amount
                    self.faction.bowl1 -= cost_amount
                    exec(f"self.faction.{exchange} -= {exchange_amount}")
                elif exchange == "powertoken":
                    exec(f"self.faction.{cost} += {cost_amount}")
                    self.faction.bowl1 -= exchange_amount
                else:
                    exec(f"self.faction.{cost} += {cost_amount}")
                    exec(f"self.faction.{exchange} -= {exchange_amount}")

                # Stuff for making the cost prettier.
                if cost == "qic":
                    cost = "Q.I.C."
                else:
                    cost = cost.capitalize()

                # Stuff for making the exchange prettier.
                if exchange == "powertoken":
                    exchange = "Power Token"
                elif exchange == "qic":
                    exchange = "Q.I.C."
                elif exchange == "credits" and exchange_amount == 1:
                    exchange = "Credit"
                else:
                    exchange = exchange.capitalize()

                if cost == "Power":
                    summary.append([
                        f"+ You have re-gained {cost_amount} {cost} in bowl 3",
                        f"- You have lost {exchange_amount} {exchange}"
                    ])
                else:
                    summary.append([
                        f"+ You have re-gained {cost_amount} {cost}",
                        f"- You have lost {exchange_amount} {exchange}"
                    ])

        # Fill the string from the left with spaces until
        # it's as long as the longest string in the row
        # (in this case i chose 70 to hopefully be the longest
        # string). To line up both columns and add 7 spaces
        # between columns.
        filler = (lambda text_left: " " * (38 - len(text_left) + 7))

        print("\nYour free actions have been undone.")
        for summation in summary:
            cost = summation[0]
            exchange = summation[1]
            print(f"{cost}{filler(cost)}{exchange}")

    def mine(self,
             gp,
             rnd,
             terraform_steps=0,
             action="mine",
             extra_range=0,
             p_chosen=False):
        """Function for building a  Mine.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.
            terraform_steps (int): The amount of free terraform steps the
                player has gotten.
            action (str): What kind of action called this function.
            extra_range (int): The amount of extra range the player has gotten.
            p_chosen: Planet object. Only used in scoring.ExtraRange class.
        """

        # Error is corrected at runtime so i can ignore this.
        # pylint: disable=no-member
        available_range = self.navigation.active + extra_range

        # Check if the player has any mines left.
        if self.faction.mine_built == self.faction.mine_max:
            print(
                "! You don't have any more mines left to build. Please choose "
                "a different action."
            )
            raise e.BackToActionSelection

        # Check if the player has enough resources to pay for the mine.
        if not self.faction.credits >= 2 and not self.faction.ore >= 1:
            print(
                f"! You don't have enough credits ({self.faction.credits}) "
                f"or ore ({self.faction.ore}) to build a mine. Building a mine"
                " costs 2 credits and 1 ore."
            )
            raise e.BackToActionSelection

        print("\nYou want to build a Mine.")
        while True:
            # Payment flags
            pay_range_qic = 0
            pay_gaia_qic = 0
            pay_terraform_ore = 0

            if not p_chosen:
                planet = self.choose_planet(gp.universe, action)
            else:
                planet = p_chosen

            # If the planet was gaiaformed, the player only pays for the mine.
            if planet.structure == "gaiaformer":
                break

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
                    "! When you gain terraform steps, you MUST build a mine on"
                    " a planet that has to be terraformed. Please choose a "
                    "different planet type."
                )
                continue

            # Check if the player has enough range.
            enough_range, distance = self.within_range(
                gp.universe, planet, available_range
            )

            if not enough_range:
                pay_range_qic = self.ask_pay_for_range(
                    planet,
                    distance,
                    available_range,
                    p_chosen
                )
                if not pay_range_qic:
                    continue

            if planet.type == "Gaia":
                # TODO faction compatibility this function doesn't work for the
                # gleens faction as they pay ore to build on gaia planets
                qic_storage = self.faction.qic
                if pay_range_qic:
                    qic_storage -= pay_range_qic

                if not qic_storage > 0:
                    print(
                        "! You don't have a Q.I.C. to build on a Gaia planet. "
                        "Please choose a different type of planet."
                    )
                    continue

                print(
                    "To build a mine on this planet, you need to pay 1 Q.I.C. "
                    "spend 1 Q.I.C.? (Y/N)"
                )

                choose_another_planet = False
                while True:
                    pay_qic = input("--> ").lower()

                    if not pay_qic in ['y', 'n']:
                        print("! Please type Y for yes or N for no.")
                        continue
                    elif pay_qic == 'n':
                        if p_chosen:
                            raise e.ExtraRangeError
                        choose_another_planet = True
                        break
                    else:
                        break

                if choose_another_planet:
                    continue

                # Player wants to pay QIC.
                pay_gaia_qic = 1

            elif planet.type == "Trans-dim":
                print(
                    "! To build a mine on this planet, you first need to turn "
                    "this planet into a Gaia planet with the Gaia Project "
                    "action. Please choose a different type of planet."
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
                            "! You don't have enough ore to pay the "
                            "terraforming cost needed to terraform this "
                            "planet. Please choose a different type of planet."
                        )
                        continue

                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    print(
                        "To build a mine on this planet, you need to terraform"
                        f" it first. Terraforming will cost {terraform_cost} "
                        f"ore. Do you want to pay {terraform_cost} ore? (Y/N)"
                    )

                    while True:
                        pay_terraform_cost = input("--> ").lower()

                        if not pay_terraform_cost in ['y', 'n']:
                            print("! Please type Y for yes or N for no.")
                            continue
                        elif pay_terraform_cost == 'n':
                            if p_chosen:
                                raise e.ExtraRangeError
                            choose_another_planet = True
                            break
                        else:
                            # Player wants to pay terraforming cost.
                            pay_terraform_ore = terraform_cost
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

        # Apply the various payment options.
        if pay_range_qic or pay_gaia_qic:
            self.resolve_cost(f"qic{pay_range_qic + pay_gaia_qic}")
        self.resolve_cost("credits2")

        if pay_terraform_ore:
            self.resolve_cost(f"ore{pay_terraform_ore + 1}")
        else:
            self.resolve_cost("ore1")

        # Place the mine.
        planet.owner = self.faction.name
        planet.structure = "Mine"
        self.faction.mine_built += 1
        self.empire.append(planet)

        if planet.type == "Gaia":
            if planet.structure == "gaiaformer":
                self.resolve_gain(
                    f"gaiaformer1", "Because you built a mine on a planet "
                    "with a Gaiaformer"
                )

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

        # Check if the current round awards points for building a mine.
        if rnd.goal == "mine":
            reason = "Because of the round"
            self.resolve_gain(f"vp{rnd.vp}", reason)

        # Check if the player has the advanced tech tile that grants points for
        # building a mine.
        if planet.type != "Gaia":
            if self.advanced_technology:
                for tile in self.advanced_technology:
                    if tile.when == "live" and tile.effect == "mine":
                        reason = "Because of an advanced technology tile"
                        self.resolve_gain(tile.reward, reason)

        gp.universe.planet_has_neighbours(planet, self, gp.players)

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
        if action.startswith("boost"):
            back_to_action = (
                "Type 8 if you want to choose a different Special action."
            )
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
                print(f"! Please only type {choose_range}.")
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
                    print("! Please only type one of the available numbers.")
                    continue

    def within_range(self, universe, target_hex, available_range):
        """Check if the player is within range of the target hex.

        Args:
            universe: The universe object used in the main GaiaProject class.
            target_hex: Object of the hex to be checked. (Planet or Space).
            available_range (int): The amount of range the player has.

        Returns:
            Tuple: [True, False], distance
                True if player is within range and False if player isn't.
                distance is the amount of distance to the closest planet the
                player has to the target_hex.
        """

        all_distances = []
        for owned_planet in self.empire:
            startx = owned_planet.location[0]
            starty = owned_planet.location[1]

            targetx = target_hex.location[0]
            targety = target_hex.location[1]

            distance = universe.distance(startx, starty, targetx, targety)
            all_distances.append(distance)

            # If the distance of the planet to one of the players planets
            # is ever smaller or equal to the amount of range the player
            # has, the planet is close enough.
            if distance <= available_range:
                return True, distance
        else:
            distance = min(all_distances)
            return False, distance

    def ask_pay_for_range(self,
                          target_hex,
                          distance,
                          available_range,
                          p_chosen=False,
                          lost_planet=True):
        """Ask the player if they want to pay for extra range.

        Args:
            target_hex: Object of the hex to be checked. (Planet or Space).
            distance (int): The distance to the hex.
            available_range (int): The amount of range the player has.
            p_chosen: Planet object. Only used in scoring.ExtraRange class.
        """

        extra_range_needed = distance - available_range
        qic_needed = ceil(extra_range_needed / 2)

        # Check if player has the required amount of qic needed to
        # increase the range enough.
        hex_ = "planet"
        if lost_planet:
            hex_ = "space"
        if qic_needed > self.faction.qic:
            print(
                f"! You don't have enough range to build on your chosen {hex_}"
                " and you don't have enough Q.I.C. to increase your range."
            )
            return False

        # Check if the player is building on a gaia planet and if
        # he/she has enough qic to increase the range AND pay a qic for
        # building on a gaia planet type.
        if target_hex.type == "Gaia" and not self.faction.qic > qic_needed:
            print(
                f"! You don't have enough Q.I.C. to increase your range AND "
                "build on a gaia planet. Please choose a different planet."
            )
            return False

        if qic_needed == 1:
            QIC = "Q.I.C."
        else:
            QIC = "Q.I.C.'s"
        print(
            "Your nearest planet is not within range of your chosen "
            f"{hex_}. Do you want to spend {qic_needed} {QIC} to "
            f"increase your range by {qic_needed * 2}? (Y/N)"
        )

        while True:
            increase_range = input("--> ").lower()

            if not increase_range in ['y', 'n']:
                print("! Please type Y for yes or N for no.")
                continue
            elif increase_range == 'n':
                if p_chosen:
                    raise e.ExtraRangeError
                return False
            else:
                break

        # Player wants to pay QIC.
        return qic_needed

    def gaia(self, universe, p_chosen=False, action="gaia", extra_range=0):
        """Function for starting a Gaia Project.

        Args:
            universe: The universe object used in the main GaiaProject class.
            planet: Planet object. Only used in scoring.ExtraRange class.
            p_chosen: Planet object. Only used in scoring.ExtraRange class.
            action (str): What kind of action called this function.
            extra_range (int): The amount of extra range the player has gotten.
        """

        # Error is corrected at runtime so i can ignore this.
        # pylint: disable=no-member
        available_range = self.navigation.active + extra_range

        # Check if the player has an available gaiaformer.
        if not self.faction.gaiaformer > 0:
            raise e.NoGaiaFormerError(
                "! You have no available Gaiaformers. Please pick a "
                "different action."
            )

        # Error is corrected at runtime so i can ignore this.
        # pylint: disable=no-member
        # Check if the player has enough powertokens to do a gaia project.
        if not self.faction.count_powertokens() >= self.gaia_project.active:
            raise e.NotEnoughPowerTokensError(
                "! You don't have enough power tokens to do this "
                "action. Please pick a different action."
            )

        print("\nYou want to start a Gaia Project.")
        while True:
            # Payment flag
            pay_range_qic = False

            if not p_chosen:
                planet = self.choose_planet(universe, action)
            else:
                planet = p_chosen

            # Check if the player is within range of the target planet.
            enough_range, distance = self.within_range(
                universe, planet, available_range
            )

            if not enough_range:
                pay_range_qic = self.ask_pay_for_range(
                    planet,
                    distance,
                    available_range,
                    p_chosen
                )
                if not pay_range_qic:
                    continue
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
            "You have started a gaia project in sector "
            f"{planet.sector} on the {planet.type} planet."
        )

        # Apply paying for range if applicable.
        if pay_range_qic:
            self.resolve_cost(f"qic{pay_range_qic}")

        planet.owner = self.faction.name
        planet.structure = "gaiaformer"
        self.gaia_forming.append(planet)
        self.resolve_cost("gaiaformer1")

    def upgrade(self, gp, rnd):
        """Upgrade a built structure to another structure.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.
        """

        print("\nYou want to upgrade a structure.")

        print(
            "Please select the planet with the structure you want to "
            "upgrade."
        )
        # TODO filter out the planets with structures which upgrades you can't
        #   afford?
        # TODO more players CRITICAL For every upgrade, check if the opponent
        #   can charge power.

        upgrade_cost = {
            "Mine": [
                "Trading Station --> 3 Credits | 2 Ore",
                "Trading Station --> 6 Credits | 2 Ore"
            ],
            "Trading Station": (
                "Research Lab --> 5 Credits | 3 Ore ; Planetary Institute "
                "--> 6 Credits 4 Ore"
            ),
            "Research Lab": "Academy --> 6 Credits | 6 Ore"
        }

        planets = [
            planet for planet in self.empire
                if planet.type != "Lost Planet"
                and planet.structure != "Planetary Institute"
                and planet.structure != "Academy"
        ]
        # Sort on sector and then on planet num.
        planets.sort(key=lambda planet: (planet.sector, planet.num))
        for i, planet in enumerate(planets, start=1):
            planet_info = (
                f"{i}. Sector: {planet.sector} "
                f"| Structure: {planet.structure} "
                f"| Type: {planet.type} "
                f"| Number: {planet.num} |"
            )

            cost = upgrade_cost[planet.structure]

            # Upgrading to a trading station costs 3 or 6 based on opponents "
            # that are neighbours.
            if planet.structure == "Mine":
                if planet.neighbours:
                    cost = upgrade_cost[planet.structure][0]
                else:
                    cost = upgrade_cost[planet.structure][1]

            print(f"{planet_info} UPGRADE COST: {cost}")
        print(f"{i + 1}. Go back to action selection.")

        # Choose a planet
        while True:
            chosen_planet = input("--> ")
            if chosen_planet in [str(n + 1) for n in range(i)]:
                planet_to_upgrade = planets[int(chosen_planet) - 1]
                break
            elif chosen_planet == f"{i + 1}":
                raise e.BackToActionSelection
            else:
                print("! Please only type one of the available numbers.")
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
                    "! You have already built all your trading stations. "
                    "Please choose a different structure to upgrade."
                )
                raise e.BackToActionSelection("3")

            # TODO faction compatibility, does this work with lantids??
            # Check if the player is a neighbour with another player. A
            # neighbour is within range 2 of the player.
            if planet_to_upgrade.neighbours:
                credit_cost = 3
            else:
                credit_cost = 6

            # Check if the player has enough credits or ore to upgrade this
            # structure.
            if self.faction.credits < credit_cost or self.faction.ore < 2:
                print(
                    "! You don't have enough credits or ore to upgrade this "
                    "Mine into a Trading Station. Please choose a different "
                    "structure."
                )
                raise e.BackToActionSelection("3")

            self.resolve_cost(f"credits{credit_cost}")
            self.resolve_cost(f"ore2")
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

        # TODO faction compatibility CRITICAL this fails with the Bescods
        # faction which has the academy and planetary institure swapped.
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
                    print("! Please only type one of the available numbers.")
                    continue

            if new_structure == "Planetary Institute":
                # Check if the planetary institute is not placed yet.
                if (
                    self.faction.planetary_institute_built
                        == self.faction.planetary_institute_max
                ):
                    print(
                        "! You have already built your Planetary Institute. "
                        "Please choose a different structure to upgrade to."
                    )
                    raise e.BackToActionSelection("3")

                # Check if the player has enough credits or ore to upgrade this
                # structure into a Planetary Institute.
                if self.faction.credits < 6 or self.faction.ore < 4:
                    print(
                        "! You don't have enough credits or ore to upgrade this "
                        "Trading Station into a Planetary Institute. "
                        "Please choose a different structure."
                    )
                    raise e.BackToActionSelection("3")

                self.resolve_cost("credits6")
                self.resolve_cost("ore4")
                planet_to_upgrade.structure = (
                    upgrade_options["Trading Station"][0]
                )
                self.faction.trading_station_built -= 1
                self.faction.planetary_institute_built += 1
                new = "Planetary Institute"

                # TODO faction compatibility CRITICAL test that this will work
                #   with the Bescod faction.
                # Check if the current round awards points for upgrading to a
                # Planetary Institute.
                if rnd.goal == "planetaryacademy":
                    reason = "Because of the round"
                    self.resolve_gain(f"vp{rnd.vp}", reason)

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
                        "! You have already built all of your Research labs. "
                        "Please choose a different structure to upgrade to."
                    )
                    raise e.BackToActionSelection("3")

                # Check if the player has enough credits or ore to upgrade this
                # structure into a Research Lab.
                if self.faction.credits < 5 or self.faction.ore < 3:
                    print(
                        "! You don't have enough credits or ore to upgrade this "
                        "Trading Station into a Research Lab. "
                        "Please choose a different structure."
                    )
                    raise e.BackToActionSelection("3")

                # Only if below doesn't raise any exceptions will the player
                # pay for the structure.
                self.resolve_technology_tile(gp.research_board, rnd, gp)

                self.resolve_cost("credits5")
                self.resolve_cost("ore3")
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
                    "! You have already built all of your Academy's. "
                    "Please choose a different structure to upgrade to."
                )
                raise e.BackToActionSelection("3")

            # Check if the player has enough credits or ore to upgrade this
            # structure.
            if self.faction.credits < 6 or self.faction.ore < 6:
                print(
                    "! You don't have enough credits or ore to upgrade this "
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
                        print(
                            "! Please only type one of the available numbers."
                        )
                        continue

            elif not self.faction.academy_income[0]:
                chosen_academy = self.faction.academy_income
            elif not self.faction.academy_special[0]:
                chosen_academy = self.faction.academy_special

            # Only if below doesn't raise any exceptions will the player pay
            # for the structure.
            self.resolve_technology_tile(gp.research_board, rnd, gp)

            # Set the built property of the chosen academy to true.
            chosen_academy[0] = True
            self.resolve_cost("credits6")
            self.resolve_cost("ore6")
            planet_to_upgrade.structure = upgrade_options["Research Lab"]
            self.faction.research_lab_built -= 1
            self.faction.academy_built += 1
            new = "Academy"

            # Check if the current round awards points for upgrading to an
            # Academy.
            if rnd.goal == "planetaryacademy":
                reason = "Because of the round"
                self.resolve_gain(f"vp{rnd.vp}", reason)

        else:
            # A Planetary Institute and an Academy can't be upgraded
            a_an = "an"
            structure = planet_to_upgrade.structure
            if structure == "Planetary Institute":
                a_an = "a"
            print(
                f"! You can't upgrade {a_an} {structure}. "
                "Please choose a different structure."
            )
            raise e.BackToActionSelection("3")
        print(
            f"You have upgraded your {old} on the {planet_to_upgrade.type} "
            f"planet in sector {planet_to_upgrade.sector} to a {new}."
        )

    def resolve_technology_tile(self, research_board, rnd, gp, pq=False):
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
                print("! Please only type one of the available numbers.")
                continue

            if isinstance(selected_tile, AdvancedTechnology):
                # Check that the player has any standard technology available.
                if not self.standard_technology:
                    print(
                        "! To take an advanced technology, you need to have a "
                        "standard technology available to place your advanced "
                        "technology tile on. Please choose a different tile."
                    )
                    continue

                # Check if the player has a federation token with the green
                # side up.
                if not "green" in [fed.state for fed in self.federations]:
                    print(
                        "! You need a federation token with the green side up "
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
                        print(
                            "! Please only type one of the available numbers."
                        )
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
                    self.research(research_board, rnd, gp, True)
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
                    self.research(research_board, rnd, gp, track_num)
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

    def federation(self, gp, rnd):
        """Function for forming a federation.

        Args:
            gp: GaiaProject main game object.
            rnd: Active Round object.
        """

        # TODO SOMEDAY this function only gives a federation tile now.
        #   It doesn't set the federation property of planets and doesn't place
        #   satellites on spaces, but just keeps track of total satellites.
        # TODO MOST STRUCTURES IN FEDERATIONS end scoring tile must be done
        # manually right now.
        # TODO faction compatibility IVITS pay qic to pay for federations.
        print(
            "\nUse your own judgement when forming a Federation as this is "
            "not yet implemented.\nHow many satellites did forming your "
            "federation take? Forming a Federation costs Power Tokens."
        )

        while True:
            amount = input("--> ")

            try:
                amount = int(amount)
            except ValueError:
                print("! Please only type a number.")

            if not self.resolve_cost(f"powertoken{amount}"):
                print(
                    "! You don't have enough Power Tokens to make that "
                    "Federation. Please make a Federation that requires less "
                    "satellites."
                )
                continue
            break

        print(
            "\nPlease type your chosen Federation token's corresponding "
            "number."
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
                print("! Please only type one of the available numbers.")
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

    def research(self, research_board, rnd, gp, tech_tile=False):
        """Function for doing the Research action.

        Args:
            research_board: Research object
            rnd: Active Round object
            gp: GaiaProject main game object.
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
            raise e.InsufficientKnowledgeError(
                "! You don't have enough knowledge to research. Please "
                "choose a different action."
            )

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
                print("! Please only type 1-7")
                continue

            track_choice = int(track_choice)
            current_level = levels[track_choice - 1]
            try:
                research_board.tech_tracks[track_choice - 1] \
                    .research(
                        current_level, self, track_choice - 1, gp, rnd
                    )
            except e.NoFederationTokensError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "! You have no federation tokens so you can't advance "
                        "on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.NoFederationGreenError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "! You have no federation token with the green side "
                        "up left so you can't advance on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.NoResearchPossibleError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "! You are already at the maximum level of 5 so you "
                        "can't advance on the "
                        f"{research_board.tech_tracks[track_choice - 1].name} "
                        "track."
                    )
                print(ex)
                continue
            except e.Level5IsFullError as ex:
                if isinstance(tech_tile, str):
                    raise e.ResearchError(
                        "! Another player is already on level 5. Only one "
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
            self.resolve_cost("knowledge4")
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

    def pq(self, gp, rnd):
        """Power and Q.I.C. action function.

        Args:
            gp: GaiaProject class.
            rnd: Active Round object.

        TODO:
            Perhaps make the power/qic cost text summary more readable.
            Show which actions are still available this round??
            If the player wants to take for example the 5. Gain 2 Knowledge
                for 4 Power action, but is already at max (15 knowledge) or
                unable to receive the full amount of 2 (if he/she is at 14)
                is that action allowed?? For now i don't allow former, but
                allow latter.
        """

        intro = (
            "\nYou want to take a Power or Q.I.C. action. Please type the "
            "number of your action."
        )
        power = "Power actions:"
        knowledge3 = "1. For 7 Power gain 3 Knowledge."
        terraform2 = "2. For 5 Power gain 2 Terraforming steps."
        ore2 = "3. For 4 Power gain 2 Ore."
        credits7 = "4. For 4 Power gain 7 Credits."
        knowledge2 = "5. For 4 Power gain 2 Knowledge."
        terraform1 = "6. For 3 Power gain 1 Terraforming step."
        powertoken2 = "7. For 3 Power gain 2 Power Tokens."
        qic_action = "Q.I.C. actions:"
        tech_tile = "8. For 4 Q.I.C. gain a technology tile."
        score_fed_token = (
            "9. For 3 Q.I.C. score one of your Federation Tokens again."
        )
        vp_for_ptypes = (
            "10. For 2 Q.I.C. gain 3 VP and 1 VP for every different planet "
            "type."
        )
        cancel = "11. Go back to action selection."

        while True:
            # Summary of resources
            resources = "Your resources are:"
            vp = f"Victory points: {self.vp}"
            credits_ = f"Credits: {self.faction.credits}"
            ore = f"Ore: {self.faction.ore}"
            knowledge = f"Knowledge: {self.faction.knowledge}"
            qic = f"Q.I.C.: {self.faction.qic}"
            power_1 = f"Power in bowl 1: {self.faction.bowl1}"
            power_2 = f"Power in bowl 2: {self.faction.bowl2}"
            power_3 = f"Power in bowl 3: {self.faction.bowl3}"

            # Fill the string from the left with spaces until it's as long as
            # the longest string in the column (in this case the intro variable
            # is the longest string) to line up both columns and add 7 spaces
            # between columns.
            filler = lambda text_left: " " * (len(intro) - len(text_left) + 7)

            prompt = (
                f"{intro}{filler(intro.lstrip())}{resources}\n"
                f"{power}{filler(power)}{vp}\n"
                f"{knowledge3}{filler(knowledge3)}{credits_}\n"
                f"{terraform2}{filler(terraform2)}{ore}\n"
                f"{ore2}{filler(ore2)}{knowledge}\n"
                f"{credits7}{filler(credits7)}{qic}\n"
                f"{knowledge2}{filler(knowledge2)}{power_1}\n"
                f"{terraform1}{filler(terraform1)}{power_2}\n"
                f"{powertoken2}{filler(powertoken2)}{power_3}\n"
                f"{qic_action}\n"
                f"{tech_tile}\n"
                f"{score_fed_token}\n"
                f"{vp_for_ptypes}\n"
                f"{cancel}"
            )
            print(prompt)
            action = input("--> ")

            if action == "11":
                raise e.BackToActionSelection
            elif not action in [str(act) for act in range(1, 11)]:
                print("! Please type the action's corresponding number.")
                continue

            # Check if the action is available
            if not self.pq_availabe(gp.research_board, int(action)):
                continue

            if action == "1":
                # Gain 3 knowledge for 7 power.

                if self.faction.knowledge >= self.faction.knowledge_max:
                    print(
                        "! You are already at the maximum Knowledge you can "
                        "have. Please choose a different Power/Q.I.C. Action."
                    )
                    continue

                if not self.enough_power(7):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{7}")
                self.resolve_gain("knowledge3")

            elif action == "2":
                # Gain 2 terraforming steps for 5 power and build a mine.

                if not self.enough_power(5):
                    continue

                try:
                    self.mine(gp, rnd, 2, "pq")
                except e.BackToActionSelection:
                    # Players want to do a different pq action.
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{5}")

            elif action == "3":
                # Gain 2 ore for 4 power.

                if self.faction.ore >= self.faction.ore_max:
                    print(
                        "! You are already at the maximum Ore you can have. "
                        "Please choose a different Power/Q.I.C. Action."
                    )
                    continue

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{4}")
                self.resolve_gain("ore2")

            elif action == "4":
                # Gain 7 credits for 4 ore.

                if self.faction.credits >= self.faction.credits_max:
                    print(
                        "! You are already at the maximum Credits you can "
                        "have. Please choose a different Power/Q.I.C. Action."
                    )
                    continue

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{4}")
                self.resolve_gain("credits7")

            elif action == "5":
                # Gain 2 knowledge for 4 power.

                if self.faction.knowledge == self.faction.knowledge:
                    print(
                        "! You are already at the maximum Knowledge you can "
                        "have. Please choose a different Power/Q.I.C. Action."
                    )
                    continue

                if not self.enough_power(4):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{4}")
                self.resolve_gain("knowledge2")

            elif action == "6":
                # Gain 1 terraforming step for 3 power and build a mine.

                if not self.enough_power(3):
                    continue

                try:
                    self.mine(gp, rnd, 2, "pq")
                except e.BackToActionSelection:
                    # Player want to do a different pq action.
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{3}")

            elif action == "7":
                # Gain 2 powertokens for 3 power.

                if not self.enough_power(3):
                    continue

                gp.research_board.pq_actions[int(action)] = False
                self.resolve_cost(f"power{3}")
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
                self.resolve_cost("qic4")

            elif action == "9":
                # Re-score a federation token in the players possession.

                if not self.enough_qic(3):
                    continue

                if not self.federations:
                    print(
                        "! You don't have any federation tiles to score again. "
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
                        print(
                            "! Please only type one of the available numbers."
                        )
                        continue

                if not chosen:
                    continue

                self.resolve_gain(
                    self.federations[int(chosen_token) - 1].reward,
                    "Because of the Federation token"
                )
                self.resolve_cost("qic3")

            elif action == "10":
                # Gain 3 vp immediately and 1 point for every unique planet
                # type that you own.

                if not self.enough_qic(2):
                    continue

                types = len({planet.type for planet in self.empire})

                self.resolve_gain(f"vp{3 + types}")
                self.resolve_cost("qic2")

            return

    def enough_power(self, amount):
        # Check if there is enough power in bowl 3.
        if not self.faction.bowl3 >= amount:
            print(
                "! You don't have enough power to do this action. "
                "Please choose a different Power/Q.I.C. Action."
            )
            return False
        return True

    def enough_qic(self, amount):
        # Check the player has enough qic's
        if not self.faction.qic >= amount:
            print(
                "! You don't have enough Q.I.C.'s to do this action. "
                "Please choose a different Power/Q.I.C. Action."
            )
            return False
        return True

    def pq_availabe(self, research_board, num):
        # Check if the action is still available.
        if not research_board.pq_actions[num]:
            print(
                "! This power action is already used this round. "
                "Please choose a different Power/Q.I.C. Action."
            )
            return False
        return True

    def special(self, universe, rnd):
        """Function for Special (Orange) actions."""

        # TODO faction compatibility CRITICAL make sure this works with
        #   factions that get a special action when their planetary institute
        #   is built.

        special_actions = []
        if self.booster.special:
            if not self.booster.used:
                special_actions.append(self.booster)

        for standard_tech in self.standard_technology:
            if standard_tech.when == "special":
                if not standard_tech.used:
                    special_actions.append(standard_tech)

        for advanced_tech in self.advanced_technology:
            if advanced_tech.when == "special":
                if not advanced_tech.used:
                    special_actions.append(advanced_tech)

        academy = self.faction.academy_special
        if academy[0]:
            if not academy[2]:
                special_actions.append(f"Academy: {academy[1]}")

        if not special_actions:
            print(
                "! You don't have any Special (Orange) actions available. "
                "Please choose a different action."
            )
            raise e.BackToActionSelection

        print(
            "\nPlease type your chosen Special action's corresponding number."
        )
        for i, spec in enumerate(special_actions, start=1):
            print(f"{i}. {spec}")
        print(f"{i + 1}. Go back to action selection.")

        while True:
            chosen_special = input("--> ")
            if chosen_special in [str(n + 1) for n in range(i)]:
                special = special_actions[int(chosen_special) - 1]
                break
            elif chosen_special == f"{i + 1}":
                raise e.BackToActionSelection
            else:
                print("! Please only type one of the available numbers.")
                continue

        # The special action comes from an Academy.
        if isinstance(special, str):
            self.resolve_gain(
                self.faction.academy_special[1],
                "Because of the special action"
            )
            self.faction.academy_special[2] = True
        # The special action comes from a technology tile or booster.
        else:
            if isinstance(special, Booster):
                try:
                    special.resolve_effect(self, universe, rnd)
                except (
                    e.NoGaiaFormerError,
                    e.NotEnoughPowerTokensError
                )as ex:
                    print(ex)
                    raise e.BackToActionSelection("7")
                except e.BackToActionSelection:
                    raise e.BackToActionSelection("7")
            else:
                special.resolve_effect(self)

    def pass_(self, gp, rnd):
        """Function for passing."""
        # TODO MINOR allow player to go back to action selection in case of a
        #   miss click and the player doesn't want to pass yet??

        # Check if no free actions have been taken. Player can't pass
        # if free action have been taken.
        if self.free_actions:
            print(
                "! You have taken free actions so you aren't allowed to pass. "
                "Please undo your free actions if you wish to pass."
            )
            raise e.BackToActionSelection()

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
                    # Add old booster to the right of the unused boosters.
                    gp.scoring_board.boosters.append(self.booster)

                    # Set own booster to the chosen booster.
                    self.booster = gp.scoring_board.boosters.pop(
                        int(booster_choice) - 1
                    )
                    break
                else:
                    print("! Please only type one of the available numbers.")
                    continue

        gp.passed += 1
        self.passed = True

        if old_booster.vp:
            old_booster.resolve_effect(self)
        if round_number != 6:
            print(f"Your new booster is {self.booster}.")

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
        if round_number != 6:
            if gp.passed == 1:
                gp.players.remove(self)
                gp.players.insert(0, self)
                print("You start first next round.")

    def free(self):
        """Function for exchanging resources as a free action.

        TODO:
            Sort out all the free actions that the player can't afford.
        """

        free_actions = self.faction.free_actions

        pattern = re.compile(r"(\D+)(\d+)")
        while True:
            intro = (
                "\nPlease type the number of the resource you want to "
                "exchange."
            )

            reminder = (
                "Remember that you can only take free actions if you will "
                "do an action!"
            )

            # Summary of resources
            resources = "Your resources are:"
            credits_ = f"Credits: {self.faction.credits}"
            ore = f"Ore: {self.faction.ore}"
            knowledge = f"Knowledge: {self.faction.knowledge}"
            qic = f"Q.I.C.: {self.faction.qic}"
            power_1 = f"Power in bowl 1: {self.faction.bowl1}"
            power_2 = f"Power in bowl 2: {self.faction.bowl2}"
            power_3 = f"Power in bowl 3: {self.faction.bowl3}"

            # Fill the string from the left with spaces until it's as long as
            # the longest string in the row (in this case the intro variable is
            # the longest string). To line up both columns and add 7 spaces
            # between columns.
            # "9. Discard 1 Power token from bowl 2 to charge 1 Power from "
            # bowl 2 to bowl 3." is 77 characters long which is the longest
            # string we need to subtract from to fill the rest to the same
            # length.
            filler = (lambda text_left: " " * (77 - len(text_left) + 7))

            summary = [
                ore,
                knowledge,
                qic,
                power_1,
                power_2,
                power_3,
            ]
            print(f"{intro}{filler(intro.strip())}{resources}")
            print(f"{reminder}{filler(reminder)}{credits_}")

            for i, free_action in enumerate(free_actions, start=1):

                # If the exchanged resource is a string.
                if isinstance(free_actions[free_action], str):
                    free_cost_match = pattern.match(free_action)
                    free_exchange_match = pattern.match(
                        free_actions[free_action]
                    )

                    # f_c_a is free_cost (payment amount to be done). (1)
                    f_c_a = f" {free_cost_match.group(2)}"

                    # f_c is free_cost (payment type to be done). (power)
                    f_c = f" {free_cost_match.group(1).capitalize()}"

                    # f_e_a free_exchange (resource amount to be received).
                    # (1).
                    f_e_a = f" {free_exchange_match.group(2)}"

                    # f_e is free_exchange (resource type to be received).
                    # (credits).
                    f_e = f" {free_exchange_match.group(1).capitalize()}"

                    pay = " Pay"
                    for_ = " for"

                    # Stuff for making the cost prettier.
                    if f_c == " Qic":
                        f_c = " Q.I.C."

                    # Stuff for making the exchange prettier.
                    if f_e == " Credits" and f_e_a == " 1":
                        f_e = " Credit"
                    elif f_e == " Qic":
                        f_e = " Q.I.C"
                    elif f_e == " Powertoken":
                        f_e = " Power Token"

                # Else the exchanged resource self.move_from_bowl2_to_bowl3
                # will be done by a function.
                else:
                    pay = ""
                    f_c_a = ""
                    f_c = f" {free_action}"
                    for_ = " to "
                    f_e_a = ""
                    f_e = "charge 1 Power from bowl 2 to bowl 3"

                total = f"{i}.{pay}{f_c_a}{f_c}{for_}{f_e_a}{f_e}."
                if i < 7:
                    print(f"{total}{filler(total)}{summary[i - 1]}")
                else:
                    print(f"{total}")
            print(
                f"{i + 1}. Undo all Free actions taken this turn.\n"
                f"{i + 2}. Go back to action selection."
            )

            chosen_free = input("--> ")
            if chosen_free in [str(n + 1) for n in range(i)]:
                cost = list(free_actions.keys())[int(chosen_free) - 1]
                cost_exchange = free_actions[cost]
            elif chosen_free == f"{i + 1}":
                if self.free_actions:
                    self.undo_free()
                else:
                    print("You haven't taken any free actions this turn.")
                continue
            elif chosen_free == f"{i + 2}":
                raise e.BackToActionSelection
            else:
                print("! Please only type one of the available numbers.")
                continue

            # Make the exchange.
            if isinstance(cost_exchange, str):
                # if player is maxed out of the gained resource so i assume
                # the free action can't be taken.
                pattern2 = r"\D+"
                exchange_check = re.search(pattern2, cost_exchange).group(0)
                if exchange_check in ["knowledge", "ore", "credits"]:
                    if eval(f"self.faction.{exchange_check} "
                            f">= self.faction.{exchange_check}_max"):
                        # Call this function because it will return a nice
                        # message if the player is full on resources.
                        self.resolve_gain(cost_exchange)
                        print(
                            "Nothing was exchanged. Please choose a "
                            "different Free action."
                        )
                        continue

                if self.resolve_cost(cost):
                    self.resolve_gain(cost_exchange)
                    self.free_actions.append([cost, cost_exchange])
                else:
                    cost_type = re.search(pattern2, cost).group(0).capitalize()

                    print(
                        f"! You don't have enough {cost_type}.\n"
                        "Nothing was exchanged. Please choose a different "
                        "Free action."
                    )
                    continue
            # The player chose to discard 1 powertoken from bowl 2 to charge
            # 1 power from bowl 2 to bowl 3.
            else:
                # Check if the player has 2 tokens available to do this free
                # action.
                if self.faction.bowl2 > 1:
                    cost_exchange()
                    self.free_actions.append(
                        ["discard1", "power1"]
                    )
                else:
                    print("! You don't have enough Power Tokens in bowl 2.")

    def clean_up(self):
        # Reset all the Special actions. For simplicity do this whether it was
        # used or not, because i think most of the time they will all be used
        # anyway.
        if self.booster.special:
            self.booster.used = False

        for standard_tech in self.standard_technology:
            if standard_tech.when == "special":
                standard_tech.used = False

        for advanced_tech in self.advanced_technology:
            if advanced_tech.when == "special":
                advanced_tech.used = False

        self.faction.academy_special[2] = False


if __name__ == "__main__":
    test = Player("hadsch halla")
    print(test.faction.home_type)
