import os
import random
import sys
from threading import Thread

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from PIL import Image

import constants as C
from automa import Automa
from federation import FederationToken
from player import Player
from research import Research
from scoring import Scoring
from universe import Universe

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class GaiaProject:
    """Class for combining all the different parts of the game."""

    def __init__(self, player_count, screen, automa=False):
        """Create a new game of GaiaProject

        Args:
            player_count (int): Amount of players.
            automa (bool): whether or not the player is playing against the
                automa.
        """

        self.player_count = player_count
        self.screen = screen  # Pygame Universe representation.
        self.automa = automa
        self.players = []  # A list with all the player objects in turn order.
        self.board_setup()

    def board_setup(self):
        """Setup all the pieces of the game."""

        if self.automa:
            amount = 2
        else:
            amount = 3
        self.federation_tokens = [
            FederationToken("FEDvps.png", amount, "vp12", "grey"),
            FederationToken("FEDqic.png", amount, ["vp8", "qic1"], "green"),
            FederationToken("FEDore.png", amount, ["vp7", "ore2"], "green"),
            FederationToken(
                "FEDcre.png", amount, ["vp7", "credits6"], "green"
            ),
            FederationToken(
                "FEDknw.png", amount, ["vp6", "knowledge2"], "green"
            )
        ]

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
        terraforming_fed_token = random.choice(self.federation_tokens)
        terraforming_fed_token.count -= 1
        self.research_board.terraforming.level5.reward = terraforming_fed_token

        # 5. Randomly place 6 round scoring and 2 final scoring tiles on the
        #    scoring board.
        self.scoring_board.randomise_scoring()

        # 6. Randomly select {amount of players} + 3 booster tiles.
        self.scoring_board.randomise_boosters(self.player_count)

        # TESTING uncomment line below when finished. Commented because
        #   it kept changing the img file which is not necessary right now.
        # Load the setup into an image to see it more easily as a human.
        self.visual_setup()

    def visual_setup(self):
        """Visualize the board setup.

        Load setup into an image for better human readability.
        """

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
        """Function for setting up the universe

        TODO:
            In the future randomise the universe.
        """

        self.universe = Universe(self.screen)

    def player_setup(self):
        """Initialise Player objects."""

        # TODO more players ask for factions here or assign randomly.
        # Choose faction (start with first player and going clockwise).
        # See Faction.select_faction for available factions for human and
        # Automa.select_faction for available factions for the Automa.
        self.players.append(Player("Hadsch Halla"))

        # If playing against the Automa, ask for the desired difficulty.
        if self.automa:
            print(
                "What difficulty do you want to set the Automa to? Please type"
                " the corresponding number."
            )
            for i, diff in enumerate(C.DIFFICULTY, start=1):
                print(f"{i}. {diff}.")

            while True:
                choice = input("--> ")

                if choice in [str(num + 1) for num in range(i)]:
                    chosen_difficulty = C.DIFFICULTY[int(choice) - 1]
                    break
                else:
                    print("! Please only type one of the available numbers.")
                    continue

            # Set desired difficulty.
            self.players.append(Automa("Taklons", chosen_difficulty))

        # Place players on level 0 of all researc7h boards and check if they
        # start on level 1 of any of them. Add the Level object to the Player
        # object for easy acces and insert the faction name of the player in
        # the Level.players list.
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
            player.start_mine("first", self, self.players)
            if type(player).__name__ == "Automa":
                input("Press Enter to continue. --> ")

        for player in reversed(self.players):
            player.start_mine("second", self, self.players)
            if type(player).__name__ == "Automa":
                input("Press Enter to continue. --> ")

        # Choose booster (start with last player and going counter-clockwise):
        print("\nBooster selection.")
        for player in reversed(self.players):
            player.choose_booster(self.scoring_board)
            if type(player).__name__ == "Automa":
                input("Press Enter to continue. --> ")

    def play(self):
        """This function will setup and allow you to start playing a game."""

        # During 6 rounds, cycle through the 4 phases of the game.
        for rnd in self.scoring_board.rounds:
            print(f"\nCurrent round {str(rnd).upper()}.")
            self.passed = 0

            # 1. Income phase followed by # 2. Gaia phase.
            for player in self.players:
                player.income_phase()
                player.gaia_phase(self)

            # 3. Action phase
            while self.passed != len(self.players):
                for player in self.players:
                    if not player.passed:
                        player.action_phase(self, rnd)
                        if type(player).__name__ == "Automa":
                            input("Press Enter to continue. --> ")

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


def start_game(screen):
    print("Gaia Project started.\n")
    while True:
        # TODO more players ask for amount of players here and if you'll
        #   play against the automa.
        player_count = 2
        automa = True
        new_game = GaiaProject(player_count, screen, automa=automa)
        # Choose factions after the whole setup has been done.
        print("The board has been set up. Please choose your factions.")
        new_game.player_setup()
        print("Factions have been chosen. The game will now start. Good luck.")
        new_game.play()

        # Pause the program to let the player recap a bit about the results.
        input("Type enter if you are done playing the game.\n")
        break


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
        os.startfile("Gaia Project Automa Rules - EN.pdf")
        # 2p map
        os.startfile("default_2p_map.png")
        # Research board
        os.startfile("research_board.png")
        # Visual Setup
        os.startfile("Setup.png")


    # Uncomment if files are opened.
    # open_stuff()

    # Start game
    pygame.init()
    size = (978, 1000)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Gaia Project Universe")

    CLOCK = pygame.time.Clock()

    game = Thread(target=start_game, args=(screen,), daemon=True)
    game.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.update()
        CLOCK.tick(2)
