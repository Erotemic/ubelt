|GithubActions| |ReadTheDocs| |Pypi| |Downloads| |Codecov| |CircleCI| |Appveyor| 

.. .. |CodeQuality| |TwitterFollow|


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
achieve 100% test coverage (with minor exceptions on Windows). 

* Goal: provide simple functions that accomplish common tasks not yet addressed by the python standard library.

* Constraints: Must be low-impact pure python; it should be easy to install and use.

* Method: All functions are written with docstrings and doctests to ensure that a baseline level of documentation and testing always exists (even if functions are copy/pasted into other libraries)

* Motto: Good utilities lift all codes. 


Read the docs here: http://ubelt.readthedocs.io/en/latest/

These are some of the tasks that ubelt's API enables:

  - extended pathlib (ub.Path)

  - hash common data structures like list, dict, int, str, etc. (hash_data)

  - hash files (hash_file)

  - cache a block of code (Cacher, CacheStamp)

  - time a block of code (Timer)

  - show loop progress with less overhead than tqdm (ProgIter)

  - download a file with optional caching and hash verification (download, grabdata)

  - run shell commands (cmd)

  - find a file or directory in candidate locations (find_path, find_exe) 

  - string-format nested data structures (repr2)

  - color text with ANSI tags (color_text)

  - horizontally concatenate multiline strings (hzcat)

  - make a directory if it doesn't exist (ensuredir)

  - delete a file, link, or entire directory (delete)

  - create cross platform symlinks (symlink)

  - expand environment variables and tildes in path strings (expandpath)

  - import a module using the path to that module (import_module_from_path)

  - check if a particular flag or value is on the command line (argflag, argval)

  - get paths to cross platform data/cache/config directories  (ensure_app_cache_dir, ...)

  - memoize functions (memoize, memoize_method, memoize_property)

  - build ordered sets (oset)

  - short defaultdict and OrderedDict aliases (ddict and odict)

  - map a function over the keys or values of a dictionary (map_keys, map_vals)

  - perform set operations on dictionaries (dict_union, dict_isect, dict_diff, dict_subset, ...)

  - perform dictionary operations like histogram, inversion, and sorting (dict_hist, invert_dict, sorted_keys, sorted_vals)

  - argmax/min/sort on lists and dictionaries (argmin, argsort,) 

  - find duplicates in a list (find_duplicates)

  - group a sequence of items by some criterion (group_items)

Ubelt is small. Its top-level API is defined using roughly 40 lines:

