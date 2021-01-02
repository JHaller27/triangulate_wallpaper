import tkinter as tk
import io
from PIL import Image

from painters import TrianglePainter
from graph import Point, Edge, Graph


POINT_SIZE = 2
POINT_COLOR = "red"
LINE_COLOR = "white"
CENTROID_COLOR = "green"


class MosaicCanvas(tk.Canvas):
    _root: tk.Tk
    _width: int
    _height: int
    _triangle_painter: TrianglePainter

    def __init__(self, painter: TrianglePainter, *, width: int, height: int):
        self._root = tk.Tk()

        super().__init__(self._root, width=width, height=height,
                         borderwidth=0, highlightthickness=0,
                         background="black")

        self._triangle_painter = painter

        self._width = width
        self._height = height

        self._edges = set()

        self.grid()

    def display(self, title: str):
        self._root.wm_title(title)
        self._root.mainloop()

    def size(self) -> (int, int):
        return self._width, self._height

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_point(self, p: Point, *, fill=None) -> None:
        if fill is None:
            fill = POINT_COLOR

        self.create_circle(p.x, p.y, POINT_SIZE, fill=fill, width=0)

    def create_edge(self, e: Edge) -> None:
        x1, y1, x2, y2 = e.coordinates
        self.create_line(x1, y1, x2, y2, fill=LINE_COLOR)

    def create_triangle(self, t: list):
        coords = []
        for p in t:
            coords.append(p.x)
            coords.append(p.y)

        self.create_polygon(*coords, fill=self._triangle_painter.get_color(*t))

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
        width = self._width
        height = self._height

        ps = self.postscript(height=height, width=width,
                             pageheight=height - 1, pagewidth=width - 1,
                             colormode="color")
        img = Image.open(io.BytesIO(ps.encode("utf-8")))
        img = img.convert(mode="RGB")
        img.save(path, "png")
        print(f"Image saved to {path}")
