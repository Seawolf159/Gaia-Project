class StandardTechnology:

    def __init__(self, img, when, reward):
        self.img = img
        self.when = when
        self.reward = reward

        # Visual setup coordinates
        self.vsetup = False

    def __str__(self):
        return (
            f"when: {self.when}\n"
            f"reward: {self.reward}\n"
        )


class AdvancedTechnology:

    def __init__(self, img, when=False, effect=False, reward=False):
        self.img = img
        self.when = when
        self.effect = effect
        self.reward = reward

        # Visual setup coordinates
        self.vsetup = False

    def __str__(self):
        if self.effect:
            effect = f"effect: {self.effect}\n"
        else:
            effect = ""

        return (
            f"when: {self.when}\n"
            f"{effect}"
            f"reward: {self.reward}\n"
        )
