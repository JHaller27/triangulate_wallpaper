import random
import tkinter as tk
import numpy as np
import scipy.spatial as ss

IMG_WIDTH = 1920
IMG_HEIGHT = 1080
POINT_SIZE = 2
POINT_COLOR = "red"
LINE_COLOR = "white"


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
        x = random.randint(0 + POINT_SIZE, max_width - POINT_SIZE)
        y = random.randint(0 + POINT_SIZE, max_height - POINT_SIZE)

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


class MyCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._edges = set()

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_point(self, p: Point) -> None:
        self.create_circle(p.x, p.y, POINT_SIZE, fill=POINT_COLOR, width=0)

    def create_edge(self, e: (Point, Point)) -> None:
        p1, p2 = e
        self.create_line(p1.x, p1.y, p2.x, p2.y, fill=LINE_COLOR)


class Graph:
    def __init__(self):
        self._points = list()
        self._edges = list()

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
        # Draw Points
        for p in self._points:
            c.create_point(p)

        # Draw edges
        for e in self._edges:
            c.create_edge(e)

    def add_point(self, p: Point):
        self._points.append(p)

    def add_edge(self, p1: Point, p2: Point):
        self._edges.append((p1, p2))
        self._edges.append((p2, p1))

    def fill_triangles(self):
        # Points -> np array
        points = np.array([[p.x, p.y] for p in self._points])

        # Triangulate
        edges = ss.Delaunay(points).simplices

        # Add edges
        for e in edges:
            a, b, c = [self._points[i] for i in e]
            for p, q in [(a, b), (b, c), (c, a)]:
                self._edges.append((p, q))


def main():
    root = tk.Tk()
    canvas = MyCanvas(root, width=IMG_WIDTH, height=IMG_HEIGHT, borderwidth=0, highlightthickness=0, background="black")
    canvas.grid()

    graph = Graph.scatter(IMG_WIDTH, IMG_HEIGHT, 100)
    graph.fill_triangles()

    graph.draw(canvas)

    root.wm_title("Delaunay Triangles")
    root.mainloop()


if __name__ == "__main__":
    main()
