# -*- coding: utf-8 -*-
"""
Timerit now exists in a standalone pip-installable module. The source code
lives in its own github repo here: https://github.com/Erotemic/timerit

Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> import math
    >>> import ubelt as ub
    >>> timer = ub.Timer('Timer demo!', verbose=1)
    >>> with timer:
    >>>     math.factorial(100000)
    tic('Timer demo!')
    ...toc('Timer demo!')=0.1453s

Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> import math
    >>> import ubelt as ub
    >>> for _ in ub.Timerit(num=200, verbose=3):
    >>>     math.factorial(10000)
    Timing for 200 loops
    Timed for: 200 loops, best of 3
        time per loop: best=2.055 ms, mean=2.145 ± 0.083 ms

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import time
# Timerit and Timer now exist in standalone modules
from timerit import Timerit, Timer

__all__ = ['Timer', 'Timerit', 'timestamp']


def timestamp(method='iso8601'):
    """
    make an iso8601 timestamp suitable for use in filenames

    Args:
        method (str, default='iso8601'): type of timestamp

    Example:
        >>> stamp = timestamp()
        >>> print('stamp = {!r}'.format(stamp))
        stamp = ...-...-...T...
    """
    if method == 'iso8601':
        # ISO 8601
        # datetime.datetime.utcnow().isoformat()
        # datetime.datetime.now().isoformat()
        # utcnow
        tz_hour = time.timezone // 3600
        utc_offset = str(tz_hour) if tz_hour < 0 else '+' + str(tz_hour)
        stamp = time.strftime('%Y-%m-%dT%H%M%S') + utc_offset
        return stamp
    else:
        raise ValueError('only iso8601 is accepted for now')
