"""
TODO instantiate even the unused tech tiles, boosters etc..???

"""

import random

from automa import Automa
from player import Player
from research import Research
from scoring import Scoring
from universe import Universe


class GaiaProject:
    """Class for combining all the different parts of the game.
    """

    def __init__(self, player1, player2,
                 player3=False, player4=False, automa=False):
        """Create a new game of GaiaProject

        Args:
            player1-4 (str): Name of the faction the corresonding player is
                playing.
        """

        self.federation_tokens = {
            "vp": [3, "vp12", "grey"],
            "vpqic" : [3, "vp8", "qic1", "green"],
            "vppowertoken": [3, "vp8, powertoken2", "green"],
            "vpore": [3, "vp7", "ore2", "green"],
            "vpcredits": [3, "vp7", "credits6", "green"],
            "vpknowledge": [3, "vp6", "knowledge2", "green"]
        }

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
        self.create_universe()

        # 3. Randomly place the standard and advanced technology tiles.
        self.research_board.randomise_tech_tiles()

        # 4. Randomly select one federation token for the terraforming research
        #    track (Against the automa each type of token only has 2 pieces).
        terraforming_token = random.choice(list(self.federation_tokens.keys()))
        self.research_board.terraforming.level5.reward = (
            self.federation_tokens[terraforming_token][1:]
        )
        self.federation_tokens[terraforming_token][0] -= 1

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

        # Start of the game:
        # Choose faction (start with first player and going clockwise):
        # TODO Let player choose faction after seeing setup?

        # Place first structures (start with first player and going clockwise):
        for player in self.players:
            player.first_mine("first")
        for player in reversed(self.players):
            player.first_mine("second")

        # Choose booster (start with last player and going counter-clockwise):


        # TODO generate the universe (first game default universe at first)

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
        """This function will setup and allow you to start playing a game.
        """
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
    print(new_game.research_board)
    # print(new_game.research_board.terraforming.advanced)
    # print(new_game.research_board.navigation.advanced)


    # new_game.play()  # Start a game by calling this if possible
