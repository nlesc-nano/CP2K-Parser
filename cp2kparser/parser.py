"""A module for converting CP2K_ input files into PLAMS_ compatible dictionaries.

The CP2K inputfile conversion is initiated by supplying the filename to :func:`.read_input`.

.. _CP2K: https://www.cp2k.org/
.. _PLAMS: https://www.scm.com/doc/plams/index.html

Index
-----
.. currentmodule:: cp2kparser.parser
.. autosummary::

    value_to_float
    value_to_int
    split_str
    parse_multi_keys
    parse_header
    parse_block
    recursive_update
    read_input

Functions
---------
.. autofunction:: cp2kparser.parser.value_to_float
.. autofunction:: cp2kparser.parser.value_to_int
.. autofunction:: cp2kparser.parser.split_str
.. autofunction:: cp2kparser.parser.parse_multi_keys
.. autofunction:: cp2kparser.parser.parse_header
.. autofunction:: cp2kparser.parser.parse_block
.. autofunction:: cp2kparser.parser.recursive_update
.. autofunction:: cp2kparser.parser.read_input

"""

from __future__ import annotations

import os
from typing import TypeVar, Any
from collections.abc import MutableMapping, Iterator

__all__ = ['read_input']

_T = TypeVar('_T')


def value_to_float(item: _T) -> _T | float:
    """Try to convert a string, **item**, into a float.

    Return **item** without any type conversion if a :exc:`ValueError` is raised.

    Examples
    --------
    .. code:: python

        >>> out1 = value_to_float('1.0')
        >>> out2 = value_to_float('one')
        >>> print(repr(out1), repr(out2))
        1.0 'one'

    Parameters
    ----------
    item : :class:`str`
        A string.

    Returns
    -------
    :class:`float` or :class:`str`
        A float constructed from **value**.
        Returns the unmodified **value** if a :exc:`ValueError` is raised.

    """
    try:
        return float(item)
    except ValueError:
        return item


def value_to_int(item: _T) -> _T | int:
    """Try to convert a string, **item**, into an integer.

    Return **item** without any type conversion if a :exc:`ValueError` is raised.

    Examples
    --------
    .. code:: python

        >>> out1 = value_to_int('1')
        >>> out2 = value_to_int('one')
        >>> print(repr(out1), repr(out2))
        1 'one'

    Parameters
    ----------
    item : :class:`str`
        A string.

    Returns
    -------
    :class:`int` or :class:`str`
        An integer constructed from **value**.
        Returns the unmodified **value** if a :exc:`ValueError` is raised.

    """
    try:
        return int(item)
    except ValueError:
        return item


def split_str(item: str, sep: None | str = None) -> tuple[str, str]:
    """Split a string into a key and a value.

    The first word in the to-be returned key is decapitalized if it contains any spaces.

    Examples
    --------
    .. code:: python

        >>> out1 = split_str('A')
        >>> out2 = split_str('A B')
        >>> out3 = split_str('A B C')
        >>> print(out1, out2, out3)
        ('a', '') ('a', 'B') ('a', 'B C')

    Parameters
    ----------
    item : :class:`str`
        A string.
    sep : :class:`str`, optional
        The delimiter according which to split **item**.
        ``None`` (the default value) means split according to any whitespace,
        and discard empty strings from the result.

    Returns
    -------
    :class:`tuple[str, str] <tuple>`
        A tuple of two string created by splitting **item**.
        The first string is decapitalized.

    """
    sep = sep if sep is not None else ' '
    try:
        key, value = item.split(sep, maxsplit=1)
    except ValueError:
        key = item
        value = ''

    if sep in key:
        key = parse_multi_keys(key)
    else:
        key = key.lower()

    return key, value


def parse_multi_keys(item: str, sep: None | str = None) -> str:
    """Parse keys that contain one or more spaces (see **sep**).

    The first word in the to-be returned key is decapitalized.

    Examples
    --------
    .. code:: python

        >>> out = parse_multi_keys('A B')
        >>> print(repr(out))
        'a B'

    Parameters
    ----------
    item : :class:`str`
        A string containing at least a single space.
    sep : :class:`str`, optional
        The delimiter according which to split **item**.
        ``None`` (the default value) means split according to any whitespace,
        and discard empty strings from the result.

    Returns
    -------
    :class:`str`
        **item** with its first word decapitalized.

    Raises
    ------
    ValueError
        Raised if **item** does not contain any whitespaces.

    """
    sep = sep if sep is not None else ' '
    i1, i2 = item.split(sep, maxsplit=1)
    i1 = i1.lstrip('&').lower()
    return sep.join((i1, i2))


