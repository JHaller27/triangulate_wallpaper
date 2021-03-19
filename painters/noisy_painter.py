from mosaic_random import get_random
from graph import Point

from .triangle_painter import TrianglePainter


class NoisyPainter(TrianglePainter):
    def __init__(self, base: TrianglePainter, tolerance: list):
        self._base = base

        if len(tolerance) == 0:
            self._rand_min = 0
            self._rand_max = 0
        elif len(tolerance) == 1:
            self._rand_min = -abs(tolerance[0])
            self._rand_max = abs(tolerance[0])
        else:
            tolerance = tolerance[:2]
            self._rand_min = min(tolerance)
            self._rand_max = max(tolerance)

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        pxl = self._base._get_color_tupe(a, b, c)
        adjustment = get_random().randint(self._rand_min, self._rand_max)
        pxl_adjd = (x + adjustment for x in pxl)

        return pxl_adjd
