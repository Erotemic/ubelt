|ReadTheDocs| |Pypi| |Downloads| |Codecov| |CircleCI| |Travis| |Appveyor| |CodeQuality|


.. The large version wont work because github strips rst image rescaling. https://i.imgur.com/AcWVroL.png
.. image:: https://i.imgur.com/PoYIsWE.png
   :height: 100px
   :align: left


..   .. raw:: html
..       <img src="https://i.imgur.com/AcWVroL.png" height="100px">

Ubelt is a small library of robust, tested, documented, and simple functions
that extend the Python standard library. It has a flat API that all behaves
similarly on Windows, Mac, and Linux (up to some small unavoidable
differences).  Almost every function in ``ubelt`` was written with a doctest.
This provides helpful documentation and example usage as well as helping
achieve 100% test coverage (with minor exceptions for Python2, Windows,
etc...). 

* Goal: provide simple functions that accomplish common tasks not yet addressed by the python standard library.

* Constraints: Must be low-impact pure python; it should be easy to install and use.

* Method: All functions are written with docstrings and doctests to ensure that a baseline level of documentation and testing always exists (even if functions are copy/pasted into other libraries)

* Motto: Good utilities lift all codes. 


Read the docs here: http://ubelt.readthedocs.io/en/latest/

These are some of the tasks that ubelt's API enables:

  - hash common data structures

  - hash files

  - cache a block of code 

  - time a block of code

  - download a file

  - run shell commands

  - string-format nested data structures

  - make a directory if it doesn't exist

  - expand environment variables and tildes in path strings

  - map a function over the keys or values of a dictionary

  - perform set operations on dictionaries

  - perform dictionary operations like histogram, duplicates, and inversion 

  - delete a file or directory

  - import a module using the path to that module 

  - check if a particular flag or value is on the command line

  - color text with ANSI tags

  - get paths to cross platform data/cache/config directories

  - create cross platform symlinks 

  - horizontally concatenate multiline strings

  - access defaultdict and OrderedDict by ddict and odict aliases

  - build ordered sets

  - memoize functions

  - argmax/min/sort on dictionaries

Ubelt is small. Its top-level API is defined using roughly 40 lines:

.. code:: python

    from ubelt.util_arg import (argflag, argval,)
    from ubelt.util_cache import (CacheStamp, Cacher,)
    from ubelt.util_colors import (color_text, highlight_code,)
    from ubelt.util_const import (NoParam,)
    from ubelt.util_cmd import (cmd,)
    from ubelt.util_dict import (AutoDict, AutoOrderedDict, ddict, dict_diff,
                                 dict_hist, dict_isect, dict_subset, dict_union,
                                 dzip, find_duplicates, group_items, invert_dict,
                                 map_keys, map_vals, odict, sorted_keys,
                                 sorted_vals,)
    from ubelt.util_download import (download, grabdata,)
    from ubelt.util_func import (identity, inject_method,)
    from ubelt.util_format import (FormatterExtensions, repr2,)
    from ubelt.util_io import (delete, readfrom, touch, writeto,)
    from ubelt.util_links import (symlink,)
    from ubelt.util_list import (allsame, argmax, argmin, argsort, argunique,
                                 boolmask, chunks, compress, flatten, iter_window,
                                 iterable, peek, take, unique, unique_flags,)
    from ubelt.util_hash import (hash_data, hash_file,)
    from ubelt.util_import import (import_module_from_name,
                                   import_module_from_path, modname_to_modpath,
                                   modpath_to_modname, split_modpath,)
    from ubelt.util_memoize import (memoize, memoize_method, memoize_property,)
    from ubelt.util_mixins import (NiceRepr,)
    from ubelt.util_path import (TempDir, augpath, ensuredir, expandpath,
                                 shrinkuser, userhome,)
    from ubelt.util_platform import (DARWIN, LINUX, POSIX, WIN32,
                                     ensure_app_cache_dir, ensure_app_config_dir,
                                     ensure_app_data_dir, find_exe, find_path,
                                     get_app_cache_dir, get_app_config_dir,
                                     get_app_data_dir, platform_cache_dir,
                                     platform_config_dir, platform_data_dir,)
    from ubelt.util_str import (codeblock, ensure_unicode, hzcat, indent,
                                paragraph,)
    from ubelt.util_stream import (CaptureStdout, CaptureStream, TeeStringIO,)
    from ubelt.util_time import (timestamp,)
    from ubelt.orderedset import (OrderedSet, oset,)
    from ubelt.progiter import (ProgIter,)
    from ubelt.timerit import (Timer, Timerit,)


