import os
import random

from PIL import Image

from automa import Automa
from federation import FederationToken
from player import Player
from research import Research
from scoring import Scoring
from universe import Universe

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class GaiaProject:
    """Class for combining all the different parts of the game.
    """

    def __init__(self, player1, player2,
                 player3=False, player4=False, automa=False):
        """Create a new game of GaiaProject

        Args:
            player1-4 (str): Name of the faction the corresonding player is
                playing.
            automa (bool): whether or not you are playing against the automa.
        """

        # more players TODO federations have 3 of each type in 3+ player games
        self.federation_tokens = [
            FederationToken("FEDvps.png", 2, "vp12", "grey"),
            FederationToken("FEDqic.png", 2, ["vp8", "qic1"], "green"),
            FederationToken("FEDore.png", 2, ["vp7", "ore2"], "green"),
            FederationToken("FEDcre.png", 2, ["vp7", "credits6"], "green"),
            FederationToken("FEDknw.png", 2, ["vp6", "knowledge2"], "green")
        ]

        # TODO FINAL FIX THIS MESS. Factions are chosen last during setup.
        # But this makes the setup faster for testing purposes.
        self.setup(player1, player2, player3, player4, automa)

    def setup(self, player1, player2,
              player3=False, player4=False, automa=False):
        """Setup all the pieces of the game

        Args:
            player1-4 (str): Name of the faction the corresonding player is
                playing.
        """

        # A list with all the player objects in turn order.
        self.players = []
        self.round = 1

        self.player1 = Player(player1)
        self.players.append(self.player1)
        if automa:
            self.player2 = Automa(player2)
            self.players.append(self.player2)
        else:
            self.player2 = Player(player2)
            self.players.append(self.player2)

        if player3:
            self.player3 = Player(player3)
            self.players.append(self.player3)
        if player4:
            self.player4 = Player(player4)
            self.players.append(self.player4)

        self.research_board = Research()
        self.scoring_board = Scoring()

        # Order of setup according to rules:
        # 1. Choose first player (Against the automa, the human goes first).
        # 2. Let the last player assemble the game board (or just some final
        #    rotation of tiles) or just do it together.
        # TODO generate the universe (first game default universe at first)
        self.create_universe()

        # 3. Randomly place the standard and advanced technology tiles.
        self.research_board.randomise_tech_tiles()

        # 4. Randomly select one federation token for the terraforming research
        #    track (Against the automa each type of token only has 2 pieces).
        terraforming_fed_token = random.choice(self.federation_tokens)
        terraforming_fed_token.count -= 1
        self.research_board.terraforming.level5.reward = terraforming_fed_token

        # 5. Randomly place 6 round scoring and 2 final scoring tiles on the
        #    scoring board.
        self.scoring_board.randomise_scoring()

        # 6. Randomly select {amount of players} + 3 booster tiles.
        player_count = 0
        if player1:
            player_count += 1
        if player2:
            player_count += 1
        if player3:
            player_count += 1
        if player4:
            player_count += 1

        self.scoring_board.randomise_boosters(player_count)

        # CIRITICAL TODO uncomment line below when finished. Commented because
        #   it kept changing the img file which is not necessary right now.
        # Load the setup into an image to see it more easily as a human.
        # self.visual_setup()

        # TODO Let player choose faction after seeing setup.
        # Start of the game:
        # Choose faction (start with first player and going clockwise):

        # Place players on level 0 of all research boards and check if they
        # start on level 1 of any of them. Add the level to the player object
        # for easy acces and insert the faction name of the player in the level
        # object for printing.
        for p in self.players:
            name = p.faction.name

            p.terraforming = self.research_board.terraforming.level0
            self.research_board.terraforming.level0.players.append(name)

            p.navigation = self.research_board.navigation.level0
            self.research_board.navigation.level0.players.append(name)

            p.a_i = self.research_board.a_i.level0
            self.research_board.a_i.level0.players.append(name)

            p.gaia_project = self.research_board.gaia_project.level0
            self.research_board.gaia_project.level0.players.append(name)

            p.economy = self.research_board.economy.level0
            self.research_board.economy.level0.players.append(name)

            p.science = self.research_board.science.level0
            self.research_board.science.level0.players.append(name)

            start_research = p.faction.start_research
            if start_research:
                levels = [
                    p.terraforming,
                    p.navigation,
                    p.a_i,
                    p.gaia_project,
                    p.economy,
                    p.science,
                ]
                for i, track in enumerate(self.research_board.tech_tracks):
                    if track.name == start_research:
                        current_level = levels[i]
                        track.research(current_level, p, i)

        # Place first structures (start with first player and going clockwise):
        for player in self.players:
            player.start_mine("first", self.universe, self.players)

        for player in reversed(self.players):
            player.start_mine("second", self.universe, self.players)

        # Choose booster (start with last player and going counter-clockwise):
        for player in reversed(self.players):
            player.choose_booster(self.scoring_board)

        # TODO Move the setup function inside the play function instead.
        self.play()

    def visual_setup(self):
        """Load setup into an image for better human readability of a setup."""

        # Canvas with technology track backgrounds at the top.
        with Image.open(os.path.join(ROOT,
                "empty_setup.png")) as canvas:

            # Terraforming setup.
            # Placing the federation token.
            with Image.open(os.path.join(IMAGES,
                   self.research_board.terraforming.level5.reward.img)) as fed:
                canvas.paste(fed, (5, 35), fed)

            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.terraforming.advanced.img)) as adv:
                canvas.paste(adv, (160, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.terraforming.standard.img)) as std:
                canvas.paste(std, (158, 127), std)

            # Navigation setup.
            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.navigation.advanced.img)) as adv:
                canvas.paste(adv, (330, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.navigation.standard.img)) as std:
                canvas.paste(std, (328, 127), std)

            # Artificial Intelligence setup.
            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.a_i.advanced.img)) as adv:
                canvas.paste(adv, (500, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.a_i.standard.img)) as std:
                canvas.paste(std, (496, 127), std)

            # Gaia Project setup.
            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.gaia_project.advanced.img)) as adv:
                canvas.paste(adv, (668, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.gaia_project.standard.img)) as std:
                canvas.paste(std, (664, 127), std)

            # Economy setup.
            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.economy.advanced.img)) as adv:
                canvas.paste(adv, (836, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.economy.standard.img)) as std:
                canvas.paste(std, (832, 127), std)

            # Science setup.
            with Image.open(os.path.join(IMAGES,
                    # Place the advanced tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.science.advanced.img)) as adv:
                canvas.paste(adv, (1012, 3), adv)

            with Image.open(os.path.join(IMAGES,
                    # Place the standard tile.
                    # Error is corrected at runtime so i can ignore this.
                    # pylint: disable=no-member
                    self.research_board.science.standard.img)) as std:
                canvas.paste(std, (1008, 127), std)

            # Free standard technology tiles setup.
            x = 240
            for free_tile in self.research_board.free_standard_technology:
                with Image.open(os.path.join(IMAGES,
                        free_tile.img)) as free_std:
                    canvas.paste(free_std, (int(x), 260), free_std)

                # To space the free tiles evenly apart
                x += 240 * 1.4

            # Booster tiles setup.
            x = 30
            for booster_tile in self.scoring_board.boosters:
                with Image.open(os.path.join(IMAGES,
                        booster_tile.img)) as booster:
                    canvas.paste(booster, (int(x), 415), booster)

                # To space the booster tiles evenly apart
                x += 80 * 2.5

            # Round scoring tiles setup.
            x = 5
            for round_tile in self.scoring_board.rounds:
                with Image.open(os.path.join(IMAGES,
                        round_tile.img)) as round_:
                    canvas.paste(round_, (int(x), 745), round_)

                # To space the round scoring tiles evenly apart
                x += 100 * 1.6

            # End scoring tiles setup.
            y = 656
            for end_tile in self.scoring_board.end_scoring:
                with Image.open(os.path.join(IMAGES,
                        end_tile.img)) as end:
                    canvas.paste(end, (974, y), end)

                # To space the end scoring tiles evenly apart
                y += 140

            canvas.save("Setup.png", "png")

    def create_universe(self):
        self.universe = Universe()

    def play(self):
        """This function will setup and allow you to start playing a game."""

        # During 6 rounds, cycle through the 4 phases of the game.
        for rnd in self.scoring_board.rounds:
            print(f"\nCurrent round {str(rnd).upper()}.")
            self.passed = 0
            # 1. Income phase followed by # 2. Gaia phase.
            for player in self.players:
                # TODO move this to cleanup?
                player.income_phase()
                player.gaia_phase()

            # 3. Action phase
            while self.passed != len(self.players):
                for player in self.players:
                    if not player.passed:
                        player.action_phase(self, rnd)

            # 4. Clean up phase
            # Reset Power/Q.I.C. actions.
            for x in range(1, 11):
                self.research_board.pq_actions[x] = True

            # Reset all players special actions and set passed to false.
            for player in self.players:
                player.clean_up()
                player.passed = False
        else:
            # End game scoring.
            self.scoring_board.end_game_scoring(self)


if __name__ == "__main__":
    # TODO for testing only
    # Open everything i need for testing the game.
    def open_stuff():
        # Gaia Project folder
        os.startfile(
            r"C:\Users\Gebruiker\Desktop\Programming\My Projects\Gaia Project"
        )
        # Rules
        os.startfile("Gaia Project Rules - EN.pdf")
        # 2p map
        os.startfile("default_2p_map.png")
        # Research board
        os.startfile(r".\images\structures\research_board.png")


    # Uncomment if files are opened.
    # open_stuff()

    new_game = GaiaProject("Hadsch Halla", "Taklons", automa=True)
    # print(new_game.universe.sector4)
    # print(new_game.universe.sector5)

    # new_game.play()  # Start a game by calling this if convenient.
