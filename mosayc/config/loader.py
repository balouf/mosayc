import os
from pathlib import Path
import json

MODULE_PATH = Path(__file__).parents[1]
CONFIG_PATH = MODULE_PATH / 'config'
DEFAULT_LOCATIONS = [Path("."), CONFIG_PATH, Path('config')]


def process_locations(locations=None):
    """
    Parameters
    ----------
    locations: :class:`str` or :class:`~pathlib.Path` or :class:`list`, optional
        Directories where to look at.

    Returns
    -------
    :class:`list`
        Sanitized homogeneous list of existing locations.

    Examples
    --------

    Load default locations:

    >>> [f.parts[-2:] for f in process_locations()]
    [(), ('mosayc', 'config')]

    Load custom locations in different formats, some may not exist but at least one does.

    >>> process_locations(["docs", Path("mosayc/config"), "Not_a_dir"])
    [WindowsPath('docs'), WindowsPath('mosayc/config')]

    None of the locations exist:

    >>> process_locations(locations=['no_valid_directory', 'does_not_exist_either'])
    Traceback (most recent call last):
    ...
    ValueError: No valid location in ['no_valid_directory', 'does_not_exist_either'].

    Bad location type error:

    >>> process_locations(42)
    Traceback (most recent call last):
    ...
    TypeError: locations should be Path, str, list of (path or str), or None.
    """
    if locations is None:
        locations = DEFAULT_LOCATIONS
    elif isinstance(locations, str) or isinstance(locations, Path):
        locations = [Path(locations)]
    elif isinstance(locations, list):
        locations = [Path(loc) for loc in locations]
    else:
        raise TypeError(f"locations should be Path, str, list of (path or str), or None.")
    valid_locations = [loc for loc in locations if loc.exists()]
    if len(valid_locations) > 0:
        locations = valid_locations
    else:
        raise ValueError(f"No valid location in {[str(loc) for loc in locations]}.")
    return locations


def load_cfg(file_stems=None, locations=None):
    """
    Loads multiple json configuration files in one directory.

    Parameters
    ----------
    file_stems: :class:`str` or :class:`~pathlib.Path` or :class:`list`, optional
        File prefixes (stem) to look at. If None, try to infer from CONFIG_ENV, otherwise default to 'config'.
    locations: :class:`str` or :class:`~pathlib.Path` or :class:`list`, optional
        Directories where to look at.

    Returns
    -------
    :class:`dict`
        Concatenation of the contents of the yaml file.

    Examples
    --------

    Without any parameter, some default locations are tried.
    Assuming a config file is present in `config/config.yaml`
    with one mysql configuration and one redshift configuration, you should get something like that.

    >>> my_cfg = load_cfg()
    >>> [k for k in my_cfg]
    ['pexels']

    You can specify the possible locations and stems.

    >>> from tempfile import TemporaryDirectory as Tmp
    >>> new_key = {'my_super_key': {'param1': "my_name", 'param2': "my_secure_password_in_plain_string"}}
    >>> with Tmp() as tmp_dir:
    ...     with open(Path(tmp_dir)/"my_config.json", "wt") as f:
    ...         json.dump(new_key, f)
    ...     cfg_simple = load_cfg(locations=tmp_dir, file_stems="my_config")
    ...     cfg_multi = load_cfg(locations=[tmp_dir, *DEFAULT_LOCATIONS], file_stems=['config', "my_config"])
    >>> cfg_simple
    {'my_super_key': {'param1': 'my_name', 'param2': 'my_secure_password_in_plain_string'}}
    >>> cfg_multi.keys()
    dict_keys(['my_super_key', 'pexels'])

    File stem can be specified from environnement. If no file is found, an error is raised.

    >>> os.environ['CONFIG_ENV'] = 'bogus_name'
    >>> my_cfg = load_cfg()
    Traceback (most recent call last):
    ...
    FileNotFoundError: Not file founds amongst: bogus_name.json.

    Bad stem type error:

    >>> my_cfg = load_cfg(file_stems=42)
    Traceback (most recent call last):
    ...
    TypeError: file_stems should be str, list of str, or None.
    """
    if file_stems is None:
        if "CONFIG_ENV" in os.environ:
            file_stems = os.environ["CONFIG_ENV"].split(",")
        else:
            file_stems = ['config']
    elif isinstance(file_stems, str):
        file_stems = [file_stems]
    elif not isinstance(file_stems, list):
        raise TypeError(f"file_stems should be str, list of str, or None.")

    locations = process_locations(locations)

    files = [(loc / stem).with_suffix(".json") for loc in locations for stem in file_stems]
    valid_files = [f for f in files if f.exists()]

    if len(valid_files) > 0:
        files = valid_files
    else:
        raise FileNotFoundError(f"Not file founds amongst: {', '.join({f.name for f in files})}.")

    cfg = {}
    for file in files:
        with open(file) as f:
            cfg.update(json.load(f))
    return cfg
