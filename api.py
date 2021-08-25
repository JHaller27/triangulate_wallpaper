from fastapi.responses import FileResponse
from fastapi import FastAPI

import painters
import mosaic_random
from graph import PolyGraph, ScatterGraph
from canvas import MosaicCanvas

from pathlib import Path
import os


app = FastAPI(title="Triangulate Wallpaper")


@app.get("/wallpaper/{color}/", response_class=FileResponse)
def wallpaper(color: str, width: int = 1920, height: int = 1080, noise: int = 15):
    painter = painters.ColorPainter(f'#{color}')
    painter = painters.NoisyPainter(painter, [noise])

    canvas = MosaicCanvas(painter, width=width, height=height)
    graph = ScatterGraph(width, height, count=100, margin=200)

    graph.triangulate()

    canvas.draw_graph(graph, ['colors'])

    store_dir = os.environ.get('IMAGE_STORE', '/tmp')
    store_path = Path(store_dir)
    path = store_path / 'triangles.png'
    canvas.save_to(str(path))

    return path

