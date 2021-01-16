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
:func:`ubelt.repr2`                                                          2140
:func:`ubelt.ProgIter`                                                        715
:func:`ubelt.expandpath`                                                      695
:func:`ubelt.ensuredir`                                                       553
:func:`ubelt.take`                                                            430
:func:`ubelt.odict`                                                           391
:func:`ubelt.map_vals`                                                        331
:func:`ubelt.dzip`                                                            278
:func:`ubelt.NiceRepr`                                                        261
:func:`ubelt.ddict`                                                           255
:func:`ubelt.augpath`                                                         229
:func:`ubelt.argflag`                                                         209
:func:`ubelt.flatten`                                                         202
:func:`ubelt.argval`                                                          200
:func:`ubelt.cmd`                                                             199
:func:`ubelt.peek`                                                            196
:func:`ubelt.NoParam`                                                         189
:func:`ubelt.Timerit`                                                         187
:func:`ubelt.dict_hist`                                                       173
:func:`ubelt.codeblock`                                                       172
:func:`ubelt.group_items`                                                     168
:func:`ubelt.iterable`                                                        168
:func:`ubelt.hash_data`                                                       142
:func:`ubelt.grabdata`                                                        127
:func:`ubelt.color_text`                                                       97
:func:`ubelt.delete`                                                           94
:func:`ubelt.dict_subset`                                                      89
:func:`ubelt.oset`                                                             88
:func:`ubelt.compress`                                                         87
:func:`ubelt.allsame`                                                          86
:func:`ubelt.Cacher`                                                           81
:func:`ubelt.Timer`                                                            70
:func:`ubelt.dict_isect`                                                       68
:func:`ubelt.indent`                                                           60
:func:`ubelt.argsort`                                                          59
:func:`ubelt.chunks`                                                           48
:func:`ubelt.map_keys`                                                         48
:func:`ubelt.invert_dict`                                                      47
:func:`ubelt.dict_union`                                                       47
:func:`ubelt.memoize`                                                          46
:func:`ubelt.timestamp`                                                        46
:func:`ubelt.find_duplicates`                                                  45
:func:`ubelt.unique`                                                           43
:func:`ubelt.import_module_from_path`                                          40
:func:`ubelt.sorted_vals`                                                      39
:func:`ubelt.dict_diff`                                                        38
:func:`ubelt.hzcat`                                                            38
:func:`ubelt.argmax`                                                           37
:func:`ubelt.memoize_property`                                                 37
:func:`ubelt.writeto`                                                          37
:func:`ubelt.iter_window`                                                      35
:func:`ubelt.readfrom`                                                         34
:func:`ubelt.paragraph`                                                        33
:func:`ubelt.identity`                                                         33
:func:`ubelt.symlink`                                                          32
:func:`ubelt.memoize_method`                                                   31
:func:`ubelt.ensure_unicode`                                                   24
:func:`ubelt.touch`                                                            24
:func:`ubelt.hash_file`                                                        24
:func:`ubelt.CacheStamp`                                                       20
:func:`ubelt.modname_to_modpath`                                               17
:func:`ubelt.highlight_code`                                                   17
:func:`ubelt.import_module_from_name`                                          16
:func:`ubelt.find_exe`                                                         14
:func:`ubelt.inject_method`                                                    13
:func:`ubelt.shrinkuser`                                                       11
:func:`ubelt.AutoDict`                                                          9
:func:`ubelt.argmin`                                                            9
:func:`ubelt.find_path`                                                         7
:func:`ubelt.download`                                                          5
:func:`ubelt.sorted_keys`                                                       5
:func:`ubelt.CaptureStdout`                                                     4
:func:`ubelt.split_modpath`                                                     4
:func:`ubelt.modpath_to_modname`                                                4
:func:`ubelt.orderedset`                                                        4
:func:`ubelt.userhome`                                                          3
:func:`ubelt.argunique`                                                         3
:func:`ubelt.AutoOrderedDict`                                                   2
:func:`ubelt.unique_flags`                                                      2
:func:`ubelt.boolmask`                                                          1
================================================================ ================

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
:func:`ubelt.PY2`
:func:`ubelt.string_types`
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
:func:`ubelt.PY2`
:func:`ubelt.iteritems`
:func:`ubelt.string_types`
:func:`ubelt.text_type`
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
:func:`ubelt.PY2`
:func:`ubelt.symlink`

:mod:`ubelt.util_list`
-------------
:func:`ubelt.PY2`
:func:`ubelt.string_types`
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
:func:`ubelt.PY2`
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
:func:`ubelt.PY2`
:func:`ubelt.string_types`
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
:func:`ubelt.PY2`
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
