from automa import Automa
from components import Components
from player import Player
from sector import Universe
from research import Research


class GaiaProject:
    """Class for combining all the different parts of the game.
    """

    def __init__(self, player1, player2,
                 player3=False, player4=False, automa=False):
        """
        To create a new game of GaiaProject you need to call it with a list of
        the faction names in order.
        """

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
        
        # TODO generate the universe (first game default universe at first)

    def setup(self):
        """Setup all the pieces of the game"""

        pass

    def create_map(self):
        self.map = Universe()

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
    print(new_game.map.sector1)
    # new_game.play()  # Start a game by calling this if possible
