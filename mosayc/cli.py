"""Usage: mosayc [OPTIONS]

  Console script for mosayc.

Options:
  -I, --input PATH         Location of the main photo  [default: main.jpeg]
  -O, --output PATH        Mosaic name  [default: mosaic.jpeg]
  -D, --tiles_dir PATH     Location of the tiles directory  [default: tiles]
  -S, --scale FLOAT        Scaling factor of main photo  [default: 3.0]
  -T, --tilt FLOAT         Max tilt of tiles  [default: 10.0]
  -C, --color_shift FLOAT  Color adjustment intensity  [default: 100.0]
  -Q, --quotas INTEGER     Max number of copies of a tile  [default: 3]
  -R, --root_dir PATH      Working directory  [default: .]
  --help                   Show this message and exit.
"""

import sys
import click
from pathlib import Path

from mosayc.parameters import get_parameters
from mosayc.mosayc import Mosayc

params = get_parameters()


@click.command()
@click.option(
    "--input",
    "-I",
    type=click.Path(),
    default=params.input,
    show_default=True,
    help="Location of the main photo",
)
@click.option(
    "--output",
    "-O",
    type=click.Path(),
    default=params.output,
    show_default=True,
    help="Mosaic name",
)
@click.option(
    "--tiles_dir",
    "-D",
    type=click.Path(),
    default=params.tiles_dir,
    help="Location of the tiles directory",
    show_default=True,
)
@click.option(
    "--scale",
    "-S",
    type=click.FLOAT,
    default=params.scale,
    show_default=True,
    help="Scaling factor of main photo",
)
@click.option(
    "--tilt", "-T", default=params.tilt, help="Max tilt of tiles", show_default=True
)
@click.option(
    "--color_shift",
    "-C",
    default=params.color_shift,
    help="Color adjustment intensity",
    show_default=True,
)
@click.option(
    "--quotas",
    "-Q",
    default=params.quotas,
    help="Max number of copies of a tile",
    show_default=True,
)
@click.option(
    "--root_dir",
    "-R",
    type=click.Path(),
    default=params.root_dir,
    help="Working directory",
    show_default=True,
)
def main(**kwargs):
    """
    Console script for mosayc.
    """
    m = Mosayc(**kwargs)
    img = m.compute()
    dest = Path(m.parameters.root_dir) / m.parameters.output
    img.save(dest)
    click.echo(f"Mosaic saved at {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
