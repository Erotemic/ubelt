[![Travis](https://img.shields.io/travis/Erotemic/ubelt.svg)](https://travis-ci.org/Erotemic/ubelt)
[![Pypi](https://img.shields.io/pypi/v/ubelt.svg)](https://pypi.python.org/pypi/ubelt)
[![Codecov](https://codecov.io/github/Erotemic/ubelt/badge.svg?branch=master&service=github)](https://codecov.io/github/Erotemic/ubelt?branch=master)


## What is UBelt?
UBelt is a "utility belt" of commonly needed utility and helper functions.
It is a migration of the most useful parts of `utool`
  (https://github.com/Erotemic/utool) into a minimal and standalone module.

The `utool` library contains a number of useful utility functions, however a
number of these are too specific or not well documented. The goal of this
migration is to slowly port over the most re-usable parts of `utool` into a
stable package.

In addition to utility functions `utool` also contains a custom doctest
  harness and code introspection and auto-generation features.
This port will contain a rewrite of the doctest harness.
Some of the code introspection features will be ported, but most
  auto-generation abilities will be ported into a new module that depends on
  `ubelt`.

## Available Functions:
This list of functions and classes is currently available

```
import ubelt as ub

ub.dict_hist
ub.dict_subset
ub.dict_take
ub.find_duplicates
ub.group_items
ub.map_keys
ub.map_vals
ub.readfrom
ub.writeto
ub.ensuredir
ub.ensure_app_resource_dir
ub.compress
ub.take
ub.flatten
ub.memoize
ub.NiceRepr
ub.NoParam
ub.CaptureStdout
ub.Timer
ub.Timerit
ub.ProgIter
```

A minimal version of the doctest harness has been completed.
This can be accessed using `ub.doctest_package`.

## Installation:
```
pip install git+https://github.com/Erotemic/ubelt.git
```
