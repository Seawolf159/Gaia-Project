from components import Components
from sector import Universe


class GaiaProject:
    """Class for combining all the different parts of the game.
    """

    def __init__(self, player1, player2, player3=False, player4=False):
        """
        To create a new game of GaiaProject you need to call it with a list of
        the faction names in order.
        """

        self.components = Components()
        self.research = self.components.research
        self.map = Universe()
        # TODO generate the universe (first game universe to begin with)

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
        answer = input(prompt)

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
    new_game = GaiaProject("Hadsch Halla", "Taklons")
    print(new_game.map.sector1)
    # new_game.play()  # Start a game by calling this if possible
