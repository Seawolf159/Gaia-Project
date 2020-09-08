import random


class Booster:

    def __init__(self, income1=False, income2=False, special=False, vp=False):
        self.income1 = income1
        self.income2 = income2
        self.special = special
        self.vp = vp

    def __str__(self):
        return f"{self.income1 or self.special or self.vp} | {self.income2}"


class RoundScoring:

    def __init__(self, vp, goal, first_half, second_half):
        self.vp = 0
        self.goal = goal
        self.first_half = first_half
        self.second_half = second_half

    def __str__(self):
        return self.goal


class EndScoring:

    def __init__(self, goal, neutral):
        self.goal = goal

        # Neutral player in 2 player game.
        self.neutral = neutral

    def __str__(self):
        return self.goal


class Scoring:
    """Scoring board."""

    def __init__(self):

        # These lists are filled in the randomise functions
        # Boosters
        self.boosters = []

        # Round scoring
        self.rounds = []

        # End scoring
        self.end_scoring = []

    def randomise_boosters(self, players):
        boosters = [
            Booster(income1="ore1", income2="knowledge1"),
            Booster(income1="powertoken2", income2="ore1"),
            Booster(income1="credits2", income2="qic1"),
            Booster(special="terraforming", income2="credits2"),
            Booster(special="range3", income2="power2"),
            Booster(vp="mine1", income2="ore1"),
            Booster(vp="trade2", income2="ore1"),
            Booster(vp="researchlab3", income2="knowledge1"),
            Booster(vp="planetaryacademy4", income2="power4"),
            Booster(vp="gaia1", income2="credits4"),
        ]

        for _ in range(players + 3):
            self.boosters.append(
                boosters.pop(random.randrange(len(boosters)))
            )


    def randomise_scoring(self):
        round_tiles = [
            RoundScoring(2, "terraforming", 4, 6),
            RoundScoring(2, "research", 2, 4),
            RoundScoring(2, "mine", 4, 6),
            RoundScoring(5, "fedtoken", 0, 5),
            RoundScoring(3, "trade3", 3, 6),
            RoundScoring(4, "trade4", 3, 6),
            RoundScoring(3, "gaiamine3", 2, 2),
            RoundScoring(4, "gaiamine4", 2, 2),
            RoundScoring(5, "planetaryacademy", 0, 5),
            RoundScoring(5, "planetaryacademy", 0, 5)
        ]

        self.rounds = []
        for _ in range(6):
            self.rounds.append(
                round_tiles.pop(random.randrange(len(round_tiles)))
            )

        end_scoring_tiles = [
            EndScoring("structures_federation", 10),
            EndScoring("structures", 11),
            EndScoring("different_planets", 5),
            EndScoring("gaia planets", 4),
            EndScoring("sectors", 6),
            EndScoring("sattelites", 8)
        ]

        self.end_scoring = [
            end_scoring_tiles.pop(random.randrange(len(end_scoring_tiles))),
            end_scoring_tiles.pop(random.randrange(len(end_scoring_tiles)))
        ]

    def __str__(self):
        boosters = []
        rounds = []
        end_scoring = []

        for booster in self.boosters:
            boosters.append(str(booster))

        for round_ in self.rounds:
            rounds.append(str(round_))

        for end_scoring_ in self.end_scoring:
            end_scoring.append(str(end_scoring_))

        return (
            f"Boosters: {boosters}\n"
            f"Rounds: {rounds}\n"
            f"End scoring: {end_scoring}"
        )


def any_(items):
    for item in items:
        if item:
            return item
