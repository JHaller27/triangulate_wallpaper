import fastapi.exceptions
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends

import mosaic_random
import painters
from graph import Graph, PolyGraph, ScatterGraph
from canvas import ICanvas, MosaicCanvas

import random
from pathlib import Path
import os
from typing import Callable, Optional


MAX_PIXEL_COUNT = 3840*2160


app = FastAPI(title="Triangulate Wallpaper")


def get_base(url: str = None, color: str = None) -> str:
    if url is not None:
        return url

    if color is not None:
        return f'#{color}'

    color_values = (random.randrange(0, 0x100) for _ in range(3))
    color = '#{:02x}{:02x}{:02x}'.format(*color_values)

    return color


def get_noisy_painter(noise: int = 20, gauss: int = None) -> Callable[[painters.TrianglePainter], painters.TrianglePainter]:
    if gauss is not None:
        return lambda base: painters.GaussyPainter(base, gauss)
    if noise is not None:
        return lambda base: painters.NoisyPainter(base, [noise])
    return lambda base: base


def get_canvas(base=Depends(get_base), noisy_paint_getter=Depends(get_noisy_painter),
               width: int = 1920, height: int = 1080, count: int = 100, seed: int = None) -> ICanvas:
    if seed is not None:
        mosaic_random.set_seed(seed)
    if width * height > MAX_PIXEL_COUNT:
        raise fastapi.exceptions.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                                               detail="Too many pixels! Try a smaller size (maximum of 4k resolution)")

    if base.startswith('#'):
        painter = painters.ColorPainter(base)
    else:
        painter = painters.UrlTemplatePainter(width, height, base)
    painter = noisy_paint_getter(painter)

    canvas = MosaicCanvas(painter, width=width, height=height)

    graph = ScatterGraph(canvas.width, canvas.height, count=count, margin=200)
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
