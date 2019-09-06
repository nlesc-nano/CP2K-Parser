#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit cp2kparser/__version__.py
version = {}
with open(os.path.join(here, 'cp2kparser', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='CP2K-Parser',
    version=version['__version__'],
    description=('A package for converting CP2K input files into PLAMS-compatible dictionaries.'),
    long_description=readme + '\n\n',
    long_description_content_type='text/x-rst',
    author='Bas van Beek',
    author_email='b.f.van.beek@vu.nl',
    url='https://github.com/nlesc-nano/CP2K-Parser',
    package_dir={'cp2kparser': 'cp2kparser'},
    packages=[
        'cp2kparser',
    ],
    include_package_data=True,
    license="GNU General Public License v3 or later (GPLv3+)",
    zip_safe=False,
    keywords=[
        'python-3',
        'python-3-5',
        'python-3-6',
        'python-3-7',
        'dictionary',
        'parsing',
        'cp2k',
        'plams'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    test_suite='tests',
    python_requires='>=3.5',
    install_requires=[],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle'
    ],
    extras_require={
        'test': ['pytest', 'pytest-cov', 'pycodestyle']
    }
)
