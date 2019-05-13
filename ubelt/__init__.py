# -*- coding: utf-8 -*-
"""
UBelt is a "utility belt" of commonly needed utility and helper functions.  It
is a currated collection of utilities with functionality that falls into a
mixture of the following categories:

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

For more detailed high level documentation see the README on github: `https://github.com/Erotemic/ubelt <https://github.com/Erotemic/ubelt>`_. For demos see the `Jupyter notebook <https://github.com/Erotemic/ubelt/blob/master/docs/notebooks/Ubelt%20Demo.ipynb>`_.

The ubelt API is organized by submodules containing related functionality.
Each submodule contains top level overview documentation, and each function
contains a docstring with at least one example. Please see specific submodule
documentation for more details.

AutogenInit:
    mkinit ubelt -w  # todo: get sphinx to ignore this
"""
# Todo:
#     The following functions and classes are candidates to be ported from utool:
#     * rsync
from __future__ import absolute_import, division, print_function, unicode_literals

__version__ = '0.8.0'

__submodules__ = [
    'util_arg',
    'util_cache',
    'util_colors',
    'util_const',
    'util_cmd',
    'util_dict',
    'util_download',
    'util_func',
    'util_format',
    'util_io',
    'util_links',
    'util_list',
    'util_hash',
    'util_import',
    'util_memoize',
    'util_mixins',
    'util_path',
    'util_platform',
    'util_str',
    'util_stream',
    'util_time',
    'orderedset',
    'progiter',
]

# <AUTOGEN_INIT>
from ubelt import util_arg
from ubelt import util_cache
from ubelt import util_colors
from ubelt import util_const
from ubelt import util_cmd
from ubelt import util_dict
from ubelt import util_download
from ubelt import util_func
from ubelt import util_format
from ubelt import util_io
from ubelt import util_links
from ubelt import util_list
from ubelt import util_hash
from ubelt import util_import
from ubelt import util_memoize
from ubelt import util_mixins
from ubelt import util_path
from ubelt import util_platform
from ubelt import util_str
from ubelt import util_stream
from ubelt import util_time
from ubelt import orderedset
from ubelt import progiter

from ubelt.util_arg import (argflag, argval,)
from ubelt.util_cache import (CacheStamp, Cacher,)
from ubelt.util_colors import (color_text, highlight_code,)
from ubelt.util_const import (NoParam,)
from ubelt.util_cmd import (cmd,)
from ubelt.util_dict import (AutoDict, AutoOrderedDict, ddict, dict_hist,
                             dict_isect, dict_subset, dict_take, dict_union,
                             dzip, find_duplicates, group_items, invert_dict,
                             map_keys, map_vals, odict,)
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

__all__ = ['AutoDict', 'AutoOrderedDict', 'CacheStamp', 'Cacher',
           'CaptureStdout', 'CaptureStream', 'DARWIN', 'FormatterExtensions',
           'LINUX', 'NiceRepr', 'NoParam', 'OrderedSet', 'POSIX', 'ProgIter',
           'TeeStringIO', 'TempDir', 'Timer', 'Timerit', 'WIN32', 'allsame',
           'argflag', 'argmax', 'argmin', 'argsort', 'argunique', 'argval',
           'augpath', 'boolmask', 'chunks', 'cmd', 'codeblock', 'color_text',
           'compress', 'compressuser', 'ddict', 'delete', 'dict_hist',
           'dict_isect', 'dict_subset', 'dict_take', 'dict_union', 'download',
           'dzip', 'editfile', 'ensure_app_cache_dir', 'ensure_app_config_dir',
           'ensure_app_data_dir', 'ensure_app_resource_dir', 'ensure_unicode',
           'ensuredir', 'expandpath', 'find_duplicates', 'find_exe',
           'find_path', 'flatten', 'get_app_cache_dir', 'get_app_config_dir',
           'get_app_data_dir', 'get_app_resource_dir', 'grabdata',
           'group_items', 'hash_data', 'hash_file', 'highlight_code', 'hzcat',
           'identity', 'import_module_from_name', 'import_module_from_path',
           'indent', 'inject_method', 'invert_dict', 'iter_window', 'iterable',
           'map_keys', 'map_vals', 'memoize', 'memoize_method',
           'memoize_property', 'modname_to_modpath', 'modpath_to_modname',
           'odict', 'orderedset', 'oset', 'paragraph', 'peek',
           'platform_cache_dir', 'platform_config_dir', 'platform_data_dir',
           'platform_resource_dir', 'progiter', 'readfrom', 'repr2',
           'split_modpath', 'startfile', 'symlink', 'take', 'timestamp',
           'touch', 'truepath', 'unique', 'unique_flags', 'userhome',
           'util_arg', 'util_cache', 'util_cmd', 'util_colors', 'util_const',
           'util_dict', 'util_download', 'util_format', 'util_func',
           'util_hash', 'util_import', 'util_io', 'util_links', 'util_list',
           'util_memoize', 'util_mixins', 'util_path', 'util_platform',
           'util_str', 'util_stream', 'util_time', 'writeto']
# </AUTOGEN_INIT>
