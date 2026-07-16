class DependencyContainer:
    def __init__(self):
        self._dependencies = {}

    def register(self, key, value) -> None:
        self._dependencies[key] = value

    def resolve(self, key):
        return self._dependencies[key]
