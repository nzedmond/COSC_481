from systems.level import Level


class LevelLoader:
    @staticmethod
    def load(path):
        return Level(path)
