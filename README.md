# Triangulate Wallpaper
_Create a triangle-mosaic desktop wallpaper based on a given image_

## Requirements

* Python 3.9 or higher (3.6 - 3.8 may work but have not been tested)
* Pip packages in `requirements.txt`
* [tkinter](https://tkdocs.com/tutorial/install.html)

## Installation

1. Download the source code
1. (Optional) Create a Python venv and activate
   - (See "Virtual Environments" section below for instructions)
1. Pip install requirements
   - `pip install -r requirements.txt`

### Virtual Environments
- `python -m venv venv`
- Run the activate script
 - Windows
   - PowerShell `.\venv\Sripts\Activate.ps1`
   - Cmd `.\venv\Scripts\activate.bat`
 - Linux `./venv/scripts/activate`
- When done creating mosaics, `deactivate`

## Usage

`python main.py -h|--help` to see usage. Where the README and `--help` conflict, the `--help` is correct.

### `--size`
_Format: `--size preset | --size width height`_

_Default: `1920 1080`_


The size of the mosaic. You may specify either a preset - `4k` or `2k` - or a `width` and `height` in pixels.

Note: If the size of the image is larger than your screen, you may have trouble viewing the image.
In this case, for now it is best to save with `--save` (see below) and open the output in a separate image viewer.

### `--margin`
_Format: `--margin size`_

_Default: `20`_

This is the margin outside of the viewable image area in which triangle vertices may be generated.

### `--count`
_Format: `--count POINT_COUNT`_

_Default: `200`_

The number of vertices - and consequently triangles - to generate.

More points equals smaller triangles.

### `--seed`
_Format: `--seed SEED`_

_Default: random_

The value with which to seed the random generator.

Two mosaics given the same canvas size, margins, number of points, noise flag, and seed are guaranteed to have the same arrangement of triangles.

Note that every run will print the seed to the console.
This means a common workflow is to generate images one after another until you find one you like.
Then generate that same image again, copy+pasting the seed to the `--seed` argument and saving with `--save`.

### `--show`
_Format: `--show [LAYER [LAYER ...]]`_

_Default: `colors`_

The mosaic layers to display. See table below for valid options and descriptions.

This is useful primarily for debugging.

| Layer | Description |
|:------|:------------|
| `colors` | Color of the triangles |
| `lines` | The lines (edges) of the triangles |
| `points` | The points (vertices) of the triangles |
| `centers` | The centers of the triangles (identical to the locations where colors are read from on the base image)


### `--save`
_Format: `--save PATH`_

_Default: show in window_

Save the image to a file instead of displaying it to the screen.

To auto-generate a file name, use `--save .`


### `--noise`
_Formate: `--noise`_

Toggle on auto-generate noise in image.

Randomly raises or lowers the RGB value of each triangle's color by 20 (min 0, max 255).

### Notes
This requires a source image that the mosaic output is based on.

This source image can be of any size and will be scaled to match the size of the mosaic.

The most interesting mosaics have "noisy" sources,
that is, source images where no two nearby pixels are identical.
Good rules of thumb are to find images that are **gradients**, **noisy**, or both.

Such images can be found via your favorite search engine, or generated.
I've found that the best mosaics come from sources that have a gradient and are run through a solid noise filter.