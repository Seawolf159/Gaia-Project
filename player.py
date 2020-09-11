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
        faction_name: f"{self.faction.name}:\n"
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
            "1": mine,
            "2": gaia,
            "3": upgrade,
            "4": federation,
            "5": research,
            "6": pq,
            "7": special,
            "8": pass_,
            "9": free
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
                print("Please type the action's corresponding number.")
        else:
            action()

    def first_mine(self, count):
        faction_name: f"{self.faction.name}:\n"
        question = "Where whould you like to place your {count} mine?"

        # TODO make placement function. Choose placement system. Example:
        # say sector number followed by planet colour etc. Or something else?

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

    def free(self):
        pass



if __name__ == "__main__":
    test = Player("hadsch halla")
    print(test.faction.home_type)
