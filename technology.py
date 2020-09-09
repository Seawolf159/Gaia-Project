class StandardTechnology:

    def __init__(self, when, reward):
        self.when = when
        self.reward = reward

    def __str__(self):
        return (
            f"when: {self.when}\n"
            f"reward: {self.reward}\n"
        )


class AdvancedTechnology:

    def __init__(self, when=False, effect=False, reward=False):
        self.when = when
        self.effect = effect
        self.reward = reward

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
