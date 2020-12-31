class StandardTechnology:

    def __init__(self, img, when, reward):
        self.img = img
        self.when = when
        self.reward = reward

        # Only used on the StandardTechnology with a special action.
        self.used = False

    def resolve_effect(self, player):
        """Receive the reward from doing the special action.

        Args:
            player: Player object of the player that does the special action.
        """

        player.resolve_gain(
            self.reward,
            "Because of the special action"
        )
        self.used = True


    def __str__(self):
        # TODO Print this prettier!
        return f"Standard: when: {self.when} | reward: {self.reward}"


class OreQic(StandardTechnology):
    """
    More specific class for the gain 1 ore and 1 qic immediately upon
    receiving standard technology tile.
    """

    def resolve_effect(self, player):
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

    def resolve_effect(self, player):
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

    def resolve_effect(self, player):
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

        # Only used on AdvancedTechnology with a special action.
        self.used = False

    def __str__(self):
        # TODO Print this prettier!
        if self.effect:
            effect = f"effect: {self.effect} | "
        else:
            effect = ""

        return f"Advanced: when: {self.when} | {effect}reward: {self.reward}"


class FedVpPass(AdvancedTechnology):
    """
    More specific class for the gain 3 vp for every federation token you have
    when passing.
    """

    def resolve_effect(self, player):
        """Player receives the reward when passing.

        Args:
            player: Player object of the player that has the tile.
        """

        player.resolve_gain(
            f"vp{len(player.federations) * 3}",
            "Because of an Advanced Technology"
        )


class LabVpPass(AdvancedTechnology):
    """
    More specific class for the gain 3 vp for every Research Lab you have have
    built when passing.
    """

    def resolve_effect(self, player):
        """Player receives the reward when passing.

        Args:
            player: Player object of the player that has the tile.
        """

        # Get the amount of Research Labs the player has built.
        amount = (
            len([
                planet for planet in player.empire
                if planet.structure == "Research Lab"
            ])
        )
        player.resolve_gain(
            f"vp{amount * 3}",
            "Because of an Advanced Technology"
        )

class TypesVpPass(AdvancedTechnology):
    """
    More specific class for the gain 1 vp for every different planet type you
    have built on when passing.
    """

    def resolve_effect(self, player):
        """Player receives the reward when passing.

        Args:
            player: Player object of the player that has the tile.
        """

        # Get the amount of different planet types the player has built on.
        types = len({planet.type for planet in player.empire})
        player.resolve_gain(
            f"vp{types}",
            "Because of an Advanced Technology"
        )


class MineVp(AdvancedTechnology):
    """
    More specific class for the gain 2 vp for every mine you have built
    immediately upon receiving advanced technology tile.
    """

    def resolve_effect(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Check if the player has the lost planet.
        lost_planet = 0
        if player.lost_planet:
            lost_planet = 1
        player.resolve_gain(
            f"vp{(player.faction.mine_built + lost_planet) * 2}",
            "Because of the Advanced Technology"
        )


class TradeVp(AdvancedTechnology):
    """
    More specific class for the gain 4 vp for every Trading Station you have
    built immediately upon receiving advanced technology tile.
    """

    def resolve_effect(self, player):
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

    def resolve_effect(self, player):
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

    def resolve_effect(self, player):
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

    def resolve_effect(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        # Get the amount of Gaia Planets the player has built on.
        gaia_planets = len(
            [
                planet for planet in player.empire
                    if planet.type == "Gaia"
                    and planet.strucure != "Gaiaformer"
            ]
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

    def resolve_effect(self, player):
        """Receive the reward from acquiring this technology tile.

        Args:
            player: Player object of the player that acquired the tile.
        """

        player.resolve_gain(
            f"vp{len(player.federations) * 5}",
            "Because of the Advanced Technology"
        )


class SpecialAdvanced(AdvancedTechnology):
    """
    More specific class for the gain
    1 Q.I.C. and 5 credits / 3 ore / 3 knowledge
    Advanced Technology special action.
    """

    def resolve_effect(self, player):
        """Receive the reward from doing the special action.

        Args:
            player: Player object of the player that does the special action.
        """

        player.resolve_gain(
            self.reward,
            "Because of the special action"
        )
        self.used = True
