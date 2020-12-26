import random
import tkinter as tk
from typing import Optional

IMG_WIDTH = 1920
IMG_HEIGHT = 1080


class Queue:
    def __init__(self, init=None):
        if init is None:
            self._lst = []
        else:
            self._lst = list()

    def __len__(self):
        return len(self._lst)

    def __repr__(self):
        return f"<Q {self._lst}>"

    def push(self, item):
        self._lst.append(item)

    def peek(self):
        return self._lst[0]

    def pop(self):
        return self._lst.pop(0)


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
        self._points = set()
        self._edges = set()

    @classmethod
    def scatter(cls, width, height, count):
        g = cls()

        while len(g._points) < count:
            p = Point.random(width, height)
            if p in g._points:
                continue
            g.add_point(p)

        return g

    def _find_closest(self, p: Point, blacklist: set = None) -> Optional[Point]:
        if blacklist is None:
            blacklist = set()

        blacklist.add(p)
        try:
            return min(filter(lambda o: o not in blacklist, self._points), key=p.dist_to)
        except ValueError:
            return None

    def _find_closest_between(self, p1: Point, p2: Point) -> Optional[Point]:
        x = 0

        blklst = {p2}
        p3 = self._find_closest(p1, blklst)
        while self._has_intersection(p1, p3) or self._has_intersection(p2, p3):
            x += 1

            blklst.add(p3)
            p3 = self._find_closest(p1, blklst)
            if p3 is None:
                return None
        return p3

    # Given three colinear points p, q, r, the function checks if
    # point q lies on line segment 'pr'
    @staticmethod
    def _on_segment(p, q, r):
        if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
                (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
            return True
        return False

    @staticmethod
    def orientation(p, q, r):
        # to find the orientation of an ordered triplet (p,q,r)
        # function returns the following values:
        # 0 : Colinear points
        # 1 : Clockwise points
        # 2 : Counterclockwise

        # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
        # for details of below formula.

        val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
        if val > 0:

            # Clockwise orientation
            return 1
        elif val < 0:

            # Counterclockwise orientation
            return 2
        else:

            # Colinear orientation
            return 0

    # The main function that returns true if
    # the line segment 'p1q1' and 'p2q2' intersect.
    @staticmethod
    def _do_intersect(p1, q1, p2, q2):

        # Find the 4 orientations required for
        # the general and special cases
        o1 = Graph.orientation(p1, q1, p2)
        o2 = Graph.orientation(p1, q1, q2)
        o3 = Graph.orientation(p2, q2, p1)
        o4 = Graph.orientation(p2, q2, q1)

        # General case
        if (o1 != o2) and (o3 != o4):
            return True

        # Special Cases

        # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
        if (o1 == 0 and o2 == 0) and Graph._on_segment(p1, p2, q1):
            return True

        # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
        if (o2 == 0 and o1 == 0) and Graph._on_segment(p1, q2, q1):
            return True

        # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
        if (o3 == 0 and o4 == 0) and Graph._on_segment(p2, p1, q2):
            return True

        # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
        if (o4 == 0 and o3 == 0) and Graph._on_segment(p2, q1, q2):
            return True

        # If none of the cases
        return False

    def _has_intersection(self, p1: Point, q1: Point) -> bool:
        for p2, q2 in self._edges:
            if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
                continue

            if Graph._do_intersect(p1, q1, p2, q2):
                return True

        return False

    def draw(self, c: MyCanvas):
        # Draw Points
        for p in self._points:
            c.create_circle(p.x, p.y, p.r, fill="red", width=0)

        # Draw edges
        for e in self._edges:
            p1, p2 = e
            c.create_line(p1.x, p1.y, p2.x, p2.y, fill="white")

    def add_point(self, p: Point):
        self._points.add(p)

    def add_edge(self, p1: Point, p2: Point):
        self._edges.add((p1, p2))
        self._edges.add((p2, p1))

    def fill_triangles(self):
        edge_queue = Queue()

        # First, create pilot triangle
        origin = next(iter(self._points))

        a = self._find_closest(origin)
        edge_queue.push((origin, a))
        self.add_edge(origin, a)

        b = self._find_closest(origin, {a})
        edge_queue.push((a, b))
        self.add_edge(a, b)

        edge_queue.push((b, origin))
        self.add_edge(b, origin)

        # Must have at most 2n-2 edges (where n = # of nodes, points)
        max_edges = 2*len(self._points) - 2

        # For each edge in the queue, draw a triangle, pushing edges
        while len(self._edges)//2 < max_edges and len(edge_queue) > 0:
        # for _ in range(max_edges):
            a, b = edge_queue.pop()
            c = self._find_closest_between(a, b)
            if c is None:
                break

            edge_queue.push((a, c))
            self.add_edge(a, b)

            edge_queue.push((b, c))
            self.add_edge(b, c)


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
    root = tk.Tk()
    canvas = MyCanvas(root, width=IMG_WIDTH, height=IMG_HEIGHT, borderwidth=0, highlightthickness=0, background="black")
    canvas.grid()

    g = Graph()

    """
    4       5 6
    2         3
    0         1
    """
    ps = [
        Point(100, 100),   # 0
        Point(1000, 100),  # 1
        Point(100, 200),   # 2
        Point(1000, 200),  # 3
        # Point(1, 3),   # 4
        # Point(8, 3),   # 5
        # Point(10, 3),  # 6
    ]
    for p in ps:
        g.add_point(p)
    # g.add_edge(ps[0], ps[1])
    # g.add_edge(ps[0], ps[2])
    # g.add_edge(ps[0], ps[5])

    # print(g._find_closest_between(ps[0], ps[1]))
    g.fill_triangles()
    g.draw(canvas)

    root.mainloop()

    # main()
