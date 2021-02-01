from PIL import Image
from urllib.request import urlopen

from ..template_painter import TemplatePainter


class UrlTemplatePainter(TemplatePainter):
    _url: str

    def __init__(self, width: int, height: int, url: str):
        super().__init__(width, height)
        self._url = url

    def _get_new_image(self) -> Image:
        fp = urlopen(self._url)
        return Image.open(fp)
