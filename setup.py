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

tests_require = [
    'pytest',
    'pytest-cov',
]

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
    package_data={'cp2kparser': ['py.typed']},
    packages=['cp2kparser'],
    include_package_data=True,
    license='Apache Software License',
    zip_safe=False,
    keywords=[
        'python-3',
        'python-3-7',
        'python-3-8',
        'python-3-9',
        'python-3-10',
        'dictionary',
        'parsing',
        'cp2k',
        'plams',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Typing :: Typed',
    ],
    test_suite='tests',
    python_requires='>=3.7',
    install_requires=[],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    }
)