Installation:
=============

Ubelt is distributed on pypi as a universal wheel and can be pip installed on
Python 2.7, Python 3.4+. Installations are tested on CPython and PyPy
implementations.

::

    pip install ubelt

Note that our distributions on pypi are signed with GPG. The signing public key
is ``D297D757``; this should agree with the value in `dev/public_gpg_key`.


It is also possible to simply install it from source.

::

    pip install git+https://github.com/Erotemic/ubelt.git


History:
========

Ubelt is a migration of the most useful parts of
``utool``\ (https://github.com/Erotemic/utool) into a standalone module
with minimal dependencies.

The ``utool`` library contains a number of useful utility functions, but it
also contained non-useful functions, as well as the kitchen sink. A number of
the functions were too specific or not well documented. The ``ubelt`` is a port
of the simplest and most useful parts of ``utool``.

Note that there are other cool things in ``utool`` that are not in ``ubelt``.
Notably, the doctest harness ultimately became `xdoctest <https://github.com/Erotemic/xdoctest>`__. 
Code introspection and dynamic analysis tools were ported to `xinspect <https://github.com/Erotemic/xinspect>`__.
The more IPython-y tools were ported to `xdev <https://github.com/Erotemic/xdev>`__.
Parts of it made their way into `scriptconfig <https://gitlab.kitware.com/utils/scriptconfig>`__.
The init-file generation was moved to `mkinit <https://github.com/Erotemic/mkinit>`__.
Some vim and system-y things can be found in `vimtk <https://github.com/Erotemic/vimtk>`__.


Function Usefulness 
===================

When I had to hand pick a set of functions that I thought were the most useful
I chose these and provided some comment on why:

.. code:: python

    import ubelt as ub

    ub.ensuredir  # os.makedirs(exist_ok=True) is 3 only and too verbose
    ub.Timerit  # powerful multiline alternative to timeit
    ub.Cacher  # configuration based on-disk cachine
    ub.cmd  # combines the best of subprocess.Popen and os.system
    ub.hash_data  # extremely useful with Cacher to config strings
    ub.repr2  # readable representations of nested data structures
    ub.download  # why is this not a one liner --- also see grabdata for the same thing, but builtin caching.
    ub.AutoDict  # one of the most useful tools in Perl, 
    ub.modname_to_modpath  # (works via static analysis)
    ub.modpath_to_modname  # (works via static analysis)
    ub.import_module_from_path  # (Unlike importlib, this does not break pytest)
    ub.import_module_from_name  # (Unlike importlib, this does not break pytest)


But a better way might to objectively measure the frequency of usage and built
a histogram of usefulness. I generated this histogram using ``python dev/count_usage_freq.py``.

.. code:: python

    {
    'repr2': 1209,
    'ProgIter': 250,
    'odict': 210,
    'take': 209,
    'dzip': 180,
    'ensuredir': 168,
    'expandpath': 168,
    'argval': 148,
    'map_vals': 132,
    'flatten': 129,
    'Timerit': 113,
    'NoParam': 104,
    'NiceRepr': 102,
    'cmd': 102,
    'hzcat': 95,
    'argflag': 95,
    'ddict': 92,
    'codeblock': 87,
    'iterable': 82,
    'dict_hist': 78,
    'hash_data': 67,
    'group_items': 65,
    'compress': 64,
    'grabdata': 63,
    'color_text': 58,
    'augpath': 48,
    'allsame': 48,
    'delete': 48,
    'Cacher': 42,
    'invert_dict': 39,
    'peek': 39,
    'chunks': 38,
    'writeto': 38,
    'argsort': 37,
    'Timer': 37,
    'timestamp': 30,
    'find_duplicates': 27,
    'indent': 26,
    'unique': 23,
    'map_keys': 23,
    'iter_window': 22,
    'memoize': 21,
    'ensure_unicode': 21,
    'readfrom': 21,
    'identity': 19,
    'oset': 18,
    'modname_to_modpath': 16,
    'dict_subset': 15,
    'memoize_method': 14,
    'highlight_code': 14,
    'argmax': 13,
    'memoize_property': 13,
    'find_exe': 12,
    'touch': 12,
    'hash_file': 11,
    'import_module_from_path': 10,
    'dict_isect': 9,
    'inject_method': 8,
    'AutoDict': 6,
    'argmin': 6,
    'dict_union': 6,
    'symlink': 6,
    'split_modpath': 5,
    'CaptureStdout': 4,
    'dict_diff': 4,
    'import_module_from_name': 4,
    'download': 3,
    'modpath_to_modname': 3,
    'paragraph': 3,
    'CacheStamp': 3,
    'AutoOrderedDict': 2,
    'unique_flags': 2,
    'find_path': 2,
    }
    
   


Examples
========

Be sure to checkout the new Jupyter notebook: https://github.com/Erotemic/ubelt/blob/master/docs/notebooks/Ubelt%20Demo.ipynb

Here are some examples of some features inside ``ubelt``


Timing
------

Quickly time a single line.

.. code:: python

    >>> import math
    >>> import ubelt as ub
    >>> timer = ub.Timer('Timer demo!', verbose=1)
    >>> with timer:
    >>>     math.factorial(100000)
    tic('Timer demo!')
    ...toc('Timer demo!')=0.1453s


Robust Timing and Benchmarking
------------------------------

Easily do robust timings on existing blocks of code by simply indenting
them. There is no need to refactor into a string representation or
convert to a single line. With ``ub.Timerit`` there is no need to resort
to the ``timeit`` module!

The quick and dirty way just requires one indent.

Note: Timerit is also defined in a standalone module: ``pip install timerit``)

