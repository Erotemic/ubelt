The API by usefulness
=====================

.. to help generate python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --extra_modname=bioharn,watch --remove_zeros=False

Perhaps the most useful way to learn this API is to sort by "usefulness".
I measure usefulness as the number of times I've used a particular function in
my own code (excluding ubelt itself).


================================================================================= ================
 Function name                                                                          Usefulness
================================================================================= ================
:func:`ubelt.urepr<ubelt.util_repr.urepr>`                                                    4327
:func:`ubelt.Path<ubelt.util_path.Path>`                                                      2125
:func:`ubelt.paragraph<ubelt.util_str.paragraph>`                                             1349
:func:`ubelt.ProgIter<ubelt.progiter.ProgIter>`                                                747
:func:`ubelt.cmd<ubelt.util_cmd.cmd>`                                                          657
:func:`ubelt.codeblock<ubelt.util_str.codeblock>`                                              611
:func:`ubelt.udict<ubelt.util_dict.udict>`                                                     603
:func:`ubelt.expandpath<ubelt.util_path.expandpath>`                                           508
:func:`ubelt.take<ubelt.util_list.take>`                                                       462
:func:`ubelt.oset<ubelt.orderedset.oset>`                                                      342
:func:`ubelt.ddict<ubelt.util_dict.ddict>`                                                     341
:func:`ubelt.iterable<ubelt.util_list.iterable>`                                               313
:func:`ubelt.flatten<ubelt.util_list.flatten>`                                                 303
:func:`ubelt.group_items<ubelt.util_dict.group_items>`                                         287
:func:`ubelt.NiceRepr<ubelt.util_mixins.NiceRepr>`                                             270
:func:`ubelt.ensuredir<ubelt.util_path.ensuredir>`                                             267
:func:`ubelt.map_vals<ubelt.util_dict.map_vals>`                                               265
:func:`ubelt.peek<ubelt.util_list.peek>`                                                       262
:func:`ubelt.NoParam<ubelt.util_const.NoParam>`                                                248
:func:`ubelt.dzip<ubelt.util_dict.dzip>`                                                       239
:func:`ubelt.odict<ubelt.util_dict.odict>`                                                     236
:func:`ubelt.hash_data<ubelt.util_hash.hash_data>`                                             200
:func:`ubelt.argflag<ubelt.util_arg.argflag>`                                                  184
:func:`ubelt.grabdata<ubelt.util_download.grabdata>`                                           161
:func:`ubelt.dict_hist<ubelt.util_dict.dict_hist>`                                             156
:func:`ubelt.identity<ubelt.util_func.identity>`                                               156
:func:`ubelt.dict_isect<ubelt.util_dict.dict_isect>`                                           152
:func:`ubelt.Timer<ubelt.util_time.Timer>`                                                     145
:func:`ubelt.memoize<ubelt.util_memoize.memoize>`                                              142
:func:`ubelt.argval<ubelt.util_arg.argval>`                                                    134
:func:`ubelt.allsame<ubelt.util_list.allsame>`                                                 133
:func:`ubelt.color_text<ubelt.util_colors.color_text>`                                         129
:func:`ubelt.schedule_deprecation<ubelt.util_deprecate.schedule_deprecation>`                  123
:func:`ubelt.augpath<ubelt.util_path.augpath>`                                                 120
:func:`ubelt.dict_diff<ubelt.util_dict.dict_diff>`                                             117
:func:`ubelt.IndexableWalker<ubelt.util_indexable.IndexableWalker>`                            116
:func:`ubelt.compress<ubelt.util_list.compress>`                                               116
:func:`ubelt.JobPool<ubelt.util_futures.JobPool>`                                              107
:func:`ubelt.named_product<ubelt.util_dict.named_product>`                                     104
:func:`ubelt.hzcat<ubelt.util_str.hzcat>`                                                       90
:func:`ubelt.delete<ubelt.util_io.delete>`                                                      88
:func:`ubelt.unique<ubelt.util_list.unique>`                                                    84
:func:`ubelt.WIN32<ubelt.util_platform.WIN32>`                                                  78
:func:`ubelt.dict_union<ubelt.util_dict.dict_union>`                                            76
:func:`ubelt.symlink<ubelt.util_links.symlink>`                                                 76
:func:`ubelt.indent<ubelt.util_str.indent>`                                                     69
:func:`ubelt.ensure_app_cache_dir<ubelt.util_platform.ensure_app_cache_dir>`                    67
:func:`ubelt.iter_window<ubelt.util_list.iter_window>`                                          62
:func:`ubelt.invert_dict<ubelt.util_dict.invert_dict>`                                          58
:func:`ubelt.memoize_property<ubelt.util_memoize.memoize_property>`                             57
:func:`ubelt.import_module_from_name<ubelt.util_import.import_module_from_name>`                56
:func:`ubelt.argsort<ubelt.util_list.argsort>`                                                  55
:func:`ubelt.timestamp<ubelt.util_time.timestamp>`                                              54
:func:`ubelt.modname_to_modpath<ubelt.util_import.modname_to_modpath>`                          53
:func:`ubelt.find_duplicates<ubelt.util_dict.find_duplicates>`                                  53
:func:`ubelt.hash_file<ubelt.util_hash.hash_file>`                                              51
:func:`ubelt.find_exe<ubelt.util_platform.find_exe>`                                            50
:func:`ubelt.map_keys<ubelt.util_dict.map_keys>`                                                50
:func:`ubelt.dict_subset<ubelt.util_dict.dict_subset>`                                          50
:func:`ubelt.Cacher<ubelt.util_cache.Cacher>`                                                   49
:func:`ubelt.chunks<ubelt.util_list.chunks>`                                                    47
:func:`ubelt.sorted_vals<ubelt.util_dict.sorted_vals>`                                          40
:func:`ubelt.CacheStamp<ubelt.util_cache.CacheStamp>`                                           38
:func:`ubelt.highlight_code<ubelt.util_colors.highlight_code>`                                  37
:func:`ubelt.argmax<ubelt.util_list.argmax>`                                                    36
:func:`ubelt.writeto<ubelt.util_io.writeto>`                                                    36
:func:`ubelt.ensure_unicode<ubelt.util_str.ensure_unicode>`                                     32
:func:`ubelt.sorted_keys<ubelt.util_dict.sorted_keys>`                                          30
:func:`ubelt.memoize_method<ubelt.util_memoize.memoize_method>`                                 29
:func:`ubelt.compatible<ubelt.util_func.compatible>`                                            24
:func:`ubelt.import_module_from_path<ubelt.util_import.import_module_from_path>`                24
:func:`ubelt.Executor<ubelt.util_futures.Executor>`                                             23
:func:`ubelt.readfrom<ubelt.util_io.readfrom>`                                                  23
:func:`ubelt.modpath_to_modname<ubelt.util_import.modpath_to_modname>`                          17
:func:`ubelt.AutoDict<ubelt.util_dict.AutoDict>`                                                17
:func:`ubelt.touch<ubelt.util_io.touch>`                                                        17
:func:`ubelt.inject_method<ubelt.util_func.inject_method>`                                      14
:func:`ubelt.timeparse<ubelt.util_time.timeparse>`                                              13
:func:`ubelt.ChDir<ubelt.util_path.ChDir>`                                                      11
:func:`ubelt.shrinkuser<ubelt.util_path.shrinkuser>`                                            11
:func:`ubelt.argmin<ubelt.util_list.argmin>`                                                    10
:func:`ubelt.varied_values<ubelt.util_dict.varied_values>`                                       9
:func:`ubelt.split_modpath<ubelt.util_import.split_modpath>`                                     8
:func:`ubelt.LINUX<ubelt.util_platform.LINUX>`                                                   8
:func:`ubelt.download<ubelt.util_download.download>`                                             7
:func:`ubelt.NO_COLOR<ubelt.util_colors.NO_COLOR>`                                               7
:func:`ubelt.OrderedSet<ubelt.orderedset.OrderedSet>`                                            6
:func:`ubelt.zopen<ubelt.util_zip.zopen>`                                                        6
:func:`ubelt.CaptureStdout<ubelt.util_stream.CaptureStdout>`                                     6
:func:`ubelt.DARWIN<ubelt.util_platform.DARWIN>`                                                 5
:func:`ubelt.boolmask<ubelt.util_list.boolmask>`                                                 4
:func:`ubelt.find_path<ubelt.util_platform.find_path>`                                           4
:func:`ubelt.get_app_cache_dir<ubelt.util_platform.get_app_cache_dir>`                           4
:func:`ubelt.indexable_allclose<ubelt.util_indexable.indexable_allclose>`                        3
:func:`ubelt.UDict<ubelt.util_dict.UDict>`                                                       3
:func:`ubelt.SetDict<ubelt.util_dict.SetDict>`                                                   2
:func:`ubelt.AutoOrderedDict<ubelt.util_dict.AutoOrderedDict>`                                   2
:func:`ubelt.argunique<ubelt.util_list.argunique>`                                               2
:func:`ubelt.map_values<ubelt.util_dict.map_values>`                                             1
:func:`ubelt.unique_flags<ubelt.util_list.unique_flags>`                                         1
:func:`ubelt.userhome<ubelt.util_path.userhome>`                                                 0
:func:`ubelt.split_archive<ubelt.util_zip.split_archive>`                                        0
:func:`ubelt.sorted_values<ubelt.util_dict.sorted_values>`                                       0
:func:`ubelt.sdict<ubelt.util_dict.sdict>`                                                       0
:func:`ubelt.platform_data_dir<ubelt.util_platform.platform_data_dir>`                           0
:func:`ubelt.platform_config_dir<ubelt.util_platform.platform_config_dir>`                       0
:func:`ubelt.platform_cache_dir<ubelt.util_platform.platform_cache_dir>`                         0
:func:`ubelt.get_app_data_dir<ubelt.util_platform.get_app_data_dir>`                             0
:func:`ubelt.get_app_config_dir<ubelt.util_platform.get_app_config_dir>`                         0
:func:`ubelt.ensure_app_data_dir<ubelt.util_platform.ensure_app_data_dir>`                       0
:func:`ubelt.ensure_app_config_dir<ubelt.util_platform.ensure_app_config_dir>`                   0
:func:`ubelt.TempDir<ubelt.util_path.TempDir>`                                                   0
:func:`ubelt.TeeStringIO<ubelt.util_stream.TeeStringIO>`                                         0
:func:`ubelt.ReprExtensions<ubelt.util_repr.ReprExtensions>`                                     0
:func:`ubelt.POSIX<ubelt.util_platform.POSIX>`                                                   0
:func:`ubelt.DownloadManager<ubelt.util_download_manager.DownloadManager>`                       0
:func:`ubelt.CaptureStream<ubelt.util_stream.CaptureStream>`                                     0
================================================================================= ================

