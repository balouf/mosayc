# Mosayc


[![PyPI Status](https://img.shields.io/pypi/v/mosayc.svg)](https://pypi.python.org/pypi/mosayc)
[![Build Status](https://github.com/balouf/mosayc/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/balouf/mosayc/actions?query=workflow%3Abuild)
[![Documentation Status](https://github.com/balouf/mosayc/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/balouf/mosayc/actions?query=workflow%3Adocs)
[![License](https://img.shields.io/github/license/balouf/mosayc)](https://github.com/balouf/mosayc/blob/main/LICENSE)
[![Code Coverage](https://codecov.io/gh/balouf/mosayc/branch/main/graphs/badge.svg)](https://codecov.io/gh/balouf/mosayc/tree/main)

Mosayc creates tile-based mosaics of pictures.


- Free software: MIT license
- Documentation: https://balouf.github.io/mosayc/.

This software is inspired by the script proposed here:
https://towardsdatascience.com/how-to-create-a-photo-mosaic-in-python-45c94f6e8308

--------
Features
--------

* Command-line interface
* Tile assignement is powered by matching theory, avoiding to re-use always the same tiles.
* Tile colors can be shifted to be more consistent with the target *pixel*.
* Multi-processing.
* Automatic computation of the median aspect ratio.
* Original aspect ratios of tiles can be preserved.
* Can add a random tilt to pictures to give a *manual* feeling.


## Credits

This package was created with [Cookiecutter][CC] and the [Package Helper 3][PH3] project template.

[CC]: https://github.com/audreyr/cookiecutter
[PH3]: https://balouf.github.io/package-helper-3/