.. code:: python

    >>> import math
    >>> import ubelt as ub
    >>> for _ in ub.Timerit(num=200, verbose=3):
    >>>     math.factorial(10000)
    Timing for 200 loops
    Timed for: 200 loops, best of 3
        time per loop: best=2.055 ms, mean=2.145 ± 0.083 ms

Use the loop variable as a context manager for more accurate timings or
to incorporate an setup phase that is not timed. You can also access
properties of the ``ub.Timerit`` class to programmatically use results.

.. code:: python

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


Loop Progress
-------------

``ProgIter`` is a no-threads attached Progress meter that writes to stdout.  It
is a mostly drop-in alternative to `tqdm
<https://pypi.python.org/pypi/tqdm>`__. 
*The advantage of ``ProgIter`` is that it does not use any python threading*,
and therefore can be safer with code that makes heavy use of multiprocessing.

Note: ``ProgIter`` is also defined in a standalone module: ``pip install progiter``)

.. code:: python

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


Caching
-------

Cache intermediate results in a script with minimal boilerplate. 
It looks like 4 lines of boilerplate is the best you can do with Python 3.8 syntax.
See <https://raw.githubusercontent.com/Erotemic/ubelt/master/ubelt/util_cache.py>`__ for details.


.. code:: python

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

Hashing
-------

The ``ub.hash_data`` constructs a hash corresponding to a (mostly)
arbitrary ordered python object. A common use case for this function is
to construct the ``cfgstr`` mentioned in the example for ``ub.Cacher``.
Instead of returning a hex, string, ``ub.hash_data`` encodes the hash
digest using the 26 lowercase letters in the roman alphabet. This makes
the result easy to use as a filename suffix.

.. code:: python

    >>> import ubelt as ub
    >>> data = [('arg1', 5), ('lr', .01), ('augmenters', ['flip', 'translate'])]
    >>> ub.hash_data(data)[0:8]
    5f5fda5e

There exists an undocumented plugin architecture to extend this function
to arbitrary types. See ``ubelt/util_hash.py`` for details.

