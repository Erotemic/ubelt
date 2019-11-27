.. UBelt documentation master file, created by
   sphinx-quickstart on Sun Apr  8 19:53:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:github_url: https://github.com/Erotemic/ubelt


.. The large version wont work because github strips rst image rescaling. https://i.imgur.com/AcWVroL.png
.. image:: https://i.imgur.com/PoYIsWE.png
   :height: 100px
   :align: left


UBelt documentation
===================


.. The __init__ files contains the top-level documentation overview
.. automodule:: ubelt.__init__
   :show-inheritance:

.. commented out
.. :members:
.. :undoc-members:


The API by usefulness 
=====================

Perhaps the most useful way to learn this API is to sort by "usefulness".
I measure usefulness as the number of times I've used a particular function in
my own code (excluding ubelt itself).


================================================================ ================
 Function name                                                   Usefulness
================================================================ ================
:func:`ubelt.repr2`                                                          1051
:func:`ubelt.take`                                                            180
:func:`ubelt.dzip`                                                            177
:func:`ubelt.odict`                                                           167
:func:`ubelt.argval`                                                          130
:func:`ubelt.ProgIter`                                                        128
:func:`ubelt.flatten`                                                         123
:func:`ubelt.NoParam`                                                         103
:func:`ubelt.Timerit`                                                         100
:func:`ubelt.NiceRepr`                                                         95
:func:`ubelt.hzcat`                                                            94
:func:`ubelt.argflag`                                                          89
:func:`ubelt.iterable`                                                         87
:func:`ubelt.cmd`                                                              82
:func:`ubelt.codeblock`                                                        82
:func:`ubelt.ensuredir`                                                        80
:func:`ubelt.map_vals`                                                         76
:func:`ubelt.ddict`                                                            73
:func:`ubelt.expandpath`                                                       72
:func:`ubelt.grabdata`                                                         70
:func:`ubelt.compress`                                                         56
:func:`ubelt.group_items`                                                      56
:func:`ubelt.hash_data`                                                        50
:func:`ubelt.color_text`                                                       50
:func:`ubelt.delete`                                                           42
:func:`ubelt.writeto`                                                          38
:func:`ubelt.invert_dict`                                                      37
:func:`ubelt.chunks`                                                           36
:func:`ubelt.allsame`                                                          36
:func:`ubelt.dict_hist`                                                        32
:func:`ubelt.Timer`                                                            31
:func:`ubelt.indent`                                                           30
:func:`ubelt.argsort`                                                          29
:func:`ubelt.Cacher`                                                           26
:func:`ubelt.identity`                                                         23
:func:`ubelt.peek`                                                             23
:func:`ubelt.ensure_unicode`                                                   22
:func:`ubelt.iter_window`                                                      20
:func:`ubelt.map_keys`                                                         19
:func:`ubelt.readfrom`                                                         19
:func:`ubelt.oset`                                                             18
:func:`ubelt.timestamp`                                                        18
:func:`ubelt.find_duplicates`                                                  18
:func:`ubelt.modname_to_modpath`                                               16
:func:`ubelt.unique`                                                           15
:func:`ubelt.memoize_property`                                                 14
:func:`ubelt.memoize`                                                          13
:func:`ubelt.touch`                                                            12
:func:`ubelt.highlight_code`                                                   12
:func:`ubelt.find_exe`                                                         10
:func:`ubelt.argmax`                                                           10
:func:`ubelt.inject_method`                                                     8
:func:`ubelt.memoize_method`                                                    8
:func:`ubelt.dict_subset`                                                       7
:func:`ubelt.augpath`                                                           6
:func:`ubelt.import_module_from_path`                                           6
:func:`ubelt.hash_file`                                                         6
:func:`ubelt.symlink`                                                           6
:func:`ubelt.dict_union`                                                        5
:func:`ubelt.split_modpath`                                                     5
:func:`ubelt.CaptureStdout`                                                     4
:func:`ubelt.dict_diff`                                                         4
:func:`ubelt.shrinkuser`                                                        4
:func:`ubelt.argmin`                                                            3
:func:`ubelt.modpath_to_modname`                                                3
:func:`ubelt.import_module_from_name`                                           3
:func:`ubelt.paragraph`                                                         3
:func:`ubelt.CacheStamp`                                                        3
:func:`ubelt.AutoDict`                                                          2
:func:`ubelt.AutoOrderedDict`                                                   2
:func:`ubelt.unique_flags`                                                      2
:func:`ubelt.dict_isect`                                                        2
:func:`ubelt.find_path`                                                         2
:func:`ubelt.download`                                                          1
================================================================ ================


The API by submodule 
====================

Alternatively you might prefer a module-based approach where functions are
grouped based on similar functionality.


:mod:`ubelt.orderedset`
-------------
:func:`ubelt.OrderedSet`
:func:`ubelt.oset`

