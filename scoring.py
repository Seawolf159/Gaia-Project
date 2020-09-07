class RoundScoring:

    def __init__(self, vp, goal, first_half, second_half):
        self.vp = 0
        self.goal = goal
        self.first_half = first_half
        self.second_half = second_half


class EndScoring:

    def __init__(self):
        self.goal = False



class Scoring:
    """Scoring board."""

    def __init__(self):
        self.terraforming = RoundScoring(2, "terraforming", 4, 6)
        self.research = RoundScoring(2, "research", 2, 4)
        self.mine = RoundScoring(2, "mine", 4, 6)
        self.fedtoken = RoundScoring(5, "fedtoken", 0, 5)
        self.trade3 = RoundScoring(3, "trade3", 3, 6)
        self.trade4 = RoundScoring(4, "trade4", 3, 6)
        self.gaiamine3 = RoundScoring(3, "gaiamine3", 2, 2)
        self.gaiamine4 = RoundScoring(4, "gaiamine4", 2, 2)
        self.planetaryacademy1 = RoundScoring(5, "planetaryacademy", 0, 5)
        self.planetaryacademy2 = RoundScoring(5, "planetaryacademy", 0, 5)


    def randomise_scoring(self):
        pass
