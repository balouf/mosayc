from pathlib import Path
from PIL import ImageOps, Image, UnidentifiedImageError
from fractions import Fraction
from pydantic import BaseModel
from tqdm.auto import tqdm
import numpy as np

from mosayc.parameters import get_parameters


class ImageInfo:
    """
    Parameters
    ----------
    path: :class:`~pathlib.Path` or :class:`str`
        Path to the image.

    Examples
    --------

    >>> img = ImageInfo('example/main.jpeg')
    >>> img  # doctest: +ELLIPSIS
    img(...main.jpeg, size=1024x1024 (1/1), color=[75.18568993 59.76046181 26.39377594])

    >>> ImageInfo('not_a_file_that_exists.jpeg')
    Traceback (most recent call last):
    ...
    ValueError: File not_a_file_that_exists.jpeg does not exists.
    """

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            raise ValueError(f"File {self.path} does not exists.")
        img = self.pil
        self.color = np.array(img).mean(axis=0).mean(axis=0)
        self.width, self.height = img.size
        ratio = Fraction(self.width / self.height).limit_denominator(20)
        self.ratio = (ratio.numerator, ratio.denominator)
        self.thumb = None

    @property
    def pil(self):
        """
        The PIL Image object.
        """
        return ImageOps.exif_transpose(Image.open(self.path)).convert("RGB")

    def __repr__(self):
        return f"img({self.path}, size={self.width}x{self.height} ({self.ratio[0]}/{self.ratio[1]}), color={self.color})"


class Numerology(BaseModel):
    big_width: int
    big_height: int
    x: int
    y: int
    tile_width: int
    tile_height: int


class Mosayc:
    """
    Parameters
    ----------
    kwargs: :class:`dict`
        Cf :meth:`~mosayc.parameters.get_parameters`

    Examples
    --------

    >>> mosayc = Mosayc(root_dir='example', quotas=1, scale=.4)
    >>> img = mosayc.compute()
    >>> img.size
    (409, 409)

    Command line usage:

    >>> import subprocess
    >>> result = subprocess.run(["mosayc", "--help"], capture_output=True, text=True)
    >>> print(result.stdout)  # doctest: +SKIP
    Usage: mosayc [OPTIONS]
    <BLANKLINE>
      Console script for mosayc.
    <BLANKLINE>
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

    Some errors:

    >>> Mosayc(not_expected=True)
    Traceback (most recent call last):
    ...
    TypeError: Mosayc got an unexpected keyword argumment: not_expected
    """

    def __init__(self, **kwargs):
        self.parameters = get_parameters()
        for k, v in kwargs.items():
            if hasattr(self.parameters, k):
                setattr(self.parameters, k, v)
            else:
                raise TypeError(f"Mosayc got an unexpected keyword argumment: {k}")

        self.main = None
        self.tiles = None
        self.numerology = None

    def fetch(self):
        self.main = ImageInfo(Path(self.parameters.root_dir) / self.parameters.input)
        tiles_dir = Path(self.parameters.root_dir) / self.parameters.tiles_dir
        self.tiles = []
        tiles = tiles_dir.glob("*")
        for tile in tqdm(tiles, desc="Parse images", leave=False, position=1):
            try:
                self.tiles.append(ImageInfo(tile))
            except (UnidentifiedImageError, PermissionError):
                pass

    def numbers(self):
        big_width = int(self.main.width * self.parameters.scale)
        big_height = int(self.main.height * self.parameters.scale)
        max_tiles = len(self.tiles) * self.parameters.quotas
        ratio = np.median([i.width / i.height for i in self.tiles])
        x = max(1, int(np.floor(np.sqrt(max_tiles * big_width / big_height / ratio))))
        tile_width = (big_width // x) + 1
        y = max(1, max_tiles // x)
        tile_height = (big_height // y) + 1
        self.numerology = Numerology(
            big_width=big_width,
            big_height=big_height,
            x=x,
            y=y,
            tile_width=tile_width,
            tile_height=tile_height,
        )

    def compute(self):
        phases = tqdm(total=4, desc="Step", position=0)
        # Retrieve infos on photos
        self.fetch()
        phases.update(1)

        # Compute canvas and distances
        self.numbers()
        x = self.numerology.x
        y = self.numerology.y
        canvas = self.main.pil.resize((self.numerology.x, self.numerology.y))
        xy = x * y
        n = len(self.tiles)
        dist = np.zeros(n * xy)
        targets = np.zeros((xy, 3), dtype=int)
        for p in tqdm(range(xy), desc="Compute scores", leave=False, position=1):
            i = p // y
            j = p % y
            target = canvas.getpixel((i, j))
            targets[p] = target
            for k in range(n):
                dist[k * xy + p] = np.linalg.norm(target - self.tiles[k].color)
        phases.update(1)

        # Compute allocation
        edges = np.argsort(dist)
        quotas = self.parameters.quotas * np.ones(n, dtype=np.int32)
        results = n * np.ones((x, y), dtype=np.int32)
        order = []
        todo = xy
        allo = tqdm(edges, desc="Allocate tiles", leave=False, position=1)
        for e in allo:
            tile_index = e // xy
            if quotas[tile_index] > 0:
                ij = e % xy
                i = ij // y
                j = ij % y
                if results[i, j] == n:
                    results[i, j] = tile_index
                    order.append((i, j))
                    quotas[tile_index] -= 1
                    todo -= 1
                    if todo == 0:
                        break
        if hasattr(allo, "container"):
            allo.container.close()
        phases.update(1)

        # Build image
        big_w, big_h = self.numerology.big_width, self.numerology.big_height
        output = Image.new("RGBA", (big_w, big_h))
        t_w, t_h = self.numerology.tile_width, self.numerology.tile_height
        tilt = self.parameters.tilt
        # Draw tiles
        for i, j in tqdm(order[::-1], desc="Build image", leave=False, position=1):
            # Offset of tile
            xx, yy = i * t_w, j * t_h
            c_i = i * y + j
            # tile
            obj = self.tiles[results[i, j]]
            tile = obj.pil
            stretch = max(t_w / tile.size[0], t_h / tile.size[1]) * (1 + tilt / 100)
            tile = ImageOps.scale(tile, stretch)
            tile = np.array(tile) + self.parameters.color_shift / 100 * (
                targets[c_i] - obj.color
            )
            tile = np.minimum(tile, 255)
            tile = np.maximum(tile, 0)
            tile = Image.fromarray(tile.astype(np.uint8)).convert("RGBA")
            tile = tile.rotate(np.random.randint(2 * tilt + 1) - tilt, expand=True)
            output.paste(tile, (xx, yy), tile)
        phases.update(1)
        return output.convert("RGB")
