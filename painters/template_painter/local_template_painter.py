from PIL import Image

from ..template_painter import TemplatePainter


class LocalTemplatePainter(TemplatePainter):
    _path: str

    def __init__(self, width: int, height: int, path: str):
        super().__init__(width, height)

        self._path = path

    def _get_new_image(self) -> Image:
        return Image.open(self._path)
