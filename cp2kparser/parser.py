"""A module for converted CP2K input files into dictionaries."""

from typing import Generator, Union, Tuple

__all__ = ['read_input']


def value_to_float(value: str) -> Union[float, str]:
    """Try to convert a string into a float.

    Parameters
    ----------
    value : :class:`str`
        A string.

    Returns
    -------
    :class:`float` or :class:`str`
        A float constructed from **value**.
        Returns **value** as string if a :exc:`ValueError` is raised.

    """
    try:
        return float(value)
    except ValueError:
        return value


def value_to_int(value: str) -> Union[int, str]:
    """Try to convert a string into an integer.

    Parameters
    ----------
    value : :class:`str`
        A string.

    Returns
    -------
    :class:`int` or :class:`str`
        An integer constructed from **value**.
        Returns **value** as string if a :exc:`ValueError` is raised.

    """
    try:
        return int(value)
    except ValueError:
        return value


def split_item(item: str) -> Tuple[str, str]:
    """Split a string into a key and a value.

    The first word in the to-be returned key is decapitalized if it contains any spaces.

    Parameters
    ----------
    item : :class:`str`
        A string.

    Returns
    -------
    :class:`tuple` [class`str`, class`str`]
        A tuple of two string created by splitting **item**.
        The first word of the first string is decapitalized.

    """
    try:
        key, value = item.split(maxsplit=1)
    except ValueError:
        key = item
        value = ''

    if ' ' in key:
        key = parse_multi_keys(key)
    else:
        key = key.lower()

    return key, value


def parse_multi_keys(item: str) -> str:
    """Parse keys that contain one or more spaces.

    The first word in the to-be returned key is decapitalized.

    Parameters
    ----------
    item : :class:`str`
        A string containing at least a single space.

    Returns
    -------
    :class:`str`
        **item*8 with its first word decapitalized.

    Raises
    ------
    ValueError
        Raised if **item** does not contain any whitespaces.

    """
    i1, i2 = item.split(maxsplit=1)
    i1 = i1.lstrip('&').lower()
    return '{} {}'.format(i1, i2)


def parse_header(input_gen: Generator,
                 item: str,
                 dict_: dict) -> None:
    """Parse CP2K headers.

    Parameters
    ----------
    input_gen : :class:`abc.Generator`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    item : :class:`str`
        A string containing a key and value.

    dict : :class:`dict`
        A to-be filled dictionary.

    """
    if ' ' in item:
        key = parse_multi_keys(item)
    else:
        key = item.lstrip('&').lower()

    # dict_[key] is a list; append the list
    if key in dict_ and isinstance(dict_[key], list):
        dict_[key].append({})
        recurse_update(input_gen, dict_[key][-1])

    # A duplicate key; convert dict_[key] into a list of dictionaries
    elif key in dict_:
        value_old = dict_[key]
        dict_[key] = [value_old, {}]
        recurse_update(input_gen, dict_[key][-1])

    # Create a new nested dctionary
    else:
        dict_[key] = {}
        recurse_update(input_gen, dict_[key])


def parse_block(item: str,
                dict_: dict) -> None:
    """Parse CP2K blocks.

    Parameters
    ----------
    item : :class:`str`
        A string containing a key and value.

    dict : :class:`dict`
        A to-be filled dictionary.

    """
    key, value = split_item(item)
    if '.' in value:
        value = value_to_float(value)
    else:
        value = value_to_int(value)
    dict_[key] = value


def recurse_update(input_gen: Generator,
                   dict_: dict) -> None:
    """Update **dict_** an a recursive manner.

    Parameters
    ----------
    input_gen : :class:`abc.Generator`
        A generator looping over a sanitized CP2K input file
        Tabs (``"\t"``), new lines  (``"\n"``) and trailing whitespaces are expected to be removed.

    dict : :class:`dict`
        A to-be filled dictionary.

    """
    for item in input_gen:
        if item[0] == '&' and item[0:4] != '&END':
            parse_header(input_gen, item, dict_)
        elif item[0:4] != '&END':
            parse_block(item, dict_)
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
    recurse_update(input_gen, ret)

    return ret
