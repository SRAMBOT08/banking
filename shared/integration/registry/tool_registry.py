class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, tool) -> None:
        self._tools[name] = tool

    def get(self, name: str):
        return self._tools[name]

    def all(self) -> dict:
        return dict(self._tools)
