import os

from PIL import Image

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class Space:
    """Empty spaces on the sector tiles.
    """

    def __init__(self, location):
        self.location = location  # (x, y)

        # Home world of each player that has a sattelite here.
        self.sattelites = set()

    def __str__(self):
        return f"X: {self.location[0]} Y:{self.location[1]}: x"


class Planet:
    """Planet type on the sector tile.
    """

    def __init__(self, type_, location):
        self.type = type_  # Oxide, Desert, Gaia, Trans-dim etc.
        self.location = location  # (x, y)
        self.owner = False  # Home world of owner
        self.structure = False  # Type of building built
        self.federation = False  # Part of federation? True or False

    def __str__(self):
        return (
            f"X: {self.location[0]} Y:{self.location[1]}\n"
            f"Type: {self.type}\n"
            f"Owner: {self.owner}\n"
            f"Structure: {self.structure}\n"
            f"Federation: {self.federation}"
        )


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
            hexes = [
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
    """

    def __init__(self, hexes, img, universe_grid, rotation):
        """Initialising the sector object.

        Args:
            hexes (dict): Hex number: planet type.
            img (path): Absolute path to the image file.
            universe_grid (list): Location of planets and spaces in the sector.
            rotation (int): Rotated amount. Can be 1-5.
        """

        self.hexes = [[hexes.get(10, Space(location=universe_grid[0][0]))]]

        # TODO open image here or somewhere else?
        # self.img = Image.open(f"{img}.png")
        self.img = f"{img}.png"

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
                self.inner.append(
                    Planet(
                        type_=hexes[num],
                        location=location
                    )
                )
            else:
                self.inner.append(Space(location=location))

        outer = [1, 2, 3, 7, 12, 16, 19, 18, 17, 13, 8, 4]
        for i, num in enumerate(outer):
            # If num is in the hexes dictionary, that means it was provided to
            # the instance and that a planet is there.

            location = universe_grid[2][i]
            if hexes.get(num, False):
                self.outer.append(
                    Planet(
                        type_=hexes[num],
                        location=location
                    )
                )
            else:
                self.outer.append(Space(location=location))

        # Add the inner and outer circle to the list of hexes
        self.hexes.append(self.inner)
        self.hexes.append(self.outer)

    def rotate_sector(self, x=1):
        """Rotating a sector x times."""

        #      1     2     3

        #   4     5     6     7

        # 8    9     10    11    12

        #   13    14    15    16

        #      17    18    19

        # hexes = [
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

        # Moving the last number of the inner circle to the beginning and moving
        # the last 2 numbers of the outer circle to the beginning, complete a
        # rotation.

        # hexes = [
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
            img = os.path.join(IMAGES, "sector1"),
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
            img=os.path.join(IMAGES, "sector2"),
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
            img=os.path.join(IMAGES, "sector3"),
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
            img=os.path.join(IMAGES, "sector4"),
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
            img=os.path.join(IMAGES, "sector5b"),
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
        #     img=os.path.join(IMAGES, "sector5"),
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
            img=os.path.join(IMAGES, "sector6b"),
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
            img=os.path.join(IMAGES, "sector7b"),
            universe_grid=eval(f"self.{sector7[0]}"),
            rotation=sector7[1]
        )

    def generate(self):
        self.universe = "default_2p"

        default_2p = {
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

    def locate_planet(self, sector, ptype, faction):
        """Looking for a planet.

        Args:
            sector (str): Number of the sector where you want to find a planet.
            ptype (str): Specific type of planet that your are looking for.

        TODO:
            Make it impossible to choose a planet that is already taken.
        """

        if sector == "6" and ptype == "gaia":
            pass
        if sector == "7" and ptype == "trans-dim":
            pass

        # skip center as it's always empty
        for circle in eval(f"self.sector{sector}.hexes[1:]"):
            for hex_ in circle:
                if hasattr(hex_, "type"):
                    if hex_.type.lower() == faction.home_type.lower():
                        return hex_
        else:
            return False


if __name__ == "__main__":
    test = Universe()
    print(test.sector1)
