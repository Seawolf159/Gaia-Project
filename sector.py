class Space:
    """Empty spaces on the sector tiles.
    """

    def __init__(self):
        self.sattelites = set()

    def __repr__(self):
        return "Empty space!"


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

    This class handles everything related to the Sector tiles.
    """

    def __init__(self, hexes):
        self.hexes = {}
        for hex_ in range(1, 20):
            if hexes.get(hex_):
                self.hexes[hex_] = Planet(hexes[hex_])
            else:
                self.hexes[hex_] = Space()

    def __repr__(self):
        tiles = []
        for hex_, type_ in self.hexes.items():
            tiles.extend([str(hex_), ' ', str(type_), "\n"])
        return ''.join(tiles)

