import os

from PIL import Image

ROOT = os.path.dirname(__file__)
IMAGES = os.path.join(ROOT, "images")


class Space:
    """Empty spaces on the sector tiles.
    """

    def __init__(self):
        self.sattelites = set()

    def __repr__(self):
        return "x"


class Planet:
    """Planet type on the sector tile.
    """

    def __init__(self, type_):
        self.type = type_
        self.owner = False
        self.structure = False
        self.federation = False

    def __repr__(self):
        return self.type


class Sector:
    """Sector tiles.
    """

    def __init__(self, hexes, img):
        self.hexes = {}
        self.img = Image.open(f"{img}.png")
        self.rotation = 0

        for hex_ in range(1, 20):
            if hexes.get(hex_):
                self.hexes[hex_] = Planet(hexes[hex_])
            else:
                self.hexes[hex_] = Space()

    def __str__(self):
        tiles = []

        for hex_, type_ in self.hexes.items():
            tiles.extend([str(hex_), ' ', str(type_), "\n"])
        return ''.join(tiles)

    def rotate_sector_once(self):
        """Rotating a sector

                1     2      3
             4     5     6     8
           9    10    11    12    13
             13    14    15    16
                17    18    19

        sector_data = [
            [11],  # Center
            [5, 6, 12, 15, 14, 10],  # Inner circle
            [1, 2, 3, 8, 13, 16, 19, 18, 17, 13, 9, 4]  # Outer circle
        ]

        Moving the last number of the inner circle to the beginning and moving
        the last 2 numbers of the outer circle to the beginning, complete a
        rotation.

        sector_data = [
            [11],  # Center
            [10, 5, 6, 12, 15, 14],  # Inner circle
            [9, 4, 1, 2, 3, 8, 13, 16, 19, 18, 17, 13]  # Outer circle
        ]

                9     4     1
             4     10    5     3
          13    14    11    6     8
             17    15    12    13
                18    19    16
        """

        for i in [1, 2]:
            if i == 1:
                self.content[i] = self.content[i][-1:] + self.content[i][:-1]
            if i == 2:
                self.content[i] = self.content[i][-2:] + self.content[i][:-2]

        self.rotation += 1
        if self.rotation == 6:
            self.rotation = 0


class Universe:

    def __init__(self):
        self.sector1 = Sector({
            4: "Desert",
            5: "Swamp",
            11: "Terra",
            16: "Trans-dim",
            17: "Oxide",
            18: "Volcanic"
        }, os.path.join(IMAGES, "sector1"))
        self.sector2 = Sector({
            2: "Volcanic",
            3: "Titanium",
            9: "Swamp",
            11: "Ice",
            13: "Oxide",
            16: "Desert",
            18: "Trans-dim"
        }, os.path.join(IMAGES, "sector2"))
        self.sector3 = Sector({
            3: "Trans-dim",
            5: "Gaia",
            13: "Terra",
            15: 'Ice',
            16: "Titanium",
            17: "Desert"
        }, os.path.join(IMAGES, "sector3"))
        self.sector4 = Sector({
            3: "Titanium",
            4: "Ice",
            6: "Oxide",
            9: "Volcanic",
            15: "Swamp",
            19: "Terra"
        }, os.path.join(IMAGES, "sector4"))
        self.sector5b = Sector({
            3: "Ice",
            5: "Gaia",
            12: "Trans-dim",
            13: "Volcanic",
            16: "Oxide"
        }, os.path.join(IMAGES, "sector5b"))
        self.sector6b = Sector({
            7: "Trans-dim",
            11: "Terra",
            14: "Gaia",
            18: "Trans-dim",
            19: "Desert"
        }, os.path.join(IMAGES, "sector6b"))
        self.sector7b = Sector({
            1: "Trans-dim",
            6: "Gaia",
            9: "Gaia",
            15: "Swamp",
            17: "Titanium"
        }, os.path.join(IMAGES, "sector7b"))

    def generate(self):
        self.universe = "2pdefault"

        # Sector Slots 2 players
        ss2p = {
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
        map_.paste(self.sector5b.img, (3265, 1060), self.sector5b.img)

        # South East (3060, 2829)
        map_.paste(self.sector6b.img, (3060, 2829), self.sector6b.img)

        # South (1427, 3539)
        map_.paste(self.sector7b.img, (1427, 3539), self.sector7b.img)

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

        TODO:
            Figure out where this function is best placed.
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


if __name__ == "__main__":
    test = Universe()
    # test.generate()
    distance = Universe.distance
    print(distance(7, 10, 7, 12))

    # Open the generated map
    # os.startfile("2p Default.png")
