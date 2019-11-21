"""
Utilities for compatibility between python versions and maybe other things in
the future.
"""
import sys


if sys.version_info.major == 2:  # nocover
    text_type = unicode
    string_types = (basestring,)
    default_timer = time.clock if sys.platform.startswith('win32') else time.time
else:
    text_type = str
    string_types = (str,)
    default_timer = time.perf_counter
