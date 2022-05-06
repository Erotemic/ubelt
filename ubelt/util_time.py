"""
This is util_time, it contains functions for handling time related code.

The :func:`timestamp` function returns an iso8601 timestamp without much fuss.

The :class:`Timer` class is a context manager that times a block of indented
code. It includes `tic` and `toc` methods a more matlab like feel.

Timerit is gone! Use the standalone and separate module
:class:`timerit.Timerit` But the :class:`.
"""
import time
import sys

__all__ = ['timestamp', 'Timer']


def timestamp(datetime=None, precision=0, method='iso8601'):
    """
    Make an iso8601 timestamp suitable for use in filenames

    Args:
        method (str):
            Type of timestamp. Currently the only option is iso8601.

        precision (int):
            if non-zero, adds up to 6 digits of sub-second precision.

    Returns:
        str: stamp

    References:
        https://en.wikipedia.org/wiki/ISO_8601
        https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        https://docs.python.org/3/library/time.html

    Notes:
        The time.strftime and datetime.datetime.strftime methods seem
        to work differently. The former does not support %f

    Example:
        >>> import ubelt as ub
        >>> stamp = ub.timestamp()
        >>> print('stamp = {!r}'.format(stamp))
        stamp = ...-...-...T...

    Example:
        >>> import ubelt as ub
        >>> stamp = ub.timestamp(precision=2)
        >>> print('stamp = {!r}'.format(stamp))
        stamp = ...-...-...T.......

    Ignore:
        # Make sure we are compatible with dateutil
        from dateutil import parser
        from ubelt.util_time import *  # NOQA
        print(timestamp(precision=0))
        print(timestamp(precision=1))
        print(timestamp(precision=2))
        print(timestamp(precision=6))
        print(timestamp(precision=9))
    """
    if method == 'iso8601':
        # ISO 8601
        # datetime.datetime.utcnow().isoformat()
        # datetime.datetime.now().isoformat()
        # utcnow
        import datetime
        now = datetime.datetime.now()
        tz_hour = time.timezone // 3600
        utc_offset = str(tz_hour) if tz_hour < 0 else '+' + str(tz_hour)
        if precision > 0:
            fprecision = 6  # microseconds are padded to 6 decimals
            ms_offset = -max(0, fprecision - precision)
            local_stamp = now.strftime('%Y-%m-%dT%H%M%S.%f')
            now.strftime('%z')
            local_stamp = local_stamp[:ms_offset]
        else:
            local_stamp = time.strftime('%Y-%m-%dT%H%M%S')
        stamp = local_stamp + utc_offset
        return stamp
    else:
        raise ValueError('only iso8601 is accepted for now')


class Timer(object):
    """
    Measures time elapsed between a start and end point. Can be used as a
    with-statement context manager, or using the tic/toc api.

    Args:
        label (str, default=''):
            identifier for printing
        verbose (int, default=None):
            verbosity flag, defaults to True if label is given
        newline (bool, default=True):
            if False and verbose, print tic and toc on the same line

    Attributes:
        elapsed (float): number of seconds measured by the context manager
        tstart (float): time of last `tic` reported by `self._time()`

    Example:
        >>> # Create and start the timer using the context manager
        >>> import math
        >>> timer = Timer('Timer test!', verbose=1)
        >>> with timer:
        >>>     math.factorial(10)
        >>> assert timer.elapsed > 0
        tic('Timer test!')
        ...toc('Timer test!')=...

    Example:
        >>> # Create and start the timer using the tic/toc interface
        >>> timer = Timer().tic()
        >>> elapsed1 = timer.toc()
        >>> elapsed2 = timer.toc()
        >>> elapsed3 = timer.toc()
        >>> assert elapsed1 <= elapsed2
        >>> assert elapsed2 <= elapsed3
    """
    # TODO: If sys.version >= 3.7, then use time.perf_counter_ns
    _default_time = time.perf_counter

    def __init__(self, label='', verbose=None, newline=True):
        if verbose is None:
            verbose = bool(label)
        self.label = label
        self.verbose = verbose
        self.newline = newline
        self.tstart = -1
        self.elapsed = -1
        self.write = sys.stdout.write
        self.flush = sys.stdout.flush
        self._time = self._default_time

    def tic(self):
        """ starts the timer """
        if self.verbose:
            self.flush()
            self.write('\ntic(%r)' % self.label)
            if self.newline:
                self.write('\n')
            self.flush()
        self.tstart = self._time()
        return self

    def toc(self):
        """ stops the timer """
        elapsed = self._time() - self.tstart
        if self.verbose:
            self.write('...toc(%r)=%.4fs\n' % (self.label, elapsed))
            self.flush()
        return elapsed

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.elapsed = self.toc()
        if trace is not None:
            return False
