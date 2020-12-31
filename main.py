import argparse
import random
import tkinter as tk
import numpy as np
import scipy.spatial as ss
import sys
import io
from PIL import Image


POINT_SIZE = 2
POINT_COLOR = "red"
LINE_COLOR = "white"
CENTROID_COLOR = "green"

RNG: random.Random
RNG_SEED: int


# noinspection PyTypeChecker
def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    def resolution_type(x) -> [int, int]:
        named_sizes = {
            '1k': [1024, 768],
            '2k': [2560, 1440],
            '4k': [3840, 2160],
        }

        if x in named_sizes:
            return named_sizes[x]

        return int(x)

    default_noise = 20
    valid_layers = {'colors', 'centers', 'lines', 'points'}

    def layer(x: str) -> str:
        if x not in valid_layers:
            raise argparse.ArgumentError(f"Layer '{x}' is not a valid layer.")
        return x

    parser.add_argument('template', type=str,
                        help='Path to template image to retrieve colors from')
    parser.add_argument('--size', nargs='*', type=resolution_type, default=[1920, 1080],
                        help='Size of output image (WxH)')
    parser.add_argument('--margin', type=int, default=20,
                        help='Size of margin (out of view) within which triangles may be drawn')
    parser.add_argument('--count', dest='point_count', type=int, default=200,
                        help='Number of points (triangle vertices) to randomly generate')
    parser.add_argument('--seed', type=int, default=None,
                        help='Number to seed generator with')
    parser.add_argument('--show', dest='layers', nargs='*', type=layer, default=['colors'],
                        help=f'List of layers to display. Valid options: [{"|".join(valid_layers)}]. '
                             f'Note: if specified, this overrides - not adds to - the default')
    parser.add_argument('--save', nargs='?', type=str, default='',
                        help="Save image to png file. Use '.' to auto-generate a file name (recommended)")
    parser.add_argument('--noise', nargs='*', type=int,
                        help="Add noise to the template/source image, optionally defining a tolerance.")
    parser.add_argument('--gauss', action='store_true',
                        help="Add gaussian noise to each RGB value individually")

    args = parser.parse_args()

    if isinstance(args.size[0], list):
        args.size = args.size[0]

    if args.noise is not None and len(args.noise) == 0:
        args.noise = [default_noise]

    return args


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

        x = RNG.randint(0 + POINT_SIZE - margin, max_width - POINT_SIZE + margin)
        y = RNG.randint(0 + POINT_SIZE - margin, max_height - POINT_SIZE + margin)

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


class Edge:
    _p: Point
    _q: Point

    def __init__(self, p: Point, q: Point):
        self._p = p
        self._q = q

    def __eq__(self, other: 'Edge'):
        return (self._p == other._p and self._q == other._q) or (self._p == other._q and self._q == other._p)

    def __hash__(self):
        p = min(self._p, self._q, key=lambda x: x.x)
        q = max(self._p, self._q, key=lambda x: x.x)
        return (p, q).__hash__()

    def __repr__(self):
        return f'<{repr(self._p)}, {repr(self._q)}>'

    @property
    def points(self) -> (Point, Point):
        return self._p, self._q

    @property
    def coordinates(self) -> (int, int, int, int):
        return self._p.x, self._p.y, self._q.x, self._q.y


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


class RandomPainter(TrianglePainter):
    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        r = random.randint(0, 0xff)
        g = random.randint(0, 0xff)
        b = random.randint(0, 0xff)

        return r, b, g


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

        c = find_centroid([a, b, c], self._img_width, self._img_height)
        r, g, b = self._get_pixel(c.x, c.y)

        return r, g, b


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
        adjustment = RNG.randint(self._rand_min, self._rand_max)
        pxl_adjd = (x + adjustment for x in pxl)

        return pxl_adjd


class GaussyPainter(TrianglePainter):
    def __init__(self, base: TrianglePainter):
        self._base = base
        self._sigma = 20

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        pxl = self._base._get_color_tupe(a, b, c)
        pxl_adjd = (int(RNG.gauss(x, self._sigma)) for x in pxl)

        return pxl_adjd


