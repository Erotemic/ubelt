[![Travis](https://img.shields.io/travis/Erotemic/ubelt/master.svg?label=Travis%20CI)](https://travis-ci.org/Erotemic/ubelt)
[![Codecov](https://codecov.io/github/Erotemic/ubelt/badge.svg?branch=master&service=github)](https://codecov.io/github/Erotemic/ubelt?branch=master)
[![Appveyor](https://ci.appveyor.com/api/projects/status/github/Erotemic/ubelt?svg=True)](https://ci.appveyor.com/project/Erotemic/ubelt/branch/master)
[![Pypi](https://img.shields.io/pypi/v/ubelt.svg)](https://pypi.python.org/pypi/ubelt)


Good utilities lift all codes.  


## Purpose
UBelt is a "utility belt" of commonly needed utility and helper functions.
It is a migration of the most useful parts of `utool`
  (https://github.com/Erotemic/utool) into a minimal and standalone module.

The `utool` library contains a number of useful utility functions, however a
number of these are too specific or not well documented. The goal of this
migration is to slowly port over the most re-usable parts of `utool` into a
stable package.

The doctest harness in `utool` was ported and rewritten in a new module called:
[`xdoctest`](https://github.com/Erotemic/xdoctest), which integrates with
`pytest` as a plugin. All of the doctests in `ubelt` are run using `xdoctest`.

A small subset of the static-analysis and code introspection tools in
`xdoctest` are made visible through `ubelt`.

In addition to utility functions `utool` also contains a feature for
auto-generating `__init__.py` files. See `ubelt/__init__.py` for an example.

UBelt is cross platform and all top-level functions behave similarly on
Windows, Mac, and Linux (up to some small unavoidable differences).
Every function in `ubelt` is written with a doctest, which provides helpful
documentation and example usage as well as helping achieve 100% test coverage.

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
For the following functions, see corresponding doc-strings for more details.

Some of the more interesting and useful functions and classes implemented are:

```python
import ubelt as ub

ub.ensuredir
ub.Timerit  # powerful multiline alternative to timeit
ub.Cacher  # configuration based on-disk cachine
ub.cmd  # combines the best of subprocess.Popen and os.system
ub.hash_data  # extremely useful with Cacher to config strings
ub.repr2
ub.download 
ub.AutoDict
ub.modname_to_modpath  # (works via static analysis)
ub.modpath_to_modname  # (works via static analysis)
ub.import_module_from_path  # (Unlike importlib, this does not break pytest)
ub.import_module_from_name  # (Unlike importlib, this does not break pytest)
```


A complete list of available functions can be seen in the auto-generated `ubelt/__init__.py` file:

```python
from ubelt.util_arg import (argflag, argval,)
from ubelt.util_cache import (Cacher,)
from ubelt.util_colors import (color_text, highlight_code,)
from ubelt.util_const import (NoParam,)
from ubelt.util_cmd import (cmd,)
from ubelt.util_decor import (memoize,)
from ubelt.util_dict import (AutoDict, AutoOrderedDict, ddict, dict_hist,
                             dict_subset, dict_take, dict_union,
                             find_duplicates, group_items, invert_dict,
                             map_keys, map_vals, odict,)
from ubelt.util_download import (download, grabdata,)
from ubelt.util_func import (identity,)
from ubelt.util_format import (repr2,)
from ubelt.util_io import (delete, readfrom, touch, writeto,)
from ubelt.util_links import (symlink,)
from ubelt.util_list import (argsort, boolmask, chunks, compress, flatten,
                             iter_window, iterable, take, unique,
from ubelt.util_hash import (hash_data, hash_file,)
from ubelt.util_import import (import_module_from_name,
                               import_module_from_path, modname_to_modpath,
                               modpath_to_modname, split_modpath,)
from ubelt.util_mixins import (NiceRepr,)
from ubelt.util_path import (TempDir, augpath, compressuser, ensuredir,
                             truepath, userhome,)
from ubelt.util_platform import (DARWIN, LINUX, POSIX, PY2, PY3, WIN32,
                                 editfile, ensure_app_cache_dir,
                                 ensure_app_resource_dir, get_app_cache_dir,
                                 get_app_resource_dir, platform_cache_dir,
                                 platform_resource_dir, startfile,)
from ubelt.util_str import (CaptureStdout, codeblock, ensure_unicode, hzcat,
                            indent,)
from ubelt.util_time import (Timer, Timerit, timestamp,)
from ubelt.orderedset import (OrderedSet, oset,)
from ubelt.progiter import (ProgIter,)
```

## Examples

Here are some examples of some features inside `ubelt`


### Timing
Quickly time a single line.
```python
>>> import math
>>> import ubelt as ub
>>> timer = ub.Timer('Timer demo!', verbose=1)
>>> with timer:
>>>     math.factorial(100000)
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
>>> import math
>>> import ubelt as ub
>>> for _ in ub.Timerit(num=200, verbose=2):
>>>     math.factorial(10000)
Timing for 200 loops
Timed for: 200 loops, best of 3
    time per loop: best=2.055 ms, mean=2.145 ± 0.083 ms
```


Use the loop variable as a context manager for more accurate timings or to
incorporate an setup phase that is not timed.  You can also access properties
of the `ub.Timerit` class to programmatically use results.
```python
>>> import math
>>> import ubelt as ub
>>> t1 = ub.Timerit(num=200, verbose=2)
>>> for timer in t1:
>>>     setup_vars = 10000
>>>     with timer:
>>>         math.factorial(setup_vars)
>>> print('t1.total_time = %r' % (t1.total_time,))
Timing for 200 loops
Timed for: 200 loops, best of 3
    time per loop: best=2.064 ms, mean=2.115 ± 0.05 ms
t1.total_time = 0.4427177629695507
```


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


### Hashing
The `ub.hash_data` constructs a hash corresponding to a (mostly) arbitrary
ordered python object. A common use case for this function is to construct the
`cfgstr` mentioned in the example for `ub.Cacher`. Instead of returning a hex,
string, `ub.hash_data` encodes the hash digest using the 26 lowercase letters
in the roman alphabet. This makes the result easy to use as a filename suffix.

```python
>>> import ubelt as ub
>>> data = [('arg1', 5), ('lr', .01), ('augmenters', ['flip', 'translate'])]
>>> ub.hash_data(data)[0:8]
crfrgdbi
```


There exists an undocumented plugin architecture to extend this function to
arbitrary types. See `ubelt/util_hash.py` for details.


### Command Line Interaction
The builtin Python `subprocess.Popen` module is great, but it can be a bit
clunky at times. The `os.system` command is easy to use, but it doesn't have
much flexibility. The `ub.cmd` function aims to fix this. It is as simple to
run as `os.system`, but it returns a dictionary containing the return code,
standard out, standard error, and the `Popen` object used under the hood.
```python
>>> import ubelt as ub
>>> info = ub.cmd('gcc --version')
>>> print(ub.repr2(info))
{
    'command': 'gcc --version',
    'err': '',
    'out': 'gcc (Ubuntu 5.4.0-6ubuntu1~16.04.9) 5.4.0 20160609\nCopyright (C) 2015 Free Software Foundation, Inc.\nThis is free software; see the source for copying conditions.  There is NO\nwarranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n',
    'proc': <subprocess.Popen object at 0x7ff98b310390>,
    'ret': 0,
}
```

Also note the use of `ub.repr2` to nicely format the output dictionary.

Additionally, if you specify `verbout=True`, `ub.cmd` will simultaneously
capture the standard output and display it in real time.
```python
>>> import ubelt as ub
>>> info = ub.cmd('gcc --version', verbout=True)
gcc (Ubuntu 5.4.0-6ubuntu1~16.04.9) 5.4.0 20160609
Copyright (C) 2015 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```


A common use case for `ub.cmd` is parsing version numbers of programs
```python
>>> import ubelt as ub
>>> cmake_version = ub.cmd('cmake --version')['out'].splitlines()[0].split()[-1]
>>> print('cmake_version = {!r}'.format(cmake_version))
cmake_version = 3.11.0-rc2
```

This allows you to easily run a command line executable as part of a python
process, see what it is doing, and then do something based on its output, just
as you would if you were interacting with the command line itself.

Lastly, `ub.cmd` removes the need to think about if you need to pass a list of
args, or a string. Both will work. This utility has been tested on both Windows
and Linux.


### Cross-Platform Resource and Cache Directories
If you have an application which writes configuration or cache files, the
standard place to dump those files differs depending if you are on Windows,
Linux, or Mac. UBelt offers a unified functions for determining what these
paths are.

The `ub.ensure_app_cache_dir` and `ub.ensure_app_resource_dir` functions 
find the correct platform-specific location for these files and ensures that
the directories exist. (Note: replacing "ensure" with "get" will simply return
the path, but not ensure that it exists)

The resource root directory is `~/AppData/Roaming` on Windows, `~/.config` on Linux and `~/Library/Application Support` on Mac.
The cache root directory is `~/AppData/Local` on Windows, `~/.config` on Linux and `~/Library/Caches` on Mac.

Example usage on Linux might look like this:
```python
>>> import ubelt as ub
>>> print(ub.compressuser(ub.ensure_app_cache_dir('my_app')))
~/.cache/my_app
>>> print(ub.compressuser(ub.ensure_app_resource_dir('my_app')))
~/.config/my_app
```

### Symlinks

The `ub.symlink` function will create a symlink similar to `os.symlink`.
The main differences are that 
    1) it will not error if the symlink exists and already points to the correct location.
    2) it works* on Windows (*hard links and junctions are used if real symlinks are not available)

```python
>>> import ubelt as ub
>>> dpath = ub.ensure_app_cache_dir('ubelt', 'demo_symlink')
>>> real_path = join(dpath, 'real_file.txt')
>>> link_path = join(dpath, 'link_file.txt')
>>> ub.writeto(real_path, 'foo')
>>> ub.symlink(real_path, link_path)
```


### Downloading Files

The function `ub.download` provides a simple interface to download a URL and
save its data to a file.

```python
>>> import ubelt as ub
>>> url = 'http://i.imgur.com/rqwaDag.png'
>>> fpath = ub.download(url, verbose=0)
>>> print(ub.compressuser(fpath))
~/.cache/ubelt/rqwaDag.png
```

The function `ub.grabdata` works similarly to `ub.download`, but whereas
`ub.download` will always re-download the file, `ub.grabdata` will check if the
file exists and only re-download it if it needs to.

```python
>>> import ubelt as ub
>>> url = 'http://i.imgur.com/rqwaDag.png'
>>> fpath = ub.grabdata(url, verbose=0)
>>> print(ub.compressuser(fpath))
~/.cache/ubelt/rqwaDag.png
```


### Grouping

Group items in a sequence into a dictionary by a second id list
```python
>>> import ubelt as ub
>>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
>>> groupid_list = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
>>> ub.group_items(item_list, groupid_list)
{'dairy': ['cheese'], 'fruit': ['jam', 'bannana'], 'protein': ['ham', 'spam', 'eggs']}
```


### Dictionary Histogram

Find the frequency of items in a sequence
```python
>>> import ubelt as ub
>>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
>>> ub.dict_hist(item_list)
{1232: 2, 1: 1, 2: 4, 900: 3, 39: 1}
```


### Find Duplicates

Find all duplicate items in a list.  More specifically, `ub.find_duplicates`
searches for items that appear more than `k` times, and returns a mapping from
each duplicate item to the positions it appeared in.

```
>>> import ubelt as ub
>>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
>>> ub.find_duplicates(items, k=2)
{0: [0, 1, 6], 2: [3, 8], 3: [4, 5]}
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

Invert the mapping defined by a dictionary. 
By default `invert_dict` assumes that all dictionary values are distinct (i.e.
the mapping is one-to-one / injective). 

```python
>>> import ubelt as ub
>>> mapping = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}
>>> ub.invert_dict(mapping)
{'a': 0, 'b': 1, 'c': 2, 'd': 3}
```

However, by specifying `unique_vals=False` the inverted dictionary builds a set
of keys that were associated with each value.

```python
>>> import ubelt as ub
>>> mapping = {'a': 0, 'A': 0, 'b': 1, 'c': 2, 'C': 2, 'd': 3}
>>> ub.invert_dict(mapping, unique_vals=False)
{0: {'A', 'a'}, 1: {'b'}, 2: {'C', 'c'}, 3: {'d'}}
```


### AutoDict - Autovivification
While the `collections.defaultdict` is nice, it is sometimes more convenient to
have an infinitely nested dictionary of dictionaries. 

```python
>>> import ubelt as ub
>>> auto = ub.AutoDict()
>>> print('auto = {!r}'.format(auto))
auto = {}
>>> auto[0][10][100] = None
>>> print('auto = {!r}'.format(auto))
auto = {0: {10: {100: None}}}
>>> auto[0][1] = 'hello'
>>> print('auto = {!r}'.format(auto))
auto = {0: {1: 'hello', 10: {100: None}}}
```


### String-based imports

Ubelt contains functions to import modules dynamically without using the python
`import` statement. While `importlib` exists, the `ubelt` implementation is
simpler to user and does not have the disadvantage of breaking `pytest`.

Note `ubelt` simply provides an interface to this functionality, the core
implementation is in `xdoctest`. 


```python
>>> import ubelt as ub
>>> module = ub.import_module_from_path(ub.truepath('~/code/ubelt/ubelt'))
>>> print('module = {!r}'.format(module))
module = <module 'ubelt' from '/home/joncrall/code/ubelt/ubelt/__init__.py'>
>>> module = ub.import_module_from_path('ubelt')
>>> print('module = {!r}'.format(module))
module = <module 'ubelt' from '/home/joncrall/code/ubelt/ubelt/__init__.py'>
```


Related to this functionality are the functions `ub.modpath_to_modname` and
`ub.modname_to_modpath`, which *statically* transform (i.e. no code in the target modules
is imported or executed) between module names (e.g. `ubelt.util_import`) and
module paths (e.g.
`~/.local/conda/envs/cenv3/lib/python3.5/site-packages/ubelt/util_import.py`).


```python
>>> import ubelt as ub
>>> modpath = ub.util_import.__file__
>>> print(ub.modpath_to_modname(modpath))
ubelt.util_import
>>> modname = ub.util_import.__name__
>>> assert ub.truepath(ub.modname_to_modpath(modname)) == modpath
```


### Loop Progress
`ProgIter` is a (mostly) drop-in alternative to [`tqdm`](https://pypi.python.org/pypi/tqdm).
It is recommended to use `tqdm` in most cases. The advantage of `ProgIter` is
that it does not use any python threading, and therefore can be safer with code
that makes heavy use of multiprocessing.
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

Sometimes its just prettier to horizontally concatenate two blocks of text.

```python
>>> import ubelt as ub
>>> B = ub.repr2([[1, 2], [3, 4]], nl=1, cbr=True, trailsep=False)
>>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
>>> print(ub.hzcat(['A = ', B, ' * ', C]))
A = [[1, 2], * [[5, 6],
     [3, 4]]    [7, 8]]
```