def parse_header(
    input_gen: Iterator[str],
    item: str,
    container: MutableMapping[str, Any],
) -> None:
    r"""Parse CP2K headers.

    Parameters
    ----------
    input_gen : :class:`Iterator[str] <collections.abc.Iterator>`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.
    item : :class:`str`
        A string containing the header key.
    container : :class:`MutableMapping[str, Any] <collections.abc.MutableMapping>`
        A to-be filled dictionary.

    """
    if ' ' in item:
        key = parse_multi_keys(item)
    else:
        key = item.lstrip('&').lower()

    # container[key] is a list; append the list
    if key in container and isinstance(container[key], list):
        container[key].append({})
        recursive_update(input_gen, container[key][-1])

    # container[key] already exists; convert container[key] into a list of dictionaries
    elif key in container:
        value_old = container[key]
        container[key] = [value_old, {}]
        recursive_update(input_gen, container[key][-1])

    # Create a new nested dctionary
    else:
        container[key] = {}
        recursive_update(input_gen, container[key])


def parse_block(item: str, container: MutableMapping[str, float | str]) -> None:
    """Parse CP2K blocks.

    Parameters
    ----------
    item : :class:`str`
        A string containing a key and value.
    container : :class:`MutableMapping[str, Any] <collections.abc.MutableMapping>`
        A to-be filled dictionary.

    """
    key, _value = split_str(item)
    if '.' in _value:
        value: str | float = value_to_float(_value)
    else:
        value = value_to_int(_value)
    container[key] = value


def parse_coord_block(
    input_gen: Iterator[str],
    container: MutableMapping[str, MutableMapping[str, list[str]]],
) -> None:
    """Parse ``"coord"`` blocks.

    Parameters
    ----------
    input_gen : :class:`Iterator[str] <collections.abc.Iterator>`
        A string containing a key and value.
    container : :class:`MutableMapping[str, Any] <collections.abc.MutableMapping>`
        A to-be filled dictionary.

    """
    coord: list[str] = []

    item = next(input_gen)
    container['coord'] = {}
    container['coord']['_1'] = coord
    while item.lower() != '&end':
        coord.append(item)
        item = next(input_gen)
    return


def recursive_update(
    input_gen: Iterator[str],
    container: MutableMapping[str, Any],
) -> None:
    r"""Update **container** an a recursive manner.

    Parameters
    ----------
    input_gen : :class:`Iterator[str] <collections.abc.Iterator>`
        A generator looping over a sanitized CP2K input file.
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.
    container : :class:`MutableMapping[str, Any] <collections.abc.MutableMapping>`
        A to-be filled dictionary.

    """
    for item in input_gen:
        if item.lower() == '&coord':
            parse_coord_block(input_gen, container)
        elif item[0] == '&' and item[0:4].lower() != '&end':
            parse_header(input_gen, item, container)
        elif item[0:4].lower() != '&end':
            parse_block(item, container)
        else:  # End of a block
            return


def _prepare_test() -> str:
    """Helper function for the :func:`read_input` doctest."""
    import textwrap
    import tempfile

    _, file = tempfile.mkstemp(text=True)
    with open(file, "w") as f:
        f.write(textwrap.dedent("""            &FORCE_EVAL
                &DFT
                    BASIS_SET_FILE_NAME  /path/to/basis
                    &MGRID
                        CUTOFF  400
                        NGRIDS  4
                    &END
                    &POISSON
                    &END
                    &LOCALIZE T
                    &END
                    POTENTIAL_FILE_NAME  /path/to/potential
                    &QS
                        METHOD  GPW
                    &END
                    &SCF
                        EPS_SCF  1e-06
                        MAX_SCF  200
                    &END
                    &XC
                        &XC_FUNCTIONAL PBE
                        &END
                    &END
                &END
                &SUBSYS
                    &CELL
                        A  16.11886919 0.07814137 -0.697284243
                        B  -0.215317662 4.389405268 1.408951791
                        C  -0.216126961 1.732808365 9.748961085
                        PERIODIC  XYZ
                    &END
                    &KIND  C
                        BASIS_SET  DZVP-MOLOPT-SR-GTH-q4
                        POTENTIAL  GTH-PBE-q4
                    &END
                    &KIND  H
                        BASIS_SET  DZVP-MOLOPT-SR-GTH-q1
                        POTENTIAL  GTH-PBE-q1
                    &END
                    &TOPOLOGY
                        COORD_FILE_NAME  ./geometry.xyz
                        COORDINATE  XYZ
                    &END
                &END
            &END

            &GLOBAL
                PRINT_LEVEL  LOW
                PROJECT  example
                RUN_TYPE  ENERGY_FORCE
            &END
        """))
    return file


def read_input(filename: str | bytes | os.PathLike[Any]) -> dict[str, Any]:
    """Read a CP2K input file and convert it into a dictionary.

    Parameters
    ----------
    filename : :class:`str`, :class:`bytes` or :class:`os.PathLike`
        The path+filename of the CP2K input file.

    Returns
    -------
    :class:`dict[str, Any] <dict>`
        A (nested) dictionary constructed from **filename**.
        Duplicate keys are converted into a lists of dictionaries.

    """
    def _sanitize_line(item: str) -> str:
        """Sanitize and return a single line from **filename**."""
        return item.rstrip('\n').rstrip().replace('\t', '').lstrip(' ')

    with open(filename, 'r') as f:
        input_list = [_sanitize_line(item) for item in f if item != '\n']

    # Fill the to-be returned dictionary in a recursive manner.
    ret: dict[str, Any] = {}
    recursive_update(iter(input_list), ret)
    return ret
