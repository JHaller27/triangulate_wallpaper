from graph import Point

from .triangle_painter import TrianglePainter


class ColorPainter(TrianglePainter):
    def __init__(self, color: str = None):
        r, g, b = 0xff, 0xff, 0xff  # Black

        if color is not None:
            if len(color) - 1 == 6:
                r, g, b = (int(color[i:i+2], 16) for i in range(1, len(color), 2))
            elif len(color) - 1 == 3:
                r, g, b = (int(c+c, 16) for c in color[1:])

        self._tup = r, g, b

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        return self._tup
