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


====================================================================================== ================
 Function name                                                                               Usefulness
====================================================================================== ================
:func:`ubelt.repr2<ubelt.util_format.repr2>`                                                       2001
:func:`ubelt.expandpath<ubelt.util_path.expandpath>`                                                728
:func:`ubelt.ProgIter<ubelt.progiter.ProgIter>`                                                     694
:func:`ubelt.ensuredir<ubelt.util_path.ensuredir>`                                                  539
:func:`ubelt.take<ubelt.util_list.take>`                                                            383
:func:`ubelt.odict<ubelt.util_dict.odict>`                                                          338
:func:`ubelt.map_vals<ubelt.util_dict.map_vals>`                                                    305
:func:`ubelt.dzip<ubelt.util_dict.dzip>`                                                            272
:func:`ubelt.augpath<ubelt.util_path.augpath>`                                                      250
:func:`ubelt.ddict<ubelt.util_dict.ddict>`                                                          227
:func:`ubelt.NiceRepr<ubelt.util_mixins.NiceRepr>`                                                  220
:func:`ubelt.cmd<ubelt.util_cmd.cmd>`                                                               209
:func:`ubelt.flatten<ubelt.util_list.flatten>`                                                      206
:func:`ubelt.peek<ubelt.util_list.peek>`                                                            189
:func:`ubelt.NoParam<ubelt.util_const.NoParam>`                                                     184
:func:`ubelt.argval<ubelt.util_arg.argval>`                                                         179
:func:`ubelt.group_items<ubelt.util_dict.group_items>`                                              173
:func:`ubelt.argflag<ubelt.util_arg.argflag>`                                                       173
:func:`ubelt.codeblock<ubelt.util_str.codeblock>`                                                   171
:func:`ubelt.Timerit<ubelt.timerit.Timerit>`                                                        164
:func:`ubelt.dict_hist<ubelt.util_dict.dict_hist>`                                                  161
:func:`ubelt.iterable<ubelt.util_list.iterable>`                                                    144
:func:`ubelt.hash_data<ubelt.util_hash.hash_data>`                                                  124
:func:`ubelt.grabdata<ubelt.util_download.grabdata>`                                                106
:func:`ubelt.oset<ubelt.orderedset.oset>`                                                           103
:func:`ubelt.paragraph<ubelt.util_str.paragraph>`                                                   100
:func:`ubelt.delete<ubelt.util_io.delete>`                                                           97
:func:`ubelt.allsame<ubelt.util_list.allsame>`                                                       90
:func:`ubelt.compress<ubelt.util_list.compress>`                                                     87
:func:`ubelt.color_text<ubelt.util_colors.color_text>`                                               84
:func:`ubelt.dict_subset<ubelt.util_dict.dict_subset>`                                               76
:func:`ubelt.dict_isect<ubelt.util_dict.dict_isect>`                                                 75
:func:`ubelt.Cacher<ubelt.util_cache.Cacher>`                                                        70
:func:`ubelt.dict_diff<ubelt.util_dict.dict_diff>`                                                   65
:func:`ubelt.memoize<ubelt.util_memoize.memoize>`                                                    54
:func:`ubelt.indent<ubelt.util_str.indent>`                                                          54
:func:`ubelt.argsort<ubelt.util_list.argsort>`                                                       53
:func:`ubelt.Timer<ubelt.timerit.Timer>`                                                             52
:func:`ubelt.dict_union<ubelt.util_dict.dict_union>`                                                 50
:func:`ubelt.invert_dict<ubelt.util_dict.invert_dict>`                                               49
:func:`ubelt.identity<ubelt.util_func.identity>`                                                     49
:func:`ubelt.find_duplicates<ubelt.util_dict.find_duplicates>`                                       43
:func:`ubelt.map_keys<ubelt.util_dict.map_keys>`                                                     43
:func:`ubelt.timestamp<ubelt.util_time.timestamp>`                                                   42
:func:`ubelt.unique<ubelt.util_list.unique>`                                                         40
:func:`ubelt.chunks<ubelt.util_list.chunks>`                                                         38
:func:`ubelt.hzcat<ubelt.util_str.hzcat>`                                                            37
:func:`ubelt.argmax<ubelt.util_list.argmax>`                                                         35
:func:`ubelt.import_module_from_path<ubelt.util_import.import_module_from_path>`                     35
:func:`ubelt.memoize_property<ubelt.util_memoize.memoize_property>`                                  34
:func:`ubelt.iter_window<ubelt.util_list.iter_window>`                                               33
:func:`ubelt.readfrom<ubelt.util_io.readfrom>`                                                       31
:func:`ubelt.sorted_vals<ubelt.util_dict.sorted_vals>`                                               30
:func:`ubelt.hash_file<ubelt.util_hash.hash_file>`                                                   30
:func:`ubelt.writeto<ubelt.util_io.writeto>`                                                         30
:func:`ubelt.memoize_method<ubelt.util_memoize.memoize_method>`                                      29
:func:`ubelt.symlink<ubelt.util_links.symlink>`                                                      28
:func:`ubelt.ensure_unicode<ubelt.util_str.ensure_unicode>`                                          25
:func:`ubelt.CacheStamp<ubelt.util_cache.CacheStamp>`                                                23
:func:`ubelt.touch<ubelt.util_io.touch>`                                                             22
:func:`ubelt.modname_to_modpath<ubelt.util_import.modname_to_modpath>`                               21
:func:`ubelt.find_exe<ubelt.util_platform.find_exe>`                                                 17
:func:`ubelt.import_module_from_name<ubelt.util_import.import_module_from_name>`                     17
:func:`ubelt.highlight_code<ubelt.util_colors.highlight_code>`                                       17
:func:`ubelt.AutoDict<ubelt.util_dict.AutoDict>`                                                     13
:func:`ubelt.inject_method<ubelt.util_func.inject_method>`                                           11
:func:`ubelt.argmin<ubelt.util_list.argmin>`                                                          8
:func:`ubelt.shrinkuser<ubelt.util_path.shrinkuser>`                                                  8
:func:`ubelt.split_modpath<ubelt.util_import.split_modpath>`                                          6
:func:`ubelt.find_path<ubelt.util_platform.find_path>`                                                5
:func:`ubelt.download<ubelt.util_download.download>`                                                  5
:func:`ubelt.sorted_keys<ubelt.util_dict.sorted_keys>`                                                5
:func:`ubelt.CaptureStdout<ubelt.util_stream.CaptureStdout>`                                          4
:func:`ubelt.modpath_to_modname<ubelt.util_import.modpath_to_modname>`                                4
:func:`ubelt.userhome<ubelt.util_path.userhome>`                                                      3
:func:`ubelt.argunique<ubelt.util_list.argunique>`                                                    2
:func:`ubelt.AutoOrderedDict<ubelt.util_dict.AutoOrderedDict>`                                        1
:func:`ubelt.unique_flags<ubelt.util_list.unique_flags>`                                              1
:func:`ubelt.varied_values<ubelt.util_dict.varied_values>`                                            0
:func:`ubelt.platform_data_dir<ubelt.util_platform.platform_data_dir>`                                0
:func:`ubelt.platform_config_dir<ubelt.util_platform.platform_config_dir>`                            0
:func:`ubelt.named_product<ubelt.util_dict.named_product>`                                            0
:func:`ubelt.indexable_allclose<ubelt.util_indexable.indexable_allclose>`                             0
:func:`ubelt.get_app_data_dir<ubelt.util_platform.get_app_data_dir>`                                  0
:func:`ubelt.get_app_config_dir<ubelt.util_platform.get_app_config_dir>`                              0
:func:`ubelt.ensure_app_data_dir<ubelt.util_platform.ensure_app_data_dir>`                            0
:func:`ubelt.ensure_app_config_dir<ubelt.util_platform.ensure_app_config_dir>`                        0
:func:`ubelt.compatible<ubelt.util_func.compatible>`                                                  0
:func:`ubelt.boolmask<ubelt.util_list.boolmask>`                                                      0
:func:`ubelt.TempDir<ubelt.util_path.TempDir>`                                                        0
:func:`ubelt.TeeStringIO<ubelt.util_stream.TeeStringIO>`                                              0
:func:`ubelt.POSIX<ubelt.util_platform.POSIX>`                                                        0
:func:`ubelt.OrderedSet<ubelt.orderedset.OrderedSet>`                                                 0
:func:`ubelt.NO_COLOR<ubelt.util_colors.NO_COLOR>`                                                    0
:func:`ubelt.JobPool<ubelt.util_futures.JobPool>`                                                     0
:func:`ubelt.IndexableWalker<ubelt.util_indexable.IndexableWalker>`                                   0
:func:`ubelt.FormatterExtensions<ubelt.util_format.FormatterExtensions>`                              0
:func:`ubelt.Executor<ubelt.util_futures.Executor>`                                                   0
:func:`ubelt.DownloadManager<ubelt.util_download_manager.DownloadManager>`                            0
:func:`ubelt.CaptureStream<ubelt.util_stream.CaptureStream>`                                          0
====================================================================================== ================


