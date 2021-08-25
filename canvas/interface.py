from graph import Graph


class ICanvas:
    @property
    def width(self) -> int:
        raise NotImplementedError

    @property
    def height(self) -> int:
        raise NotImplementedError

    def display(self, title: str):
        raise NotImplementedError

    def draw_graph(self, g: Graph, show_layers: list):
        raise NotImplementedError

    def save_to(self, path: str):
        raise NotImplementedError