Command Line Interaction
------------------------

The builtin Python ``subprocess.Popen`` module is great, but it can be a
bit clunky at times. The ``os.system`` command is easy to use, but it
doesn't have much flexibility. The ``ub.cmd`` function aims to fix this.
It is as simple to run as ``os.system``, but it returns a dictionary
containing the return code, standard out, standard error, and the
``Popen`` object used under the hood.

.. code:: python

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

Also note the use of ``ub.repr2`` to nicely format the output
dictionary.

Additionally, if you specify ``verbose=True``, ``ub.cmd`` will
simultaneously capture the standard output and display it in real time.

.. code:: python

    >>> import ubelt as ub
    >>> info = ub.cmd('gcc --version', verbose=True)
    gcc (Ubuntu 5.4.0-6ubuntu1~16.04.9) 5.4.0 20160609
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

A common use case for ``ub.cmd`` is parsing version numbers of programs

.. code:: python

    >>> import ubelt as ub
    >>> cmake_version = ub.cmd('cmake --version')['out'].splitlines()[0].split()[-1]
    >>> print('cmake_version = {!r}'.format(cmake_version))
    cmake_version = 3.11.0-rc2

This allows you to easily run a command line executable as part of a
python process, see what it is doing, and then do something based on its
output, just as you would if you were interacting with the command line
itself.

Lastly, ``ub.cmd`` removes the need to think about if you need to pass a
list of args, or a string. Both will work. This utility has been tested
on both Windows and Linux.

Cross-Platform Resource and Cache Directories
---------------------------------------------

If you have an application which writes configuration or cache files,
the standard place to dump those files differs depending if you are on
Windows, Linux, or Mac. Ubelt offers a unified functions for determining
what these paths are.

The ``ub.ensure_app_cache_dir`` and ``ub.ensure_app_resource_dir``
functions find the correct platform-specific location for these files
and ensures that the directories exist. (Note: replacing "ensure" with
"get" will simply return the path, but not ensure that it exists)

The resource root directory is ``~/AppData/Roaming`` on Windows,
``~/.config`` on Linux and ``~/Library/Application Support`` on Mac. The
cache root directory is ``~/AppData/Local`` on Windows, ``~/.config`` on
Linux and ``~/Library/Caches`` on Mac.

Example usage on Linux might look like this:

.. code:: python

    >>> import ubelt as ub
    >>> print(ub.compressuser(ub.ensure_app_cache_dir('my_app')))
    ~/.cache/my_app
    >>> print(ub.compressuser(ub.ensure_app_resource_dir('my_app')))
    ~/.config/my_app

Symlinks
--------

The ``ub.symlink`` function will create a symlink similar to
``os.symlink``. The main differences are that 1) it will not error if
the symlink exists and already points to the correct location. 2) it
works\* on Windows (\*hard links and junctions are used if real symlinks
are not available)

.. code:: python

    >>> import ubelt as ub
    >>> dpath = ub.ensure_app_cache_dir('ubelt', 'demo_symlink')
    >>> real_path = join(dpath, 'real_file.txt')
    >>> link_path = join(dpath, 'link_file.txt')
    >>> ub.writeto(real_path, 'foo')
    >>> ub.symlink(real_path, link_path)

Downloading Files
-----------------

The function ``ub.download`` provides a simple interface to download a
URL and save its data to a file.

.. code:: python

    >>> import ubelt as ub
    >>> url = 'http://i.imgur.com/rqwaDag.png'
    >>> fpath = ub.download(url, verbose=0)
    >>> print(ub.compressuser(fpath))
    ~/.cache/ubelt/rqwaDag.png

The function ``ub.grabdata`` works similarly to ``ub.download``, but
whereas ``ub.download`` will always re-download the file,
``ub.grabdata`` will check if the file exists and only re-download it if
it needs to.

.. code:: python

    >>> import ubelt as ub
    >>> url = 'http://i.imgur.com/rqwaDag.png'
    >>> fpath = ub.grabdata(url, verbose=0, hash_prefix='944389a39')
    >>> print(ub.compressuser(fpath))
    ~/.cache/ubelt/rqwaDag.png