.. code:: python

    usage stats = {
        'mean': 54.349514,
        'std': 147.71915,
        'min': 0.0,
        'max': 1426.0,
        'med': 19.0,
        'sum': 5598,
        'shape': (103,),
    }


The following is a breakdown of the API by module


:mod:`ubelt.orderedset`
-----------------------
:func:`<ubelt.OrderedSet><ubelt.orderedset.OrderedSet>`
:func:`<ubelt.oset><ubelt.orderedset.oset>`

:mod:`ubelt.progiter`
---------------------
:func:`<ubelt.ProgIter><ubelt.progiter.ProgIter>`

:mod:`ubelt.timerit`
--------------------
:func:`<ubelt.Timer><ubelt.timerit.Timer>`
:func:`<ubelt.Timerit><ubelt.timerit.Timerit>`

:mod:`ubelt.util_arg`
---------------------
:func:`<ubelt.argval><ubelt.util_arg.argval>`
:func:`<ubelt.argflag><ubelt.util_arg.argflag>`

:mod:`ubelt.util_cache`
-----------------------
:func:`<ubelt.Cacher><ubelt.util_cache.Cacher>`
:func:`<ubelt.CacheStamp><ubelt.util_cache.CacheStamp>`

:mod:`ubelt.util_cmd`
---------------------
:func:`<ubelt.cmd><ubelt.util_cmd.cmd>`

