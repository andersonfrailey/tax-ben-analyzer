import os
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
from io import StringIO
from taxcalc import Growfactors, Policy, Records, Calculator


def test_incorrect_Records_instantiation(puf_1991):
    with pytest.raises(ValueError):
        recs = Records(data=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, gfactors=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, gfactors=None, weights=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, gfactors=None, weights=None,
                       start_year=list())
    with pytest.raises(ValueError):
        recs = Records(data=puf_1991, gfactors=None, weights=None,
                       adjust_ratios=list())


def test_correct_Records_instantiation(puf_1991, puf_1991_path, weights_1991):
    rec1 = Records(data=puf_1991_path, gfactors=None, weights=weights_1991)
    assert rec1
    assert np.all(rec1.MARS != 0)
    assert rec1.current_year == Records.PUF_YEAR
    sum_e00200_in_puf_year = rec1.e00200.sum()
    rec1.set_current_year(Records.PUF_YEAR + 1)
    sum_e00200_in_puf_year_plus_one = rec1.e00200.sum()
    assert sum_e00200_in_puf_year_plus_one == sum_e00200_in_puf_year
    assert rec1.positive_weights()
    rec2 = Records(data=puf_1991, gfactors=Growfactors(), weights=None)
    assert rec2
    assert np.all(rec2.MARS != 0)
    assert rec2.current_year == Records.PUF_YEAR
    assert not rec2.positive_weights()
    adj_df = pd.read_csv(Records.ADJUST_RATIOS_PATH)
    adj_df = adj_df.transpose()
    rec3 = Records(data=puf_1991, weights=None, adjust_ratios=adj_df)
    assert rec3
    assert np.all(rec3.MARS != 0)
    assert rec3.current_year == Records.PUF_YEAR
    assert not rec3.positive_weights()


def test_correct_Records_instantiation_sample(puf_1991, weights_1991):
    sample = puf_1991.sample(frac=0.10)
    # instantiate Records object with no extrapolation
    rec1 = Records(data=sample, gfactors=None, weights=weights_1991)
    assert rec1
    assert np.all(rec1.MARS != 0)
    assert rec1.current_year == Records.PUF_YEAR
    sum_e00200_in_puf_year = rec1.e00200.sum()
    rec1.set_current_year(Records.PUF_YEAR + 1)
    sum_e00200_in_puf_year_plus_one = rec1.e00200.sum()
    assert sum_e00200_in_puf_year_plus_one == sum_e00200_in_puf_year
    # instantiate Records object with default extrapolation
    rec2 = Records(data=sample, gfactors=Growfactors(), weights=None)
    assert rec2
    assert np.all(rec2.MARS != 0)
    assert rec2.current_year == Records.PUF_YEAR


@pytest.mark.parametrize("csv", [
    (
        u'RECID,MARS,e00200,e00200p,e00200s\n'
        u'1,    2,   200000, 200000,   0.02\n'
    ),
    (
        u'RECID,MARS,e00900,e00900p,e00900s\n'
        u'1,    2,   200000, 200000,   0.02\n'
    ),
    (
        u'RECID,MARS,e02100,e02100p,e02100s\n'
        u'1,    2,   200000, 200000,   0.02\n'
    ),
    (
        u'RxCID,MARS\n'
        u'1,    2\n'
    ),
    (
        u'RECID,e00300\n'
        u'1,    456789\n'
    ),
    (
        u'RECID,MARS,e00600,e00650\n'
        u'1,    1,        8,     9\n'
    )
])
def test_read_data(csv):
    df = pd.read_csv(StringIO(csv))
    with pytest.raises(ValueError):
        Records(data=df)


def test_extrapolation_timing(puf_1991, weights_1991):
    pol1 = Policy()
    assert pol1.current_year == Policy.JSON_START_YEAR
    rec1 = Records(data=puf_1991, weights=weights_1991)
    assert rec1.current_year == Records.PUF_YEAR
    calc1 = Calculator(policy=pol1, records=rec1, sync_years=True)
    assert calc1.records.current_year == Policy.JSON_START_YEAR
    pol2 = Policy()
    assert pol2.current_year == Policy.JSON_START_YEAR
    rec2 = Records(data=puf_1991, weights=weights_1991)
    assert rec2.current_year == Records.PUF_YEAR
    rec2.set_current_year(Policy.JSON_START_YEAR)
    assert rec2.current_year == Policy.JSON_START_YEAR
    calc2 = Calculator(policy=pol2, records=rec2, sync_years=False)
    assert calc2.policy.current_year == Policy.JSON_START_YEAR
    assert calc2.records.current_year == Policy.JSON_START_YEAR


def test_for_duplicate_names():
    varnames = set()
    for varname in Records.USABLE_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.CALCULATED_VARS
    varnames = set()
    for varname in Records.CALCULATED_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.USABLE_READ_VARS
    varnames = set()
    for varname in Records.INTEGER_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname in Records.USABLE_READ_VARS


def test_csv_input_vars_md_contents(tests_path):
    """
    Check CSV_INPUT_VARS.md contents against Records.USABLE_READ_VARS
    """
    # read variable names in CSV_INPUT_VARS.md file (checking for duplicates)
    civ_path = os.path.join(tests_path, '..', 'validation',
                            'CSV_INPUT_VARS.md')
    civ_set = set()
    with open(civ_path, 'r') as civfile:
        msg = 'DUPLICATE VARIABLE(S) IN CSV_INPUT_VARS.MD FILE:\n'
        found_duplicates = False
        for line in civfile:
            str_list = line.split('|', 2)
            if len(str_list) != 3:
                continue  # because line is not part of the markdown table
            assert str_list[0] == ''  # because line starts with | character
            var = (str_list[1]).strip()  # remove surrounding whitespace
            if var == 'Var-name' or var[0] == ':':
                continue  # skip two lines that are the table head
            if var in civ_set:
                found_duplicates = True
                msg += 'VARIABLE= {}\n'.format(var)
            else:
                civ_set.add(var)
        if found_duplicates:
            raise ValueError(msg)
    # check that civ_set is a subset of Records.USABLE_READ_VARS set
    if not civ_set.issubset(Records.USABLE_READ_VARS):
        valid_less_civ = Records.USABLE_READ_VARS - civ_set
        msg = 'VARIABLE(S) IN USABLE_READ_VARS BUT NOT CSV_INPUT_VARS.MD:\n'
        for var in valid_less_civ:
            msg += 'VARIABLE= {}\n'.format(var)
        raise ValueError(msg)
