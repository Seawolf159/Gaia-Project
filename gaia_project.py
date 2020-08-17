from components import Components


class GaiaProject:
    """Class for combining all the different parts of the game.
    """

    def __init__(self, player1, player2, player3=False, player4=False):
        """
        To create a new game of GaiaProject you need to call it with a list of
        the faction names in order.
        """

        components = Components()

    def play(self):
        """This function will setup and allow you to start playing a game.
        """

        pass


if __name__ == "__main__":
    new_game = GaiaProject("Hadsch Halla", "Taklons")
    new_game.play()
