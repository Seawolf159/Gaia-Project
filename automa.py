class Automa:

    def __init__(self, faction, difficulty="automächtig"):
        self.faction = faction

        # TODO handle this in a difficulty setup function ??
        if difficulty.lower() == "automalein":
            self.score = 0
        else:
            self.score = 10

        self.booster = False

    def income(self):
        pass

    def mine(self):
        pass

    def gaia(self):
        pass

    def upgrade(self):
        pass

    def federation(self):
        pass

    def research(self):
        pass

    def pq(self):
        pass

    def special(self):
        pass

    def pass_(self):
        pass


class Taklons:
    pass
