# -*- coding: utf-8 -*-
"""
Timerit now exists in a standalone pip-installable module. The source code
lives in its own github repo here: https://github.com/Erotemic/timerit
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import time
# Timerit and Timer now exist in standalone modules
from timerit import Timerit, Timer

__all__ = ['Timer', 'Timerit', 'timestamp']


def timestamp(method='iso8601'):
    """
    make an iso8601 timestamp

    Args:
        method (str): type of timestamp

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
