from pydantic import BaseModel
from pathlib import Path
import yaml


default_parameters = {
    "input": "main.jpeg",
    "output": "mosaic.jpeg",
    "tiles_dir": "tiles",
    "scale": 3,
    "tilt": 10,
    "color_shift": 100,
    "quotas": 3,
    "root_dir": ".",
}
"""Default values. Can be overriden by `.mosayc` config file or input values."""


class Parameters(BaseModel):
    """
    Dataclass representing parameters for a mosaic.
    """

    input: str
    output: str
    tiles_dir: str
    scale: float
    tilt: float
    color_shift: float
    quotas: int
    root_dir: str


def get_parameters(erase_config=False):
    """

    Parameters
    ----------
    erase_config: :class:`bool`, default=False
        Restore config file with default values.


    Returns
    -------
    :class:`~mosayc.parameters.Parameters`
        Values to use.

    Examples
    --------

    If no config file is provided, the default parameters are used and a config file is created.

    >>> p = get_parameters()
    >>> p
    Parameters(input='main.jpeg', output='mosaic.jpeg', tiles_dir='tiles', scale=3.0, tilt=10.0, color_shift=100.0, quotas=3, root_dir='.')

    If the config file exists, its values are loaded.

    >>> p.scale = .4
    >>> conf_file = Path.home() / ".mosayc"
    >>> with open(conf_file, "wt", encoding="utf8") as f:
    ...     yaml.dump(p.__dict__, f)
    >>> p = get_parameters()
    >>> p.scale
    0.4

    If `erase_config` is True, the config file is re-created with default values.

    >>> p = get_parameters(erase_config=True)
    >>> p.scale
    3.0
    """
    conf_file = Path.home() / ".mosayc"
    if conf_file.exists() and not erase_config:
        with open(conf_file, "rt", encoding="utf8") as f:
            return Parameters(**yaml.safe_load(f))
    else:
        with open(conf_file, "wt", encoding="utf8") as f:
            yaml.dump(default_parameters, f)
        return Parameters(**default_parameters)
