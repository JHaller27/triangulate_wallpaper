from graph import Graph
from .interface import ICanvas


class ImageDrawMosaicCanvas(ICanvas):
    def display(self, title: str):
        pass

    def draw_graph(self, g: Graph, show_layers: list):
        pass

    def save_to(self, path: str):
        pass
