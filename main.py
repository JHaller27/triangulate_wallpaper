import argparse
import mosaic_random
import tkinter as tk
import io
from os import path as os_path
from PIL import Image

from graph import Point, Edge, Graph, PolyGraph, ScatterGraph


POINT_SIZE = 2
POINT_COLOR = "red"
LINE_COLOR = "white"
CENTROID_COLOR = "green"


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
    default_gauss_sigma = 15
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
    parser.add_argument('--gauss', nargs='?', type=int, default=0,
                        help="Add gaussian noise to each RGB value individually. "
                             "If no value is defined, or if value is 0, will use default sigma value of 20.")
    parser.add_argument('--poly', action='store_true',
                        help='Show regularly-placed triangles instead of random triangles')

    args = parser.parse_args()

    if isinstance(args.size[0], list):
        args.size = args.size[0]

    if args.save is None:
        # This means param list has just `--save`
        args.save = ''
    elif args.save == '':
        # This means param list is missing the save flag
        args.save = None

    if args.noise is not None and len(args.noise) == 0:
        args.noise = [default_noise]

    if args.gauss is None:
        # This means param list has just `--gauss`
        args.gauss = default_gauss_sigma
    elif args.gauss == 0:
        # This means param list has `--gauss 0` or is missing the gauss flag
        args.gauss = None

    return args


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
        adjustment = mosaic_random.get_random().randint(self._rand_min, self._rand_max)
        pxl_adjd = (x + adjustment for x in pxl)

        return pxl_adjd


class GaussyPainter(TrianglePainter):
    def __init__(self, base: TrianglePainter, sigma: int):
        self._base = base
        self._sigma = sigma

    def _get_color_tupe(self, a: Point, b: Point, c: Point) -> (int, int, int):
        pxl = self._base._get_color_tupe(a, b, c)
        pxl_adjd = (int(mosaic_random.get_random().gauss(x, self._sigma)) for x in pxl)

        return pxl_adjd


class MosaicCanvas(tk.Canvas):
    _root: tk.Tk
    _width: int
    _height: int
    _triangle_painter: TrianglePainter

    def __init__(self, painter: TrianglePainter, *args, **kwargs):
        self._root = tk.Tk()

        super().__init__(self._root, *args, **kwargs)

        self._triangle_painter = painter

        self._width = kwargs['width']
        self._height = kwargs['height']

        self._edges = set()

    def display(self, title: str):
        self._root.wm_title(title)
        self._root.mainloop()

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

    def draw_graph(self, g: Graph, show_layers: list):
        show_centers = 'centers' in show_layers
        for t in g.triangles:
            self.create_triangle(t)

            # Draw centroids
            if show_centers:
                centroid = find_centroid(t, self._width, self._height)
                self.create_point(centroid, fill=CENTROID_COLOR)

        # Draw edges
        if 'lines' in show_layers:
            for e in g.edges:
                self.create_edge(e)

        # Draw Points
        if 'points' in show_layers:
            for p in g.points:
                self.create_point(p)

    def save_to(self, path: str):
        width = self._width
        height = self._height

        ps = self.postscript(height=height, width=width,
                             pageheight=height - 1, pagewidth=width - 1,
                             colormode="color")
        img = Image.open(io.BytesIO(ps.encode("utf-8")))
        img = img.convert(mode="RGB")
        img.save(path, "png")
        print(f"Image saved to {path}")


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


def get_save_path(args) -> str:
    def auto_generate_path():
        if args.template.startswith("#"):
            start = f"rgb_{args.template[1:]}"
        else:
            start = os_path.splitext(os_path.basename(args.template))[0]

        return f"{start}_{args.size[0]}x{args.size[1]}_{mosaic_random.get_seed()}.png"

    if args.save == "":
        return auto_generate_path()

    if os_path.isdir(args.save):
        basename = auto_generate_path()
        dirpath = args.save
    else:
        basename = os_path.basename(args.save)
        dirpath = os_path.dirname(args.save)

    return os_path.join(dirpath, basename)


def main():
    args = get_args()
    img_width, img_height = args.size

    if args.seed is not None:
        mosaic_random.set_seed(args.seed)

    print(f"Seed {mosaic_random.get_seed()}")

    title = f"Wallpaper ({img_width}x{img_height})"

    if 'colors' not in args.layers:
        painter = ColorPainter()
    elif args.template.startswith('#'):
        painter = ColorPainter(args.template)
    else:
        painter = TemplatePainter(args.template, img_width, img_height)
        title += f"- {args.template}"

    if args.gauss is not None:
        painter = GaussyPainter(painter, args.gauss)
    if args.noise:
        painter = NoisyPainter(painter, args.noise)

    canvas = MosaicCanvas(painter,
                          width=img_width, height=img_height,
                          borderwidth=0, highlightthickness=0,
                          background="black")
    canvas.grid()

    if args.poly:
        graph = PolyGraph(img_width, img_height, args.point_count, args.margin)
    else:
        graph = ScatterGraph(img_width, img_height, args.point_count, args.margin)
    graph.triangulate()

    canvas.draw_graph(graph, args.layers)

    if args.save is not None:
        path = get_save_path(args)
        canvas.save_to(path)
    else:
        print('Displaying image in window')
        canvas.display(title)


if __name__ == "__main__":
    main()
