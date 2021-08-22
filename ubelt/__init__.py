# -*- coding: utf-8 -*-
"""
UBelt is a "utility belt" of commonly needed utility and helper functions.  It
is a currated collection of top-level utilities with functionality that falls
into a mixture of categories.

The source code is available at `https://github.com/Erotemic/ubelt <https://github.com/Erotemic/ubelt>`_.
We also have `Jupyter notebook demos <https://github.com/Erotemic/ubelt/blob/master/docs/notebooks/Ubelt%20Demo.ipynb>`_.

The ubelt API is organized by submodules containing related functionality.
Each submodule contains top level overview documentation, and each function
contains a docstring with at least one example.

NOTE: The `README <https://github.com/Erotemic/ubelt#readme>`_ on github
contains information and examples complementary to these docs.
"""
# flake8: noqa
from __future__ import absolute_import, division, print_function, unicode_literals


__dev__="""
AutogenInit:
    mkinit ubelt --diff
    mkinit ubelt -w  # todo: get sphinx to ignore this

    # TODO: Lazy imports with mkinit

Testing:
    xdoctest ubelt
"""

__version__ = '0.10.0'

__submodules__ = [
    'util_arg',
    'util_cache',
    'util_colors',
    'util_const',
    'util_cmd',
    'util_dict',
    'util_download',
    'util_download_manager',
    'util_func',
    'util_format',
    'util_futures',
    'util_io',
    'util_links',
    'util_list',
    'util_hash',
    'util_import',
    'util_indexable',
    'util_memoize',
    'util_mixins',
    'util_path',
    'util_platform',
    'util_str',
    'util_stream',
    'util_time',
    'orderedset',
    'progiter',
    'timerit',
    '_util_deprecated',
]

# <AUTOGEN_INIT>
from ubelt import _util_deprecated
from ubelt import orderedset
from ubelt import progiter
from ubelt import timerit
from ubelt import util_arg
from ubelt import util_cache
from ubelt import util_cmd
from ubelt import util_colors
from ubelt import util_const
from ubelt import util_dict
from ubelt import util_download
from ubelt import util_download_manager
from ubelt import util_format
from ubelt import util_func
from ubelt import util_futures
from ubelt import util_hash
from ubelt import util_import
from ubelt import util_indexable
from ubelt import util_io
from ubelt import util_links
from ubelt import util_list
from ubelt import util_memoize
from ubelt import util_mixins
from ubelt import util_path
from ubelt import util_platform
from ubelt import util_str
from ubelt import util_stream
from ubelt import util_time

from ubelt.util_arg import (argflag, argval,)
from ubelt.util_cache import (CacheStamp, Cacher,)
from ubelt.util_colors import (NO_COLOR, color_text, highlight_code,)
from ubelt.util_const import (NoParam,)
from ubelt.util_cmd import (cmd,)
from ubelt.util_dict import (AutoDict, AutoOrderedDict, ddict, dict_diff,
                             dict_hist, dict_isect, dict_subset, dict_union,
                             dzip, find_duplicates, group_items, invert_dict,
                             map_keys, map_vals, named_product, odict,
                             sorted_keys, sorted_vals, varied_values,)
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
from ubelt._util_deprecated import (compressuser, dict_take, dict_take,
                                    editfile, editfile,
                                    ensure_app_resource_dir,
                                    get_app_resource_dir,
                                    platform_resource_dir,
                                    schedule_deprecation, startfile, truepath,)

__all__ = ['AutoDict', 'AutoOrderedDict', 'CacheStamp', 'Cacher',
           'CaptureStdout', 'CaptureStream', 'DARWIN', 'DownloadManager',
           'Executor', 'FormatterExtensions', 'IndexableWalker', 'JobPool',
           'LINUX', 'NO_COLOR', 'NiceRepr', 'NoParam', 'OrderedSet', 'POSIX',
           'ProgIter', 'TeeStringIO', 'TempDir', 'Timer', 'Timerit', 'WIN32',
           '_util_deprecated', 'allsame', 'argflag', 'argmax', 'argmin',
           'argsort', 'argunique', 'argval', 'augpath', 'boolmask', 'chunks',
           'cmd', 'codeblock', 'color_text', 'compatible', 'compress',
           'compressuser', 'ddict', 'delete', 'dict_diff', 'dict_hist',
           'dict_isect', 'dict_subset', 'dict_take', 'dict_union', 'download',
           'dzip', 'editfile', 'ensure_app_cache_dir', 'ensure_app_config_dir',
           'ensure_app_data_dir', 'ensure_app_resource_dir', 'ensure_unicode',
           'ensuredir', 'expandpath', 'find_duplicates', 'find_exe',
           'find_path', 'flatten', 'get_app_cache_dir', 'get_app_config_dir',
           'get_app_data_dir', 'get_app_resource_dir', 'grabdata',
           'group_items', 'hash_data', 'hash_file', 'highlight_code', 'hzcat',
           'identity', 'import_module_from_name', 'import_module_from_path',
           'indent', 'indexable_allclose', 'inject_method', 'invert_dict',
           'iter_window', 'iterable', 'map_keys', 'map_vals', 'memoize',
           'memoize_method', 'memoize_property', 'modname_to_modpath',
           'modpath_to_modname', 'named_product', 'odict', 'orderedset',
           'oset', 'paragraph', 'peek', 'platform_cache_dir',
           'platform_config_dir', 'platform_data_dir', 'platform_resource_dir',
           'progiter', 'readfrom', 'repr2', 'schedule_deprecation',
           'shrinkuser', 'sorted_keys', 'sorted_vals', 'split_modpath',
           'startfile', 'symlink', 'take', 'timerit', 'timestamp', 'touch',
           'truepath', 'unique', 'unique_flags', 'userhome', 'util_arg',
           'util_cache', 'util_cmd', 'util_colors', 'util_const', 'util_dict',
           'util_download', 'util_download_manager', 'util_format',
           'util_func', 'util_futures', 'util_hash', 'util_import',
           'util_indexable', 'util_io', 'util_links', 'util_list',
           'util_memoize', 'util_mixins', 'util_path', 'util_platform',
           'util_str', 'util_stream', 'util_time', 'varied_values', 'writeto']
# </AUTOGEN_INIT>
