# -*- coding: utf-8 -*-
# flake8: noqa
"""
CommandLine:
    # Partially regenerate __init__.py
    python -c "import ubelt"
    python -c "import ubelt" --print-ubelt-init
    python -c "import ubelt" --update-ubelt-init
"""
from __future__ import absolute_import, division, print_function, unicode_literals

__version__ = '0.0.1'

GLOBAL_MODULES = [
    'util_dict',
    'util_list',
    'util_time',
]


__DYNAMIC__ = False
_DOELSE = False

if __DYNAMIC__:
    from ubelt._internal import dynamic_make_init
    dynamic_make_init.dynamic_import(__name__, GLOBAL_MODULES)
    _DOELSE = False
else:
    # Do the nonexec import (can force it to happen no matter what if alwyas set
    # to True)
    _DOELSE = True

if _DOELSE:
    # <AUTOGEN_INIT>

    from ubelt import util_dict
    from ubelt import util_list
    from ubelt import util_time
    from ubelt.util_dict import (group_items,)
    from ubelt.util_list import (compress, flatten, take,)
    from ubelt.util_time import (Timer, Timerit, VERBOSE_TIME,)
    # </AUTOGEN_INIT>

del _DOELSE
