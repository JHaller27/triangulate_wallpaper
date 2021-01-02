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
 - Linux `. ./venv/scripts/activate`
- When done creating mosaics, `deactivate`

## Usage

`python main.py -h|--help` to see usage. Where the README and `--help` conflict, the `--help` is correct.

### `template`

The only required argument is the `template` - a path to the source image to use for choosing colors.

Optionally, you may instead specify an HTML RGB color preceeded by `#` (e.g. `#00f` / `#0000ff` for blue).
This looks best with the `--noise` flag set.

### `--url`
_Format: `--url`_

Interpret the `template` parameter as a url (using [urllib.request.urlopen](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen)).

### `--size`
_Format: `--size preset` or `--size width height`_

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

### `--poly`
_Format: `--poly`_

_Default: Random distribution_

When set, triangles are placed regularly rather than randomly.

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
_Format: `--save [PATH]`_

_Default: show in window_

Save the image to a file instead of displaying it to the screen.

May specify a new file in an existing directory,
or specify a directory and the file name will be auto-generated.

If no `PATH` is specified, a file name will be auto-generated.


### `--noise`
_Format: `--noise [TOLERANCE]` or `--noise [TOLERANCE1 TOLERANCE2]`_

_Default: No noise_

Toggle on auto-generate noise in image.

Randomly raises or lowers the RGB value of each triangle's color by the tolerance.

If no values are given, the tolerance will be +/- 20.

If a single value is given, the tolerance will be +/- that value.

If multiple values are given, the tolerance will be (min_value, max_value) - i.e. order does not matter;
positive values denote lightening, negative values denote darkening.


### `--gauss`
_Format: `--gauss [SIGMA]`_

_Default: `15`_

If you're feeling extra, this flag randomly deviates each RGB color individually.

Play around with the `SIGMA` value to get a feel for how much it changes, and to find something you like.

This usually looks like `--noise`, but with the color altered instead of brightness,
giving it a sort of multi-colored crystalline effect. Sehr schön!

Note: This can be combined with `--noise`, but noise from `--noise` is always applied after `--gauss`.

This is a serendipitous bug found during development that was refactored into a full feature!
Normally, a Gaussian distribution would have _mu_ = 0, then use the output as a (+/-) noise tolerance.
However, the previously-mentioned bug used the R/G/B value as _mu_, and generated a new noise variance for each color.
While this was not the intention, it was pretty nonetheless, and was deemed "interesting" enough to keep.


### Notes
This requires a source image that the mosaic output is based on.

This source image can be of any size and will be scaled to match the size of the mosaic.

The most interesting mosaics have "noisy" sources,
that is, source images where no two nearby pixels are identical.
Good rules of thumb are to find images that are **gradients**, **noisy**, or both.

Such images can be found via your favorite search engine, or generated.
I've found that the best mosaics come from sources that have a gradient and are run through a solid noise filter.
