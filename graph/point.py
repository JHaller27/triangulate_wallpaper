from mosaic_random import get_random


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
    def random(cls, max_width: int, max_height: int, margin: int):
        x = get_random().randint(0 - margin, max_width + margin)
        y = get_random().randint(0 - margin, max_height + margin)

        return cls(x, y)

    @staticmethod
    def find_centroid(vertices: ['Point', 'Point', 'Point'], width: int, height: int) -> 'Point':
        # If width/height are defined, replace out-of-bounds Points with in-bounds
        def check_bounds(p: Point) -> Point:
            x = None
            y = None

            if p.x < 0:
                x = 0
            elif p.x >= width:
                x = width - 1
            if p.y < 0:
                y = 0
            elif p.y >= height:
                y = height - 1

            return p.set_coords(x=x, y=y)

        a, b, c = [check_bounds(p) for p in vertices]

        center_x = (a.x + b.x + c.x) // 3
        center_y = (a.y + b.y + c.y) // 3

        return Point(center_x, center_y)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def set_coords(self, *, x: int = None, y: int = None) -> 'Point':
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        return Point(x, y)
