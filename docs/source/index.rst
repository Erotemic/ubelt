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
:func:`ubelt.repr2`                                                          1598
:func:`ubelt.ProgIter`                                                        610
:func:`ubelt.expandpath`                                                      610
:func:`ubelt.ensuredir`                                                       482
:func:`ubelt.take`                                                            337
:func:`ubelt.odict`                                                           311
:func:`ubelt.map_vals`                                                        272
:func:`ubelt.dzip`                                                            246
:func:`ubelt.augpath`                                                         209
:func:`ubelt.NiceRepr`                                                        197
:func:`ubelt.ddict`                                                           191
:func:`ubelt.argval`                                                          184
:func:`ubelt.cmd`                                                             176
:func:`ubelt.argflag`                                                         171
:func:`ubelt.flatten`                                                         168
:func:`ubelt.codeblock`                                                       159
:func:`ubelt.Timerit`                                                         158
:func:`ubelt.NoParam`                                                         149
:func:`ubelt.dict_hist`                                                       146
:func:`ubelt.group_items`                                                     138
:func:`ubelt.peek`                                                            134
:func:`ubelt.iterable`                                                        124
:func:`ubelt.hash_data`                                                       116
:func:`ubelt.grabdata`                                                         93
:func:`ubelt.delete`                                                           82
:func:`ubelt.compress`                                                         76
:func:`ubelt.color_text`                                                       76
:func:`ubelt.dict_subset`                                                      72
:func:`ubelt.Cacher`                                                           68
:func:`ubelt.allsame`                                                          66
:func:`ubelt.Timer`                                                            57
:func:`ubelt.argsort`                                                          53
:func:`ubelt.oset`                                                             51
:func:`ubelt.invert_dict`                                                      50
:func:`ubelt.indent`                                                           47
:func:`ubelt.chunks`                                                           45
:func:`ubelt.memoize`                                                          44
:func:`ubelt.dict_isect`                                                       42
:func:`ubelt.timestamp`                                                        40
:func:`ubelt.import_module_from_path`                                          39
:func:`ubelt.unique`                                                           36
:func:`ubelt.map_keys`                                                         35
:func:`ubelt.hzcat`                                                            35
:func:`ubelt.find_duplicates`                                                  35
:func:`ubelt.writeto`                                                          35
:func:`ubelt.dict_union`                                                       34
:func:`ubelt.ensure_unicode`                                                   30
:func:`ubelt.readfrom`                                                         30
:func:`ubelt.iter_window`                                                      29
:func:`ubelt.sorted_vals`                                                      29
:func:`ubelt.argmax`                                                           26
:func:`ubelt.memoize_property`                                                 26
:func:`ubelt.modname_to_modpath`                                               25
:func:`ubelt.symlink`                                                          25
:func:`ubelt.memoize_method`                                                   23
:func:`ubelt.dict_diff`                                                        23
:func:`ubelt.identity`                                                         22
:func:`ubelt.hash_file`                                                        21
:func:`ubelt.touch`                                                            19
:func:`ubelt.import_module_from_name`                                          17
:func:`ubelt.highlight_code`                                                   16
:func:`ubelt.find_exe`                                                         15
:func:`ubelt.CacheStamp`                                                       13
:func:`ubelt.find_path`                                                         9
:func:`ubelt.AutoDict`                                                          8
:func:`ubelt.split_modpath`                                                     7
:func:`ubelt.shrinkuser`                                                        7
:func:`ubelt.argmin`                                                            6
:func:`ubelt.inject_method`                                                     6
:func:`ubelt.download`                                                          5
:func:`ubelt.modpath_to_modname`                                                5
:func:`ubelt.paragraph`                                                         5
:func:`ubelt.CaptureStdout`                                                     4
:func:`ubelt.sorted_keys`                                                       3
:func:`ubelt.userhome`                                                          2
:func:`ubelt.AutoOrderedDict`                                                   2
:func:`ubelt.argunique`                                                         2
:func:`ubelt.unique_flags`                                                      2
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

:mod:`ubelt.timerit`
-------------
:func:`ubelt.Timer`
:func:`ubelt.Timerit`

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
:func:`ubelt.NO_COLOR`
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
:func:`ubelt.sorted_keys`
:func:`ubelt.sorted_vals`
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
:func:`ubelt.timestamp`


.. toctree::
   :maxdepth: 8
   :caption: Package Layout

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