New in version 0.4.0: both functions now accepts the ``hash_prefix`` keyword
argument, which if specified will check that the hash of the file matches the
provided value. The ``hasher`` keyword argument can be used to change which
hashing algorithm is used (it defaults to ``"sha512"``).

Grouping
--------

Group items in a sequence into a dictionary by a second id list

.. code:: python

    >>> import ubelt as ub
    >>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
    >>> groupid_list = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
    >>> ub.group_items(item_list, groupid_list)
    {'dairy': ['cheese'], 'fruit': ['jam', 'bannana'], 'protein': ['ham', 'spam', 'eggs']}

Dictionary Histogram
--------------------

Find the frequency of items in a sequence

.. code:: python

    >>> import ubelt as ub
    >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
    >>> ub.dict_hist(item_list)
    {1232: 2, 1: 1, 2: 4, 900: 3, 39: 1}

Find Duplicates
---------------

Find all duplicate items in a list. More specifically,
``ub.find_duplicates`` searches for items that appear more than ``k``
times, and returns a mapping from each duplicate item to the positions
it appeared in.

.. code:: python

    >>> import ubelt as ub
    >>> items = [0, 0, 1, 2, 3, 3, 0, 12, 2, 9]
    >>> ub.find_duplicates(items, k=2)
    {0: [0, 1, 6], 2: [3, 8], 3: [4, 5]}

Dictionary Manipulation
-----------------------

Take a subset of a dictionary.

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
    >>> subdict_ = ub.dict_subset(dict_, ['K', 'dcvs_clip_max'])
    >>> print(subdict_)
    {'K': 3, 'dcvs_clip_max': 0.2}

Take only the values, optionally specify a default value.

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
    >>> print(list(ub.take(dict_, [1, 2, 3, 4, 5], default=None)))
    ['a', 'b', 'c', None, None]

Apply a function to each value in the dictionary (see also
``ub.map_keys``).

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {'a': [1, 2, 3], 'b': []}
    >>> newdict = ub.map_vals(len, dict_)
    >>> print(newdict)
    {'a': 3, 'b': 0}

Invert the mapping defined by a dictionary. By default ``invert_dict``
assumes that all dictionary values are distinct (i.e. the mapping is
one-to-one / injective).

.. code:: python

    >>> import ubelt as ub
    >>> mapping = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}
    >>> ub.invert_dict(mapping)
    {'a': 0, 'b': 1, 'c': 2, 'd': 3}

However, by specifying ``unique_vals=False`` the inverted dictionary
builds a set of keys that were associated with each value.

.. code:: python

    >>> import ubelt as ub
    >>> mapping = {'a': 0, 'A': 0, 'b': 1, 'c': 2, 'C': 2, 'd': 3}
    >>> ub.invert_dict(mapping, unique_vals=False)
    {0: {'A', 'a'}, 1: {'b'}, 2: {'C', 'c'}, 3: {'d'}}

AutoDict - Autovivification
---------------------------

While the ``collections.defaultdict`` is nice, it is sometimes more
convenient to have an infinitely nested dictionary of dictionaries.

.. code:: python

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

String-based imports
--------------------

Ubelt contains functions to import modules dynamically without using the
python ``import`` statement. While ``importlib`` exists, the ``ubelt``
implementation is simpler to user and does not have the disadvantage of
breaking ``pytest``.

Note ``ubelt`` simply provides an interface to this functionality, the
core implementation is in ``xdoctest`` (over as of version ``0.7.0``, 
the code is statically copied into an autogenerated file such that ``ubelt``
does not actually depend on ``xdoctest`` during runtime).

.. code:: python

    >>> import ubelt as ub
    >>> module = ub.import_module_from_path(ub.truepath('~/code/ubelt/ubelt'))
    >>> print('module = {!r}'.format(module))
    module = <module 'ubelt' from '/home/joncrall/code/ubelt/ubelt/__init__.py'>
    >>> module = ub.import_module_from_name('ubelt')
    >>> print('module = {!r}'.format(module))
    module = <module 'ubelt' from '/home/joncrall/code/ubelt/ubelt/__init__.py'>

