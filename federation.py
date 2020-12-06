class FederationToken:

    def __init__(self, img, count, reward, state):
        self.img = img
        self.count = count
        self.reward = reward
        self.state = state  # grey or green

    def __str__(self):
        # TODO make printing this better.
        return f"Reward: {self.reward} | Side: {self.state}"
