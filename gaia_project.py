from automa import Automa
from player import Player
from universe import Universe
from research import Research


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

        self.setup(player1, player2, player3, player4, automa)

    def setup(self, player1, player2,
              player3=False, player4=False, automa=False):
        """Setup all the pieces of the game"""

        self.player1 = Player(1, player1)
        if automa:
            self.player2 = Automa(2, player2)
        else:
            self.player2 = Player(2, player2)

        if player3:
            self.player3 = Player(3, player3)
        if player4:
            self.player4 = Player(4, player4)

        self.research_board = Research()

        # Order of setup according to rules
        # 1. Choose first player (Against the automa, the human goes first).
        # 2. Let the last player assemble the game board (or just some final
        #    rotation of tiles) or just do it together.
        # 3. Randomly place the standard and advanced technology tiles.
        self.research_board.randomise_tech_tiles()
        
        # 4. Randomly select one federation token for the terraforming research
        #    track (Against the automa each type of token only has 2 pieces).
        

        # 5. Randomly place 6 round scoring and 2 final scoring tiles on the
        #    scoring board.
        # 6. Randomly select {amount of players} + 3 booster tiles.

        # TODO generate the universe (first game default universe at first)

    def create_universe(self):
        self.universe = Universe()

    def income(self):
        pass

    def take_action(self):
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

        prompt = (
            f"{intro}{mine}{gaia}{upgrade}{federation}{research}{pq}"
            f"{special}{pass_}{free}--> "
        )
        action = input(prompt)

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

    def change_phase(self):
        pass

    def change_turn(self):
        pass

    def play(self):
        """This function will setup and allow you to start playing a game.
        """
        # TODO generate the board and show some sort of summary of the current
        # board?

        pass


if __name__ == "__main__":
    new_game = GaiaProject("Hadsch Halla", "Taklons", automa=True)
    print(new_game.universe.sector1)
    # new_game.play()  # Start a game by calling this if possible