Related to this functionality are the functions
``ub.modpath_to_modname`` and ``ub.modname_to_modpath``, which
*statically* transform (i.e. no code in the target modules is imported
or executed) between module names (e.g. ``ubelt.util_import``) and
module paths (e.g.
``~/.local/conda/envs/cenv3/lib/python3.5/site-packages/ubelt/util_import.py``).

.. code:: python

    >>> import ubelt as ub
    >>> modpath = ub.util_import.__file__
    >>> print(ub.modpath_to_modname(modpath))
    ubelt.util_import
    >>> modname = ub.util_import.__name__
    >>> assert ub.truepath(ub.modname_to_modpath(modname)) == modpath

Horizontal String Concatenation
-------------------------------

Sometimes its just prettier to horizontally concatenate two blocks of
text.

.. code:: python

    >>> import ubelt as ub
    >>> B = ub.repr2([[1, 2], [3, 4]], nl=1, cbr=True, trailsep=False)
    >>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
    >>> print(ub.hzcat(['A = ', B, ' * ', C]))
    A = [[1, 2], * [[5, 6],
         [3, 4]]    [7, 8]]

External tools.
---------------

Some of the tools in ``ubelt`` also exist as standalone modules. I haven't
decided if its best to statically copy them into ubelt or require on pypi to
satisfy the dependency. There are some tools that are not used by default 
unless you explicitly allow for them. 

Code that is currently statically included:

-  ProgIter - https://github.com/Erotemic/progiter
-  Timerit - https://github.com/Erotemic/timerit

Code that is currently linked via pypi:

-  OrderedSet - https://github.com/LuminosoInsight/ordered-set


Code that is completely optional, and only used in specific cases:

- Numpy - ``ub.repr2`` will format a numpy array nicely by default
- xxhash - this can be specified as a hasher to ``ub.hash_data``
- Pygments - used by the ``util_color`` module.


Also, in the future some of the functionality in ubelt may be ported and integrated
into the ``boltons`` project: https://github.com/mahmoud/boltons.


Notes.
------
Ubelt will support Python2 for the foreseeable future (at least until the
projects I work on are off it followed by a probation period).

PRs are welcome. If you have a utility function that you think is useful then
write a PR. I'm likely to respond promptly.

Also check out my other projects (many of which are powered by ubelt):

-  ProgIter https://github.com/Erotemic/progiter
-  Timerit https://github.com/Erotemic/timerit
-  mkinit https://github.com/Erotemic/mkinit
-  xdoctest https://github.com/Erotemic/xdoctest
-  xinspect https://github.com/Erotemic/xinspect
-  xdev https://github.com/Erotemic/xdev
-  vimtk https://github.com/Erotemic/vimtk
-  graphid https://github.com/Erotemic/graphid
-  ibeis https://github.com/Erotemic/ibeis
  

.. |CircleCI| image:: https://circleci.com/gh/Erotemic/ubelt.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/ubelt
.. |Travis| image:: https://img.shields.io/travis/Erotemic/ubelt/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/ubelt?branch=master
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Erotemic/ubelt?branch=master&svg=True
   :target: https://ci.appveyor.com/project/Erotemic/ubelt/branch/master
.. |Codecov| image:: https://codecov.io/github/Erotemic/ubelt/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/ubelt?branch=master
.. |Pypi| image:: https://img.shields.io/pypi/v/ubelt.svg
   :target: https://pypi.python.org/pypi/ubelt
.. |Downloads| image:: https://img.shields.io/pypi/dm/ubelt.svg
   :target: https://pypistats.org/packages/ubelt
.. |ReadTheDocs| image:: https://readthedocs.org/projects/ubelt/badge/?version=latest
    :target: http://ubelt.readthedocs.io/en/latest/
.. |CodeQuality| image:: https://api.codacy.com/project/badge/Grade/4d815305fc014202ba7dea09c4676343   
    :target: https://www.codacy.com/manual/Erotemic/ubelt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Erotemic/ubelt&amp;utm_campaign=Badge_Grade
