class StandardTechnology:

    def __init__(self, effect, reward):
        self.effect = effect
        self.reward = reward


class AdvancedTechnology:

    def __init__(self, when=False, effect=False, reward=False, special=False):
        self.when = when
        self.effect = effect
        self.reward = reward

    def __str__(self):
        return (
            f"when: {self.when}\n"
            f"effect {self.effect}\n"
        )
