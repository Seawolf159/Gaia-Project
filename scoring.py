import random

import constants as C
import exceptions as e


class Booster:

    def __init__(self, img, income1=False, income2=False,
                 special=False, vp=False):
        self.img = img
        self.income1 = income1
        self.income2 = income2
        self.special = special
        self.vp = vp
        self.used = False  # Only used on boosters with special actions.

    def resolve_effect(self, player):
        """Function for giving the player points when passing.

        Args:
            player: Player object of the player that passed.
        """

        reason = "Because of your old booster"
        if self.vp == "mine1":
            mines = player.faction.mine_built
            if player.lost_planet:
                mines += 1
            player.resolve_gain(f"vp{mines}", reason)
        elif self.vp == "trade2":
            trading_stations = player.faction.trading_station_built
            player.resolve_gain(f"vp{trading_stations * 2}", reason)
        elif self.vp == "researchlab3":
            research_labs = player.faction.research_lab_built
            player.resolve_gain(f"vp{research_labs * 3}", reason)
        elif self.vp == "planetaryacademy4":
            academys = player.faction.academy_built
            planetary_institutes = player.faction.planetary_institute_built
            total = academys + planetary_institutes
            player.resolve_gain(f"vp{total * 4}", reason)
        elif self.vp == "gaia1":
            gaia_planets = len(
                [
                    planet for planet in player.empire
                        if planet.type == "Gaia"
                        # TODO CRITICAL test that it doesn't include planets
                        #   with gaiaformers.
                        and planet.structure != "gaiaformer"
                ]
            )
            player.resolve_gain(f"vp{gaia_planets}", reason)

    def __str__(self):
        return (
            f"Booster: {self.income1 or self.special or self.vp} "
            f"| {self.income2}"
        )


class Terraform(Booster):
    """
    More specific class for the gain 1 terraforming step booster
    special action.
    """

    def resolve_effect(self, player, universe, rnd):
        """Receive the reward from doing this boosters special action.

        Args:
            player: Player object of the player that acquired the tile.
            universe: The universe object used in the main GaiaProject class.
            rnd: Active Round object.
        """

        print(
            "You have gained 1 terraforming step. You must now build a mine."
        )
        player.mine(universe, rnd, 1, action="boost_terraform")
        self.used = True


class ExtraRange(Booster):
    """
    More specific class for the gain 3 extra range booster special action.
    """

    def resolve_effect(self, player, universe, rnd):
        """Receive the reward from doing this boosters special action.

        Args:
            player: Player object of the player that acquired the tile.
            universe: The universe object used in the main GaiaProject class.
            rnd: Active Round object.
        """

        print(
            "You have gained 3 extra range. You must now build a Mine or "
            "start a Gaia Project."
        )
        action = "boost_range"

        while True:
            planet = player.choose_planet(universe, action)
            try:
                # Player want to build a mine.
                if planet.type in C.mine_types:
                    player.mine(
                        universe,
                        rnd,
                        extra_range=3,
                        p_chosen=planet,
                        action=action
                    )
                # Player wants to start a gaia Project.
                else:
                    player.gaia(
                        universe,
                        p_chosen=planet,
                        action=action,
                        extra_range=3
                    )
            except e.ExtraRangeError:
                continue

            break

        self.used = True


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
            Terraform(
                "BOOter.png", special="terraforming1", income2="credits2"
            ),
            ExtraRange("BOOnav.png", special="range3", income2="power2"),
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
