======
Mosayc
======


.. image:: https://img.shields.io/pypi/v/mosayc.svg
        :target: https://pypi.python.org/pypi/mosayc
        :alt: PyPI Status

.. image:: https://github.com/balouf/mosayc/workflows/build/badge.svg?branch=main
        :target: https://github.com/balouf/mosayc/actions?query=workflow%3Abuild
        :alt: Build Status

.. image:: https://github.com/balouf/mosayc/workflows/docs/badge.svg?branch=main
        :target: https://github.com/balouf/mosayc/actions?query=workflow%3Adocs
        :alt: Documentation Status


.. image:: https://codecov.io/gh/balouf/mosayc/branch/main/graphs/badge.svg
        :target: https://codecov.io/gh/balouf/mosayc/tree/main
        :alt: Code Coverage



Mosayc creates tile-based mosaics of pictures.


* Free software: GNU General Public License v3
* Documentation: https://balouf.github.io/mosayc/.

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

-------
Credits
-------

This package was created with Cookiecutter_ and the `francois-durand/package_helper_2`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`francois-durand/package_helper_2`: https://github.com/francois-durand/package_helper_2