.. code:: python

    usage stats = {
        'mean': 164.10257,
        'std': 467.12064,
        'min': 0.0,
        'max': 4327.0,
        'q_0.25': 6.0,
        'q_0.50': 50.0,
        'q_0.75': 134.0,
        'med': 50.0,
        'sum': 19200,
        'shape': (117,),
    }

:mod:`ubelt.orderedset`
-----------------------
:func:`<ubelt.OrderedSet><ubelt.orderedset.OrderedSet>`
:func:`<ubelt.oset><ubelt.orderedset.oset>`

:mod:`ubelt.progiter`
---------------------
:func:`<ubelt.ProgIter><ubelt.progiter.ProgIter>`

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

:mod:`ubelt.util_deprecate`
---------------------------
:func:`<ubelt.schedule_deprecation><ubelt.util_deprecate.schedule_deprecation>`

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
:func:`<ubelt.map_values><ubelt.util_dict.map_values>`
:func:`<ubelt.sorted_keys><ubelt.util_dict.sorted_keys>`
:func:`<ubelt.sorted_vals><ubelt.util_dict.sorted_vals>`
:func:`<ubelt.sorted_values><ubelt.util_dict.sorted_values>`
:func:`<ubelt.odict><ubelt.util_dict.odict>`
:func:`<ubelt.named_product><ubelt.util_dict.named_product>`
:func:`<ubelt.varied_values><ubelt.util_dict.varied_values>`
:func:`<ubelt.SetDict><ubelt.util_dict.SetDict>`
:func:`<ubelt.UDict><ubelt.util_dict.UDict>`
:func:`<ubelt.sdict><ubelt.util_dict.sdict>`
:func:`<ubelt.udict><ubelt.util_dict.udict>`

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
:func:`<ubelt.urepr><ubelt.util_format.urepr>`
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
:func:`<ubelt.Path><ubelt.util_path.Path>`
:func:`<ubelt.TempDir><ubelt.util_path.TempDir>`
:func:`<ubelt.augpath><ubelt.util_path.augpath>`
:func:`<ubelt.shrinkuser><ubelt.util_path.shrinkuser>`
:func:`<ubelt.userhome><ubelt.util_path.userhome>`
:func:`<ubelt.ensuredir><ubelt.util_path.ensuredir>`
:func:`<ubelt.expandpath><ubelt.util_path.expandpath>`
:func:`<ubelt.ChDir><ubelt.util_path.ChDir>`

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

:mod:`ubelt.util_repr`
----------------------
:func:`<ubelt.urepr><ubelt.util_repr.urepr>`
:func:`<ubelt.ReprExtensions><ubelt.util_repr.ReprExtensions>`

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
:func:`<ubelt.timeparse><ubelt.util_time.timeparse>`
:func:`<ubelt.Timer><ubelt.util_time.Timer>`

:mod:`ubelt.util_zip`
---------------------
:func:`<ubelt.zopen><ubelt.util_zip.zopen>`
:func:`<ubelt.split_archive><ubelt.util_zip.split_archive>`
