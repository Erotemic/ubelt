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
    Make a concise iso8601 timestamp suitable for use in filenames

    Args:
        datetime (datetime.datetime | None):
            A datetime to format into a timestamp. If unspecified, the current
            local time is used.

        method (str):
            Type of timestamp. Currently the only option is iso8601.
            This argument may be removed in the future.

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
        >>> import datetime as datetime_mod
        >>> from datetime import datetime as datetime_cls
        >>> # Create a datetime object with timezone information
        >>> ast_tzinfo = datetime_mod.timezone(datetime_mod.timedelta(hours=-4), 'AST')
        >>> datetime = datetime_cls.utcfromtimestamp(123456789.123456789).replace(tzinfo=ast_tzinfo)
        >>> stamp = ub.timestamp(datetime, precision=2)
        >>> print('stamp = {!r}'.format(stamp))
        stamp = '1973-11-29T213309.12-4'

        >>> # Demo with a fractional hour timezone
        >>> act_tzinfo = datetime_mod.timezone(datetime_mod.timedelta(hours=+9.5), 'ACT')
        >>> datetime = datetime_cls.utcfromtimestamp(123456789.123456789).replace(tzinfo=act_tzinfo)
        >>> stamp = ub.timestamp(datetime, precision=2)
        >>> print('stamp = {!r}'.format(stamp))
        stamp = '1973-11-29T213309.12+0930'

    Ignore:
        >>> # xdoctest: +REQUIRES(module:dateutil)
        >>> # Make sure we are compatible with dateutil
        >>> import dateutil
        >>> from dateutil import parser
        >>> import datetime as datetime_mod
        >>> from datetime import datetime as datetime_cls
        >>> tzinfo_list = [
        >>>     datetime_mod.timezone(datetime_mod.timedelta(hours=+9.5), 'ACT'),
        >>>     datetime_mod.timezone(datetime_mod.timedelta(hours=-4), 'AST'),
        >>>     datetime_mod.timezone(datetime_mod.timedelta(hours=0), 'UTC'),
        >>>     datetime_mod.timezone.utc,
        >>>     None,
        >>>     dateutil.tz.tzlocal()
        >>> ]
        >>> datetime_list = [
        >>>     datetime_cls.utcfromtimestamp(123456789.123456789),
        >>>     datetime_cls.utcfromtimestamp(0),
        >>> ]
        >>> basis = {
        >>>     #'precision': [0, 3, 9],
        >>>     'tzinfo': tzinfo_list,
        >>>     'datetime': datetime_list,
        >>> }
        >>> import copy
        >>> for params in ub.named_product(basis):
        >>>     dtime = params['datetime'].replace(tzinfo=params['tzinfo'])
        >>>     precision = params.get('precision', 0)
        >>>     stamp = ub.timestamp(datetime=dtime, precision=precision)
        >>>     recon = parser.parse(stamp)
        >>>     alt = recon.strftime('%Y-%m-%dT%H%M%S.%f%z')
        >>>     print('---')
        >>>     print('params = {}'.format(ub.repr2(params, nl=1)))
        >>>     print(f'dtime={dtime}')
        >>>     print(f'stamp={stamp}')
        >>>     print(f'recon={recon}')
        >>>     print(f'alt  ={alt}')
        >>>     shift = 10 ** precision
        >>>     assert int(dtime.timestamp() * shift) == int(recon.timestamp() * shift)
    """
    if method == 'iso8601':
        from datetime import datetime as datetime_cls
        if datetime is None:
            datetime = datetime_cls.now()

        if datetime.tzinfo is None:
            # Assume the local timezone (time.timezone is negated)
            offset_seconds = -time.timezone
        else:
            offset_seconds = datetime.tzinfo.utcoffset(datetime).total_seconds()

        seconds_per_hour = 3600
        tz_hour, tz_remain = divmod(offset_seconds, seconds_per_hour)
        tz_hour = int(tz_hour)
        if tz_remain:
            seconds_per_minute = 60
            tz_min = int(tz_remain // seconds_per_minute)
            utc_offset = '{:+03d}{:02d}'.format(tz_hour, tz_min)
        else:
            utc_offset = str(tz_hour) if tz_hour < 0 else '+' + str(tz_hour)
        if precision > 0:
            fprecision = 6  # microseconds are padded to 6 decimals
            local_stamp = datetime.strftime('%Y-%m-%dT%H%M%S.%f')
            ms_offset = len(local_stamp) - max(0, fprecision - precision)
            local_stamp = local_stamp[:ms_offset]
        else:
            local_stamp = datetime.strftime('%Y-%m-%dT%H%M%S')
        stamp = local_stamp + utc_offset
        return stamp
    else:
        raise ValueError('only iso8601 is allowed for method')


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
