import random
import tkinter as tk
import numpy as np
import scipy.spatial as ss

IMG_WIDTH = 1920
IMG_HEIGHT = 1080


class Point:
    _x: int
    _y: int
    RADIUS = 2

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
        x = random.randint(0 + Point.RADIUS, max_width - Point.RADIUS)
        y = random.randint(0 + Point.RADIUS, max_height - Point.RADIUS)

        return cls(x, y)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def r(self) -> int:
        return Point.RADIUS

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
            c.create_circle(p.x, p.y, p.r, fill="red", width=0)

        # Draw edges
        for e in self._edges:
            p1, p2 = e
            c.create_line(p1.x, p1.y, p2.x, p2.y, fill="white")

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

    root.wm_title("Circles and Arcs")
    root.mainloop()


if __name__ == "__main__":
    main()
