"""A module for testing pep8 compliance."""

import os
import textwrap
from typing import List

import pycodestyle  # formerly known as pep8

__all__: List[str] = []


def test_pep8_conformance() -> None:
    """Test that we conform to PEP-8."""
    check_paths = [
        'cp2kparser',
        'tests',
    ]
    exclude_paths = []

    print("PEP8 check of directories: {}\n".format(', '.join(check_paths)))

    # Get paths wrt package root
    package_root = os.path.dirname(os.path.dirname(__file__))
    for paths in (check_paths, exclude_paths):
        for i, path in enumerate(paths):
            paths[i] = os.path.join(package_root, path)

    style = pycodestyle.StyleGuide(max_line_length=100)
    style.options.exclude.extend(exclude_paths)

    success = style.check_files(check_paths).total_errors == 0

    if not success:
        print(textwrap.dedent("""
            Your Python code does not conform to the official Python style
            guide (PEP8), see https://www.python.org/dev/peps/pep-0008

            A list of warning and error messages can be found above,
            prefixed with filename:line number:column number.

            Run `yapf -i yourfile.py` to automatically fix most errors.
            Run `yapf -d yourfile.py` to preview what would be changed.
            Run `pip install --upgrade yapf` to install the latest version
            of yapf.
        """))

    assert success, "Your code does not conform to PEP8"
