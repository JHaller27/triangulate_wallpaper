from fastapi.responses import FileResponse
from fastapi import FastAPI

import painters
import mosaic_random
from graph import PolyGraph, ScatterGraph
from canvas import MosaicCanvas


app = FastAPI(title="Triangulate Wallpaper")


@app.get("/wallpaper/{color}/", response_class=FileResponse)
def wallpaper(color: str, width: int = 1920, height: int = 1080, noise: int = 15):
    painter = painters.ColorPainter(f'#{color}')
    painter = painters.NoisyPainter(painter, [noise])

    canvas = MosaicCanvas(painter, width=width, height=height)
    graph = ScatterGraph(width, height, count=100, margin=200)

    graph.triangulate()

    canvas.draw_graph(graph, ['colors'])

    path = f'/tmp/triangles.png'
    canvas.save_to(path)

    return path