:mod:`ubelt.util_colors`
------------------------
:func:`<ubelt.NO_COLOR><ubelt.util_colors.NO_COLOR>`
:func:`<ubelt.highlight_code><ubelt.util_colors.highlight_code>`
:func:`<ubelt.color_text><ubelt.util_colors.color_text>`

:mod:`ubelt.util_const`
-----------------------
:func:`<ubelt.NoParam><ubelt.util_const.NoParam>`

:mod:`ubelt.util_dict`
----------------------
:func:`<ubelt.AutoDict><ubelt.util_dict.AutoDict>`
:func:`<ubelt.AutoOrderedDict><ubelt.util_dict.AutoOrderedDict>`
:func:`<ubelt.dzip><ubelt.util_dict.dzip>`
:func:`<ubelt.ddict><ubelt.util_dict.ddict>`
:func:`<ubelt.dict_hist><ubelt.util_dict.dict_hist>`
:func:`<ubelt.dict_subset><ubelt.util_dict.dict_subset>`
:func:`<ubelt.dict_union><ubelt.util_dict.dict_union>`
:func:`<ubelt.dict_isect><ubelt.util_dict.dict_isect>`
:func:`<ubelt.dict_diff><ubelt.util_dict.dict_diff>`
:func:`<ubelt.find_duplicates><ubelt.util_dict.find_duplicates>`
:func:`<ubelt.group_items><ubelt.util_dict.group_items>`
:func:`<ubelt.invert_dict><ubelt.util_dict.invert_dict>`
:func:`<ubelt.map_keys><ubelt.util_dict.map_keys>`
:func:`<ubelt.map_vals><ubelt.util_dict.map_vals>`
:func:`<ubelt.sorted_keys><ubelt.util_dict.sorted_keys>`
:func:`<ubelt.sorted_vals><ubelt.util_dict.sorted_vals>`
:func:`<ubelt.odict><ubelt.util_dict.odict>`
:func:`<ubelt.named_product><ubelt.util_dict.named_product>`
:func:`<ubelt.varied_values><ubelt.util_dict.varied_values>`

