from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends

import painters
from graph import Graph, PolyGraph, ScatterGraph
from canvas import ICanvas, MosaicCanvas

from pathlib import Path
import os


MAX_PIXEL_COUNT = 3840*2160


app = FastAPI(title="Triangulate Wallpaper")


def get_color(color: str = None) -> str:
    if color is not None:
        return color

    import random
    color_values = (random.randrange(0, 0x100) for _ in range(3))
    color = '{:02x}{:02x}{:02x}'.format(*color_values)

    return color


def get_painter(color=Depends(get_color), noise: int = 20) -> painters.TrianglePainter:
    painter = painters.ColorPainter(f'#{color}')
    painter = painters.NoisyPainter(painter, [noise])

    return painter


def get_canvas(width: int = 1920, height: int = 1080, painter=Depends(get_painter)) -> ICanvas:
    canvas = MosaicCanvas(painter, width=width, height=height)

    graph = ScatterGraph(canvas.width, canvas.height, count=100, margin=200)
    graph.triangulate()

    canvas.draw_graph(graph, ['colors'])

    return canvas


@app.get("/", response_class=FileResponse)
def wallpaper(canvas=Depends(get_canvas)):
    store_dir = os.environ.get('IMAGE_STORE', '/tmp')
    store_path = Path(store_dir)
    path = store_path / 'triangles.png'

    canvas.save_to(str(path))

    return path