class MyCanvas(tk.Canvas):
    _width: int
    _height: int
    _triangle_painter: TrianglePainter

    def __init__(self, painter: TrianglePainter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._triangle_painter = painter

        self._width = kwargs['width']
        self._height = kwargs['height']

        self._edges = set()

    def size(self) -> (int, int):
        return self._width, self._height

    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_point(self, p: Point, *, fill=None) -> None:
        if fill is None:
            fill = POINT_COLOR

        self.create_circle(p.x, p.y, POINT_SIZE, fill=fill, width=0)

    def create_edge(self, e: Edge) -> None:
        x1, y1, x2, y2 = e.coordinates
        self.create_line(x1, y1, x2, y2, fill=LINE_COLOR)

    def create_triangle(self, t: list):
        coords = []
        for p in t:
            coords.append(p.x)
            coords.append(p.y)

        self.create_polygon(*coords, fill=self._triangle_painter.get_color(*t))


class Graph:
    def __init__(self):
        self._points = list()
        self._edges = set()
        self._triangles = list()

    @classmethod
    def scatter(cls, width, height, count, margin):
        g = cls()

        # Ensure points exist in all 4 corners
        g.add_point(Point(0, 0))
        g.add_point(Point(0, height))
        g.add_point(Point(width, 0))
        g.add_point(Point(width, height))

        while len(g._points) < count:
            p = Point.random(width, height, margin)
            if p in g._points:
                continue
            g.add_point(p)

        return g

    def draw(self, c: MyCanvas, show_layers: list):
        # Draw triangles
        for t in self._triangles:
            c.create_triangle(t)

        # Draw centroids
        if 'centers' in show_layers:
            width, height = c.size()
            for t in self._triangles:
                centroid = find_centroid(t, width, height)
                c.create_point(centroid, fill=CENTROID_COLOR)

        # Draw edges
        if 'lines' in show_layers:
            for e in self._edges:
                c.create_edge(e)

        # Draw Points
        if 'points' in show_layers:
            for p in self._points:
                c.create_point(p)

    def add_point(self, p: Point):
        self._points.append(p)

    def add_edge(self, p1: Point, p2: Point):
        e = Edge(p1, p2)
        self._edges.add(e)

    def add_triangle(self, points: list):
        self._triangles.append(points)

        points_ex = points[1:] + points[:1]

        for p, q in zip(points, points_ex):
            self.add_edge(p, q)

    def triangulate(self):
        # Points -> np array
        points = np.array([[p.x, p.y] for p in self._points])

        # Triangulate
        edges = ss.Delaunay(points).simplices

        # Add edges
        for e in edges:
            vertices = [self._points[i] for i in e]
            self.add_triangle(vertices)


def find_centroid(vertices: [Point, Point, Point], width: int = None, height: int = None) -> Point:
    # If width/height are defined, replace out-of-bounds Points with in-bounds
    def check_bounds(p: Point) -> Point:
        x = None
        y = None

        if p.x < 0:
            x = 0
        elif p.x >= width:
            x = width-1
        if p.y < 0:
            y = 0
        elif p.y >= height:
            y = height-1

        return p.set_coords(x=x, y=y)

    a, b, c = [check_bounds(p) for p in vertices]

    center_x = (a.x + b.x + c.x) // 3
    center_y = (a.y + b.y + c.y) // 3

    return Point(center_x, center_y)


def save_canvas(c: MyCanvas, width: int, height: int, path: str):
    global RNG_SEED

    if path is None or path == '.':
        path = f"triangles_{width}x{height}_{RNG_SEED}.png"

    ps = c.postscript(height=height, width=width,
                      pageheight=height - 1, pagewidth=width - 1,
                      colormode="color")
    img = Image.open(io.BytesIO(ps.encode("utf-8")))
    img = img.convert(mode="RGB")
    img.save(path, "png")
    print(f"Image saved to {path}")


def main():
    global RNG, RNG_SEED

    args = get_args()
    img_width, img_height = args.size

    if args.seed is None:
        RNG_SEED = random.randrange(sys.maxsize)
    else:
        RNG_SEED = args.seed
    print(f"Seed {RNG_SEED}")
    RNG = random.Random(RNG_SEED)

    root = tk.Tk()

    title = f"Wallpaper ({img_width}x{img_height})"

    if 'colors' not in args.layers:
        painter = ColorPainter()
    elif args.template is None:
        painter = RandomPainter()
    elif args.template.startswith('#'):
        painter = ColorPainter(args.template)
    else:
        painter = TemplatePainter(args.template, img_width, img_height)
        title += f"- {args.template}"

    if args.gauss:
        painter = GaussyPainter(painter)
    if args.noise:
        painter = NoisyPainter(painter, args.noise)

    canvas = MyCanvas(painter, root,
                      width=img_width, height=img_height,
                      borderwidth=0, highlightthickness=0,
                      background="black")
    canvas.grid()

    graph = Graph.scatter(img_width, img_height, args.point_count, args.margin)
    graph.triangulate()

    graph.draw(canvas, args.layers)

    root.wm_title(title)

    if args.save:
        save_canvas(canvas, img_width, img_height, args.save)
    else:
        print('Displaying image in window')
        root.mainloop()


if __name__ == "__main__":
    main()
