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

        for hex_ in range(1, 20):
            if hexes.get(hex_):
                self.hexes[hex_] = Planet(hexes[hex_])
            else:
                self.hexes[hex_] = Space()

    def __str__(self):
        # return (
        #     f"   {self.hexes[1]} {self.hexes[2]} {self.hexes[3]}\n"
        #     f" {self.hexes[4]} {self.hexes[5]} {self.hexes[6]} {self.hexes[7]}\n"
        #     # f"{} {} {} {} {}\n"
        #     # f" {} {} {} {}\n"
        #     # f"   {} {} {}\n"
        # )

        tiles = []

        for hex_, type_ in self.hexes.items():
            tiles.extend([str(hex_), ' ', str(type_), "\n"])
        return ''.join(tiles)


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

    def show(self):
        self.sector1.image.show


if __name__ == "__main__":
    test = Universe()
    test.generate()

    # Open the generated map
    os.startfile("2p Default.png")