:mod:`ubelt.util_download`
--------------------------
:func:`<ubelt.download><ubelt.util_download.download>`
:func:`<ubelt.grabdata><ubelt.util_download.grabdata>`

:mod:`ubelt.util_download_manager`
----------------------------------
:func:`<ubelt.DownloadManager><ubelt.util_download_manager.DownloadManager>`

:mod:`ubelt.util_format`
------------------------
:func:`<ubelt.repr2><ubelt.util_format.repr2>`
:func:`<ubelt.FormatterExtensions><ubelt.util_format.FormatterExtensions>`

:mod:`ubelt.util_func`
----------------------
:func:`<ubelt.identity><ubelt.util_func.identity>`
:func:`<ubelt.inject_method><ubelt.util_func.inject_method>`
:func:`<ubelt.compatible><ubelt.util_func.compatible>`

:mod:`ubelt.util_futures`
-------------------------
:func:`<ubelt.Executor><ubelt.util_futures.Executor>`
:func:`<ubelt.JobPool><ubelt.util_futures.JobPool>`

:mod:`ubelt.util_hash`
----------------------
:func:`<ubelt.hash_data><ubelt.util_hash.hash_data>`
:func:`<ubelt.hash_file><ubelt.util_hash.hash_file>`

:mod:`ubelt.util_import`
------------------------
:func:`<ubelt.split_modpath><ubelt.util_import.split_modpath>`
:func:`<ubelt.modname_to_modpath><ubelt.util_import.modname_to_modpath>`
:func:`<ubelt.modpath_to_modname><ubelt.util_import.modpath_to_modname>`
:func:`<ubelt.import_module_from_name><ubelt.util_import.import_module_from_name>`
:func:`<ubelt.import_module_from_path><ubelt.util_import.import_module_from_path>`

:mod:`ubelt.util_indexable`
---------------------------
:func:`<ubelt.IndexableWalker><ubelt.util_indexable.IndexableWalker>`
:func:`<ubelt.indexable_allclose><ubelt.util_indexable.indexable_allclose>`

:mod:`ubelt.util_io`
--------------------
:func:`<ubelt.readfrom><ubelt.util_io.readfrom>`
:func:`<ubelt.writeto><ubelt.util_io.writeto>`
:func:`<ubelt.touch><ubelt.util_io.touch>`
:func:`<ubelt.delete><ubelt.util_io.delete>`

:mod:`ubelt.util_links`
-----------------------
:func:`<ubelt.symlink><ubelt.util_links.symlink>`

:mod:`ubelt.util_list`
----------------------
:func:`<ubelt.allsame><ubelt.util_list.allsame>`
:func:`<ubelt.argmax><ubelt.util_list.argmax>`
:func:`<ubelt.argmin><ubelt.util_list.argmin>`
:func:`<ubelt.argsort><ubelt.util_list.argsort>`
:func:`<ubelt.argunique><ubelt.util_list.argunique>`
:func:`<ubelt.boolmask><ubelt.util_list.boolmask>`
:func:`<ubelt.chunks><ubelt.util_list.chunks>`
:func:`<ubelt.compress><ubelt.util_list.compress>`
:func:`<ubelt.flatten><ubelt.util_list.flatten>`
:func:`<ubelt.iter_window><ubelt.util_list.iter_window>`
:func:`<ubelt.iterable><ubelt.util_list.iterable>`
:func:`<ubelt.peek><ubelt.util_list.peek>`
:func:`<ubelt.take><ubelt.util_list.take>`
:func:`<ubelt.unique><ubelt.util_list.unique>`
:func:`<ubelt.unique_flags><ubelt.util_list.unique_flags>`

