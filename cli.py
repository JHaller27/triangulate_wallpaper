import argparse
from os import path as os_path

import painters
import mosaic_random
from graph import PolyGraph, ScatterGraph
from canvas import MosaicCanvas


# noinspection PyTypeChecker
def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    def resolution_type(x: str) -> list[int]:
        named_sizes = {
            '1k': [1024, 768],
            '2k': [2560, 1440],
            '4k': [3840, 2160],
        }

        if named_size := named_sizes.get(x):
            return named_size

        return [int(x)]

    default_noise = 20
    default_gauss_sigma = 15
    valid_layers = {'colors', 'centers', 'lines', 'points'}

    def layer(x: str) -> str:
        if x not in valid_layers:
            raise argparse.ArgumentError(None, f"Layer '{x}' is not a valid layer.")
        return x

    parser.add_argument('template', type=str,
                        help='Path to template image to retrieve colors from')
    parser.add_argument('--url', action='store_true',
                        help='Interpret the template as a url')
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


def get_save_path(args) -> str:
    def auto_generate_path():
        if args.template.startswith("#"):
            start = f"rgb_{args.template[1:]}"
        else:
            start = os_path.splitext(os_path.basename(args.template))[0]

        return f"{start}_{args._size[0]}x{args._size[1]}_{mosaic_random.get_seed()}.png"

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

    title = f"Wallpaper ({img_width}x{img_height}) - {args.template}"

    if 'colors' not in args.layers:
        painter = painters.ColorPainter()
    elif args.url:
        painter = painters.UrlTemplatePainter(img_width, img_height, args.template)
    elif args.template.startswith('#'):
        painter = painters.ColorPainter(args.template)
    else:
        painter = painters.LocalTemplatePainter(img_width, img_height, args.template)

    if args.gauss is not None:
        painter = painters.GaussyPainter(painter, args.gauss)
    if args.noise:
        painter = painters.NoisyPainter(painter, args.noise)

    canvas = MosaicCanvas(painter, width=img_width, height=img_height)

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
