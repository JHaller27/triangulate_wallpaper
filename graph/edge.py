from .point import Point


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
