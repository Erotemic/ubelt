# -*- coding: utf-8 -*-
"""
Simple ways to interact with the commandline without defining a full blown
CLI.These are usually used for developer hacks. Any real interface should
probably be defined using `argparse` or `click`. Be sure to ignore unknown
arguments if you use them in conjuction with these functions.

The `argflag` function checks if a boolean `--flag` style CLI argument exists
on the command line.

The `argval` function returns the value of a `--key=value` style CLI argument.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import six
import sys
from ubelt import util_const


def argval(key, default=util_const.NoParam, argv=None):
    """
    Get the value of a keyword argument specified on the command line.

    Values can be specified as `<key> <value>` or `<key>=<value>`

    Args:
        key (str or tuple): string or tuple of strings. Each key should be
            prefixed with two hyphens (i.e. `--`)
        default (Optional[object]): value to return if not specified
        argv (Optional[list]): overrides `sys.argv` if specified

    Returns:
        str: value : the value specified after the key. It they key is
            specified multiple times, then the first value is returned.

    TODO:
        - [ ] Can we handle the case where the value is a list of long paths?
        - [ ] Should we default the first or last specified instance of the flag.

    Example:
        >>> import ubelt as ub
        >>> argv = ['--ans', '42', '--quest=the grail', '--ans=6', '--bad']
        >>> assert ub.argval('--spam', argv=argv) == ub.NoParam
        >>> assert ub.argval('--quest', argv=argv) == 'the grail'
        >>> assert ub.argval('--ans', argv=argv) == '42'
        >>> assert ub.argval('--bad', argv=argv) == ub.NoParam
        >>> assert ub.argval(('--bad', '--bar'), argv=argv) == ub.NoParam

    Example:
        >>> # Test fix for GH Issue #41
        >>> import ubelt as ub
        >>> argv = ['--path=/path/with/k=3']
        >>> ub.argval('--path', argv=argv) == '/path/with/k=3'
    """
    if argv is None:  # nocover
        argv = sys.argv

    keys = [key] if isinstance(key, six.string_types) else key
    n_max = len(argv) - 1
    for argx, item in enumerate(argv):
        for key_ in keys:
            if item == key_:
                if argx < n_max:
                    value = argv[argx + 1]
                    return value
            elif item.startswith(key_ + '='):
                value = '='.join(item.split('=')[1:])
                return value
    value = default
    return value


def argflag(key, argv=None):
    """
    Determines if a key is specified on the command line

    Args:
        key (str or tuple): string or tuple of strings. Each key should be
            prefixed with two hyphens (i.e. `--`)
        argv (Optional[list]): overrides `sys.argv` if specified

    Returns:
        bool: flag : True if the key (or any of the keys) was specified

    Example:
        >>> import ubelt as ub
        >>> argv = ['--spam', '--eggs', 'foo']
        >>> assert ub.argflag('--eggs', argv=argv) is True
        >>> assert ub.argflag('--ans', argv=argv) is False
        >>> assert ub.argflag('foo', argv=argv) is True
        >>> assert ub.argflag(('bar', '--spam'), argv=argv) is True
    """
    if argv is None:  # nocover
        argv = sys.argv
    keys = [key] if isinstance(key, six.string_types) else key
    flag = any(k in argv for k in keys)
    return flag
