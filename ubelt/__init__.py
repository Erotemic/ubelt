# -*- coding: utf-8 -*-
# flake8: noqa
"""
CommandLine:
    # Partially regenerate __init__.py
    python -c "import ubelt"
    python -c "import ubelt" --print-ubelt-init --dyn
    python -c "import ubelt" --update-ubelt-init --dyn

    # TODO: ensure this new way will work with multilevel modules
    python -c "import ubelt._internal as a; a.autogen_init('ubelt', dry=True)"
TODO:
    The following functions and classes are candidates to be ported from utool:
    * reload_class
    * inject_func_as_method
    * inject_func_as_property
    * parse_cfgstr3
    * accumulate
    * itertwo
    * iterwin
    * ParamInfo - move to dtool
    * embed
    * rsync
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import sys

__version__ = '0.0.37'

GLOBAL_MODULES = [
    'util_arg',
    'util_cache',
    'util_colors',
    'util_const',
    'util_cmd',
    'util_decor',
    'util_dict',
    'util_download',
    'util_func',
    'util_format',
    'util_io',
    'util_list',
    'util_import',
    'util_mixins',
    'util_path',
    'util_platform',
    'util_str',
    'util_stress',
    'util_time',
    'progiter',
    'meta',
]

__DYNAMIC__ = '--dyn' in sys.argv

if __DYNAMIC__:  # nocover
    # If dynamic, imports can be autogenerated
    from ubelt._internal import dynamic_make_init
    dynamic_make_init.dynamic_import(__name__, GLOBAL_MODULES)
    _DOELSE = False
else:  # pragma: nobranch
    # Run the autogenerated imports
    _DOELSE = True

if _DOELSE:  # pragma: nobranch
    # <AUTOGEN_INIT>

    from ubelt import util_arg
    from ubelt import util_cache
    from ubelt import util_colors
    from ubelt import util_const
    from ubelt import util_cmd
    from ubelt import util_decor
    from ubelt import util_dict
    from ubelt import util_download
    from ubelt import util_func
    from ubelt import util_format
    from ubelt import util_io
    from ubelt import util_list
    from ubelt import util_import
    from ubelt import util_mixins
    from ubelt import util_path
    from ubelt import util_platform
    from ubelt import util_str
    from ubelt import util_stress
    from ubelt import util_time
    from ubelt import progiter
    from ubelt import meta
    from ubelt.util_arg import (argflag, argval,)
    from ubelt.util_cache import (Cacher,)
    from ubelt.util_colors import (color_text, highlight_code,)
    from ubelt.util_const import (NoParam,)
    from ubelt.util_cmd import (cmd,)
    from ubelt.util_decor import (memoize,)
    from ubelt.util_dict import (AutoDict, AutoOrderedDict, OrderedDict, ddict,
                                 defaultdict, dict_hist, dict_subset, dict_take,
                                 find_duplicates, group_items, invert_dict,
                                 map_keys, map_vals, odict,)
    from ubelt.util_download import (download, grabdata, urlopen, urlparse,)
    from ubelt.util_func import (identity,)
    from ubelt.util_format import (repr2,)
    from ubelt.util_io import (readfrom, writeto, touch, delete,)
    from ubelt.util_list import (argsort, boolmask, chunks, compress, flatten,
                                 iterable, take, unique, unique_flags,)
    from ubelt.util_import import (PythonPathContext, import_module_from_name,
                                   import_module_from_path,)
    from ubelt.util_mixins import (NiceRepr,)
    from ubelt.util_path import (abspath, augpath, compressuser, ensuredir,
                                 expandvars, split, truepath, userhome,)
    from ubelt.util_platform import (DARWIN, LINUX, POSIX, PY2, PY3, WIN32,
                                     editfile, ensure_app_cache_dir,
                                     ensure_app_resource_dir, get_app_cache_dir,
                                     get_app_resource_dir, platform_cache_dir,
                                     platform_resource_dir, startfile,)
    from ubelt.util_str import (CaptureStdout, cStringIO, codeblock,
                                ensure_unicode, hzcat, indent,)
    from ubelt.util_stress import (find_nth_prime,)
    from ubelt.util_time import (Timer, Timerit, timestamp,)
    from ubelt.progiter import (ProgIter,)
    
    # </AUTOGEN_INIT>

del _DOELSE
