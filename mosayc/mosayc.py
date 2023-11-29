from pathlib import Path
from PIL import Image, ImageOps
from fractions import Fraction
from multiprocessing import cpu_count
from joblib import Parallel, delayed

import numpy as np


def get_tiles(tile_path):
    """
    Parameters
    ----------
    tile_path: :class:`str` or :class:`~pathlib.Path`
        Location of the tiles (all files inside the directory should be images).

    Returns
    -------
    :class:`list`
        List of images

    Examples
    --------

    >>> get_tiles("pictures/tiles")[:2]
    [WindowsPath('pictures/tiles/10874552.jpeg'), WindowsPath('pictures/tiles/10874555.jpeg')]
    """
    return [path for path in Path(tile_path).rglob('*')]


def compute_tile_ratio(tiles):
    """

    Parameters
    ----------
    tiles: :class:`list`
        Tiles

    Returns
    -------
    w: :class:`int`
        Width ratio
    h: :class:`int`
        Height ratio

    Examples
    --------

    >>> compute_tile_ratio(get_tiles("pictures/tiles"))
    (3, 4)
    """
    ratios = []
    for tile in tiles:
        if isinstance(tile, Path) or isinstance(tile, str):
            s = Image.open(tile).size
        elif isinstance(tile, Image):
            s = tile.size
        else:
            continue
        ratios.append(s[0] / s[1])
    ratios = np.array(ratios)
    f = Fraction(np.median(ratios)).limit_denominator(20)
    return f.numerator, f.denominator


def compute_tile_size(tiles, final_size, tile_ratio=None, redundancy=1):
    """
    Parameters
    ----------
    tiles: :class:`list`
        Tiles
    final_size: :class:`tuple`
        Dimension of the target in pixels
    tile_ratio: :class:`tuple`
        Target aspect ratio of tiles
    redundancy: :class:`int`
        Allowed redundancy in tiles

    Returns
    -------
    :class:`tuple`
        Target dimension of tiles

    Examples
    --------

    >>> tiles = get_tiles("pictures/tiles")
    >>> len(tiles)
    160
    >>> compute_tile_size(tiles, (3000, 4000))
    (240, 320)
    >>> compute_tile_size(tiles, (1000, 1000))
    (69, 92)
    >>> compute_tile_size(tiles, (3000, 4000), tile_ratio=(16, 9))
    (368, 207)
    >>> compute_tile_size(tiles, (3000, 4000), redundancy=5)
    (108, 144)
    """
    if tile_ratio is None:
        aspect = compute_tile_ratio(tiles)
    else:
        aspect = tile_ratio
    area = final_size[0] * final_size[1]
    pix_area = aspect[0] * aspect[1]
    n = len(tiles)
    x = int(np.ceil(np.sqrt(area / n / redundancy / pix_area)))
    return aspect[0] * x, aspect[1] * x


