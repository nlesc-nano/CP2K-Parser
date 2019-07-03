"""A module for converted CP2K input files into dictionaries."""

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
    :class:`float` or :class:`str`
        A float constructed from **value**.
        Returns **value** as string if a :exc:`ValueError` is raised.

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
    :class:`int` or :class:`str`
        An integer constructed from **value**.
        Returns **value** as string if a :exc:`ValueError` is raised.

    """
    try:
        return int(item)
    except ValueError:
        return item


def split_item(item: str,
               sep: Optional[str] = None) -> Tuple[str, str]:
    """Split a string into a key and a value.

    The first word in the to-be returned key is decapitalized if it contains any spaces.

    Examples
    --------
    .. code:: python

        >>> out1 = split_item('A')
        >>> out2 = split_item('A B')
        >>> out3 = split_item('A B C')
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
        The first word of the first string is decapitalized.

    """
    sep = sep or ' '
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
    sep = sep or ' '
    i1, i2 = item.split(sep, maxsplit=1)
    i1 = i1.lstrip('&').lower()
    return ''.join((i1, sep, i2))


def parse_header(input_gen: Generator,
                 item: str,
                 container: Union[dict, MutableSequence]) -> None:
    """Parse CP2K headers.

    Parameters
    ----------
    input_gen : :class:`.abc.Generator`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    item : :class:`str`
        A string containing a key and value.

    container : :class:`dict` or :class:`.abc.MutableSequence`
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

    # A duplicate key; convert container[key] into a list of dictionaries
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

    container : :class:`dict` or :class:`.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

    """
    key, value = split_item(item)
    if '.' in value:
        value = value_to_float(value)
    else:
        value = value_to_int(value)
    container[key] = value


def recursive_update(input_gen: Generator,
                     container: Union[dict, MutableSequence]) -> None:
    """Update **container** an a recursive manner.

    Parameters
    ----------
    input_gen : :class:`.abc.Generator`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    container : :class:`dict` or :class:`.abc.MutableSequence`
        A to-be filled dictionary or mutable sequence.

    """
    for item in input_gen:
        if item[0] == '&' and item[0:4].lower() != '&end':  # Beginning of a block
            parse_header(input_gen, item, container)
        elif item[0:4].lower() != '&end':  # End of a block
            parse_block(item, container)
        else:
            return


def read_input(filename: str) -> dict:
    """Read a CP2K input file and convert it into a dictionary.

    Parameters
    ----------
    filename : :class:`str`
        The path+filename of the CP2K input file.

    Returns
    -------
    :class:`dict`
        A dictionary constructed from **filename**.
        Duplicate keys are converted into a list of dictionaries.

    """
    with open(filename, 'r') as f:
        input_list = []
        for i in f:
            if i == '\n':
                continue
            input_list.append(i.rstrip('\n').replace('\t', '').lstrip(' '))

    # Fill the to-be returned dictionary in a recursive manner.
    ret = {}
    input_gen = (i for i in input_list)
    recursive_update(input_gen, ret)

    return ret
