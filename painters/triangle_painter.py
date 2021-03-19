from graph import Point


class TrianglePainter:
    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        raise NotImplementedError

    def get_color(self, a: Point, b: Point, c: Point) -> str:
        def validate_color(x: int):
            if x < 0x0:
                return 0x0
            if x > 0xff:
                return 0xff
            return x

        rgb = self._get_color_tupe(a, b, c)
        rgb = (validate_color(x) for x in rgb)
        r, g, b = rgb

        return f'#{r:02X}{g:02X}{b:02X}'
