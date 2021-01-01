import numpy as np
import scipy.spatial as ss


from .point import Point
from .edge import Edge


class Graph:
    def __init__(self, points: list):
        self._points = list()
        self._edges = set()
        self._triangles = list()

        for p in points:
            self.add_point(p)

    @property
    def triangles(self) -> list:
        return self._triangles

    @property
    def edges(self) -> set:
        return self._edges

    @property
    def points(self) -> list:
        return self._points

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


class ScatterGraph(Graph):
    def __init__(self, width, height, count, margin):
        points = [
            # Ensure points exist in all 4 corners
            Point(0, 0),
            Point(0, height),
            Point(width, 0),
            Point(width, height)
        ]

        while len(points) < count:
            p = Point.random(width, height, margin)
            if p in points:
                continue
            points.append(p)

        super().__init__(points)


class PolyGraph(Graph):
    def __init__(self, width, height, count, margin):
        w = width + 2 * margin
        h = height + 2 * margin

        n_x = int((((w * count) / h) + ((w - h) ** 2 / (4 * h ** 2))) ** 0.5 - ((w - h) / (2 * h)))
        n_y = int(count / n_x)

        d_x = w // n_x
        d_y = h // n_y

        points = []

        for x in range(-margin, width + margin, d_x):
            row = 0
            for y in range(-margin, height + margin, d_y):
                if row % 2 == 0:
                    points.append(Point(x, y))
                else:
                    points.append(Point(x + (d_x // 2), y))
                row += 1

        # Ensure points exist in all 4 corners
        points.append(Point(0, 0))
        points.append(Point(0, height))
        points.append(Point(width, 0))
        points.append(Point(width, height))

        super().__init__(points)