:mod:`ubelt.progiter`
-------------
:func:`ubelt.ProgIter`

:mod:`ubelt.util_arg`
-------------
:func:`ubelt.argval`
:func:`ubelt.argflag`

:mod:`ubelt.util_cache`
-------------
:func:`ubelt.Cacher`
:func:`ubelt.CacheStamp`

:mod:`ubelt.util_cmd`
-------------
:func:`ubelt.cmd`

:mod:`ubelt.util_colors`
-------------
:func:`ubelt.highlight_code`
:func:`ubelt.color_text`

:mod:`ubelt.util_const`
-------------
:func:`ubelt.NoParam`

:mod:`ubelt.util_dict`
-------------
:func:`ubelt.AutoDict`
:func:`ubelt.AutoOrderedDict`
:func:`ubelt.dzip`
:func:`ubelt.ddict`
:func:`ubelt.dict_hist`
:func:`ubelt.dict_subset`
:func:`ubelt.dict_union`
:func:`ubelt.dict_isect`
:func:`ubelt.dict_diff`
:func:`ubelt.find_duplicates`
:func:`ubelt.group_items`
:func:`ubelt.invert_dict`
:func:`ubelt.map_keys`
:func:`ubelt.map_vals`
:func:`ubelt.odict`

:mod:`ubelt.util_download`
-------------
:func:`ubelt.download`
:func:`ubelt.grabdata`

:mod:`ubelt.util_format`
-------------
:func:`ubelt.repr2`
:func:`ubelt.FormatterExtensions`

:mod:`ubelt.util_func`
-------------
:func:`ubelt.identity`
:func:`ubelt.inject_method`

:mod:`ubelt.util_hash`
-------------
:func:`ubelt.hash_data`
:func:`ubelt.hash_file`

:mod:`ubelt.util_import`
-------------
:func:`ubelt.split_modpath`
:func:`ubelt.modname_to_modpath`
:func:`ubelt.modpath_to_modname`
:func:`ubelt.import_module_from_name`
:func:`ubelt.import_module_from_path`

:mod:`ubelt.util_io`
-------------
:func:`ubelt.readfrom`
:func:`ubelt.writeto`
:func:`ubelt.touch`
:func:`ubelt.delete`

:mod:`ubelt.util_links`
-------------
:func:`ubelt.symlink`

:mod:`ubelt.util_list`
-------------
:func:`ubelt.chunks`
:func:`ubelt.iterable`
:func:`ubelt.take`
:func:`ubelt.compress`
:func:`ubelt.flatten`
:func:`ubelt.unique`
:func:`ubelt.argunique`
:func:`ubelt.unique_flags`
:func:`ubelt.boolmask`
:func:`ubelt.iter_window`
:func:`ubelt.allsame`
:func:`ubelt.argsort`
:func:`ubelt.argmax`
:func:`ubelt.argmin`
:func:`ubelt.peek`

:mod:`ubelt.util_memoize`
-------------
:func:`ubelt.memoize`
:func:`ubelt.memoize_method`
:func:`ubelt.memoize_property`

:mod:`ubelt.util_mixins`
-------------
:func:`ubelt.NiceRepr`

:mod:`ubelt.util_path`
-------------
:func:`ubelt.TempDir`
:func:`ubelt.augpath`
:func:`ubelt.shrinkuser`
:func:`ubelt.userhome`
:func:`ubelt.ensuredir`
:func:`ubelt.expandpath`

:mod:`ubelt.util_platform`
-------------
:func:`ubelt.WIN32`
:func:`ubelt.LINUX`
:func:`ubelt.DARWIN`
:func:`ubelt.POSIX`
:func:`ubelt.platform_data_dir`
:func:`ubelt.platform_config_dir`
:func:`ubelt.platform_cache_dir`
:func:`ubelt.get_app_data_dir`
:func:`ubelt.ensure_app_data_dir`
:func:`ubelt.get_app_config_dir`
:func:`ubelt.ensure_app_config_dir`
:func:`ubelt.get_app_cache_dir`
:func:`ubelt.ensure_app_cache_dir`
:func:`ubelt.find_exe`
:func:`ubelt.find_path`

:mod:`ubelt.util_str`
-------------
:func:`ubelt.indent`
:func:`ubelt.codeblock`
:func:`ubelt.paragraph`
:func:`ubelt.hzcat`
:func:`ubelt.ensure_unicode`

:mod:`ubelt.util_stream`
-------------
:func:`ubelt.TeeStringIO`
:func:`ubelt.CaptureStream`
:func:`ubelt.CaptureStdout`

:mod:`ubelt.util_time`
-------------
:func:`ubelt.Timer`
:func:`ubelt.Timerit`
:func:`ubelt.timestamp`



.. toctree::
   :maxdepth: 8
   :caption: Package Layout

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
