class ScoreManager:
    """Tracks score and collectible pickup count for the current run."""

    def __init__(self):
        self.score     = 0
        self.collected = 0
        self.total     = 0

    def setup(self, total):
        """Call once per level load with the total number of collectibles."""
        self.score     = 0
        self.collected = 0
        self.total     = total

    def collect(self, value):
        """Register one pickup worth *value* points."""
        self.score     += value
        self.collected += 1
