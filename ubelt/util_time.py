# -*- coding: utf-8 -*-
"""
This is util_time, it contains functions for handling time related code that I
wish there was standard library support for. Currently there is only one
function.


The :func:`timestamp` is less interesting than the previous two methods, but I
have found it useful to have a function that quickly returns an iso8601
timestamp without much fuss.


Timerit is back! But it no longer lives in util_time. Instead it now lives in
ubelt/timerit.py
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import time

__all__ = ['timestamp']


def timestamp(method='iso8601'):
    """
    Make an iso8601 timestamp suitable for use in filenames

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
