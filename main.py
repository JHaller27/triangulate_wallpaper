import random
import tkinter as tk
import numpy as np
import scipy.spatial as ss
from PIL import Image

IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MARGIN = 100
POINT_SIZE = 2
POINT_COUNT = 500
POINT_COLOR = "red"
LINE_COLOR = "white"

SHOW_TRIANGLES = True
SHOW_LINES = False
SHOW_POINTS = False


def random_rgb() -> str:
    r = random.randint(0, 0xff)
    g = random.randint(0, 0xff)
    b = random.randint(0, 0xff)

    return f'#{r:02X}{g:02X}{b:02X}'


class Point:
    _x: int
    _y: int

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False

        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    @classmethod
    def random(cls, max_width: int, max_height: int):
        x = random.randint(0 + POINT_SIZE - MARGIN, max_width - POINT_SIZE + MARGIN)
        y = random.randint(0 + POINT_SIZE - MARGIN, max_height - POINT_SIZE + MARGIN)

        return cls(x, y)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def dist_to(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** .5

    def find_closest(self, others, blacklist: set = None) -> 'Point':
        if blacklist is None:
            blacklist = set()

        blacklist.add(self)
        return min(filter(lambda o: o not in blacklist, others), key=self.dist_to)


class Edge:
    _p: Point
    _q: Point

    def __init__(self, p: Point, q: Point):
        self._p = p
        self._q = q

    def __eq__(self, other: 'Edge'):
        return (self._p == other._p and self._q == other._q) or (self._p == other._q and self._q == other._p)

    def __hash__(self):
        p = min(self._p, self._q, key=lambda x: x.x)
        q = max(self._p, self._q, key=lambda x: x.x)
        return (p, q).__hash__()

    def __repr__(self):
        return f'<{repr(self._p)}, {repr(self._q)}>'

    @property
    def points(self) -> (Point, Point):
        return self._p, self._q

    @property
    def coordinates(self) -> (int, int, int, int):
        return self._p.x, self._p.y, self._q.x, self._q.y


class MyCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._edges = set()

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_point(self, p: Point) -> None:
        self.create_circle(p.x, p.y, POINT_SIZE, fill=POINT_COLOR, width=0)

    def create_edge(self, e: Edge) -> None:
        x1, y1, x2, y2 = e.coordinates
        self.create_line(x1, y1, x2, y2, fill=LINE_COLOR)

    def create_triangle(self, t: list):
        coords = []
        for p in t:
            coords.append(p.x)
            coords.append(p.y)

        self.create_polygon(*coords, fill=random_rgb())


class Graph:
    def __init__(self):
        self._points = list()
        self._edges = set()
        self._triangles = list()

    @classmethod
    def scatter(cls, width, height, count):
        g = cls()

        while len(g._points) < count:
            p = Point.random(width, height)
            if p in g._points:
                continue
            g.add_point(p)

        return g

    def draw(self, c: MyCanvas):
        # Draw triangles
        if SHOW_TRIANGLES:
            for t in self._triangles:
                c.create_triangle(t)

        # Draw edges
        if SHOW_LINES:
            for e in self._edges:
                c.create_edge(e)

        # Draw Points
        if SHOW_POINTS:
            for p in self._points:
                c.create_point(p)

    def add_point(self, p: Point):
        self._points.append(p)

    def add_edge(self, p1: Point, p2: Point):
        e = Edge(p1, p2)
        self._edges.add(e)

    def add_triangle(self, points: list):
        self._triangles.append(points)

        points_ex = points[1:] + points[:1]

        for p, q in zip(points, points_ex):
            self.add_edge(p, q)

    def triangulate(self):
        # Points -> np array
        points = np.array([[p.x, p.y] for p in self._points])

        # Triangulate
        edges = ss.Delaunay(points).simplices

        # Add edges
        for e in edges:
            vertices = [self._points[i] for i in e]
            self.add_triangle(vertices)


def save_canvas(c: MyCanvas):
    c.postscript(file="triangles.eps")
    img = Image.open("triangles.eps")
    img.save("triangles.png", "png")


def main():
    root = tk.Tk()
    canvas = MyCanvas(root, width=IMG_WIDTH, height=IMG_HEIGHT, borderwidth=0, highlightthickness=0, background="black")
    canvas.grid()

    graph = Graph.scatter(IMG_WIDTH, IMG_HEIGHT, POINT_COUNT)
    graph.triangulate()

    graph.draw(canvas)

    root.wm_title("Delaunay Triangles")
    root.mainloop()

    # save_canvas(canvas)


if __name__ == "__main__":
    main()
