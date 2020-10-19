import os

from PIL import Image

import constants as C
import exceptions as e

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class Space:
    """Empty spaces on the sector tiles.
    """

    def __init__(self, sector, location):
        self.sector = sector  # Name of the sector this planet is in.
        self.location = location  # (x, y) on universe grid.

        # Home world of each player that has a sattelite here.
        self.sattelites = []

    def __str__(self):
        return f"X: {self.location[0]} Y:{self.location[1]}: x"


class Planet:
    """Planet inside a sector."""

    def __init__(self, sector, type_, location, num):
        self.sector = sector  # Name of the sector this planet is in.
        self.type = type_  # Oxide, Desert, Gaia, Trans-dim etc.
        self.location = location  # Universe grid (x, y).
        self.num = num  # Number inside the sector (1-19).
        self.owner = False  # Faction name of owner
        self.structure = False  # Type of building built
        self.federation = False  # Part of federation? True or False

    def __str__(self):
        owner = ""
        structure = ""
        if self.owner:
            owner = f"Owner: {self.owner} | "
            structure = f"Structure: {self.structure} | "
        return f"Type: {self.type} | {owner}{structure}Num: {self.num}"
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

    def __init__(self, name, hexes, img, universe_grid, rotation):
        """Initialising the sector object.

        Args:
            hexes (dict): Hex number: planet type.
            img (path): Absolute path to the image file.
            universe_grid (list): Location of planets and spaces in the sector.
            rotation (int): Rotated amount. Can be 1-5.

        TODO:
            Right now the rotation does nothing really.
        """

        self.name = name
        self.hexes = [[hexes.get(10, Space(sector=self.name,
                                           location=universe_grid[0][0]))]]

        self.planets = []  # List of all planets in the sector

        # TODO open image here or somewhere else?
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
                    sector=self.name,
                    type_=hexes[num],
                    location=location,
                    num=num
                )
                self.inner.append(new_planet)
                self.planets.append(new_planet)
            else:
                self.inner.append(Space(sector=self.name,
                                        location=location))

        outer = [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]
        for i, num in enumerate(outer):
            # If num is in the hexes dictionary, that means it was provided to
            # the instance and that a planet is there.

            location = universe_grid[2][i]
            if hexes.get(num, False):
                new_planet = Planet(
                    sector=self.name,
                    type_=hexes[num],
                    location=location,
                    num=num
                )
                self.inner.append(new_planet)
                self.planets.append(new_planet)
            else:
                self.outer.append(Space(sector=self.name,
                                        location=location))

        # Add the inner and outer circle to the list of hexes
        self.hexes.append(self.inner)
        self.hexes.append(self.outer)

    def rotate_sector(self, x=1):
        """Rotate a sector x times.

        TODO:
            If i ever use rotation, rotate first before creating planet and
            empty space instances.
        """

        #      1     2     3

        #   4     5     6     7

        # 8    9     10    11    12

        #   13    14    15    16

        #      17    18    19

        # hex_nums = [
        #     [10],  # Center
        #     [5, 6, 11, 15, 14, 9],  # Inner circle
        #     [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]  # Outer circle
        # ]

        # universe grid mapping = center sector = [
        #     [(8, 13)],
        #     [(7, 12), (7, 14), (8, 15), (9, 14), (9, 12), (8, 11)],
        #     [(6, 11), (6, 13), (6, 15), (7, 16), (8, 17), (9, 16),
        #     (10, 15), (10, 13), (10, 11), (9, 10), (8, 9), (7, 10)]
        # ]

        # Moving the last number of the inner circle to the beginning and
        # moving the last 2 numbers of the outer circle to the beginning,
        # completes a rotation.

        # hex_nums = [
        #     [10],  # Center
        #     [9, 5, 6, 11, 15, 14],  # Inner circle
        #     [8, 4, 1, 2, 3, 7, 12, 16, 19, 18, 17, 13]  # Outer circle
        # ]

        #       8     4     1

        #    13    9    5     2

        # 17    14    10    6     3

        #    18    15    11    7

        #       19    16    12

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

        self.sector1 = Sector(
            hexes = {
            4: "Desert",
            5: "Swamp",
            11: "Terra",
            16: "Trans-dim",
            17: "Oxide",
            18: "Volcanic"
        },
            name="sector1",
            img=os.path.join(IMAGES, "sector1.png"),
            universe_grid=eval(f"self.{sector1[0]}"),
            rotation = sector1[1]
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
            name="sector2",
            img=os.path.join(IMAGES, "sector2.png"),
            universe_grid=eval(f"self.{sector2[0]}"),
            rotation=sector2[1]
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
            name="sector3",
            img=os.path.join(IMAGES, "sector3.png"),
            universe_grid=eval(f"self.{sector3[0]}"),
            rotation=sector3[1]
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
            name="sector4",
            img=os.path.join(IMAGES, "sector4.png"),
            universe_grid=eval(f"self.{sector4[0]}"),
            rotation=sector4[1]
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
            name="sector5",
            img=os.path.join(IMAGES, "sector5b.png"),
            universe_grid=eval(f"self.{sector5[0]}"),
            rotation=sector5[1]
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
        # name="sector5",
        # img=os.path.join(IMAGES, "sector5.png"),
        #     universe_grid=eval(f"self.{sector5[0]}"),
        #     rotation=sector5[1]
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
            name="sector6",
            img=os.path.join(IMAGES, "sector6b.png"),
            universe_grid=eval(f"self.{sector6[0]}"),
            rotation=sector6[1]
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
            name="sector7",
            img=os.path.join(IMAGES, "sector7b.png"),
            universe_grid=eval(f"self.{sector7[0]}"),
            rotation=sector7[1]
        )

    def generate(self):
        self.universe = "default_2p_map"

        default_2p_map = {
            1: (1632, 1769),  # Center
            2: (1837, 0),  # North
            3: (3265, 1060),  # North East
            4: (3060, 2829),  # South East
            5: (1427, 3539),  # South
            6: (0, 2478),  # South West
            7: (205, 709)  # North West
        }

        # TODO find better way to do this, maybe don't have the images open in
        # the sector and open them here somehow. Also figure out exactly how to
        # generate the map when it's not the default after everything works
        # with the default.

        # Stitching together the tiles to form the map for 2 players.
        # (width, height)
        map_ = Image.new("RGBA", (5312, 5430), "white")

        # Center (1632, 1769)
        map_.paste(self.sector3.img, (1632, 1769), self.sector3.img)

        # North (1837, 0)
        map_.paste(self.sector1.img, (1837, 0), self.sector1.img)

        # North East (3265, 1060)
        map_.paste(self.sector5.img, (3265, 1060), self.sector5.img)

        # South East (3060, 2829)
        map_.paste(self.sector6.img, (3060, 2829), self.sector6.img)

        # South (1427, 3539)
        map_.paste(self.sector7.img, (1427, 3539), self.sector7.img)

        # South West (0, 2478)
        map_.paste(self.sector4.img, (0, 2478), self.sector4.img)

        # North West (205, 709)
        map_.paste(self.sector2.img, (205, 709), self.sector2.img)

        map_.save("2p Default.png", "png")

    @ classmethod
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
            types = C.mine_types
        elif action == "pq":
            types = C.home_types
        elif action == "automa_mine":
            types = C.PLANETS
        elif action == "upgrade":
            types = [player.faction.home_type]
        elif action == "gaia":
            types = ["Trans-dim"]

        # Filtor out unnecessary planets.
        planets = []
        for planet in eval(f"self.sector{sector}.planets"):
            if planet.type in types:
                if not planet.owner \
                        or planet.owner == player.faction.name \
                        and planet.structure == "gaiaformer" \
                        or action == "upgrade":
                    planets.append(planet)

        if not planets:
            raise e.NoValidMinePlanetsError

        return planets


if __name__ == "__main__":
    test = Universe()
    for planet in test.sector6.planets:
        print(planet)
