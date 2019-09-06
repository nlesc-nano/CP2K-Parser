"""
cp2kparser.parser
=================

A module for converting CP2K_ input files into PLAMS_ compatible dictionaries.

The CP2K inputfile conversion is initiated by supplying the filename to :func:`.read_input`:

.. code:: python

    >>> import cp2kparser

    >>> filename = 'my_cp2k_input.inp'
    >>> cp2k_dict = cp2kparser.read_input(filename)

    >>> print(type(cp2k_dict))
    <class 'dict'>


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

from pathlib import PurePath
from typing import (Generator, Union, Tuple, Optional, MutableSequence, TypeVar)

__all__ = ['read_input']

T = TypeVar('T')


def value_to_float(item: T) -> Union[T, float]:
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
    :class:`float` or :class:`object`
        A float constructed from **value**.
        Returns the unmodified **value** if a :exc:`ValueError` is raised.

    """
    try:
        return float(item)
    except ValueError:
        return item


def value_to_int(item: T) -> Union[T, int]:
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
    :class:`int` or :class:`object`
        An integer constructed from **value**.
        Returns the unmodified **value** if a :exc:`ValueError` is raised.

    """
    try:
        return int(item)
    except ValueError:
        return item


def split_str(item: str,
              sep: Optional[str] = None) -> Tuple[str, str]:
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

    sep : :class:`str`
        The delimiter according which to split **item**.
        ``None`` (the default value) means split according to any whitespace,
        and discard empty strings from the result.

    Returns
    -------
    :class:`tuple` [:class:`str`, :class:`str`]
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


def parse_multi_keys(item: str,
                     sep: Optional[str] = None) -> str:
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

    sep : :class:`str`
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


def parse_header(input_gen: Generator[str, None, None],
                 item: str,
                 container: Union[dict, MutableSequence]) -> None:
    r"""Parse CP2K headers.

    Parameters
    ----------
    input_gen : :class:`collections.abc.Generator`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    item : :class:`str`
        A string containing the header key.

    container : :class:`dict` or :class:`collections.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

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


def parse_block(item: str,
                container: Union[dict, MutableSequence]) -> None:
    """Parse CP2K blocks.

    Parameters
    ----------
    item : :class:`str`
        A string containing a key and value.

    container : :class:`dict` or :class:`collections.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

    """
    key, value = split_str(item)
    if '.' in value:
        value = value_to_float(value)
    else:
        value = value_to_int(value)
    container[key] = value


def parse_coord_block(input_gen: Generator[str, None, None],
                      container: Union[dict, MutableSequence]) -> None:
    """Parse ``"coord"`` blocks.

    Parameters
    ----------
    item : :class:`str`
        A string containing a key and value.

    container : :class:`dict` or :class:`collections.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

    """
    item = next(input_gen)
    container['coord'] = {}
    container['coord']['_1'] = coord = []
    while item.lower() != '&end':
        coord.append(item)
        item = next(input_gen)
    return


def recursive_update(input_gen: Generator[str, None, None],
                     container: Union[dict, MutableSequence]) -> None:
    r"""Update **container** an a recursive manner.

    Parameters
    ----------
    input_gen : :class:`collections.abc.Generator`
        A generator looping over a sanitized CP2K input file.
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    container : :class:`dict` or :class:`collections.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

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


def read_input(filename: Union[str, bytes, PurePath]) -> dict:
    """Read a CP2K input file and convert it into a dictionary.

    Examples
    --------
    .. code:: python

        >>> import cp2kparser

        >>> filename = 'my_cp2k_input.inp'
        >>> print(open(filename).read())
        &FORCE_EVAL
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

        >>> cp2k_dict = cp2kparser.read_input(filename)
        >>> print(cp2k_dict)
        {'force_eval':
            {'dft':
                {'basis_set_file_name': '/path/to/basis',
                 'mgrid': {'cutoff': 400, 'ngrids': 4},
                 'poisson': {},
                 'localize T': {},
                 'potential_file_name': '/path/to/potential',
                 'qs': {'method': 'GPW'},
                 'scf': {'eps_scf': '1e-06', 'max_scf': 200},
                 'xc': {'xc_functional PBE': {}}},
            'subsys':
                {'cell':
                    {'a': '16.11886919 0.07814137 -0.697284243',
                     'b': '-0.215317662 4.389405268 1.408951791',
                     'c': '-0.216126961 1.732808365 9.748961085',
                     'periodic': 'XYZ'},
                 'kind C':
                     {'basis_set': 'DZVP-MOLOPT-SR-GTH-q4',
                      'potential': 'GTH-PBE-q4'},
                 'kind H':
                     {'basis_set': 'DZVP-MOLOPT-SR-GTH-q1',
                      'potential': 'GTH-PBE-q1'},
                 'topology':
                     {'coord_file_name': './geometry.xyz',
                      'coordinate': 'XYZ'}}},
        'global':
            {'print_level': 'LOW',
             'project': 'example',
             'run_type': 'ENERGY_FORCE'}}

    Parameters
    ----------
    filename : :class:`str`
        The path+filename of the CP2K input file.

    Returns
    -------
    :class:`dict`
        A (nested) dictionary constructed from **filename**.
        Duplicate keys are converted into a lists of dictionaries.

    """
    def _sanitize_line(item: str) -> str:
        """Sanitize and return a single line from **filename**."""
        return item.rstrip('\n').rstrip().replace('\t', '').lstrip(' ')

    with open(filename, 'r') as f:
        input_list = [_sanitize_line(item) for item in f if item != '\n']

    # Fill the to-be returned dictionary in a recursive manner.
    ret = {}
    input_gen = (i for i in input_list)
    recursive_update(input_gen, ret)

    return ret