def crop_center(pil_img, final_size, shift=0):
    """
    Crops an image so it fits the target ratio.

    Parameters
    ----------
    pil_img: :class:`~PIL.Image`
        Input image.
    final_size: :class:`tuple`
        Final resolution.
    shift: :class:`float`, optional
        Relative shift to apply to the cropping. Image is centered by default.

    Returns
    -------
    :class:`~PIL.Image`

    Examples
    --------

    >>> img = Image.open("pictures/original.jpeg")
    >>> img.size
    (5472, 3452)
    >>> cropped_img = crop_center(img, (3000, 3000))
    >>> cropped_img.size
    (3452, 3452)
    >>> cropped_img = crop_center(img, (3000, 1500), shift=.2)
    >>> cropped_img.size
    (5472, 2736)
    """
    img_width, img_height = pil_img.size
    if img_height / img_width > final_size[1] / final_size[0]:
        crop_width = img_width
        crop_height = int(img_width * final_size[1] / final_size[0])
        x_shift = 0
        y_shift = int((img_height - crop_height) * shift)
    else:
        crop_height = img_height
        crop_width = int(img_height * final_size[0] / final_size[1])
        x_shift = int((img_width - crop_width) * shift)
        y_shift = 0
    return pil_img.crop(((img_width - crop_width) // 2 + x_shift,
                         (img_height - crop_height) // 2 + y_shift,
                         (img_width + crop_width) // 2 + x_shift,
                         (img_height + crop_height) // 2 + y_shift))


def auto_switch(img, final_size):
    """
    Parameters
    ----------
    img: :class:`~PIL.Image`
        Input image.
    final_size: :class:`tuple`
        Final resolution.

    Returns
    -------
    :class:`tuple`
        Possibly rotated final size

    Examples
    ---------

    >>> img = Image.open("pictures/original.jpeg")
    >>> img.size
    (5472, 3452)
    >>> auto_switch(img, (400, 300))
    (400, 300)
    >>> auto_switch(img, (300, 400))
    (400, 300)
    """
    img_size = img.size
    if (img_size[0] < img_size[1]) != (final_size[0] < final_size[1]):
        return final_size[1], final_size[0]
    else:
        return final_size


def main_pixelate(main_photo, final_size, tile_size, shift=0):
    """
    Resize the original so one pixel is a tile.

    Parameters
    ----------
    main_photo
    final_size
    tile_size
    shift

    Returns
    -------

    """
    main_photo = crop_center(main_photo, final_size, shift=shift)
    width = int(np.round(final_size[0] / tile_size[0]))
    height = int(np.round(final_size[1] / tile_size[1]))
    return main_photo.resize((width, height))


def resize(path, tile_size):
    tile = ImageOps.exif_transpose(Image.open(path))
    xs = tile_size[0] / tile.size[0]
    ys = tile_size[1] / tile.size[1]
    #     tile = tile.resize(tile_size)
    tile = ImageOps.scale(tile, max(xs, ys) * 1.1)
    return tile


# Import and resize all tiles
def get_thumbs(tiles, tile_size):
    return Parallel(n_jobs=max(1, cpu_count() - 1))(delayed(resize)(path, tile_size)
                                                    for path in tiles)


# Calculate dominant color
def get_tile_colors(tiles):
    colors = []
    for tile in tiles:
        mean_color = np.array(tile).mean(axis=0).mean(axis=0)
        colors.append(mean_color)
    return colors


def compute(resized_photo, colors):
    #
    width, height = resized_photo.size
    xy = width * height
    # total photos quota
    total_b = round(xy)
    # Compute distances between all pictures and all pixels
    s = len(colors)
    dist = np.zeros(s * xy)
    for p in range(xy):
        x = p // height
        y = p % height
        for si in range(s):
            dist[si * xy + p] = np.linalg.norm(resized_photo.getpixel((x, y))-colors[si])
    # Sort the indexes by increasing distance
    edges = np.argsort(dist)
    # Prepare main loop
    bb = np.ceil(total_b / s)
    print(bb)
    quotas = bb * np.ones(s, dtype=np.int32)
    results = s * np.ones((width, height), dtype=np.int32)
    order = []
    pixels = xy
    # Main allocation loop
    for e in edges:
        # edge center
        si = e // xy
        # Check center needs to expand
        if quotas[si] != 0:
            # Pixel
            xyi = e % xy
            xi = xyi // height
            yi = xyi % height
            # Check pixel is free
            if results[xi, yi] == s:
                results[xi, yi] = si
                order.append((xi, yi))
                quotas[si] -= 1
                pixels -= 1
                if pixels == 0:
                    break
    return results, order


def build_image(final_size, tiles, tile_size, colors, resized_photo, tilt, assignment, order):
    # Create an output image
    output = Image.new('RGBA', final_size)

    # Draw tiles
    for i, j in order[::-1]:
        # Offset of tile
        x, y = i*tile_size[0], j*tile_size[1]
        # Index of tile
        index = assignment[i, j] # closest_tiles[i, j]
        # get photo
        current_tile = np.array(tiles[index]) + (resized_photo.getpixel((i, j))-colors[index])
        current_tile = np.minimum(current_tile, 255)
        current_tile = np.maximum(current_tile, 0)
        current_tile = Image.fromarray(current_tile.astype(np.uint8)).convert('RGBA')
        current_tile = current_tile.rotate(np.random.randint(2*tilt+1)-tilt, expand=True)
        output.paste(current_tile, (x, y), current_tile)
    return output


# Save output
def mozaic(main_photo_path, tile_path, final_size = (6406, 4819), redundancy=1, tilt=10):

    main_photo = ImageOps.exif_transpose(Image.open(Path(main_photo_path)))
    final_size = auto_switch(main_photo, final_size)

    tiles = get_tiles(tile_path)
    tile_size = compute_tile_size(tiles, final_size, redundancy=redundancy)
    print(f"Target tile size for redundancy {redundancy}: {tile_size}")

    resized_photo = main_pixelate(main_photo, final_size, tile_size)
    print("Main photo resized.")

    tiles = get_thumbs(tiles, tile_size)
    print(f"{len(tiles)} base tiles computed.")

    colors = get_tile_colors(tiles)
    print(f"Tiles colors computed.")

    assignment, order = compute(resized_photo, colors)
    print(f"Matching completed")

    output = build_image(final_size, tiles, tile_size, colors, resized_photo, tilt, assignment, order)
    print(f"Image built.")
    return output

    
def save_img(img, name="output.jpg"):
    img.convert('RGB').save(name)
