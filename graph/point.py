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
        global RNG

        x = RNG.randint(0 - margin, max_width + margin)
        y = RNG.randint(0 - margin, max_height + margin)

        return cls(x, y)

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