:mod:`ubelt.util_memoize`
-------------------------
:func:`<ubelt.memoize><ubelt.util_memoize.memoize>`
:func:`<ubelt.memoize_method><ubelt.util_memoize.memoize_method>`
:func:`<ubelt.memoize_property><ubelt.util_memoize.memoize_property>`

:mod:`ubelt.util_mixins`
------------------------
:func:`<ubelt.NiceRepr><ubelt.util_mixins.NiceRepr>`

:mod:`ubelt.util_path`
----------------------
:func:`<ubelt.TempDir><ubelt.util_path.TempDir>`
:func:`<ubelt.augpath><ubelt.util_path.augpath>`
:func:`<ubelt.shrinkuser><ubelt.util_path.shrinkuser>`
:func:`<ubelt.userhome><ubelt.util_path.userhome>`
:func:`<ubelt.ensuredir><ubelt.util_path.ensuredir>`
:func:`<ubelt.expandpath><ubelt.util_path.expandpath>`

:mod:`ubelt.util_platform`
--------------------------
:func:`<ubelt.WIN32><ubelt.util_platform.WIN32>`
:func:`<ubelt.LINUX><ubelt.util_platform.LINUX>`
:func:`<ubelt.DARWIN><ubelt.util_platform.DARWIN>`
:func:`<ubelt.POSIX><ubelt.util_platform.POSIX>`
:func:`<ubelt.find_exe><ubelt.util_platform.find_exe>`
:func:`<ubelt.find_path><ubelt.util_platform.find_path>`
:func:`<ubelt.ensure_app_cache_dir><ubelt.util_platform.ensure_app_cache_dir>`
:func:`<ubelt.ensure_app_config_dir><ubelt.util_platform.ensure_app_config_dir>`
:func:`<ubelt.ensure_app_data_dir><ubelt.util_platform.ensure_app_data_dir>`
:func:`<ubelt.get_app_cache_dir><ubelt.util_platform.get_app_cache_dir>`
:func:`<ubelt.get_app_config_dir><ubelt.util_platform.get_app_config_dir>`
:func:`<ubelt.get_app_data_dir><ubelt.util_platform.get_app_data_dir>`
:func:`<ubelt.platform_cache_dir><ubelt.util_platform.platform_cache_dir>`
:func:`<ubelt.platform_config_dir><ubelt.util_platform.platform_config_dir>`
:func:`<ubelt.platform_data_dir><ubelt.util_platform.platform_data_dir>`

:mod:`ubelt.util_str`
---------------------
:func:`<ubelt.indent><ubelt.util_str.indent>`
:func:`<ubelt.codeblock><ubelt.util_str.codeblock>`
:func:`<ubelt.paragraph><ubelt.util_str.paragraph>`
:func:`<ubelt.hzcat><ubelt.util_str.hzcat>`
:func:`<ubelt.ensure_unicode><ubelt.util_str.ensure_unicode>`

:mod:`ubelt.util_stream`
------------------------
:func:`<ubelt.TeeStringIO><ubelt.util_stream.TeeStringIO>`
:func:`<ubelt.CaptureStdout><ubelt.util_stream.CaptureStdout>`
:func:`<ubelt.CaptureStream><ubelt.util_stream.CaptureStream>`

:mod:`ubelt.util_time`
----------------------
:func:`<ubelt.timestamp><ubelt.util_time.timestamp>`



.. toctree::
   :maxdepth: 8
   :caption: Package Layout

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
