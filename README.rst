|CircleCI| |Travis| |Appveyor| |Codecov| |Pypi| |Downloads| |ReadTheDocs|


.. The large version wont work because github strips rst image rescaling. https://i.imgur.com/AcWVroL.png
.. image:: https://i.imgur.com/PoYIsWE.png
   :height: 100px
   :align: left


..   .. raw:: html
..       <img src="https://i.imgur.com/AcWVroL.png" height="100px">

Ubelt is a small library of robust, tested, documented, and simple functions
that extend the Python standard library.  You've probably written and
re-written some of the functions in ubelt before (or wrote out the logic
inline). Next time, try ``pip install ubelt`` instead. 

* Goal: provide simple functions that acomplish common tasks not yet addressed by the python standard library.

* Constraints: Must be low-impact pure python; it should be easy to install and use.

* Method: All functions are written with docstrings and doctests to ensure that a baseline level of documentation and testing always exists (even if functions are copy/pasted into other libraries)

* Motto: Good utilities lift all codes. 


Description:
============

UBelt is cross platform and all top-level functions behave similarly on
Windows, Mac, and Linux (up to some small unavoidable differences).
Almost every function in ``ubelt`` was written with a doctest. This
provides helpful documentation and example usage as well as helping
achieve 100% test coverage (sans Python2, Windows, stuff that could not
be tested automatically, etc).

See the (Available Functions) section for detailed information.

Read the docs here: http://ubelt.readthedocs.io/en/latest/


Current Functionality
=====================
Ubelt is a currated collection of utilities. 

UBelt's functionality is a mixture of the following categories:

- Timing
- Caching
- Hashing
- Command Line / Shell Interaction
- Cross-Platform Cache, Config, and Data Directories
- Symlinks
- Downloading Files
- Dictionary Histogram
- Find Duplicates
- Dictionary Manipulation
- AutoDict - Autovivification
- String-based imports
- Horizontal String Concatenation
- Standalone modules.
    - `progiter <https://github.com/Erotemic/progiter>`__ for Loop Progress
    - `timerit <https://github.com/Erotemic/timerit>`__ for Robust Timing and Benchmarking
    - `ordered-set <https://github.com/LuminosoInsight/ordered-set>`__ for ordered set collections


Installation:
=============

UBelt is written in pure Python and integrated into the python package
index. Just pip install it and then import it!

From pypi:
----------

::

    pip install ubelt

From github:
------------

::

    pip install git+https://github.com/Erotemic/ubelt.git


Purpose
=======

UBelt is a "utility belt" of commonly needed utility and helper
functions.

-  Reusable code - Many functions in ``ubelt`` are simple to write
   yourself (e.g. ``take``, ``memoize``, ``ensure_unicode``), but even
   re-writing trivial functions takes time better spent on more
   important tasks. Rewriting has its place, but not when you can just
   ``pip install ubelt``!

-  Easy access - The entire ``ubelt`` API is exposed at the top level.
   While the functions are defined in submodules, explicit imports make
   easy to access any function. There are also a small number of
   functions (e.g. ``ub.odict``, ``ub.ddict``, ``ub.flatten``, which are
   aliases for ``collections.OrderedDict``, ``collections.DefaultDict``,
   and ``itertools.chain.from_iterable``, respectively) that are
   essentially aliases for functions already in Python's standard
   library. I found myself using these functions so much that I wanted
   easier access to them, thus they are included in ``ubelt``.

-  Extra batteries - Python's standard library is "batteries included"
   and provides great APIs for a variety of tasks. UBelt both extends
   these batteries and provides simplified interfaces to others.

-  Copy paste - It is often not desirable to add extra dependencies to
   code. While I encourage installation and use of this module, I
   realize that option is not always feasible. Most (but not all)
   functions were also written in a way where they can be copy and
   pasted into your packages own utility library without needing to add
   a dependency on ``ubelt``.

History:
========

