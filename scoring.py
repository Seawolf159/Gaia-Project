import random


class Booster:

    def __init__(self, img, income1=False, income2=False,
                 special=False, vp=False):
        self.img = img
        self.income1 = income1
        self.income2 = income2
        self.special = special
        self.vp = vp

    def __str__(self):
        return f"{self.income1 or self.special or self.vp} | {self.income2}"


class RoundScoring:

    def __init__(self, img, vp, goal, first_half, second_half):
        self.img = img
        self.vp = vp
        self.goal = goal
        self.first_half = first_half
        self.second_half = second_half

    def __str__(self):
        return self.goal


class EndScoring:

    def __init__(self, img, goal, neutral):
        self.img = img
        self.goal = goal

        # Neutral player in 2 player game.
        self.neutral = neutral

    def __str__(self):
        return self.goal


class Scoring:
    """Scoring board."""

    def __init__(self):

        # These lists are filled in the randomise functions.
        # Boosters
        self.boosters = []

        # Round scoring
        self.rounds = []  # Filled in the randomise_scoring function.

        # End scoring
        self.end_scoring = []  # Filled in the randomise_scoring function.

    def randomise_boosters(self, players):
        boosters = [
            Booster("BOOknw.png", income1="ore1", income2="knowledge1"),
            Booster("BOOpwt.png", income1="powertoken2", income2="ore1"),
            Booster("BOOqic.png", income1="credits2", income2="qic1"),
            Booster("BOOter.png", special="terraforming1", income2="credits2"),
            Booster("BOOnav.png", special="range3", income2="power2"),
            Booster("BOOmin.png", vp="mine1", income2="ore1"),
            Booster("BOOtrs.png", vp="trade2", income2="ore1"),
            Booster("BOOlab.png", vp="researchlab3", income2="knowledge1"),
            Booster("BOOpia.png", vp="planetaryacademy4", income2="power4"),
            Booster("BOOgai.png", vp="gaia1", income2="credits4"),
        ]

        for _ in range(players + 3):
            self.boosters.append(
                boosters.pop(random.randrange(len(boosters)))
            )

    def randomise_scoring(self):
        round_tiles = [
            RoundScoring("RNDter.png", 2, "terraforming", 4, 6),
            RoundScoring("RNDstp.png", 2, "research", 2, 4),
            RoundScoring("RNDmin.png", 2, "mine", 4, 6),
            RoundScoring("RNDfed.png", 5, "fedtoken", 0, 5),
            RoundScoring("RNDtrs3.png", 3, "trade", 3, 6),
            RoundScoring("RNDtrs4.png", 4, "trade", 3, 6),
            RoundScoring("RNDgai3.png", 3, "gaiamine", 2, 2),
            RoundScoring("RNDgai4.png", 4, "gaiamine", 2, 2),
            RoundScoring("RNDpia.png", 5, "planetaryacademy", 0, 5),
            RoundScoring("RNDpia.png", 5, "planetaryacademy", 0, 5)
        ]

        for _ in range(6):
            self.rounds.append(
                round_tiles.pop(random.randrange(len(round_tiles)))
            )

        end_scoring_tiles = [
            EndScoring("FINfed.png", "structures_federation", 10),
            EndScoring("FINbld.png", "structures", 11),
            EndScoring("FINtyp.png", "planet_types", 5),
            EndScoring("FINgai.png", "gaia_planets", 4),
            EndScoring("FINsec.png", "sectors", 6),
            EndScoring("FINsat.png", "satellites", 8)
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
