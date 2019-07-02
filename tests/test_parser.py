"""A module for :mod:`.parser`."""

import os
import textwrap
from typing import List

import pycodestyle  # formerly known as pep8

from cp2kparser.parser import (
    value_to_float, value_to_int, split_item, parse_multi_keys, read_input
)

__all__: List[str] = []

FILENAME: str = './cp2k_job_opt.in'


def test_value_to_float():
    """Test :func:`.parser.value_to_float`."""
    assert 1.5 == value_to_float('1.5')
    assert 2.0 == value_to_float('2')
    assert 2.0 == value_to_float(2)
    assert 2.0 == value_to_float(2.0)
    assert 'test' == value_to_float('test')


def test_value_to_int():
    """Test :func:`.parser.value_to_int`."""
    assert '1.5' == value_to_int('1.5')
    assert 2 == value_to_int('2')
    assert 2 == value_to_int(2)
    assert '2.0' == value_to_int(2.0)
    assert 'test' == value_to_int('test')


def test_split_item():
    """Test :func:`.parser.split_item`."""
    assert ('a', '') == split_item('A')
    assert ('a', 'B') == split_item('A B')
    assert ('a B', 'C') == split_item('A B C')


def test_parse_multi_keys():
    """Test :func:`.parser.parse_multi_keys`."""
    assert ('a', 'B') == split_item('A B')
    try:
        split_item('A')
    except ValueError:
        pass
    else:
        raise AssertionError

def test_read_input():
    """Test :func:`.parser.read_input`."""
    out = read_input(FILENAME)
    ref = {'global': {'project': 'cd68se55_26hcoo', 'run_type': 'geo_opt', 'print_level': 'MEDIUM'}, 'force_eval': {'method': 'FIST', 'mm': {'print': {'ff_info': {}}, 'forcefield': {'ignore_missing_critical_params': '', 'parm_file_name': './nc_ff.pot', 'parmtype': 'CHM', 'do_nonbonded': '', 'shift_cutoff': '.TRUE.', 'nonbonded': {'lennard-jones': [{'atoms': 'CD CD', 'epsilon': 37.29669, 'sigma': 1.234, 'rcut': 11.4}, {'atoms': 'SE SE', 'epsilon': 51.30851, 'sigma': 4.852, 'rcut': 11.4}, {'atoms': 'CD SE', 'epsilon': 183.1158, 'sigma': 2.94, 'rcut': 11.4}, {'atoms': 'CD O_2', 'epsilon': 220.5809, 'sigma': 2.471, 'rcut': 11.4}, {'atoms': 'Se O_2', 'epsilon': 194.0607, 'sigma': 3.526, 'rcut': 11.4}]}}, 'poisson': {'ewald': {'ewald_type': 'spme', 'alpha': 0.44, 'gmax': 24}}}, 'subsys': {'cell': {'abc': '[angstrom] 45.0 45.0 45.0', 'periodic': 'NONE'}, 'topology': {'charge_beta': '', 'coord_file_format': 'PDB', 'coord_file_name': 'cd68se55_26hcoo.xyz.pdb', 'connectivity': 'MOL_SET', 'mol_set': {'molecule': [{'nmol': 1, 'conn_file_name': 'cd_new.xyz.psf'}, {'nmol': 1, 'conn_file_name': 'se_new.xyz.psf'}, {'nmol': 26, 'conn_file_name': 'formate.xyz.psf'}]}, 'dump_pdb': {}, 'dump_psf': {}, 'center_coordinates': {}}, 'print': {'topology_info': {'psf_info': ''}}, 'kind Cd': {'element': 'Cd'}, 'kind Se': {'element': 'Se'}, 'kind C_2': {'element': 'C'}, 'kind O_2': {'element': 'O'}, 'kind H_': {'element': 'H'}}}, 'motion': {'md': {'thermostat': {'type': 'CSVR', 'csvr': {'timecon': 250}}, 'ensemble': 'NVT', 'steps': 2000, 'timestep': 1.0, 'temperature': 300.0}}}  # noqa
    assert ref == out
