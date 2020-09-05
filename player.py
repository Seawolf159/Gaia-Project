from faction import select_faction


class Player:

    def __init__(self, number, faction):
        """

        Args
            number (int): 1 for first 2 for second etc.
            faction (str): name of a faction
                Options to choose from are:
                hadsch halla,
                TODO name all factions and possibly move the options elsewhere
        """
        self.number = number
        self.faction = select_faction(faction.lower())()
        self.score = 10
        self.technology = []
        self.advanced_technology = []
        self.booster = False




if __name__ == "__main__":
    test = Player(1, "hadsch halla")
    print(test.faction.home_type)
