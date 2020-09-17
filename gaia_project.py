"""
TODO instantiate even the unused tech tiles, boosters etc..???

"""

import os
import random

from PIL import Image

from automa import Automa
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
            automa (bool): Wether or not you are playing against the automa.
        """

        # TODO Make the tokens classes!
        self.federation_tokens = {
            "vp": ["FEDvps.png", 3, "vp12", "grey"],
            "vpqic" : ["FEDqic.png", 3, "vp8", "qic1", "green"],
            "vppowertoken": ["FEDpwt.png", 3, "vp8, powertoken2", "green"],
            "vpore": ["FEDore.png", 3, "vp7", "ore2", "green"],
            "vpcredits": ["FEDcre.png", 3, "vp7", "credits6", "green"],
            "vpknowledge": ["FEDknw.png", 3, "vp6", "knowledge2", "green"]
        }

        # TODO FIX THIS MESS. Factions are on chosen at the start normally.
        self.setup(player1, player2, player3, player4, automa)

    def setup(self, player1, player2,
              player3=False, player4=False, automa=False):
        """Setup all the pieces of the game

        Args:
            player1-4 (str): Name of the faction the corresonding player is
                playing.
        """

        # A list with all the player objects
        self.players = []
        self.player_turn = 1
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

        self.change_turn()

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
        terraforming_token = random.choice(list(self.federation_tokens.keys()))
        self.research_board.terraforming.level5.reward = (
            self.federation_tokens[terraforming_token][:]
        )
        self.federation_tokens[terraforming_token][1] -= 1

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

        # Load the setup into an image to see it more easily.
        self.visual_setup()

        # Start of the game:
        # Choose faction (start with first player and going clockwise):
        # TODO Let player choose faction after seeing setup

        # Place first structures (start with first player and going clockwise):
        for player in self.players:
            player.start_mines("first", self.universe)
        for player in reversed(self.players):
            player.start_mines("second", self.universe)

        # Choose booster (start with last player and going counter-clockwise):
        for player in reversed(self.players):
            player.choose_booster(self.scoring_board)

    def visual_setup(self):
        """Load setup into an image for better awareness of the setup"""

        # Create empty canvas.
        # setup = Image.new("RGBA", (1184, 936), "white")

        # Technology backgrounds
        with Image.open(os.path.join(ROOT,
                "empty_setup.png")) as canvas:

            with Image.open(os.path.join(IMAGES,
                    self.research_board.terraforming.level5.reward[0])) as fed:
                canvas.paste(fed, (10, 40), fed)

            for track in self.research_board.tracks:
                with Image.open(os.path.join(IMAGES,
                        # Error is corrected at runtime so i can ignore this.
                        # pylint: disable=no-member
                        track.standard.img)) as std:
                    canvas.paste(std, (144, 113), std)

                with Image.open(os.path.join(IMAGES,
                        # Error is corrected at runtime so i can ignore this.
                        # pylint: disable=no-member
                        track.advanced.img)) as adv:
                    canvas.paste(adv, (144, 0), adv)
                break

            canvas.save("setup.png", "png")

    def create_universe(self):
        self.universe = Universe()

    def update_board(self):
        pass

    def income_phase(self):
        pass

    def gaia_phase(self):
        pass

    def action_phase(self):
        pass

    def change_phase(self):
        pass

    def change_turn(self):
        self.current_player = self.players[self.player_turn]

    def play(self):
        """This function will setup and allow you to start playing a game."""

        # TODO generate the board and show some sort of summary of the current
        # board?

        print("You can currently only play against the Taklons automa as"
              "the Hadsch Halla")
        playing = True
        while playing:
            # During 6 rounds, cycle through the 6 phases of the game.
            # 1. Income phase followed by Gaia phase.
            for player in self.players:
                player.income()
                player.gaia_phase()

            # 3. Action phase


            # 4. Clean up phase


        # self.update_board()


if __name__ == "__main__":
    new_game = GaiaProject("Hadsch Halla", "Taklons", automa=True)
    new_game.visual_setup()
    # print(new_game.universe.sector4)
    # print(new_game.universe.sector5)



    # new_game.play()  # Start a game by calling this if possible