.. code:: python

    from ubelt.util_arg import (argflag, argval,)
    from ubelt.util_cache import (CacheStamp, Cacher,)
    from ubelt.util_colors import (NO_COLOR, color_text, highlight_code,)
    from ubelt.util_const import (NoParam,)
    from ubelt.util_cmd import (cmd,)
    from ubelt.util_dict import (AutoDict, AutoOrderedDict, SetDict, UDict, ddict,
                                 dict_diff, dict_hist, dict_isect, dict_subset,
                                 dict_union, dzip, find_duplicates, group_items,
                                 invert_dict, map_keys, map_vals, map_values,
                                 named_product, odict, sdict, sorted_keys,
                                 sorted_vals, sorted_values, udict, varied_values,)
    from ubelt.util_deprecate import (schedule_deprecation,)
    from ubelt.util_download import (download, grabdata,)
    from ubelt.util_download_manager import (DownloadManager,)
    from ubelt.util_func import (compatible, identity, inject_method,)
    from ubelt.util_format import (FormatterExtensions, repr2,)
    from ubelt.util_futures import (Executor, JobPool,)
    from ubelt.util_io import (delete, readfrom, touch, writeto,)
    from ubelt.util_links import (symlink,)
    from ubelt.util_list import (allsame, argmax, argmin, argsort, argunique,
                                 boolmask, chunks, compress, flatten, iter_window,
                                 iterable, peek, take, unique, unique_flags,)
    from ubelt.util_hash import (hash_data, hash_file,)
    from ubelt.util_import import (import_module_from_name,
                                   import_module_from_path, modname_to_modpath,
                                   modpath_to_modname, split_modpath,)
    from ubelt.util_indexable import (IndexableWalker, indexable_allclose,)
    from ubelt.util_memoize import (memoize, memoize_method, memoize_property,)
    from ubelt.util_mixins import (NiceRepr,)
    from ubelt.util_path import (Path, TempDir, augpath, ensuredir, expandpath,
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
    from ubelt.util_time import (Timer, timeparse, timestamp,)
    from ubelt.util_zip import (split_archive, zopen,)
    from ubelt.orderedset import (OrderedSet, oset,)
    from ubelt.progiter import (ProgIter,)



Installation:
=============

Ubelt is distributed on pypi as a universal wheel and can be pip installed on
Python 3.6+. Installations are tested on CPython and PyPy implementations. For
Python 2.7 and 3.5, the last supported version was 0.11.1.

::

    pip install ubelt

Note that our distributions on pypi are signed with GPG. The signing public key
is ``D297D757``; this should agree with the value in `dev/public_gpg_key`.


Function Usefulness 
===================

When I had to hand pick a set of functions that I thought were the most useful
I chose these and provided some comment on why:

.. code:: python

    import ubelt as ub

    ub.Path  # inherits from pathlib.Path with quality of life improvements
    ub.UDict  # inherits from dict with keywise set operations and quality of life improvements
    ub.Cacher  # configuration based on-disk cachine
    ub.CacheStamp  # indirect caching with corruption detection
    ub.hash_data  # hash mutable python containers, useful with Cacher to config strings
    ub.cmd  # combines the best of subprocess.Popen and os.system
    ub.download  # download a file with a single command. Also see grabdata for the same thing, but caching from CacheStamp.
    ub.JobPool   # easy multi-threading / multi-procesing / or single-threaded processing
    ub.ProgIter  # a minimal progress iterator. It's single threaded, informative, and faster than tqdm.
    ub.dict_isect  # like set intersection, but with dictionaries
    ub.dict_union  # like set union, but with dictionaries
    ub.dict_diff  # like set difference, but with dictionaries
    ub.map_keys  # shorthand for ``dict(zip(map(func, d.keys()), d.values()))``
    ub.map_vals  # shorthand for ``dict(zip(d.keys(), map(func, d.values())))``
    ub.memoize  # like ``functools.cache``, but uses ub.hash_data if the args are not hashable.
    ub.repr2  # readable representations of nested data structures


But a better way might to objectively measure the frequency of usage and built
a histogram of usefulness. I generated this histogram using ``python dev/gen_api_for_docs.py``, 
which roughly counts the number of times I've used a ubelt function in another
project. Note: this measure is biased towards older functions.

================================================================================================================================================ ================
 Function name                                                                                                                                         Usefulness
================================================================================================================================================ ================
`ubelt.repr2 <https://ubelt.readthedocs.io/en/latest/ubelt.util_format.html#ubelt.util_format.repr2>`__                                                      2384
`ubelt.Path <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.Path>`__                                                             624
`ubelt.ProgIter <https://ubelt.readthedocs.io/en/latest/ubelt.progiter.html#ubelt.progiter.ProgIter>`__                                                       539
`ubelt.expandpath <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.expandpath>`__                                                 419
`ubelt.paragraph <https://ubelt.readthedocs.io/en/latest/ubelt.util_str.html#ubelt.util_str.paragraph>`__                                                     358
`ubelt.take <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.take>`__                                                             342
`ubelt.cmd <https://ubelt.readthedocs.io/en/latest/ubelt.util_cmd.html#ubelt.util_cmd.cmd>`__                                                                 283
`ubelt.codeblock <https://ubelt.readthedocs.io/en/latest/ubelt.util_str.html#ubelt.util_str.codeblock>`__                                                     273
`ubelt.ensuredir <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.ensuredir>`__                                                   252
`ubelt.map_vals <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.map_vals>`__                                                     248
`ubelt.odict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.odict>`__                                                           234
`ubelt.ddict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.ddict>`__                                                           225
`ubelt.flatten <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.flatten>`__                                                       218
`ubelt.peek <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.peek>`__                                                             202
`ubelt.ensure_app_cache_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.ensure_app_cache_dir>`__                     201
`ubelt.NiceRepr <https://ubelt.readthedocs.io/en/latest/ubelt.util_mixins.html#ubelt.util_mixins.NiceRepr>`__                                                 195
`ubelt.group_items <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.group_items>`__                                               192
`ubelt.oset <https://ubelt.readthedocs.io/en/latest/ubelt.orderedset.html#ubelt.orderedset.oset>`__                                                           182
`ubelt.dzip <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dzip>`__                                                             169
`ubelt.iterable <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.iterable>`__                                                     159
`ubelt.dict_isect <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dict_isect>`__                                                 157
`ubelt.NoParam <https://ubelt.readthedocs.io/en/latest/ubelt.util_const.html#ubelt.util_const.NoParam>`__                                                     154
`ubelt.hash_data <https://ubelt.readthedocs.io/en/latest/ubelt.util_hash.html#ubelt.util_hash.hash_data>`__                                                   141
`ubelt.argflag <https://ubelt.readthedocs.io/en/latest/ubelt.util_arg.html#ubelt.util_arg.argflag>`__                                                         136
`ubelt.dict_diff <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dict_diff>`__                                                   129
`ubelt.Timer <https://ubelt.readthedocs.io/en/latest/ubelt.util_time.html#ubelt.util_time.Timer>`__                                                           125
`ubelt.augpath <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.augpath>`__                                                       120
`ubelt.dict_hist <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dict_hist>`__                                                   115
`ubelt.grabdata <https://ubelt.readthedocs.io/en/latest/ubelt.util_download.html#ubelt.util_download.grabdata>`__                                             114
`ubelt.color_text <https://ubelt.readthedocs.io/en/latest/ubelt.util_colors.html#ubelt.util_colors.color_text>`__                                             104
`ubelt.identity <https://ubelt.readthedocs.io/en/latest/ubelt.util_func.html#ubelt.util_func.identity>`__                                                     102
`ubelt.delete <https://ubelt.readthedocs.io/en/latest/ubelt.util_io.html#ubelt.util_io.delete>`__                                                              99
`ubelt.argval <https://ubelt.readthedocs.io/en/latest/ubelt.util_arg.html#ubelt.util_arg.argval>`__                                                            93
`ubelt.dict_union <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dict_union>`__                                                  90
`ubelt.memoize <https://ubelt.readthedocs.io/en/latest/ubelt.util_memoize.html#ubelt.util_memoize.memoize>`__                                                  89
`ubelt.compress <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.compress>`__                                                      87
`ubelt.allsame <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.allsame>`__                                                        81
`ubelt.unique <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.unique>`__                                                          64
`ubelt.named_product <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.named_product>`__                                            61
`ubelt.hzcat <https://ubelt.readthedocs.io/en/latest/ubelt.util_str.html#ubelt.util_str.hzcat>`__                                                              61
`ubelt.invert_dict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.invert_dict>`__                                                61
`ubelt.JobPool <https://ubelt.readthedocs.io/en/latest/ubelt.util_futures.html#ubelt.util_futures.JobPool>`__                                                  60
`ubelt.timestamp <https://ubelt.readthedocs.io/en/latest/ubelt.util_time.html#ubelt.util_time.timestamp>`__                                                    48
`ubelt.dict_subset <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.dict_subset>`__                                                46
`ubelt.Cacher <https://ubelt.readthedocs.io/en/latest/ubelt.util_cache.html#ubelt.util_cache.Cacher>`__                                                        44
`ubelt.indent <https://ubelt.readthedocs.io/en/latest/ubelt.util_str.html#ubelt.util_str.indent>`__                                                            44
`ubelt.argsort <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.argsort>`__                                                        43
`ubelt.IndexableWalker <https://ubelt.readthedocs.io/en/latest/ubelt.util_indexable.html#ubelt.util_indexable.IndexableWalker>`__                              41
`ubelt.writeto <https://ubelt.readthedocs.io/en/latest/ubelt.util_io.html#ubelt.util_io.writeto>`__                                                            41
`ubelt.iter_window <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.iter_window>`__                                                40
`ubelt.chunks <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.chunks>`__                                                          39
`ubelt.hash_file <https://ubelt.readthedocs.io/en/latest/ubelt.util_hash.html#ubelt.util_hash.hash_file>`__                                                    38
`ubelt.find_duplicates <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.find_duplicates>`__                                        38
`ubelt.map_keys <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.map_keys>`__                                                      36
`ubelt.symlink <https://ubelt.readthedocs.io/en/latest/ubelt.util_links.html#ubelt.util_links.symlink>`__                                                      34
`ubelt.sorted_vals <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.sorted_vals>`__                                                33
`ubelt.ensure_unicode <https://ubelt.readthedocs.io/en/latest/ubelt.util_str.html#ubelt.util_str.ensure_unicode>`__                                            32
`ubelt.find_exe <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.find_exe>`__                                              32
`ubelt.memoize_property <https://ubelt.readthedocs.io/en/latest/ubelt.util_memoize.html#ubelt.util_memoize.memoize_property>`__                                31
`ubelt.modname_to_modpath <https://ubelt.readthedocs.io/en/latest/ubelt.util_import.html#ubelt.util_import.modname_to_modpath>`__                              29
`ubelt.WIN32 <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.WIN32>`__                                                    28
`ubelt.CacheStamp <https://ubelt.readthedocs.io/en/latest/ubelt.util_cache.html#ubelt.util_cache.CacheStamp>`__                                                27
`ubelt.import_module_from_name <https://ubelt.readthedocs.io/en/latest/ubelt.util_import.html#ubelt.util_import.import_module_from_name>`__                    25
`ubelt.argmax <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.argmax>`__                                                          23
`ubelt.highlight_code <https://ubelt.readthedocs.io/en/latest/ubelt.util_colors.html#ubelt.util_colors.highlight_code>`__                                      23
`ubelt.varied_values <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.varied_values>`__                                            22
`ubelt.readfrom <https://ubelt.readthedocs.io/en/latest/ubelt.util_io.html#ubelt.util_io.readfrom>`__                                                          22
`ubelt.import_module_from_path <https://ubelt.readthedocs.io/en/latest/ubelt.util_import.html#ubelt.util_import.import_module_from_path>`__                    21
`ubelt.compatible <https://ubelt.readthedocs.io/en/latest/ubelt.util_func.html#ubelt.util_func.compatible>`__                                                  20
`ubelt.memoize_method <https://ubelt.readthedocs.io/en/latest/ubelt.util_memoize.html#ubelt.util_memoize.memoize_method>`__                                    20
`ubelt.sorted_keys <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.sorted_keys>`__                                                20
`ubelt.Executor <https://ubelt.readthedocs.io/en/latest/ubelt.util_futures.html#ubelt.util_futures.Executor>`__                                                19
`ubelt.touch <https://ubelt.readthedocs.io/en/latest/ubelt.util_io.html#ubelt.util_io.touch>`__                                                                17
`ubelt.get_app_cache_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.get_app_cache_dir>`__                            14
`ubelt.AutoDict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.AutoDict>`__                                                      13
`ubelt.inject_method <https://ubelt.readthedocs.io/en/latest/ubelt.util_func.html#ubelt.util_func.inject_method>`__                                            13
`ubelt.zopen <https://ubelt.readthedocs.io/en/latest/ubelt.util_zip.html#ubelt.util_zip.zopen>`__                                                              11
`ubelt.shrinkuser <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.shrinkuser>`__                                                  11
`ubelt.userhome <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.userhome>`__                                                       8
`ubelt.schedule_deprecation <https://ubelt.readthedocs.io/en/latest/ubelt.util_deprecate.html#ubelt.util_deprecate.schedule_deprecation>`__                     8
`ubelt.LINUX <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.LINUX>`__                                                     8
`ubelt.split_modpath <https://ubelt.readthedocs.io/en/latest/ubelt.util_import.html#ubelt.util_import.split_modpath>`__                                         7
`ubelt.modpath_to_modname <https://ubelt.readthedocs.io/en/latest/ubelt.util_import.html#ubelt.util_import.modpath_to_modname>`__                               7
`ubelt.CaptureStdout <https://ubelt.readthedocs.io/en/latest/ubelt.util_stream.html#ubelt.util_stream.CaptureStdout>`__                                         5
`ubelt.DARWIN <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.DARWIN>`__                                                   5
`ubelt.argmin <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.argmin>`__                                                           4
`ubelt.download <https://ubelt.readthedocs.io/en/latest/ubelt.util_download.html#ubelt.util_download.download>`__                                               3
`ubelt.find_path <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.find_path>`__                                             2
`ubelt.AutoOrderedDict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.AutoOrderedDict>`__                                         2
`ubelt.argunique <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.argunique>`__                                                     1
`ubelt.unique_flags <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.unique_flags>`__                                               1
`ubelt.udict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.udict>`__                                                             0
`ubelt.timeparse <https://ubelt.readthedocs.io/en/latest/ubelt.util_time.html#ubelt.util_time.timeparse>`__                                                     0
`ubelt.split_archive <https://ubelt.readthedocs.io/en/latest/ubelt.util_zip.html#ubelt.util_zip.split_archive>`__                                               0
`ubelt.sorted_values <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.sorted_values>`__                                             0
`ubelt.sdict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.sdict>`__                                                             0
`ubelt.platform_data_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.platform_data_dir>`__                             0
`ubelt.platform_config_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.platform_config_dir>`__                         0
`ubelt.platform_cache_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.platform_cache_dir>`__                           0
`ubelt.map_values <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.map_values>`__                                                   0
`ubelt.indexable_allclose <https://ubelt.readthedocs.io/en/latest/ubelt.util_indexable.html#ubelt.util_indexable.indexable_allclose>`__                         0
`ubelt.get_app_data_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.get_app_data_dir>`__                               0
`ubelt.get_app_config_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.get_app_config_dir>`__                           0
`ubelt.ensure_app_data_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.ensure_app_data_dir>`__                         0
`ubelt.ensure_app_config_dir <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.ensure_app_config_dir>`__                     0
`ubelt.boolmask <https://ubelt.readthedocs.io/en/latest/ubelt.util_list.html#ubelt.util_list.boolmask>`__                                                       0
`ubelt.UDict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.UDict>`__                                                             0
`ubelt.TempDir <https://ubelt.readthedocs.io/en/latest/ubelt.util_path.html#ubelt.util_path.TempDir>`__                                                         0
`ubelt.TeeStringIO <https://ubelt.readthedocs.io/en/latest/ubelt.util_stream.html#ubelt.util_stream.TeeStringIO>`__                                             0
`ubelt.SetDict <https://ubelt.readthedocs.io/en/latest/ubelt.util_dict.html#ubelt.util_dict.SetDict>`__                                                         0
`ubelt.POSIX <https://ubelt.readthedocs.io/en/latest/ubelt.util_platform.html#ubelt.util_platform.POSIX>`__                                                     0
`ubelt.OrderedSet <https://ubelt.readthedocs.io/en/latest/ubelt.orderedset.html#ubelt.orderedset.OrderedSet>`__                                                 0
`ubelt.NO_COLOR <https://ubelt.readthedocs.io/en/latest/ubelt.util_colors.html#ubelt.util_colors.NO_COLOR>`__                                                   0
`ubelt.FormatterExtensions <https://ubelt.readthedocs.io/en/latest/ubelt.util_format.html#ubelt.util_format.FormatterExtensions>`__                             0
`ubelt.DownloadManager <https://ubelt.readthedocs.io/en/latest/ubelt.util_download_manager.html#ubelt.util_download_manager.DownloadManager>`__                 0
`ubelt.CaptureStream <https://ubelt.readthedocs.io/en/latest/ubelt.util_stream.html#ubelt.util_stream.CaptureStream>`__                                         0
================================================================================================================================================ ================



Examples
========

The most up to date examples are the doctests. 
We also have a Jupyter notebook: https://github.com/Erotemic/ubelt/blob/main/docs/notebooks/Ubelt%20Demo.ipynb

Here are some examples of some features inside ``ubelt``

Paths
-----

Ubelt extends ``pathlib.Path`` by adding several new (often chainable) methods.
Namely, ``augment``, ``delete``, ``expand``, ``ensuredir``, ``shrinkuser``. It
also modifies behavior of ``touch`` to be chainable. (New in 1.0.0)


.. code:: python

        >>> # Ubelt extends pathlib functionality
        >>> import ubelt as ub
        >>> dpath = ub.Path('~/.cache/ubelt/demo_path').expand().ensuredir()
        >>> fpath = dpath / 'text_file.txt'
        >>> aug_fpath = fpath.augment(suffix='.aux', ext='.jpg').touch()
        >>> aug_dpath = dpath.augment('demo_path2')
        >>> assert aug_fpath.read_text() == ''
        >>> fpath.write_text('text data')
        >>> assert aug_fpath.exists()
        >>> assert not aug_fpath.delete().exists()
        >>> assert dpath.exists()
        >>> assert not dpath.delete().exists()
        >>> print(f'{fpath.shrinkuser()}')
        >>> print(f'{dpath.shrinkuser()}')
        >>> print(f'{aug_fpath.shrinkuser()}')
        >>> print(f'{aug_dpath.shrinkuser()}')
        ~/.cache/ubelt/demo_path/text_file.txt
        ~/.cache/ubelt/demo_path
        ~/.cache/ubelt/demo_path/text_file.aux.jpg
        ~/.cache/ubelt/demo_pathdemo_path2

Hashing
-------

The ``ub.hash_data`` constructs a hash for common Python nested data
structures. Extensions to allow it to hash custom types can be registered.  By
default it handles lists, dicts, sets, slices, uuids, and numpy arrays.

.. code:: python

    >>> import ubelt as ub
    >>> data = [('arg1', 5), ('lr', .01), ('augmenters', ['flip', 'translate'])]
    >>> ub.hash_data(data, hasher='sha256')
    0d95771ff684756d7be7895b5594b8f8484adecef03b46002f97ebeb1155fb15

Support for torch tensors and pandas data frames are also included, but needs to
be explicitly enabled.  There also exists an non-public plugin architecture to
extend this function to arbitrary types. While not officially supported, it is
usable and will become better integrated in the future. See
``ubelt/util_hash.py`` for details.

Caching
-------

Cache intermediate results from blocks of code inside a script with minimal
boilerplate or modification to the original code.  

For direct caching of data, use the ``Cacher`` class.  By default results will
be written to the ubelt's appdir cache, but the exact location can be specified
via ``dpath`` or the ``appname`` arguments.  Additionally, process dependencies
can be specified via the ``depends`` argument, which allows for implicit cache
invalidation.  As far as I can tell, this is the most concise way (4 lines of
boilerplate) to cache a block of code with existing Python syntax (as of
2022-06-03).

.. code:: python

    >>> import ubelt as ub
    >>> depends = ['config', {'of': 'params'}, 'that-uniquely-determine-the-process']
    >>> cacher = ub.Cacher('test_process', depends=depends, appname='myapp')
    >>> # start fresh
    >>> cacher.clear()
    >>> for _ in range(2):
    >>>     data = cacher.tryload()
    >>>     if data is None:
    >>>         myvar1 = 'result of expensive process'
    >>>         myvar2 = 'another result'
    >>>         data = myvar1, myvar2
    >>>         cacher.save(data)
    >>> myvar1, myvar2 = data

For indirect caching, use the ``CacheStamp`` class. This simply writes a
"stamp" file that marks that a process has completed. Additionally you can
specify criteria for when the stamp should expire. If you let ``CacheStamp``
know about the expected "product", it will expire the stamp if that file has
changed, which can be useful in situations where caches might becomes corrupt
or need invalidation.

.. code:: python

    >>> import ubelt as ub
    >>> dpath = ub.Path.appdir('ubelt/demo/cache').delete().ensuredir()
    >>> params = {'params1': 1, 'param2': 2}
    >>> expected_fpath = dpath / 'file.txt'
    >>> stamp = ub.CacheStamp('name', dpath=dpath, depends=params,
    >>>                      hasher='sha256', product=expected_fpath,
    >>>                      expires='2101-01-01T000000Z', verbose=3)
    >>> # Start fresh
    >>> stamp.clear()
    >>>     
    >>> for _ in range(2):
    >>>     if stamp.expired():
    >>>         expected_fpath.write_text('expensive process')
    >>>         stamp.renew()

See `<https://ubelt.readthedocs.io/en/latest/ubelt.util_cache.html>`_ for more
details about ``Cacher`` and ``CacheStamp``.

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


Command Line Interaction
------------------------

The builtin Python ``subprocess.Popen`` module is great, but it can be a
bit clunky at times. The ``os.system`` command is easy to use, but it
doesn't have much flexibility. The ``ub.cmd`` function aims to fix this.
It is as simple to run as ``os.system``, but it returns a dictionary
containing the return code, standard out, standard error, and the
``Popen`` object used under the hood.

This utility is designed to provide as consistent as possible behavior across
different platforms.  We aim to support Windows, Linux, and OSX. 

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
simultaneously capture the standard output and display it in real time (i.e. it
will "`tee <https://en.wikipedia.org/wiki/Tee_(command)>`__" the output).

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

The idea is that ``ub.cmd`` removes the need to think about if you need to pass
a list of args, or a string. Both will work. 

New in ``1.0.0``, a third variant with different consequences for executing
shell commands. Using the ``system=True`` kwarg will directly use ``os.system``
instead of ``Popen`` entirely. In this mode it is not possible to ``tee`` the
output because the program is executing directly in the foreground. This is
useful for doing things like spawning a vim session and returning if the user
manages to quit vim.

Downloading Files
-----------------

The function ``ub.download`` provides a simple interface to download a
URL and save its data to a file.

.. code:: python

    >>> import ubelt as ub
    >>> url = 'http://i.imgur.com/rqwaDag.png'
    >>> fpath = ub.download(url, verbose=0)
    >>> print(ub.shrinkuser(fpath))
    ~/.cache/ubelt/rqwaDag.png

The function ``ub.grabdata`` works similarly to ``ub.download``, but
whereas ``ub.download`` will always re-download the file,
``ub.grabdata`` will check if the file exists and only re-download it if
it needs to.

.. code:: python

    >>> import ubelt as ub
    >>> url = 'http://i.imgur.com/rqwaDag.png'
    >>> fpath = ub.grabdata(url, verbose=0, hash_prefix='944389a39')
    >>> print(ub.shrinkuser(fpath))
    ~/.cache/ubelt/rqwaDag.png


New in version 0.4.0: both functions now accepts the ``hash_prefix`` keyword
argument, which if specified will check that the hash of the file matches the
provided value. The ``hasher`` keyword argument can be used to change which
hashing algorithm is used (it defaults to ``"sha512"``).

Dictionary Set Operations
-------------------------


Dictionary operations that are analogous to set operations. 
See each funtions documentation for more details on the behavior of the values.
Typically the last seen value is given priority.

I hope Python decides to add these to the stdlib someday. 

* ``ubelt.dict_union`` corresponds to ``set.union``.
* ``ubelt.dict_isect`` corresponds to ``set.intersection``.
* ``ubelt.dict_diff`` corresponds to ``set.difference``.

.. code:: python 

   >>> d1 = {'a': 1, 'b': 2, 'c': 3}
   >>> d2 = {'c': 10, 'e': 20, 'f': 30}
   >>> d3 = {'e': 10, 'f': 20, 'g': 30, 'a': 40}
   >>> ub.dict_union(d1, d2, d3)
   {'a': 40, 'b': 2, 'c': 10, 'e': 10, 'f': 20, 'g': 30}

   >>> ub.dict_isect(d1, d2)
   {'c': 3}

   >>> ub.dict_diff(d1, d2)
   {'a': 1, 'b': 2}


New in Version 1.2.0: Ubelt now contains a dictionary subclass with set
operations that can be invoked as ``ubelt.SetDict`` or ``ub.sdict``. 
Note that n-ary operations are supported.


.. code:: python 

   >>> d1 = ub.sdict({'a': 1, 'b': 2, 'c': 3})
   >>> d2 = {'c': 10, 'e': 20, 'f': 30}
   >>> d3 = {'e': 10, 'f': 20, 'g': 30, 'a': 40}
   >>> d1 | d2 | d3
   {'a': 40, 'b': 2, 'c': 10, 'e': 10, 'f': 20, 'g': 30}

   >>> d1 & d2
   {'c': 3}

   >>> d1 - d2
   {'a': 1, 'b': 2}

   >>> ub.sdict.intersection({'a': 1, 'b': 2, 'c': 3}, ['b', 'c'], ['c', 'e'])
   {'c': 3}


Note this functionality and more is available in ``ubelt.UDict`` or ``ub.udict``.

Grouping Items
--------------

Given a list of items and corresponding ids, create a dictionary mapping each
id to a list of its corresponding items.  In other words, group a sequence of
items of type ``VT`` and corresponding keys of type ``KT`` given by a function
or corresponding list, group them into a ``Dict[KT, List[VT]`` such that each
key maps to a list of the values associated with the key.  This is similar to
`pandas.DataFrame.groupby <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html>`_.

Group ids can be specified by a second list containing the id for
each corresponding item. 

.. code:: python

    >>> import ubelt as ub
    >>> # Group via a corresonding list
    >>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
    >>> groupid_list = ['protein', 'fruit', 'protein',  'protein', 'dairy',  'fruit']
    >>> dict(ub.group_items(item_list, groupid_list))
    {'dairy': ['cheese'], 'fruit': ['jam', 'bannana'], 'protein': ['ham', 'spam', 'eggs']}


They can also be given by a function that is executed on each item in the list


.. code:: python

    >>> import ubelt as ub
    >>> # Group via a function
    >>> item_list    = ['ham',     'jam',   'spam',     'eggs',    'cheese', 'bannana']
    >>> def grouper(item):
    ...     return item.count('a')
    >>> dict(ub.group_items(item_list, grouper))
    {1: ['ham', 'jam', 'spam'], 0: ['eggs', 'cheese'], 3: ['bannana']}

Dictionary Histogram
--------------------

Find the frequency of items in a sequence. 
Given a list or sequence of items, this returns a dictionary mapping each
unique value in the sequence to the number of times it appeared.
This is similar to `pandas.DataFrame.value_counts <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.value_counts.html>`_.

.. code:: python

    >>> import ubelt as ub
    >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
    >>> ub.dict_hist(item_list)
    {1232: 2, 1: 1, 2: 4, 900: 3, 39: 1}
    

Each item can also be given a weight

.. code:: python

    >>> import ubelt as ub
    >>> item_list = [1, 2, 39, 900, 1232, 900, 1232, 2, 2, 2, 900]
    >>> weights   = [1, 1,  0,   0,    0,   0,  0.5, 0, 1, 1, 0.3]
    >>> ub.dict_hist(item_list, weights=weights)
    {1: 1, 2: 3, 39: 0, 900: 0.3, 1232: 0.5}

Dictionary Manipulation
-----------------------

Map functions across dictionarys to transform the keys or values in a
dictionary.  The ``ubelt.map_keys`` function applies a function to each key in
a dictionary and returns this transformed copy of the dictionary. Key conflict
behavior currently raises and error, but may be configurable in the future. The
``ubelt.map_vals`` function is the same except the function is applied to each
value instead.  I these functions are useful enough to be ported to Python
itself.

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {'a': [1, 2, 3], 'bb': [], 'ccc': [2,]}
    >>> dict_keymod = ub.map_keys(len, dict_)
    >>> dict_valmod = ub.map_vals(len, dict_)
    >>> print(dict_keymod)
    >>> print(dict_valmod)
    {1: [1, 2, 3], 2: [], 3: [2]}
    {'a': 3, 'bb': 0, 'ccc': 1}

Take a subset of a dictionary. Note this is similar to ``ub.dict_isect``,
except this will raise an error if the given keys are not in the dictionary.

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {'K': 3, 'dcvs_clip_max': 0.2, 'p': 0.1}
    >>> subdict_ = ub.dict_subset(dict_, ['K', 'dcvs_clip_max'])
    >>> print(subdict_)
    {'K': 3, 'dcvs_clip_max': 0.2}


The ``ubelt.take`` function works on dictionarys (and lists). It is similar to
``ubelt.dict_subset``, except that it returns just a list of the values, and
discards information about the keys. It is also possible to specify a default
value.

.. code:: python

    >>> import ubelt as ub
    >>> dict_ = {1: 'a', 2: 'b', 3: 'c'}
    >>> print(list(ub.take(dict_, [1, 3, 4, 5], default=None)))
    ['a', 'c', None, None]

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


New in Version 1.2.0: Ubelt now contains a dictionary subclass ``ubelt.UDict``
with these quality of life operations (and also inherits from
``ubelt.SetDict``). The alias ``ubelt.udict`` can be used for quicker access.

.. code:: python 

   >>> import ubelt as ub
   >>> d1 = ub.udict({'a': 1, 'b': 2, 'c': 3})
   >>> d1 & {'a', 'c'}
   {'a': 1, 'c': 3}

   >>> d1.map_keys(ord)
   {97: 1, 98: 2, 99: 3}
   >>> d1.invert()
   {1: 'a', 2: 'b', 3: 'c'}
   >>> d1.subdict(['b', 'c', 'e'], default=None)
   {'b': 2, 'c': 3, 'e': None}
   >>> d1.sorted_keys()
   OrderedDict([('a', 1), ('b', 2), ('c', 3)])
   >>> d1.peek_key()
   'a'
   >>> d1.peek_value()
   1

Next time you have a default configuration dictionary like and you allow the
developer to pass keyword arguments to modify these behaviors, consider using
dictionary intersection (&) to separate out only the relevant parts and
dictionary union (|) to update those relevant parts.  You can also use
dictionary differences (-) if you need to check for unused arguments.

.. code:: python 

    import ubelt as ub
    
    def run_multiple_algos(**kwargs):
        algo1_defaults = {'opt1': 10, 'opt2': 11}
        algo2_defaults = {'src': './here/', 'dst': './there'}
    
        kwargs = ub.udict(kwargs)
    
        algo1_specified = kwargs & algo1_defaults
        algo2_specified = kwargs & algo2_defaults
    
        algo1_config = algo1_defaults | algo1_specified
        algo2_config = algo2_defaults | algo2_specified
    
        unused_kwargs = kwargs - (algo1_defaults | algo2_defaults)
    
        print('algo1_specified = {}'.format(ub.repr2(algo1_specified, nl=1)))
        print('algo2_specified = {}'.format(ub.repr2(algo2_specified, nl=1)))
        print(f'algo1_config={algo1_config}')
        print(f'algo2_config={algo2_config}')
        print(f'The following kwargs were unused {unused_kwargs}')
    
    print(chr(10))
    print('-- Run with some specified --')
    run_multiple_algos(src='box', opt2='fox')
    print(chr(10))
    print('-- Run with extra unspecified --')
    run_multiple_algos(a=1, b=2)


Produces: 

.. code:: 

    -- Run with some specified --
    algo1_specified = {
        'opt2': 'fox',
    }
    algo2_specified = {
        'src': 'box',
    }
    algo1_config={'opt1': 10, 'opt2': 'fox'}
    algo2_config={'src': 'box', 'dst': './there'}
    The following kwargs were unused {}


    -- Run with extra unspecified --
    algo1_specified = {}
    algo2_specified = {}
    algo1_config={'opt1': 10, 'opt2': 11}
    algo2_config={'src': './here/', 'dst': './there'}
    The following kwargs were unused {'a': 1, 'b': 2}
        


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


Cross-Platform Config and Cache Directories
-------------------------------------------

If you have an application which writes configuration or cache files,
the standard place to dump those files differs depending if you are on
Windows, Linux, or Mac. Ubelt offers a unified functions for determining
what these paths are.

The ``ub.ensure_app_cache_dir`` and ``ub.ensure_app_config_dir``
functions find the correct platform-specific location for these files
and ensures that the directories exist. (Note: replacing "ensure" with
"get" will simply return the path, but not ensure that it exists)

The config root directory is ``~/AppData/Roaming`` on Windows,
``~/.config`` on Linux and ``~/Library/Application Support`` on Mac. The
cache root directory is ``~/AppData/Local`` on Windows, ``~/.config`` on
Linux and ``~/Library/Caches`` on Mac.

Example usage on Linux might look like this:

.. code:: python

    >>> import ubelt as ub
    >>> print(ub.shrinkuser(ub.ensure_app_cache_dir('my_app')))
    ~/.cache/my_app
    >>> print(ub.shrinkuser(ub.ensure_app_config_dir('my_app')))
    ~/.config/my_app

New in version 1.0.0: the ``ub.Path.appdir`` classmethod provides a way to
achieve the above with a chainable object oriented interface.

.. code:: python

    >>> import ubelt as ub
    >>> print(ub.Path.appdir('my_app').ensuredir().shrinkuser())
    ~/.cache/my_app
    >>> print(ub.Path.appdir('my_app', type='config').ensuredir().shrinkuser())
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
    >>> try:
    >>>     # This is where I keep ubelt on my machine, so it is not expected to work elsewhere.
    >>>     module = ub.import_module_from_path(ub.expandpath('~/code/ubelt/ubelt'))
    >>>     print('module = {!r}'.format(module))
    >>> except OSError:
    >>>     pass
    >>>         
    >>> module = ub.import_module_from_name('ubelt')
    >>> print('module = {!r}'.format(module))
    >>> #
    >>> try:
    >>>     module = ub.import_module_from_name('does-not-exist')
    >>>     raise AssertionError
    >>> except ModuleNotFoundError:
    >>>     pass
    >>> #
    >>> modpath = ub.Path(ub.util_import.__file__)
    >>> print(ub.modpath_to_modname(modpath))
    >>> modname = ub.util_import.__name__
    >>> assert ub.Path(ub.modname_to_modpath(modname)).resolve() == modpath.resolve()

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
    >>> assert ub.modname_to_modpath(modname) == modpath

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


External tools
--------------

Some of the tools in ``ubelt`` also exist as standalone modules. I haven't
decided if its best to statically copy them into ubelt or require on pypi to
satisfy the dependency. There are some tools that are not used by default 
unless you explicitly allow for them. 

Code that is currently statically included (vendored):

-  ProgIter - https://github.com/Erotemic/progiter
-  OrderedSet - https://github.com/LuminosoInsight/ordered-set

Code that is completely optional, and only used in specific cases:

- Numpy - ``ub.repr2`` will format a numpy array nicely by default
- xxhash - this can be specified as a hasher to ``ub.hash_data``
- Pygments - used by the ``util_color`` module.
- dateutil - used by the ``util_time`` module.


Similar Tools
-------------

UBelt is one of many Python utility libraries. A selection of similar libraries
are listed here.

Libraries that contain a broad scope of utilities:

* Boltons: https://github.com/mahmoud/boltons
* Toolz: https://github.com/pytoolz/toolz
* CyToolz: https://github.com/pytoolz/cytoolz/

Libraries that contain a specific scope of utilities:

* More-Itertools: iteration tools: https://pypi.org/project/more-itertools/
* Funcy: functional tools: https://github.com/Suor/funcy
* Rich: pretty CLI displays - https://github.com/willmcgugan/rich
* tempora: time related tools - https://github.com/jaraco/tempora


Libraries that contain one specific data structure or utility:

* Benedict: dictionary tools - https://pypi.org/project/python-benedict/
* tqdm: progress bars - https://pypi.org/project/tqdm/
* pooch: data downloading - https://pypi.org/project/pooch/
* timerit: snippet timing for benchmarks - https://github.com/Erotemic/timerit


Ubelt is included in the the [bestof-python list](https://github.com/ml-tooling/best-of-python), 
which contains many other tools that you should check out.


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

Development on ubelt started 2017-01-30 and development of utool mostly stopped
on utool was stopped later that year, but received patches until about 2020.
Ubelt achieved 1.0.0 and removed support for Python 2.7 and 3.5 on 2022-01-07.


Notes.
------
PRs are welcome. 

Also check out my other projects which are powered by ubelt:

-  xinspect https://github.com/Erotemic/xinspect
-  xdev https://github.com/Erotemic/xdev
-  vimtk https://github.com/Erotemic/vimtk
-  graphid https://github.com/Erotemic/graphid
-  ibeis https://github.com/Erotemic/ibeis
-  kwarray https://github.com/Kitware/kwarray
-  kwimage https://github.com/Kitware/kwimage
-  kwcoco https://github.com/Kitware/kwcoco

And my projects related to ubelt:

-  ProgIter https://github.com/Erotemic/progiter
-  Timerit https://github.com/Erotemic/timerit
-  mkinit https://github.com/Erotemic/mkinit
-  xdoctest https://github.com/Erotemic/xdoctest

  

.. |CircleCI| image:: https://circleci.com/gh/Erotemic/ubelt.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/ubelt
.. |Travis| image:: https://img.shields.io/travis/Erotemic/ubelt/main.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/ubelt?branch=main
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Erotemic/ubelt?branch=main&svg=True
   :target: https://ci.appveyor.com/project/Erotemic/ubelt/branch/main
.. |Codecov| image:: https://codecov.io/github/Erotemic/ubelt/badge.svg?branch=main&service=github
   :target: https://codecov.io/github/Erotemic/ubelt?branch=main
.. |Pypi| image:: https://img.shields.io/pypi/v/ubelt.svg
   :target: https://pypi.python.org/pypi/ubelt
.. |Downloads| image:: https://img.shields.io/pypi/dm/ubelt.svg
   :target: https://pypistats.org/packages/ubelt
.. |ReadTheDocs| image:: https://readthedocs.org/projects/ubelt/badge/?version=latest
    :target: http://ubelt.readthedocs.io/en/latest/
.. |CodeQuality| image:: https://api.codacy.com/project/badge/Grade/4d815305fc014202ba7dea09c4676343   
    :target: https://www.codacy.com/manual/Erotemic/ubelt?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Erotemic/ubelt&amp;utm_campaign=Badge_Grade
.. |GithubActions| image:: https://github.com/Erotemic/ubelt/actions/workflows/tests.yml/badge.svg?branch=main
    :target: https://github.com/Erotemic/ubelt/actions?query=branch%3Amain
.. |TwitterFollow| image:: https://img.shields.io/twitter/follow/Erotemic.svg?style=social
    :target: https://twitter.com/Erotemic
