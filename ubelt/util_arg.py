# -*- coding: utf-8 -*-
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
        default (object): value to return if not specified
        argv (list): overrides `sys.argv` if specified

    Returns:
        str: value : the value specified after the key. It they key is
            specified multiple times, then the first value is returned.

    Doctest:
        >>> import ubelt as ub
        >>> argv = ['--ans', '42', '--quest=the grail', '--ans=6', '--bad']
        >>> assert ub.argval('--spam', argv=argv) == ub.NoParam
        >>> assert ub.argval('--quest', argv=argv) == 'the grail'
        >>> assert ub.argval('--ans', argv=argv) == '42'
        >>> assert ub.argval('--bad', argv=argv) == ub.NoParam
        >>> assert ub.argval(('--bad', '--bar'), argv=argv) == ub.NoParam
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
                value = ''.join(item.split('=')[1:])
                return value
    value = default
    return value


def argflag(key, argv=None):
    """
    Determines if a key is specified on the command line

    Args:
        key (str or tuple): string or tuple of strings. Each key should be
            prefixed with two hyphens (i.e. `--`)
        argv (list): overrides `sys.argv` if specified

    Returns:
        bool: flag : True if the key (or any of the keys) was specified

    Doctest:
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


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_arg
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
