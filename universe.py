import os

import pygame
from PIL import Image

import constants as C
import exceptions as e

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class Space:
    """Empty spaces on the sector tiles.
    """

    def __init__(self, sector, location, num, pixel_x, pixel_y):
        self.sector = sector  # Number of the sector this space is in.
        self.location = location  # (x, y) on universe grid.
        self.num = num  # Number inside the sector (1-19).
        self.pixel_x = pixel_x  # Space x coordinate in pixels for the screen.
        self.pixel_y = pixel_y  # Space y coordinate in pixels for the screen.
        self.type = "Space"

        # TODO factin compatibility. Check how to handle the ivits space
        #   station.
        # Verify if that works in Universe.valid_spaces to exclude spaces with
        # a space station.
        # Home world of each player that has a sattelite here.
        self.satellites = []

    def __str__(self):
        return (
            f"Number: {self.num}"
        )


class Planet:
    """Planet inside a sector."""

    def __init__(self, sector, type_, location, num, pixel_x, pixel_y):
        self.sector = sector  # Number of the sector this planet is in.
        self.type = type_  # Oxide, Desert, Gaia, Trans-dim etc.
        self.location = location  # Universe grid (x, y).
        self.num = num  # Number inside the sector (1-19).
        self.pixel_x = pixel_x  # Planet x coordinate in pixels for the screen.
        self.pixel_y = pixel_y  # Planet y coordinate in pixels for the screen.

        self.owner = False  # Faction name of owner.
        self.structure = False  # Type of building built.
        self.federation = False  # Part of federation? True or False.
        self.neighbours = []  # List of opponents that are within range 2.

    def __str__(self):
        owner = ""
        structure = ""
        if self.owner:
            owner = f"Owner: {self.owner} | "
            structure = f"Structure: {self.structure} | "
        return (
            f"Sector: {self.sector} | Type: {self.type} | {owner}{structure}"
            f"Number: {self.num}"
        )
        # f"Federation: {self.federation}"


class LostPlanet:
    def __init__(self):
        self.sector = False  # Number of the sector this planet is in.
        self.type = "Lost Planet"
        self.location = False  # Universe grid (x, y).
        self.num = False  # Number inside the sector (1-19).
        self.owner = False  # Faction name of owner
        self.structure = "Mine"  # Type of building built
        self.federation = False  # Part of federation? True or False
        self.neighbours = []  # List of opponents that are within range 2.

    def place(self, player, gp, rnd):
        # TODO faction compatibility ivits space station check.

        print(
            "\nYou have received the Lost Planet. Where would you like to "
            "place it? You can't choose a space that contains a Planet, "
            "Satellite or Space Station."
        )

        # TODO more players only for 2p right now
        choose_range = "1-7"
        while True:
            print(
                "Please type the number of the sector you want to place the "
                "Lost Planet in."
            )

            sector_choice = input("--> ")
            if not sector_choice in C.SECTORS_2P:
                # More players TODO make this message dynamic to the board.
                # If playing with more players it would be 1-10 for example.
                print(f"! Please only type {choose_range}.")
                continue

            # Choose an empty space.
            try:
                spaces = gp.universe.valid_spaces(player, int(sector_choice))
            except e.NoValidSpacesError:
                continue

            chosen_space = False
            # If there is only one valid space, place on that space.
            if len(spaces) == 1:
                chosen_space = spaces[0]
            else:
                # If there are multiple valid spaces, choose one.
                print("Please type your chosen space's corresponding number.")
                for i, sp in enumerate(spaces, start=1):
                    print(f"{i}. {sp}")
                print(f"{i + 1}. Go back to sector selection.")

                while True:
                    space_choice = input("--> ")
                    if space_choice in [str(n + 1) for n in range(i)]:
                        chosen_space = spaces[int(space_choice) - 1]
                        break
                    elif space_choice == f"{i + 1}":
                        break
                    else:
                        print(
                            "! Please only type one of the available numbers."
                        )
                        continue

            if not chosen_space:
                continue

            # Check if the player has enough range.
            enough_range, distance = player.within_range(
                gp.universe, chosen_space, 4
            )

            if not enough_range:
                pay_range_qic = player.ask_pay_for_range(
                    chosen_space,
                    distance,
                    4,
                    lost_planet=True
                )

                if not pay_range_qic:
                    continue
                else:
                    # Pay the qic
                    player.resolve_cost(f"qic{pay_range_qic}")

            break

        # Turn the Space object into the Lost Planet object. Find the chosen
        # Hex inside the Universe.sector.hexes list.
        found = False
        old_space = chosen_space
        for i, circle in enumerate(eval(f"gp.universe.sector{sector_choice}"
                                        ".hexes")):
            for x, hex_ in enumerate(circle):
                if hex_ is chosen_space:
                    exec(
                        f"gp.universe.sector{sector_choice}.hexes[{i}][{x}]"
                        f" = self"
                    )
                    found = True
                    break
            if found:
                break

        # Set Lost Planet parameters
        self.sector = old_space.sector
        self.location = old_space.location
        self.num = old_space.num
        self.owner = player.faction.name
        self.pixel_x = old_space.pixel_x
        self.pixel_y = old_space.pixel_y

        # Place the lost planet on the screen.
        img_dir = os.path.join(IMAGES, "Miscellaneous")
        img_path = os.path.join(img_dir, "Lost Planet.png")

        structure = pygame.image.load(img_path).convert_alpha()
        x = self.pixel_x - C.PLACE["Lost Planet"][0] // 2
        y = self.pixel_y - C.PLACE["Lost Planet"][1] // 2

        gp.screen.blit(structure, (x, y))

        gp.universe.place_structure(
            gp.screen,
            self,
            player.faction.home_type,
            "Mine"
        )

        player.empire.append(self)
        player.lost_planet = True

        # Put the Lost Planet into the Universe.planets dictionary.
        gp.universe.sort_planets(self)

        print(
            f"You have placed the Lost Planet in sector "
            f"{self.sector} on number {self.num}."
        )

        # Check if the current round awards points for building a mine.
        if rnd.goal == "mine":
            reason = "Because of the round"
            player.resolve_gain(f"vp{rnd.vp}", reason)

        # Allow Neighbour charging.
        gp.universe.planet_has_neighbours(self, player, gp.players)

    def __str__(self):
        owner = ""
        structure = f"Structure: {self.structure} | "
        if self.owner:
            owner = f"Owner: {self.owner} | "
        return (
            f"Sector: {self.sector} | Type: {self.type} | {owner}{structure}"
            f"Number: {self.num}"
        )
        # f"Federation: {self.federation}"


