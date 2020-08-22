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
        self.img = f"{img}.png"

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
        })
        self.sector6b = Sector({
            7: "Trans-dim",
            11: "Terra",
            14: "Gaia",
            18: "Trans-dim",
            19: "Desert"
        })
        self.sector7b = Sector({
            1: "Trans-dim",
            6: "Gaia",
            9: "Gaia",
            15: "Swamp",
            17: "Titanium"
        })

    def generate(self):
        self.universe = "2pdefault"

        # Stitching together the tiles to form the map for 2 players.
        # (width, height)
        self.map = Image.new("RGBA", (5312, 5430), "white")

        # Center (1632, 1769)
        self.map.paste(self.sector1.img, (1632, 1769), self.sector1.img)

        # North (1837, 0)
        self.map.paste(self.sector2.img, (1837, 0), self.sector2.img)

        # North East (3265, 1060)
        self.map.paste(self.sector3.img, (3265, 1060), self.sector3.img)

        # South East (3060, 2829)
        self.map.paste(self.sector4.img, (3060, 2829), self.sector4.img)

        # South (1427, 3539)
        self.map.paste(self.sector3.img, (1427, 3539), self.sector3.img)

        # South West (0, 2478)
        self.map.paste(self.sector2.img, (0, 2478), self.sector2.img)

        # North West (205, 709)
        self.map.paste(self.sector1.img, (205, 709), self.sector1.img)

        self.map.save("Universe.png", "png")

    def show(self):
        self.sector1.image.show


if __name__ == "__main__":
    test = Universe()

    # Open the generated map
    # os.startfile("test.png")
