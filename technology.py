class StandardTechnology:

    def __init__(self, img, when, reward):
        self.img = img
        self.when = when
        self.reward = reward

    def __str__(self):
        # TODO Print this prettier!
        return f"Standard: when: {self.when} | reward: {self.reward}"


class OreQic(StandardTechnology):
    """
    More specific class for the gain 1 ore and 1 qic immediately upon
    receiving standard technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            ["ore1", "qic1"],
            "Because of the Standard Technology"
        )


class SevenVp(StandardTechnology):
    """
    More specific class for the gain 7 VP immediately upon receiving
    standard technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            "vp7",
            "Because of the Standard Technology"
        )


class TypesKnowledge(StandardTechnology):
    """
    More specific class for the gain 1 knowledge for every planet type you
    have built on immediately upon receiving standard technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Get the different planet types the player has built on.
        types = len({planet.type for planet in player.empire})
        player.resolve_gain(
            f"knowledge{types}",
            "Because of the Standard Technology"
        )


class AdvancedTechnology:

    def __init__(self, img, when=False, effect=False, reward=False):
        self.img = img
        self.when = when
        self.effect = effect
        self.reward = reward

    def __str__(self):
        # TODO Print this prettier!
        if self.effect:
            effect = f"effect: {self.effect} | "
        else:
            effect = ""

        return f"Advanced: when: {self.when} | {effect}reward: {self.reward}"


class MineVp(AdvancedTechnology):
    """
    More specific class for the gain 2 vp for every mine you have built
    immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            f"vp{player.faction.mine_built * 2}",
            "Because of the Advanced Technology"
        )


class TradeVp(AdvancedTechnology):
    """
    More specific class for the gain 4 vp for every Trading Station you have
    built immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            f"vp{player.faction.trading_station_built * 4}",
            "Because of the Advanced Technology"
        )


class SectorOre(AdvancedTechnology):
    """
    More specific class for the gain 1 ore for every sector you have built in
    immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Get the amount of sectors the player has built in.
        sectors = len({planet.sector for planet in player.empire})
        player.resolve_gain(
            f"ore{sectors}",
            "Because of the Advanced Technology"
        )


class SectorVp(AdvancedTechnology):
    """
    More specific class for the gain 2 vp for every sector you have built in
    immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Get the amount of sectors the player has built in.
        sectors = len({planet.sector for planet in player.empire})
        player.resolve_gain(
            f"vp{sectors * 2}",
            "Because of the Advanced Technology"
        )


class GaiaVp(AdvancedTechnology):
    """
    More specific class for the gain 2 vp for every Gaia planet you have built
    on immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Get the amount of Gaia Planets the player has built on.
        gaia_planets = len(
            [planet for planet in player.empire if planet.type == "Gaia"]
        )
        player.resolve_gain(
            f"vp{gaia_planets * 2}",
            "Because of the Advanced Technology"
        )


class FedVp(AdvancedTechnology):
    """
    More specific class for the gain 5 vp for every federation token you have
    immediately upon receiving advanced technology tile.
    """

    def resolve_direct(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            f"vp{len(player.federations) * 5}",
            "Because of the Advanced Technology"
        )
