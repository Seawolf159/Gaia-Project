class FederationToken:

    def __init__(self, img, count, reward, state):
        self.img = img
        self.count = count
        self.reward = reward
        self.state = state  # Grey or green

    def __str__(self):
        return f"{self.reward}"
