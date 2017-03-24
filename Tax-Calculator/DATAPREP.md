[![Travis-CI Build Status](https://travis-ci.org/open-source-economics/Tax-Calculator.svg?branch=master)](https://travis-ci.org/open-source-economics/Tax-Calculator)
[![Codecov Status](https://codecov.io/github/open-source-economics/Tax-Calculator/coverage.svg?precision=2)](https://codecov.io/github/open-source-economics/Tax-Calculator)

Tax-Calculator Data-Preparation Guidelines
==========================================

The Tax-Calculator is flexible enough to read almost any kind of
CSV-formatted input data on filing units as long as the variable names
correspond to those expected by Tax-Calculator.  The only required
input variables are `RECID` (a unique filing-unit record identifier)
and `MARS` (a positive-valued filing-status indicator as defined in
the IRS-SOI Public Use File).  Other variables in the input file must
have variable names that are in the `USABLE_READ_VARS` set in the
[records.py
file](https://github.com/open-source-economics/Tax-Calculator/blob/master/taxcalc/records.py) in order for them to affect tax calculations.
These other variable names are usually the same as those in the
IRS-SOI Public Use File.  Variables in the input file that are
not in the `USABLE_READ_VARS` set are ignored by Tax-Calculator.

Any variable in the `USABLE_READ_VARS` set that is not in an input file
is automatically set to a value of zero for every filing unit.

However, there are important data-preparation issues related to the
fact that the payroll tax is a tax on individuals, not on income-tax
filing units.  Tax-Calculator expects that the filing-unit total for
each of several earnings-related variables is split between the
taxpayer and the spouse.  It is the responsibility of anyone preparing
data for Tax-Calculator input to do this earnings splitting.  Here are
the relationships between the filing-unit variable and the taxpayer
(`p`) and spouse (`s`) variables expected by Tax-Calculator:
```
e00200 = e00200p + e00200s

e00900 = e00900p + e00900s

e02100 = e02100p + e02100s
```
Obviously, when `MARS` is not equal to 2 (married filing jointly), the
values of the three `s` variables are zero and the values of the three
`p` variables are equal to the value of their corresponding
filing-unit variable.  And obviously, the data file can omit any one,
or all, of these three sets variables.  If the variables in one of these
three sets are omitted, the required relationship will be satisfied
because zero equals zero plus zero.

But when including one of these three sets of variables, it is up to you
to specify the taxpayer-spouse split.  You will get an error message
from Tax-Calculator, and it will stop running, if you do not split the
filing-unit amount between taxpayer and spouse so that the above equations
hold for each filing unit in the input file.

In addition to this earning-splitting data-preparation issue,
Tax-Calculator expects that the value of ordinary dividends (e00600)
will be no less than the value of qualified dividends (e00650) for
each filing unit.  Again, it is the responsibility of anyone preparing
data for Tax-Calculator input to ensure that this relationship is
true.