UBelt is a migration of the most useful parts of
``utool``\ (https://github.com/Erotemic/utool) into a standalone module
with minimal dependencies.

The ``utool`` library contains a number of useful utility functions, but
it also contained non-useful functions, as well as the kitchen sink. A
number of the functions were too specific or not well documented. The
``ubelt`` packages was created to is to slowly port over the most
re-usable parts of ``utool`` into a stable package.

The doctest harness in ``utool`` was ported and rewritten in a new
module called: ```xdoctest`` <https://github.com/Erotemic/xdoctest>`__,
which integrates with ``pytest`` as a plugin. All of the doctests in
``ubelt`` are run using ``xdoctest``.

A small subset of the static-analysis and code introspection tools in
``xdoctest`` are made visible through ``ubelt``.

Available Functions:
====================

Be sure to checkout the new Jupyter notebook: https://github.com/Erotemic/ubelt/blob/master/docs/notebooks/Ubelt%20Demo.ipynb

For the following functions, see corresponding doc-strings for more
details.

Some of the more interesting and useful functions and classes
implemented are:

.. code:: python

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

A complete list of available functions can be seen in the
``ubelt/__init__.py`` file, which was auto-generated by
``mkinit``\ (https://github.com/Erotemic/mkinit):

.. code:: python

    from ubelt.util_arg import (argflag, argval,)
    from ubelt.util_cache import (CacheStamp, Cacher,)
    from ubelt.util_colors import (color_text, highlight_code,)
    from ubelt.util_const import (NoParam,)
    from ubelt.util_cmd import (cmd,)
    from ubelt.util_dict import (AutoDict, AutoOrderedDict, ddict, dict_diff,
                                 dict_hist, dict_isect, dict_subset, dict_take,
                                 dict_union, dzip, find_duplicates, group_items,
                                 invert_dict, map_keys, map_vals, odict,)
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
    from ubelt.util_path import (TempDir, augpath, compressuser, ensuredir,
                                 expandpath, truepath, userhome,)
    from ubelt.util_platform import (DARWIN, LINUX, POSIX, WIN32, editfile,
                                     ensure_app_cache_dir, ensure_app_config_dir,
                                     ensure_app_data_dir, ensure_app_resource_dir,
                                     find_exe, find_path, get_app_cache_dir,
                                     get_app_config_dir, get_app_data_dir,
                                     get_app_resource_dir, platform_cache_dir,
                                     platform_config_dir, platform_data_dir,
                                     platform_resource_dir, startfile,)
    from ubelt.util_str import (codeblock, ensure_unicode, hzcat, indent,
                                paragraph,)
    from ubelt.util_stream import (CaptureStdout, CaptureStream, TeeStringIO,)
    from ubelt.util_time import (Timer, Timerit, timestamp,)
    from ubelt.orderedset import (OrderedSet, oset,)
    from ubelt.progiter import (ProgIter,)


To provide a sense of what functions are the most useful, here is a histogram
(/ tier list) of my most used ubelt functions over several of my projects:

.. code:: python

    {
        # SS > 200
        'repr2': 638,
        'expandpath': 281,
        'ProgIter': 253,
        'ensuredir': 205,
        # S > 100
        'odict': 189,
        'take': 141,
        'Timerit': 131,
        'map_vals': 124,
        'truepath': 104,
        'NiceRepr': 101,
        # A > 50
        'argval': 93,
        'hash_data': 88,
        'cmd': 78,
        'ddict': 76,
        'argflag': 73,
        'codeblock': 71,
        'iterable': 70,
        'dict_hist': 57,
        'ensure_app_cache_dir': 56,
        # B > 25
        'NoParam': 49,
        'augpath': 47,
        'grabdata': 47,
        'flatten': 41,
        'color_text': 40,
        'import_module_from_path': 38,
        'delete': 38,
        'allsame': 36,
        'group_items': 36,
        'Cacher': 36,
        'peek': 36,
        'timestamp': 30,
        'Timer': 29,
        # C > 10
        'dict_subset': 24,
        'compressuser': 24,
        'compress': 23,
        'oset': 22,
        'memoize': 21,
        'argsort': 19,
        'memoize_method': 19,
        'indent': 19,
        'hash_file': 18,
        'find_duplicates': 18,
        'readfrom': 17,
        'dzip': 16,
        'iter_window': 15,
        'writeto': 14,
        'unique': 13,
        'dict_union': 13,
        'startfile': 13,
        'memoize_property': 13,
        'find_exe': 11,
        'chunks': 11,
        'identity': 11,
        # D > 5
        'map_keys': 10,
        'argmax': 10,
        'dict_isect': 9,
        'modname_to_modpath': 9,
        'symlink': 9,
        'highlight_code': 9,
        'CacheStamp': 8,
        'inject_method': 7,
        'ensure_unicode': 7,
        'invert_dict': 7,
        'touch': 7,
        'argmin': 6,
        # F > 0
        'dict_take': 5,
        'hzcat': 5,
        'get_app_cache_dir': 5,
        'AutoDict': 4,
        'WIN32': 3,
        'editfile': 3,
        'import_module_from_name': 3,
        'paragraph': 3,
        'download': 2,
        'userhome': 2,
        'DARWIN': 2,
        'LINUX': 2,
        'modpath_to_modname': 2,
        'argunique': 1,
        'dict_diff': 1,
        'unique_flags': 1,
        'split_modpath': 1,
    }
    
   


Examples
========

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

``ProgIter`` is a (mostly) drop-in alternative to
```tqdm`` <https://pypi.python.org/pypi/tqdm>`__. 
*The advantage of ``ProgIter`` is that it does not use any python threading*,
and therefore can be safer with code that makes heavy use of multiprocessing.

Note: ProgIter is now a standalone module: ``pip intstall progiter``)

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

Additionally, if you specify ``verbout=True``, ``ub.cmd`` will
simultaneously capture the standard output and display it in real time.

.. code:: python

    >>> import ubelt as ub
    >>> info = ub.cmd('gcc --version', verbout=True)
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
Windows, Linux, or Mac. UBelt offers a unified functions for determining
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
    >>> print(list(ub.dict_take(dict_, [1, 2, 3, 4, 5], default=None)))
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

Some of the tools in ``ubelt`` also exist as standalone modules.

Here are the repos containing the standalone utilities:

-  ProgIter - https://github.com/Erotemic/progiter
-  Timerit - https://github.com/Erotemic/timerit
-  OrderedSet - https://github.com/LuminosoInsight/ordered-set

In the future some of the functionaity in ubelt may be ported and integrated
into the ``boltons`` project: https://github.com/mahmoud/boltons.


Notes.
------
Ubelt will support Python2 for the forseeable future (at least until the
projects I work on are off it followed by a probation period).

PRs are welcome. If you have a utility function that you think is useful then
write a PR. I'm likely to respond promptly.

Also check out my other projects (many of which are powered by ubelt):

-  ProgIter https://github.com/Erotemic/netharn
-  Timerit - https://github.com/Erotemic/timerit
-  mkinit https://github.com/Erotemic/mkinit
-  xdoctest https://github.com/Erotemic/xdoctest
-  xinspect https://github.com/Erotemic/xinspect
-  xdev https://github.com/Erotemic/xdev
-  vimtk https://github.com/Erotemic/vimtk
-  futures_actors https://github.com/Erotemic/futures_actors
-  ibeis https://github.com/Erotemic/ibeis
-  graphid https://github.com/Erotemic/graphid
  

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
