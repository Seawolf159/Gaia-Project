class StandardTechnology:

    def __init__(self, img, when, reward):
        self.img = img
        self.when = when
        self.reward = reward

    def __str__(self):
        # TODO Print this prettier!
        return f"Standard: when: {self.when} | reward: {self.reward}"


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
