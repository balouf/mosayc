"""Top-level package for Mosayc."""

from importlib.metadata import metadata

from mosayc.mosayc import Mosayc as Mosayc


infos = metadata(__name__)
__version__ = infos["Version"]
__author__ = "Fabien Mathieu"
__email__ = "fabien.mathieu@normalesup.org"
