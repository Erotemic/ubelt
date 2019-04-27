# Contributing to UBelt

This is a first pass at documentation describing how you can contribute to the UBelt project. 

If you find an issue, bug, or have a proposal for new behavior please submit an issue to the github issue tracker: https://github.com/Erotemic/ubelt/issues

If you have a fix for an issue, or would like to submit a design for a new feature submit a pull-request https://github.com/Erotemic/ubelt/pulls

## Codebase structure

The ubelt package is structured as a flat list of `util_*.py` submodules. 
All top-level APIs are exposed in the `__init__.py` file. 
Currently there are no subpackage-directories, and I think its best that ubelt remains this way for simplicity. 


## Unit testing

Ubelt is tested with a combination of unit-tests and doctests. 
All tests can be run via `pytest` or using the `./run_tests.py` script. 
The doctests can be run using `./run_doctests.sh`

Some tests (like the ones that use the internet) are not enabled by default. These can be 
enabled by passing the `--network` flag to the above scripts. 


## Documentation

All documenation should be written in module-level, class-level, and function-level docstrings. 
Docstrings should follow [Google-style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). 

## Code Style

Code should follow PEP8 standards when possible. Any violations of PEP8 should be justified and have a `  # NOQA` tag to indicate that the linter should ignore an offending line.  
By default I'm using `flake8` to lint code and I disable these error messages by default:

```python
    'E126',  # continuation line hanging-indent
    'E127',  # continuation line over-indented for visual indent
    'E201',  # whitespace after '('
    'E202',  # whitespace before ']'
    'E203',  # whitespace before ', '
    'E221',  # multiple spaces before operator  
    'E222',  # multiple spaces after operator
    'E241',  # multiple spaces after ,
    'E265',  # block comment should start with "# "
    'E271',  # multiple spaces after keyword
    'E272',  # multiple spaces before keyword
    'E301',  # expected 1 blank line, found 0
    'E305',  # expected 1 blank line after class / func
    'E306',  # expected 1 blank line before func
    'E501',  # line length > 79
    'W602',  # Old reraise syntax
    'E266',  # too many leading '#' for block comment
    'N801',  # function name should be lowercase [N806]
    'N802',  # function name should be lowercase [N806]
    'N803',  # argument should be lowercase [N806]
    'N805',  # first argument of a method should be named 'self'
    'N806',  # variable in function should be lowercase [N806]
    'N811',  # constant name imported as non constant
    'N813',  # camel case
```
