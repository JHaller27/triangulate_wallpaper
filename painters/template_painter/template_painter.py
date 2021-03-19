from PIL import Image

from graph import Point

from painters import TrianglePainter


class TemplatePainter(TrianglePainter):
    _img: Image
    _img_width: int
    _img_height: int

    def __init__(self, width: int, height: int):
        self._img = None
        self._img_width = width
        self._img_height = height

    @property
    def fp(self) -> Image:
        if self._img is None:
            self._img = self._get_new_image()
            self._img = self._img.convert("RGB")
            self._img = self._img.resize((self._img_width, self._img_height))
        return self._img

    def _get_new_image(self) -> Image:
        raise NotImplementedError

    def _get_pixel(self, x, y) -> (int, int, int):
        return self.fp.getpixel((x, y))

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        c = Point.find_centroid([a, b, c], self._img_width, self._img_height)
        r, g, b = self._get_pixel(c.x, c.y)

        return r, g, b