class Sector:
    """Sector tile.

    Example:
        Human representation:
             1     2     3

          4     5     6     7

        8    9     10    11    12

          13    14    15    16

             17    18    19

        Program representation:
            hex_nums = [
                [10],  # Center
                [5, 6, 11, 15, 14, 9],  # Inner circle
                [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]  # Outer circle
            ]
            universe grid mapping. For example: center sector = [
                [(8, 13)],
                [(7, 12), (7, 14), (8, 15), (9, 14), (9, 12), (8, 11)],
                [(6, 11), (6, 13), (6, 15), (7, 16), (8, 17), (9, 16),
                 (10, 15), (10, 13), (10, 11), (9, 10), (8, 9), (7, 10)]
            ]
    """

    def __init__(self,
                 number,
                 hexes,
                 img,
                 universe_grid,
                 rotation,
                 planet_list,
                 pixel_x,
                 pixel_y):
        """Initialising the sector object.

        Args:
            number (int): Number of the hex in the Sector (1-19).
            hexes (dict): Hex number: planet type.
            img (path): Absolute path to the image file.
            universe_grid (list): Location of planets and spaces in the sector.
            rotation (int): Rotated amount. Can be 1-5.
            planet_list (List): All the planets in the Universe.
            pixel_x (Tuple): x coordinate in pixels of the center.
            pixel_y (Tuple): y coordinate in pixels of the center.

        TODO:
            Right now the rotation does nothing really.
        """

        # All middle points in pixels of all the 19 hexes relative to the
        # center.
        pixel_coords = {
            1: (pixel_x - 75, pixel_y - 66 * 2),
            2: (pixel_x, pixel_y - 66 * 2),
            3: (pixel_x + 75, pixel_y - 66 * 2),
            4: (pixel_x - 75 / 2 - 75, pixel_y - 66),
            5: (pixel_x - 75 / 2, pixel_y - 66),
            6: (pixel_x + 75 / 2, pixel_y - 66),
            7: (pixel_x + 75 / 2 + 75, pixel_y - 66),
            8: (pixel_x - 75 * 2, pixel_y),
            9: (pixel_x - 75, pixel_y),
            10: (pixel_x, pixel_y),
            11: (pixel_x + 75, pixel_y),
            12: (pixel_x + 75 * 2, pixel_y),
            13: (pixel_x - 75 / 2 - 75, pixel_y + 66),
            14: (pixel_x - 75 / 2, pixel_y + 66),
            15: (pixel_x + 75 / 2, pixel_y + 66),
            16: (pixel_x + 75 / 2 + 75, pixel_y + 66),
            17: (pixel_x - 75, pixel_y + 66 * 2),
            18: (pixel_x, pixel_y + 66 * 2),
            19: (pixel_x + 75, pixel_y + 66 * 2),
        }

        self.number = number
        self.hexes = [[hexes.get(10, Space(sector=self.number,
            location=universe_grid[0][0],
            num=10,
            pixel_x=pixel_coords[10][0],
            pixel_y=pixel_coords[10][1]
            ))]]

        self.planets = []  # List of all planets in the sector


        # TODO FINAL open image here or somewhere else?
        # self.img = Image.open(img)
        self.img = img

        self.universe_grid = universe_grid
        self.rotation = rotation

        # Populate the Program representation with planets and empty spaces.
        self.inner = []
        self.outer = []
        inner = [5, 6, 11, 15, 14, 9]
        for i, num in enumerate(inner):
            # If num is in the hexes dictionary, that means it was provided to
            # the instance and that a planet is there.

            location = universe_grid[1][i]
            if hexes.get(num, False):
                new_planet = Planet(
                    sector=self.number,
                    type_=hexes[num],
                    location=location,
                    num=num,
                    pixel_x=pixel_coords[num][0],
                    pixel_y=pixel_coords[num][1]
                )
                self.inner.append(new_planet)
                self.planets.append(new_planet)
                planet_list.append(new_planet)
            else:
                self.inner.append(Space(
                    sector=self.number,
                    location=location,
                    num=num,
                    pixel_x=pixel_coords[num][0],
                    pixel_y=pixel_coords[num][1])
                )

        outer = [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]
        for i, num in enumerate(outer):
            # If num is in the hexes dictionary, that means it was provided to
            # the instance and that a planet is there.

            location = universe_grid[2][i]
            if hexes.get(num, False):
                new_planet = Planet(
                    sector=self.number,
                    type_=hexes[num],
                    location=location,
                    num=num,
                    pixel_x=pixel_coords[num][0],
                    pixel_y=pixel_coords[num][1]
                )
                self.inner.append(new_planet)
                self.planets.append(new_planet)
                planet_list.append(new_planet)
            else:
                self.outer.append(Space(
                    sector=self.number,
                    location=location,
                    num=num,
                    pixel_x=pixel_coords[num][0],
                    pixel_y=pixel_coords[num][1]
                ))

        # Sort the list of planets by num.
        self.planets.sort(key=lambda planet: planet.num)

        # Add the inner and outer circle to the list of hexes
        self.hexes.append(self.inner)
        self.hexes.append(self.outer)

    def rotate_sector(self, x=1):
        """Rotate a sector x times.

        TODO:
            If i ever use rotation, rotate first before creating planet and
            empty space instances.

        Example:

             1     2     3

          4     5     6     7

        8    9     10    11    12

          13    14    15    16

             17    18    19

        hex_nums = [
            [10],  # Center
            [5, 6, 11, 15, 14, 9],  # Inner circle
            [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]  # Outer circle
        ]

        universe grid mapping = center sector = [
            [(8, 13)],
            [(7, 12), (7, 14), (8, 15), (9, 14), (9, 12), (8, 11)],
            [(6, 11), (6, 13), (6, 15), (7, 16), (8, 17), (9, 16),
            (10, 15), (10, 13), (10, 11), (9, 10), (8, 9), (7, 10)]
        ]

        Moving the last number of the inner circle to the beginning and
        moving the last 2 numbers of the outer circle to the beginning,
        completes a rotation.

        hex_nums = [
            [10],  # Center
            [9, 5, 6, 11, 15, 14],  # Inner circle
            [8, 4, 1, 2, 3, 7, 12, 16, 19, 18, 17, 13]  # Outer circle
        ]

              8     4     1

           13    9    5     2

        17    14    10    6     3

           18    15    11    7

              19    16    12
        """

        for _ in range(x):
            self.hexes[1] = self.hexes[1][-1:] + self.hexes[1][:-1]
            self.hexes[2] = self.hexes[2][-2:] + self.hexes[2][:-2]

            self.universe_grid[1] = (self.universe_grid[1][-1:]
                            + self.universe_grid[1][:-1])
            self.universe_grid[2] = (self.universe_grid[2][-2:]
                            + self.universe_grid[2][:-2])

            self.rotation += 1
            if self.rotation == 6:
                self.rotation = 0

    def __str__(self):
        center = [10]
        inner = [5, 6, 11, 15, 14, 9]
        outer = [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]
        output = []

        for x in range(1, 20):
            if x in center:
                output.append(f"{x}: {str(self.hexes[0][0])}\n")
            elif x in inner:
                output.append(f"{x}: {str(self.hexes[1][inner.index(x)])}\n")
            elif x in outer:
                output.append(f"{x}: {str(self.hexes[2][outer.index(x)])}\n")

        return ''.join(output)


