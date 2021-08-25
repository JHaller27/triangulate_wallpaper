from graph import Point, Edge, Graph
from .interface import ICanvas
from painters import TrianglePainter

from PIL import Image, ImageDraw


POINT_SIZE = 2
POINT_COLOR = "red"
LINE_COLOR = "white"
CENTROID_COLOR = "green"


class ImageDrawMosaicCanvas(ICanvas):
    _width: int
    _height: int
    _image: Image
    _draw: ImageDraw
    _triangle_painter: TrianglePainter

    def __init__(self, painter: TrianglePainter, *, width: int, height: int):
        self._width = width
        self._height = height
        self._triangle_painter = painter

        self._image = Image.new('RGB', self._size())
        self._draw = ImageDraw.Draw(self._image)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _size(self) -> tuple[int, int]:
        return self.width, self.height

    def create_circle(self, x, y, r, *, fill, width):
        return self._draw.ellipse([x-r, y-r, x+r, y+r], fill=fill, width=width)

    def create_point(self, p: Point, *, fill=None) -> None:
        if fill is None:
            fill = POINT_COLOR

        self.create_circle(p.x, p.y, POINT_SIZE, fill=fill, width=0)

    def create_edge(self, e: Edge) -> None:
        x1, y1, x2, y2 = e.coordinates
        self._draw.line([x1, y1, x2, y2], fill=LINE_COLOR)

    def create_triangle(self, t: list):
        coords = []
        for p in t:
            coords.append(p.x)
            coords.append(p.y)

        self._draw.polygon(coords, fill=self._triangle_painter.get_color(*t))

    def display(self, title: str):
        self._image.show()

    def draw_graph(self, g: Graph, show_layers: list):
        show_centers = 'centers' in show_layers
        for t in g.triangles:
            self.create_triangle(t)

            # Draw centroids
            if show_centers:
                centroid = Point.find_centroid(t, self._width, self._height)
                self.create_point(centroid, fill=CENTROID_COLOR)

        # Draw edges
        if 'lines' in show_layers:
            for e in g.edges:
                self.create_edge(e)

        # Draw Points
        if 'points' in show_layers:
            for p in g.points:
                self.create_point(p)

    def save_to(self, path: str):
        with open(path, 'wb') as fp:
            self._image.save(fp, "png")
