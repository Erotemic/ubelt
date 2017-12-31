[![Travis](https://img.shields.io/travis/Erotemic/ubelt/master.svg?label=Travis%20CI)](https://travis-ci.org/Erotemic/ubelt)
[![Codecov](https://codecov.io/github/Erotemic/ubelt/badge.svg?branch=master&service=github)](https://codecov.io/github/Erotemic/ubelt?branch=master)
[![Appveyor](https://ci.appveyor.com/api/projects/status/github/Erotemic/ubelt?svg=True)](https://ci.appveyor.com/project/Erotemic/ubelt/branch/master)
[![Pypi](https://img.shields.io/pypi/v/ubelt.svg)](https://pypi.python.org/pypi/ubelt)


## Purpose
UBelt is a "utility belt" of commonly needed utility and helper functions.
It is a migration of the most useful parts of `utool`
  (https://github.com/Erotemic/utool) into a minimal and standalone module.

The `utool` library contains a number of useful utility functions, however a
number of these are too specific or not well documented. The goal of this
migration is to slowly port over the most re-usable parts of `utool` into a
stable package.

In addition to utility functions `utool` also contains a custom doctest
  harness and code introspection and auto-generation features.
A rewrite of the test harness has been ported to a new module called:
[`xdoctest`](https://github.com/Erotemic/xdoctest).  A small subset of the
auto-generation and code introspection will be ported / made visible through
`ubelt`.


## Installation:

#### From github:
```
pip install git+https://github.com/Erotemic/ubelt.git
```

#### From pypi:
```
pip install ubelt
```

## Available Functions:
This list of functions and classes is currently available. 
See the corresponding doc-strings for more details.

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
ub.chunks
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
ub.Cacher
ub.cmd
ub.editfile
ub.startfile
ub.delete
ub.repr2
ub.hzcat
ub.argval
ub.argflag
ub.import_module_from_path
ub.import_module_from_name
ub.download
ub.AutoDict
```

A minimal version of the doctest harness has been completed.
This can be accessed using `ub.doctest_package`.

## Examples

Here are some examples of some features inside `ubelt`


### Caching
Cache intermediate results in a script with minimal boilerplate.
```python
>>> import ubelt as ub
>>> cfgstr = 'repr-of-params-that-uniquely-determine-the-process'
>>> cacher = ub.Cacher('test_process', cfgstr)
>>> data = cacher.tryload()
>>> if data is None:
>>>     myvar1 = 'result of expensive process'
>>>     myvar2 = 'another result'
>>>     data = myvar1, myvar2
>>>     cacher.save(data)
>>> myvar1, myvar2 = data
```


### Timing
Quickly time a single line.
```python
>>> import ubelt as ub
>>> timer = ub.Timer('Timer demo!', verbose=1)
>>> with timer:
>>>     prime = ub.find_nth_prime(40)
tic('Timer demo!')
...toc('Timer demo!')=0.0008s
```


### Robust Timing
Easily do robust timings on existing blocks of code by simply indenting them.
There is no need to refactor into a string representation or convert to a
single line.  With `ub.Timerit` there is no need to resort to the `timeit`
module!

The quick and dirty way just requires one indent.
```python
>>> import ubelt as ub
>>> for _ in ub.Timerit(num=200, verbose=2):
>>>     ub.find_nth_prime(100)
Timing for 200 loops
Timing complete, 200 loops
    time per loop : 0.003288508653640747 seconds
```


Use the loop variable as a context manager for more accurate timings or to
incorporate an setup phase that is not timed.  You can also access properties
of the `ub.Timerit` class to programmatically use results.
```python
>>> import ubelt as ub
>>> t1 = ub.Timerit(num=200, verbose=2)
>>> for timer in t1:
>>>     setup_vars = 100
>>>     with timer:
>>>         ub.find_nth_prime(setup_vars)
>>> print('t1.total_time = %r' % (t1.total_time,))
Timing for 200 loops
Timing complete, 200 loops
    time per loop : 0.003165217638015747 seconds
t1.total_time = 0.6330435276031494
```


### Grouping

Group items in a sequence into a dictionary by a second id list
```python
>>> import ubelt as ub
>>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
>>> groupid_list = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
>>> result = ub.group_items(item_list, groupid_list)
>>> print(result)
{'dairy': ['cheese'], 'fruit': ['jam', 'bannana'], 'protein': ['ham', 'spam', 'eggs']}
```


### Dictionary Histogram

Find the frequency of items in a sequence
```python
>>> import ubelt as ub
>>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
>>> hist = ub.dict_hist(item_list)
>>> print(hist)
{1232: 2, 1: 1, 2: 4, 900: 3, 39: 1}
```


### Dictionary Manipulation


Take a subset of a dictionary.
```python
>>> import ubelt as ub
>>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
>>> subdict_ = ub.dict_subset(dict_, ['K', 'dcvs_clip_max'])
>>> print(subdict_)
{'K': 3, 'dcvs_clip_max': 0.2}
```


Take only the values, optionally specify a default value.
```python
>>> import ubelt as ub
>>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
>>> print(list(ub.dict_take(dict_, [1, 2, 3, 4, 5], default=None)))
['a', 'b', 'c', None, None]
```


Apply a function to each value in the dictionary (see also `ub.map_keys`).
```python
>>> import ubelt as ub
>>> dict_ = {'a': [1, 2, 3], 'b': []}
>>> newdict = ub.map_vals(len, dict_)
>>> print(newdict)
{'a': 3, 'b': 0}
```


### Loop Progress
See also [`tqdm`](https://pypi.python.org/pypi/tqdm) for an alternative
implementation.
```python
>>> import ubelt as ub
>>> def is_prime(n):
...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
>>> for n in ub.ProgIter(range(1000), verbose=2):
>>>     # do some work
>>>     is_prime(n)
    0/1000... rate=0.00 Hz, eta=?, total=0:00:00, wall=14:05 EST 
    1/1000... rate=82241.25 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST 
  257/1000... rate=177204.69 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST 
  642/1000... rate=94099.22 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST 
 1000/1000... rate=71886.74 Hz, eta=0:00:00, total=0:00:00, wall=14:05 EST 
```


### Horizontal String Concatenation

```python
>>> import ubelt as ub
>>> B = ub.repr2([[1, 2], [3, 4]], nl=1, cbr=True, trailsep=False)
>>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
>>> print(ub.hzcat(['A = ', B, ' * ', C]))
A = [[1, 2], * [[5, 6],
     [3, 4]]    [7, 8]]
```

### Command Line interaction with captured and real-time output 

```python
>>> info = cmd(('echo', 'simple cmdline interface'), verbose=1)
simple cmdline interface
>>> assert info['ret'] == 0
>>> assert info['out'].strip() == 'simple cmdline interface'
>>> assert info['err'].strip() == ''
```