class Universe:

    def __init__(self,
                 screen,
                 sector1=('n', 0),
                 sector2=('nw', 0),
                 sector3=('c', 0),
                 sector4=('sw', 0),
                 sector5=('ne', 0),
                 sector6=('se', 0),
                 sector7=('s', 0),
                 sector8=False,
                 sector9=False,
                 sector10=False):

        """Generate the universe.

        Args:
            sector(x): (location, rotation).
                location can be n, nw, c, sw (North, North West, Center etc.).
                rotation can be 0-5.
        """

        # List with [[(x, y), Planet], [(x, y), Planet]]
        self.planet_list = []

        # Universe grid tables (left ruler (x), top ruler (y))
        # Center
        self.c = [
            [(8, 13)],
            [(7, 12), (7, 14), (8, 15), (9, 14), (9, 12), (8, 11)],
            [(6, 11), (6, 13), (6, 15), (7, 16), (8, 17), (9, 16),
             (10, 15), (10, 13), (10, 11), (9, 10), (8, 9), (7, 10)]
        ]

        # North
        self.n = [
            [(3, 14)],
            [(2, 13), (2, 15), (3, 16), (4, 15), (4, 13), (3, 12)],
            [(1, 12), (1, 14), (1, 16), (2, 17), (3, 18), (4, 17),
             (5, 16), (5, 14), (5, 12), (4, 11), (3, 10), (2, 11)]
        ]

        # North East
        self.ne = [
            [(6, 21)],
            [(5, 20), (5, 22), (6, 23), (7, 22), (7, 20), (6, 19)],
            [(4, 19), (4, 21), (4, 23), (5, 24), (6, 25), (7, 24),
             (8, 23), (8, 21), (8, 19), (7, 18), (6, 17), (5, 18)]
        ]

        # South East
        self.se = [
            [(11, 20)],
            [(10, 19), (10, 21), (11, 22), (12, 21), (12, 19), (11, 18)],
            [(9, 18), (9, 20), (9, 22), (10, 23), (11, 24), (12, 23),
             (13, 22), (13, 20), (13, 18), (12, 17), (11, 16), (10, 17)]
        ]

        # South
        self.s = [
            [(13, 12)],
            [(12, 11), (12, 13), (13, 14), (14, 13), (14, 11), (13, 10)],
            [(11, 10), (11, 12), (11, 14), (12, 15), (13, 16), (14, 15),
             (15, 14), (15, 12), (15, 10), (14, 9), (13, 8), (12, 9)]
        ]

        # South West
        self.sw = [
            [(10, 5)],
            [(9, 4), (9, 6), (10, 7), (11, 6), (11, 4), (10, 3)],
            [(8, 3), (8, 5), (8, 7), (9, 8), (10, 9), (11, 8),
             (12, 7), (12, 5), (12, 3), (11, 2), (10, 1), (9, 2)]
        ]

        # North West
        self.nw = [
            [(5, 6)],
            [(4, 5), (4, 7), (5, 8), (6, 7), (6, 5), (5, 4)],
            [(3, 4), (3, 6), (3, 8), (4, 9), (5, 10), (6, 9),
             (7, 8), (7, 6), (7, 4), (6, 3), (5, 2), (4, 3)]
        ]

        # The center x and y pixel of the sector region for the screen that
        # displays the universe.
        self.center_pixels = {
            'n': (527, 174),
            'nw': (226, 304),
            'c': (489, 500),
            'sw': (189, 630),
            'ne': (789, 369),
            'se': (752, 695),
            's': (451, 826),
        }

        self.sector1 = Sector(
            hexes = {
            4: "Desert",
            5: "Swamp",
            11: "Terra",
            16: "Trans-dim",
            17: "Oxide",
            18: "Volcanic"
        },
            number=1,
            img=os.path.join(IMAGES, "sector1.png"),
            universe_grid=eval(f"self.{sector1[0]}"),
            rotation=sector1[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector1[0]][0],
            pixel_y = self.center_pixels[sector1[0]][1]
        )

        self.sector2 = Sector(
            hexes={
            2: "Volcanic",
            3: "Titanium",
            9: "Swamp",
            11: "Ice",
            13: "Oxide",
            16: "Desert",
            18: "Trans-dim"
        },
            number=2,
            img=os.path.join(IMAGES, "sector2.png"),
            universe_grid=eval(f"self.{sector2[0]}"),
            rotation=sector2[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector2[0]][0],
            pixel_y = self.center_pixels[sector2[0]][1]
        )

        self.sector3 = Sector(
            hexes={
            3: "Trans-dim",
            5: "Gaia",
            13: "Terra",
            15: 'Ice',
            16: "Titanium",
            17: "Desert"
        },
            number=3,
            img=os.path.join(IMAGES, "sector3.png"),
            universe_grid=eval(f"self.{sector3[0]}"),
            rotation=sector3[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector3[0]][0],
            pixel_y = self.center_pixels[sector3[0]][1]
        )

        self.sector4 = Sector(
            hexes={
            3: "Titanium",
            4: "Ice",
            6: "Oxide",
            9: "Volcanic",
            15: "Swamp",
            19: "Terra"
        },
            number=4,
            img=os.path.join(IMAGES, "sector4.png"),
            universe_grid=eval(f"self.{sector4[0]}"),
            rotation=sector4[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector4[0]][0],
            pixel_y = self.center_pixels[sector4[0]][1]
        )

        # CAREFUL THESE ARE THE BACK SIDE!! Possible solution something like
        # this:
        # if 2p or something:
        self.sector5 = Sector(
            hexes={
            3: "Ice",
            5: "Gaia",
            12: "Trans-dim",
            13: "Volcanic",
            16: "Oxide"
        },
            number=5,
            img=os.path.join(IMAGES, "sector5b.png"),
            universe_grid=eval(f"self.{sector5[0]}"),
            rotation=sector5[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector5[0]][0],
            pixel_y = self.center_pixels[sector5[0]][1]
        )

        # else:
        # self.sector5 = Sector(
        #     hexes={
        #     3: "Ice",
        #     5: "Gaia",
        #     12: "Trans-dim",
        #     13: "Volcanic",
        #     16: "Oxide"
        # },
        # number="sector5",
        # img=os.path.join(IMAGES, "sector5.png"),
        #     universe_grid=eval(f"self.{sector5[0]}"),
        #     rotation=sector5[1],
        #     planet_list=self.planet_list,
        #     pixel_x = self.center_pixels[sector5[0]][0],
        #     pixel_y = self.center_pixels[sector5[0]][1]
        # )

        # CAREFUL THESE ARE THE BACK SIDE!!
        self.sector6 = Sector(
            hexes={
            7: "Trans-dim",
            11: "Terra",
            14: "Gaia",
            18: "Trans-dim",
            19: "Desert"
        },
            number=6,
            img=os.path.join(IMAGES, "sector6b.png"),
            universe_grid=eval(f"self.{sector6[0]}"),
            rotation=sector6[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector6[0]][0],
            pixel_y = self.center_pixels[sector6[0]][1]
        )

        # CAREFUL THESE ARE THE BACK SIDE!!
        self.sector7 = Sector(
            hexes={
            1: "Trans-dim",
            6: "Gaia",
            9: "Gaia",
            15: "Swamp",
            17: "Titanium"
        },
            number=7,
            img=os.path.join(IMAGES, "sector7b.png"),
            universe_grid=eval(f"self.{sector7[0]}"),
            rotation=sector7[1],
            planet_list=self.planet_list,
            pixel_x = self.center_pixels[sector7[0]][0],
            pixel_y = self.center_pixels[sector7[0]][1]
        )

        self.sort_planets()
        # self.generate()

        # Draw the generated universe on the screen.
        background = pygame.image.load("default_2p_map.png").convert_alpha()
        screen.blit(background, (0, 0))

        # Draw a colour wheel in the bottom left as a reminder.
        # color_wheel = pygame.image.load("default_2p_map.png").convert_alpha()
        # screen.blit(color_wheel, (0, 0))


    def sort_planets(self, lost_planet=False):
        if lost_planet:
            self.planet_list.append(lost_planet)

        # Sort the planet_list in order of x and than y.
        self.planet_list.sort(
            key=lambda planet: (planet.location[0], planet.location[1])
        )

        # In a dictionary insertion order is guarenteed so now that the planets
        # are sorted, insert them in order for directional selection.
        self.planets = {planet.location: planet for planet in self.planet_list}

    def generate(self):
        """Assemble the universe into an image."""

        self.universe = "default_2p_map"

        pos = {
            'c': (301, 326),  # Center
            'n': (339, 0),  # North
            'ne': (602, 196),  # North East
            'se': (564, 522),  # South East
            's': (263, 652),  # South
            'sw': (0, 456),  # South West
            'nw': (38, 130)  # North West
        }

        # TODO find better way to do this, maybe don't have the images open in
        # the sector and open them here somehow. Also figure out exactly how to
        # generate the map when it's not the default after everything works
        # with the default.

        # Stitching together the tiles to form the map for 2 players.
        # (width, height)
        map_ = Image.new("RGBA", (978, 1000), "white")

        with (
            Image.open(self.sector1.img) as s1,
            Image.open(self.sector2.img) as s2,
            Image.open(self.sector3.img) as s3,
            Image.open(self.sector4.img) as s4,
            Image.open(self.sector5.img) as s5,
            Image.open(self.sector6.img) as s6,
            Image.open(self.sector7.img) as s7
        ):

            # Canvas size is 978, 1000 (width, length)
            # Sector size is 376, 348 (width, length)

            # Center (301, 326)
            map_.paste(s3, (301, 326), s3)

            # North (339, 0)
            map_.paste(s1, (339, 0), s1)

            # North East (602, 196)
            map_.paste(s5, (602, 196), s5)

            # South East (564, 522)
            map_.paste(s6, (564, 522), s6)

            # South (263, 652)
            map_.paste(s7, (263, 652), s7)

            # South West (0, 456)
            map_.paste(s4, (0, 456), s4)

            # North West (38, 130)
            map_.paste(s2, (38, 130), s2)

            map_.save("default_2p_map.png", "png")

    def place_structure(self, screen, planet, home_type, place):
        """Place structure image on the screen.

        Args:
            screen: pygame display.
            planet: Planet object to display the structure on.
            home_type (str): home type of the player's faction to determine
                the colour of the structure.
            place (str): type of structure the player wants to place.
        """

        # First remove the old structure if applicable.
        if place != "Mine":
            background = pygame.image.load(
                os.path.join(ROOT, "default_2p_map.png")
            ).convert_alpha()

            planet_x = planet.pixel_x
            planet_y = planet.pixel_y

            img_x = C.PLACE[planet.structure][0]
            img_y = C.PLACE[planet.structure][1]

            # Blit the background over the area the old building was taking up.
            screen.blit(
                background,
                (planet_x - img_x // 2, planet_y - img_y // 2),
                (planet_x - img_x // 2, planet_y - img_y // 2, img_x, img_y)
            )

        # Place the new structure
        img_dir = os.path.join(IMAGES, place)
        img_path = os.path.join(img_dir, f"{home_type} {place}.png")

        structure = pygame.image.load(img_path).convert_alpha()
        x = planet.pixel_x - C.PLACE[place][0] // 2
        y = planet.pixel_y - C.PLACE[place][1] // 2

        screen.blit(structure, (x, y))

    def distance(self, startx, starty, targetx, targety):
        """Using the universe grid to calculate distance between two planets.

        See the file -- Universe grid.png -- for an example of the coordinates.

        Args:
            startx (int): the starting planet's x coordinate
            starty (int): the starting planet's y coordinate
            targetx (int): the target planet's x coordinate
            targety (int): the target planet's y coordinate

        Returns:
            An integer that is the distance between the two planets
        """

        traversex = startx
        traversey = starty

        distance = 0
        # Keep going until the target planet has been reached.
        while traversex != targetx or traversey != targety:

            # If the traversal is now on the same horizontal line as the
            # target, only keep traversing horizontally. Move horizontally in
            # steps of 2 because of how the grid works.
            if traversex == targetx:
                if traversey > targety:
                    traversey -= 2
                    distance += 1
                    continue
                else:
                    traversey += 2
                    distance += 1
                    continue

            # If the traversal is now on the same vertical line as the target,
            # only keep traversing vertically. Move vertically in steps of 1
            # because of how the grid works.
            elif traversey == targety:
                if traversex > targetx:
                    traversex -= 1
                    distance += 1
                    continue
                else:
                    traversex += 1
                    distance += 1
                    continue

            if traversex > targetx:
                traversex -= 1
            else:
                traversex += 1

            if traversey > targety:
                traversey -= 1
            else:
                traversey += 1

            distance += 1
        else:
            return distance

    def valid_planets(self, player, sector, action):
        """
        Return a list of valid planets for a certain action inside a certain
        sector.

        Args:
            player: Player object.
            sector (int): Number of the sector to check for valid planets.
            action (str): Name of the action to check valid planets for.
        """

        if action == "start_mine":
            types = [player.faction.home_type]
        elif action == "mine":
            types = C.MINE_TYPES
        elif action == "pq" or action == "boost_terraform":
            # When gaining terraforming steps i think you are not allowed to
            # build on gaia planets so it will be like that.
            types = C.HOME_TYPES
        elif action == "automa_mine" or action == "boost_range":
            types = C.PLANETS
        elif action == "upgrade":
            types = [player.faction.home_type]
        elif action == "gaia":
            types = ["Trans-dim"]

        # Filter out unnecessary planets.
        planets = []
        for planet in eval(f"self.sector{sector}.planets"):
            if planet.type in types:
                if not planet.owner \
                        or planet.owner == player.faction.name \
                        and planet.structure == "gaiaformer" \
                        or action == "upgrade":
                    planets.append(planet)

        if not planets:
            raise e.NoValidMinePlanetsError(types, action)

        return planets

    def valid_spaces(self, player, sector):
        """Return a list of valid planets for placing the Lost Planet.

        Args:
            player: Player object.
            sector (int): Number of the sector to check for valid Spaces.
        """

        spaces = []
        for circle in eval(f"self.sector{sector}.hexes"):
            for hex_ in circle:
                if not isinstance(hex_, Space):
                    continue

                # TODO satellites aren't placed (yet).
                if hex_.satellites:
                    continue
                spaces.append(hex_)

        if not spaces:
            raise e.NoValidSpacesError

        # Sort the spaces based on their num.
        spaces.sort(key=lambda space: space.num)
        return spaces

    def planet_has_neighbours(self,
                              planet_to_check,
                              active_player,
                              players,
                              neighbour_charge=True):
        """Determine if a planet is neighbouring opponents.

        An opponent is a neighbour if he is within a range of 2 of the planet
        in question. If a neighbour is found, look at the structure with the
        highest power value and allow the player to charge power.

        Args:
            planet_to_check: Planet object of the planet you want to check for
                neighbours.
            active_player: Player object for the player that wants to check
                for neighbours.
            players (list): gp.players list with objects of all players in the
                game.
            neighbour_charge (Bool): Whether or not to handle neighbour Power
                charging.

        """

        # Dictionary with opponents that are found to be neighbours and the
        # highest power value they may charge.
        neighbours = {}

        start_x = planet_to_check.location[0]
        start_y = planet_to_check.location[1]

        # Coordinates to check.
        coords = [
            # First ring.
            (start_x, start_y - 2),
            (start_x - 1, start_y - 1),
            (start_x - 1, start_y + 1),
            (start_x, start_y + 2),
            (start_x + 1, start_y + 1),
            (start_x + 1, start_y - 1),

            # Second ring.
            (start_x, start_y - 4),
            (start_x - 1, start_y - 3),
            (start_x - 2, start_y - 2),
            (start_x - 2, start_y),
            (start_x - 2, start_y + 2),
            (start_x - 1, start_y + 3),
            (start_x, start_y + 4),
            (start_x + 1, start_y + 3),
            (start_x + 2, start_y + 2),
            (start_x + 2, start_y),
            (start_x + 2, start_y - 2),
            (start_x + 1, start_y - 3),
        ]

        for location in coords:
            # Coordinate is a Space or is outside of the universe.
            if not location in self.planets:
                continue

            # Planet belongs to no one or to the active player or has a
            # gaiaformer on it.
            if not self.planets[location].owner \
                    or self.planets[location].owner \
                        == active_player.faction.name \
                    or self.planets[location].structure == "gaiaformer":
                continue

            # Opponent that is a neighbour is found.
            planet = self.planets[location]

            # Add the active player to the list of neighbours of the planet.
            if not active_player in planet.neighbours:
                planet.neighbours.append(active_player)

            planet_power_value = C.STRUCTURE_POWER_VALUES[planet.structure]
            if planet.owner in neighbours:
                if planet_power_value > neighbours[planet.owner]:
                    neighbours[planet.owner] = planet_power_value
            else:
                neighbours[planet.owner] = planet_power_value

        # No neighbours were found.
        if not neighbours:
            return

        # Allow the found neighbours to charge power.
        for opponent in players:
            if not opponent.faction.name in neighbours:
                continue

            # Add the neighbour to the planet_to_check's list of neighbours.
            planet_to_check.neighbours.append(opponent)

            if neighbour_charge:
                p_value = neighbours[opponent.faction.name]
                self.charge_neighbour_power(active_player, opponent, p_value)

    def charge_neighbour_power(self, trigger_player, charging_player, p_value):
        """Function for charging Power due to neighborhood.

        Args:
            trigger_player: The Player object of the player that built a mine
                or upgraded in the neighborhood of the charging player.
            charging_player: The Player object of the player that is able to
                charge power.
            p_value (int): The amount of power that can be charge by the
                charging_player.
        """

        # Automa can't charge power.
        if type(charging_player).__name__ == "Automa":
            return

        # TODO Minor If nothing can be charged, don't ask the player anything.

        for standard_tech in charging_player.standard_technology:
            if standard_tech.when == "worth4power":
                if p_value == 3:
                    p_value += 1

        print(
            f"\n{charging_player.faction.name} do you want to charge Power for"
            f" being in the neighborhood of {trigger_player.faction.name}?\n"
            f"At maximum you could charge {p_value} Power for {p_value - 1} "
            "Victory Points. (Y/N)"
        )

        print(
            f"You have {charging_player.vp} Victory Points.\n"
            f"Power in bowl 1: {charging_player.faction.bowl1}\n"
            f"Power in bowl 2: {charging_player.faction.bowl2}\n"
            f"Power in bowl 3: {charging_player.faction.bowl3}"
        )
        while True:
            charge_chosen = input("--> ").lower()

            if not charge_chosen in ['y', 'n']:
                print("! Please type Y for yes or N for no.")
                continue
            elif charge_chosen == 'n':
                print("! No power was charged.")
                return
            else:
                charge_chosen = p_value
                break

        vp_cost = charge_chosen - 1
        chargeable_power = charging_player.faction.bowl1 * 2 \
            + charging_player.faction.bowl2
        spendable_vp = charging_player.vp

        # No power to charge.
        if chargeable_power == 0:
            print("! You don't have any Power available for charging.")
            return
        # Charging is free.
        elif vp_cost == 0:
            charging_player.charge_power(1)
            return
        # No vp to spend.
        elif spendable_vp == 0:
            print("! You don't have any Victory Points to pay with.")
            return

        # Player is able to pay and charge the selected amount.
        if spendable_vp >= vp_cost \
                and chargeable_power >= charge_chosen:
            charging_player.resolve_cost(f"vp{vp_cost}")
            charging_player.charge_power(charge_chosen)
        # Player is limited by vp.
        elif spendable_vp < chargeable_power - 1:
            print(
                f"! You are only able to charge {spendable_vp + 1} Power "
                "because your Victory Points are limited."
            )
            charging_player.resolve_cost(f"vp{spendable_vp}")
            charging_player.charge_power(spendable_vp + 1)
        # Player is limited by power.
        else:
            charging_player.resolve_cost(f"vp{chargeable_power - 1}")
            charging_player.charge_power(charge_chosen)
        return
