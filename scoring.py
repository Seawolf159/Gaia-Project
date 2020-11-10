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

    def end_game_scoring(self, gp):
        # TODO MORE PLAYERS CRITICAL Only works while playing against Automa.
        # TODO MINOR pretty print end scoring tile names.

        print("\nEnd Scoring.")
        # Score points from end scoring tiles.
        for end_tile in self.end_scoring:
            print(f"Now scoring {end_tile.goal}:")

            # Used for determining the winner and for shared places.
            scores = []
            for player in gp.players:
                if end_tile.goal == "structures_federation":
                    if type(player).__name__ == "Automa":
                        end_tile_score = len(player.empire) - 1
                        scores.append([player, end_tile_score])
                    else:
                        print(
                            f"{player.faction.name}, how many structures that "
                            "are part of a Federation do you have?"
                        )

                        while True:
                            end_tile_score = input("--> ")

                            try:
                                end_tile_score = int(end_tile_score)
                            except ValueError:
                                print("Please only type a number.")
                                continue
                            else:
                                break

                        scores.append([player, end_tile_score])

                elif end_tile.goal == "structures":
                    end_tile_score = len(player.empire)
                    scores.append([player, end_tile_score])

                elif end_tile.goal == "planet_types":
                    end_tile_score = len(
                        {planet.type for planet in player.empire}
                    )
                    scores.append([player, end_tile_score])

                elif end_tile.goal == "gaia_planets":
                    end_tile_score = len(
                        [
                            planet for planet in player.empire
                                if planet.type == "Gaia"
                                # TODO CRITICAL test that it doesn't include
                                # planets with gaiaformers.
                                and planet.strucure != "gaiaformer"
                        ]
                    )
                    scores.append([player, end_tile_score])

                elif end_tile.goal == "sectors":
                    end_tile_score = len(
                        {planet.sector for planet in player.empire}
                    )
                    scores.append([player, end_tile_score])

                elif end_tile.goal == "satellites":
                    if type(player).__name__ == "Automa":
                        message = (
                            "How many satellites does the Automa have?"
                        )
                    else:
                        message = (
                            f"{player.faction.name}, how many satellites do "
                            "you have?"
                        )

                    print(message)
                    while True:
                        end_tile_score = input("--> ")

                        try:
                            end_tile_score = int(end_tile_score)
                        except ValueError:
                            print("Please only type a number.")
                            continue
                        else:
                            break
                    scores.append([player, end_tile_score])

            place123 = False
            place12 = False
            place1 = False
            place23 = False
            place2 = False
            place3 = False

            neutral_score = end_tile.neutral
            scores.append(["Neutral", neutral_score])

            # Sort by score reverse for highest to lowest.
            scores.sort(key=lambda score: score[1], reverse=True)

            # All players are tied.
            if scores[0][1] == scores[1][1] == scores[2][1]:
                place123 = scores
            elif scores[0][1] == scores[1][1]:
                place12 = scores[:2]
            else:
                place1 = scores[0]

            # Players 2 and 3 are tied
            if scores[1][1] == scores[2][1]:
                place23 = scores[1:]
            else:
                place2 = scores[1]
                place3 = scores[2]

            i = 0
            while i < 3:
                player = scores[i][0]
                if player == "Neutral":
                    i += 1
                    continue

                if type(player).__name__ == "Automa":
                    description = "Automa"
                else:
                    description = player.faction.name

                if place123:
                    player.vp += 12
                    print(
                        f"+ {description} has gained 12 Victory "
                        f"Points."
                    )
                elif place12 and i != 2:
                    player.vp += 15
                    print(
                        f"+ {description} has gained 15 Victory "
                        f"Points."
                    )
                elif place1 and i == 0:
                    player.vp += 18
                    print(
                        f"+ {description} has gained 18 Victory "
                        f"Points."
                    )

                if place23 and i > 0:
                    player.vp += 9
                    print(
                        f"+ {description} has gained 9 Victory "
                        f"Points."
                    )
                elif place2 and i == 1:
                    player.vp += 12
                    print(
                        f"+ {description} has gained 12 Victory "
                        f"Points."
                    )
                elif place3 and i == 2:
                    player.vp += 6
                    print(
                        f"+ {description} has gained 6 Victory "
                        f"Points."
                    )

                i += 1

            # Just an empty print for white space between end scoring tiles.
            print()

        # Score points for research track progress and resources.
        print(
            "Now scoring Research track progress and resources. For every "
            "step past level 2 on a research track you get 4 Victory Points.\n"
            "For every 3 Credits, Knowledge, or Ore in any combination, you "
            "get 1 Victory Point."
        )
        for player in gp.players:
            print(
                "\nResearch track progress and resource victory points for "
                f"{player.faction.name}:"
            )
            # If this flag is never set to True, a message telling the player
            # that no points were gained this way will be displayed.
            research_progress = False
            if int(player.terraforming.name[-1]) > 2:
                score = (int(player.terraforming.name[-1]) - 2) * 4
                player.vp += score
                print(f"+ {score} Victory Points from the Terraforming track.")
                research_progress = True

            if int(player.navigation.name[-1]) > 2:
                score = (int(player.navigation.name[-1]) - 2) * 4
                player.vp += score
                print(f"+ {score} Victory Points from the Navigation track.")
                research_progress = True

            if int(player.a_i.name[-1]) > 2:
                score = (int(player.a_i.name[-1]) - 2) * 4
                player.vp += score
                print(
                    f"+ {score} Victory Points from the Artificial "
                    "Intelligence track."
                )
                research_progress = True

            if int(player.gaia_project.name[-1]) > 2:
                score = (int(player.gaia_project.name[-1]) - 2) * 4
                player.vp += score
                print(f"+ {score} Victory Points from the Gaia Project track.")
                research_progress = True

            if int(player.economy.name[-1]) > 2:
                score = (int(player.economy.name[-1]) - 2) * 4
                player.vp += score
                print(f"+ {score} Victory Points from the Economy track.")
                research_progress = True

            if int(player.science.name[-1]) > 2:
                score = (int(player.science.name[-1]) - 2) * 4
                player.vp += score
                print(f"+ {score} Victory Points from the Science track.")
                research_progress = True

            if not research_progress:
                print(
                    "No Victory Points were gained through Research progress."
                )

            # Scoring points for resources.
            if type(player).__name__ != "Automa":
                # Check if the player has any resources left to be scored.
                total_resources = player.faction.credits \
                    + player.faction.ore \
                    + player.faction.knowledge
                if total_resources >= 3:
                    score = total_resources // 3
                    player.vp += score
                    print(
                        f"+ {score} Victory Points were gained through "
                        "Resources."
                    )
                else:
                    print(
                        "No Victory Points were gained through Resources."
                    )

            # Just an empty print for white space between player scoring.
            print()

        total_score = []
        for player in gp.players:
            total_score.append([player, player.vp])
        # Sort by victory points in reverse for highest to lowest.
        total_score.sort(key=lambda total: player.vp, reverse=True)

        # TODO more players. This only works when playing against Automa.
        if total_score[0][1] == total_score[1][1]:
            print(
                f"It's a draw! You both got {total_score [0][1]} Victory "
                "Points."
            )
        else:
            print(
                f"{total_score[0][0].faction.name} finished first with "
                f"{total_score[0][0].vp} and {total_score[1][0].faction.name}."
                f" finished second with {total_score[1][0].vp}."
            )

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
