from mosaic_random import get_random
from graph import Point

from .triangle_painter import TrianglePainter


class GaussyPainter(TrianglePainter):
    def __init__(self, base: TrianglePainter, sigma: int):
        self._base = base
        self._sigma = sigma

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        pxl = self._base._get_color_tupe(a, b, c)
        pxl_adjd = (int(get_random().gauss(x, self._sigma)) for x in pxl)

        return pxl_adjd
