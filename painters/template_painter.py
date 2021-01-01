from PIL import Image

from graph import Point

from .triangle_painter import TrianglePainter


class TemplatePainter(TrianglePainter):
    _path: str
    _img: Image
    _img_width: int
    _img_height: int

    def __init__(self, path: str, width: int, height: int):
        self._path = path
        self._img = None
        self._img_width = width
        self._img_height = height

    @property
    def fp(self):
        if self._img is None:
            self._img = Image.open(self._path).convert("RGB").resize((self._img_width, self._img_height))
        return self._img

    def _get_pixel(self, x, y) -> (int, int, int):
        return self.fp.getpixel((x, y))

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        c = Point.find_centroid([a, b, c], self._img_width, self._img_height)
        r, g, b = self._get_pixel(c.x, c.y)

        return r, g, b

