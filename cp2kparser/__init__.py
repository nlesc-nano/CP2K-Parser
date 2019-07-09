"""
CP2K-Parser 1.0.0
#################

A package for converting CP2K_ input files into PLAMS_ compatible dictionaries.

Installation
************

CP2K-Parser can be installed as following:

*  PyPi: ``pip install CP2K-parser --upgrade``

Usage
*****

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
             'kind C': {'basis_set': 'DZVP-MOLOPT-SR-GTH-q4', 'potential': 'GTH-PBE-q4'},
             'kind H': {'basis_set': 'DZVP-MOLOPT-SR-GTH-q1', 'potential': 'GTH-PBE-q1'},
             'topology': {'coord_file_name': './geometry.xyz', 'coordinate': 'XYZ'}}},
    'global': {'print_level': 'LOW', 'project': 'example', 'run_type': 'ENERGY_FORCE'}}

.. _CP2K: https://www.cp2k.org/
.. _PLAMS: https://www.scm.com/doc/plams/index.html

"""

from .__version__ import __version__

from .parser import read_input

__version__ = __version__
__author__ = "B. F. van Beek"
__email__ = 'b.f.van.beek@vu.nl'

__all__ = ['read_input']
