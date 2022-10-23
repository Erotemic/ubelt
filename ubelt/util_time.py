"""
This is util_time, it contains functions for handling time related code.

The :func:`timestamp` function returns an iso8601 timestamp without much fuss.

The :func:`timeparse` is the inverse of `timestamp`, and makes use of
:mod:`dateutil` if it is available.

The :class:`Timer` class is a context manager that times a block of indented
code. It includes `tic` and `toc` methods a more matlab like feel.

Timerit is gone! Use the standalone and separate module :module:`timerit`.


See Also:
    :mod:`tempora` - https://github.com/jaraco/tempora - time related utility functions from Jaraco
    :mod:`pendulum` - https://github.com/sdispater/pendulum - drop in replacement for datetime
    :mod:`arrow` - https://github.com/arrow-py/arrow
"""
import time
import sys
from functools import lru_cache

__all__ = ['timestamp', 'timeparse', 'Timer']


@lru_cache(maxsize=None)
def _needs_workaround39103():
    """
    Depending on the system C library, either %04Y or %Y wont work.
    This is an actual Python bug:
    https://bugs.python.org/issue13305

    singer-python also had a similar issue:
    https://github.com/singer-io/singer-python/issues/86

    See Also
    https://github.com/jaraco/tempora/blob/main/tempora/__init__.py#L59
    """
    from datetime import datetime as datetime_cls
    return len(datetime_cls(1, 1, 1).strftime('%Y')) != 4


def timestamp(datetime=None, precision=0, default_timezone='local',
              allow_dateutil=True):
    """
    Make a concise iso8601 timestamp suitable for use in filenames.

    Args:
        datetime (datetime.datetime | datetime.date | None):
            A datetime to format into a timestamp. If unspecified, the current
            local time is used. If given as a date, the time 00:00 is used.

        precision (int):
            if non-zero, adds up to 6 digits of sub-second precision.

        default_timezone (str | datetime.timezone):
            if the input does not specify a timezone, assume this one.
            Can be "local" or "utc", or a standardized code if dateutil is
            installed.

        allow_dateutil (bool):
            if True, will use dateutil to lookup the default timezone if needed

    Returns:
        str:
            The timestamp, which will always contain a date, time, and
            timezone.

    Note:
        For more info see [WikiISO8601]_, [PyStrptime]_, [PyTime]_.

    References:
        .. [WikiISO8601] https://en.wikipedia.org/wiki/ISO_8601
        .. [PyStrptime] https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        .. [PyTime] https://docs.python.org/3/library/time.html

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

        >>> # Can accept datetime or date objects with local, utc, or custom default timezones
        >>> act_tzinfo = datetime_mod.timezone(datetime_mod.timedelta(hours=+9.5), 'ACT')
        >>> datetime_utc = ub.timeparse('2020-03-05T112233', default_timezone='utc')
        >>> datetime_act = ub.timeparse('2020-03-05T112233', default_timezone=act_tzinfo)
        >>> datetime_notz = datetime_utc.replace(tzinfo=None)
        >>> date = datetime_utc.date()
        >>> stamp_utc = ub.timestamp(datetime_utc)
        >>> stamp_act = ub.timestamp(datetime_act)
        >>> stamp_date_utc = ub.timestamp(date, default_timezone='utc')
        >>> print(f'stamp_utc      = {stamp_utc}')
        >>> print(f'stamp_act      = {stamp_act}')
        >>> print(f'stamp_date_utc = {stamp_date_utc}')
        stamp_utc      = 2020-03-05T112233+0
        stamp_act      = 2020-03-05T112233+0930
        stamp_date_utc = 2020-03-05T000000+0

    Example:
        >>> # xdoctest: +REQUIRES(module:dateutil)
        >>> # Make sure we are compatible with dateutil
        >>> import ubelt as ub
        >>> from dateutil.tz import tzlocal
        >>> import datetime as datetime_mod
        >>> from datetime import datetime as datetime_cls
        >>> tz_act = datetime_mod.timezone(datetime_mod.timedelta(hours=+9.5), 'ACT')
        >>> tzinfo_list = [
        >>>     tz_act,
        >>>     datetime_mod.timezone(datetime_mod.timedelta(hours=-4), 'AST'),
        >>>     datetime_mod.timezone(datetime_mod.timedelta(hours=0), 'UTC'),
        >>>     datetime_mod.timezone.utc,
        >>>     None,
        >>>     tzlocal()
        >>> ]
        >>> # Note: there is a win32 bug here
        >>> # https://bugs.python.org/issue37 that means we cant use
        >>> # dates close to the epoch
        >>> datetime_list = [
        >>>     datetime_cls.utcfromtimestamp(123456789.123456789 + 315360000),
        >>>     datetime_cls.utcfromtimestamp(0 + 315360000),
        >>> ]
        >>> basis = {
        >>>     'precision': [0, 3, 9],
        >>>     'tzinfo': tzinfo_list,
        >>>     'datetime': datetime_list,
        >>>     'default_timezone': ['local', 'utc', tz_act],
        >>> }
        >>> for params in ub.named_product(basis):
        >>>     dtime = params['datetime'].replace(tzinfo=params['tzinfo'])
        >>>     precision = params.get('precision', 0)
        >>>     stamp = ub.timestamp(datetime=dtime, precision=precision)
        >>>     recon = ub.timeparse(stamp)
        >>>     alt = recon.strftime('%Y-%m-%dT%H%M%S.%f%z')
        >>>     print('---')
        >>>     print('params = {}'.format(ub.repr2(params, nl=1)))
        >>>     print(f'dtime={dtime}')
        >>>     print(f'stamp={stamp}')
        >>>     print(f'recon={recon}')
        >>>     print(f'alt  ={alt}')
        >>>     shift = 10 ** precision
        >>>     a = int(dtime.timestamp() * shift)
        >>>     b = int(recon.timestamp() * shift)
        >>>     assert a == b, f'{a} != {b}'
    """
    import datetime as datetime_mod
    from datetime import datetime as datetime_cls

    datetime_obj = datetime
    offset_seconds = None

    # datetime inherits from date. Strange, so we cant use this. See:
    # https://github.com/python/typeshed/issues/4802
    if isinstance(datetime_obj, datetime_mod.date) and not isinstance(datetime_obj, datetime_cls):
        # Coerce a date to datetime.datetime
        datetime_obj = datetime_cls.combine(datetime_obj, datetime_cls.min.time())

    if datetime_obj is None or datetime_obj.tzinfo is None:
        # In either case, we need to construct a timezone object
        tzinfo = _timezone_coerce(default_timezone,
                                  allow_dateutil=allow_dateutil)
        # If datetime_obj is unspecified, create a timezone aware now object
        if datetime_obj is None:
            datetime_obj = datetime_cls.now(tzinfo)
    else:
        tzinfo = datetime_obj.tzinfo

    # the arg to utcoffset is confusing
    offset_seconds = tzinfo.utcoffset(datetime_obj).total_seconds()
    # offset_seconds = tzinfo.utcoffset(None).total_seconds()

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
        # NOTE: The time.strftime and datetime.datetime.strftime methods
        # seem to work differently. The former does not support %f
        if _needs_workaround39103():  # nocover
            local_stamp = datetime_obj.strftime('%04Y-%m-%dT%H%M%S.%f')
        else:  # nocover
            local_stamp = datetime_obj.strftime('%Y-%m-%dT%H%M%S.%f')
        ms_offset = len(local_stamp) - max(0, fprecision - precision)
        local_stamp = local_stamp[:ms_offset]
    else:
        if _needs_workaround39103():  # nocover
            local_stamp = datetime_obj.strftime('%04Y-%m-%dT%H%M%S')
        else:  # nocover
            local_stamp = datetime_obj.strftime('%Y-%m-%dT%H%M%S')
    stamp = local_stamp + utc_offset
    return stamp


def timeparse(stamp, default_timezone='local', allow_dateutil=True):
    """
    Create a :class:`datetime.datetime` object from a string timestamp.

    Without any extra dependencies this will parse the output of
    :func:`ubelt.util_time.timestamp()` into a datetime object. In the case
    where the format differs, `dateutil.parser.parse` will be used if the
    `python-dateutil` package is installed.

    Args:
        stamp (str):
            a string encoded timestamp

        default_timezone (str):
            if the input does not specify a timezone, assume this one.
            Can be "local" or "utc".

        allow_dateutil (bool):
            if False we only use the minimal parsing and do not allow a
            fallback to dateutil.

    Returns:
        datetime.datetime: the parsed datetime

    Raises:
        ValueError: if if parsing fails.

    TODO:
        - [ ] Allow defaulting to local or utm timezone (currently default is local)

    Example:
        >>> import ubelt as ub
        >>> # Demonstrate a round trip of timestamp and timeparse
        >>> stamp = ub.timestamp()
        >>> datetime = ub.timeparse(stamp)
        >>> assert ub.timestamp(datetime) == stamp
        >>> # Round trip with precision
        >>> stamp = ub.timestamp(precision=4)
        >>> datetime = ub.timeparse(stamp)
        >>> assert ub.timestamp(datetime, precision=4) == stamp

    Example:
        >>> import ubelt as ub
        >>> # We should always be able to parse these
        >>> good_stamps = [
        >>>     '2000-11-22',
        >>>     '2000-11-22T111111.44444Z',
        >>>     '2000-11-22T111111.44444+5',
        >>>     '2000-11-22T111111.44444-05',
        >>>     '2000-11-22T111111.44444-0500',
        >>>     '2000-11-22T111111.44444+0530',
        >>>     '2000-11-22T111111Z',
        >>>     '2000-11-22T111111+5',
        >>>     '2000-11-22T111111+0530',
        >>> ]
        >>> for stamp in good_stamps:
        >>>     print(f'----')
        >>>     print(f'stamp={stamp}')
        >>>     result = ub.timeparse(stamp, allow_dateutil=0)
        >>>     print(f'result={result!r}')
        >>>     recon = ub.timestamp(result)
        >>>     print(f'recon={recon}')

    Example:
        >>> import ubelt as ub
        >>> # We require dateutil to handle these types of stamps
        >>> import pytest
        >>> conditional_stamps = [
        >>>         '2000-01-02T11:23:58.12345+5:30',
        >>>         '09/25/2003',
        >>>         'Thu Sep 25 10:36:28 2003',
        >>> ]
        >>> for stamp in conditional_stamps:
        >>>     with pytest.raises(ValueError):
        >>>         result = ub.timeparse(stamp, allow_dateutil=False)
        >>> have_dateutil = bool(ub.modname_to_modpath('dateutil'))
        >>> if have_dateutil:
        >>>     for stamp in conditional_stamps:
        >>>         result = ub.timeparse(stamp)

    Ignore:
        import timerit
        ti = timerit.Timerit(1000, 10)
        ti.reset('non-standard dateutil.parse').call(lambda: dateutil.parser.parse('2000-01-02T112358.12345+5'))
        ti.reset('non-standard ubelt.timeparse').call(lambda: ub.timeparse('2000-01-02T112358.12345+5'))
        ti.reset('standard dateutil.parse').call(lambda: dateutil.parser.parse('2000-01-02T112358.12345+0500'))
        ti.reset('standard dateutil.isoparse').call(lambda: dateutil.parser.isoparse('2000-01-02T112358.12345+0500'))
        ti.reset('standard ubelt.timeparse').call(lambda: ub.timeparse('2000-01-02T112358.12345+0500'))
        ti.reset('standard datetime_cls.strptime').call(lambda: datetime_cls.strptime('2000-01-02T112358.12345+0500', '%Y-%m-%dT%H%M%S.%f%z'))
    """
    from datetime import datetime as datetime_cls
    datetime_obj = None
    # Check if we might have a minimal format
    maybe_minimal = (
        len(stamp) >= 17 and 'T' in stamp[10:]
    )
    fixed_stamp = stamp
    if maybe_minimal:
        # Note by default %z only handles the format `[+-]HHMM(SS(.ffffff))`
        # this means we have to handle the case where `[+-]HH` is given.
        # We do this by checking the offset and padding it to at least the
        # `[+-]HHMM` format
        date_part, timetz_part = stamp.split('T', 1)
        if '-' in timetz_part[6:]:
            time_part, sign, tz_part = timetz_part.partition('-')
        elif '+' in timetz_part[6:]:
            time_part, sign, tz_part = timetz_part.partition('+')
        else:
            # In 3.7 a Z suffix is handled correctly
            # For 3.6 compatability, replace Z with +0000
            if timetz_part.endswith('Z'):
                time_part = timetz_part[:-1]
                sign = '+'
                tz_part = '0000'
            else:
                tz_part = None

        if tz_part is not None:
            if len(tz_part) == 1:
                tz_part = '0{}00'.format(tz_part)
            elif len(tz_part) == 2:
                tz_part = '{}00'.format(tz_part)
            fixed_stamp = ''.join([date_part, 'T', time_part, sign, tz_part])

    if len(stamp) == 10:
        try:
            fmt =  '%Y-%m-%d'
            datetime_obj = datetime_cls.strptime(fixed_stamp, fmt)
        except ValueError:
            pass

    if maybe_minimal and datetime_obj is None:
        minimal_formats = [
            '%Y-%m-%dT%H%M%S%z',
            '%Y-%m-%dT%H%M%S',
            '%Y-%m-%dT%H%M%S.%f%z',
            '%Y-%m-%dT%H%M%S.%f',
        ]
        for fmt in minimal_formats:
            try:
                datetime_obj = datetime_cls.strptime(fixed_stamp, fmt)
            except ValueError:
                pass
            else:
                break

    if datetime_obj is None:
        # Our minimal logic did not work, can we use dateutil?
        if not allow_dateutil:
            raise ValueError((
                'Cannot parse timestamp. '
                'Unknown string format: {!r}, and '
                'dateutil is not allowed').format(stamp))
        else:
            try:
                from dateutil.parser import parse as du_parse
            except (ModuleNotFoundError, ImportError):  # nocover
                raise ValueError((
                    'Cannot parse timestamp. '
                    'Unknown string format: {!r}, and '
                    'dateutil is not installed').format(stamp)) from None
            else:  # nocover
                datetime_obj = du_parse(stamp)

    if datetime_obj.tzinfo is None:
        # Timezone is unspecified, need to construct the default one.
        tzinfo = _timezone_coerce(default_timezone,
                                  allow_dateutil=allow_dateutil)
        datetime_obj = datetime_obj.replace(tzinfo=tzinfo)

    return datetime_obj


def _timezone_coerce(tzinfo, allow_dateutil=True):
    """
    Ensure output it a timezone instance.

    Example:
        >>> import pytest
        >>> from ubelt.util_time import *  # NOQA
        >>> from ubelt.util_time import _timezone_coerce
        >>> results = []
        >>> write = results.append
        >>> tzinfo = _timezone_coerce('utc', allow_dateutil=0)
        >>> print(f'tzinfo={tzinfo}')
        tzinfo=UTC

    Example:
        >>> # xdoctest: +REQUIRES(module:dateutil)
        >>> import pytest
        >>> results = []
        >>> write = results.append
        >>> write(_timezone_coerce('utc'))
        >>> write(_timezone_coerce('GMT'))
        >>> write(_timezone_coerce('EST'))
        >>> write(_timezone_coerce('HST'))
        >>> import datetime as datetime_mod
        >>> dt = datetime_mod.datetime.now()
        >>> for tzinfo in results:
        >>>     print(f'tzoffset={tzinfo.utcoffset(dt).total_seconds()}')
        tzoffset=0.0
        tzoffset=0.0
        tzoffset=-18000.0
        tzoffset=-36000.0

    Example:
        >>> import pytest
        >>> from ubelt.util_time import *  # NOQA
        >>> from ubelt.util_time import _timezone_coerce
        >>> with pytest.raises(ValueError):
        ...     _timezone_coerce('GMT', allow_dateutil=0)
        >>> with pytest.raises(TypeError):
        ...     _timezone_coerce(object(), allow_dateutil=0)
        >>> # xdoctest: +REQUIRES(module:dateutil)
        >>> with pytest.raises(KeyError):
        ...     _timezone_coerce('NotATimezone', allow_dateutil=1)

    Example:
        >>> import pytest
        >>> from ubelt.util_time import *  # NOQA
        >>> from ubelt.util_time import _timezone_coerce
        >>> import time
        >>> tz1 = _timezone_coerce('local', allow_dateutil=0)
        >>> tz2 = _timezone_coerce('local', allow_dateutil=1)
        >>> sec1 = tz1.utcoffset(None).total_seconds()
        >>> sec2 = tz2.utcoffset(None).total_seconds()
        >>> assert sec1 == sec2 == -time.timezone
    """
    import datetime as datetime_mod
    if isinstance(tzinfo, str):
        if tzinfo == 'local':
            # Note: the local timezone time.timezone is negated
            _delta = datetime_mod.timedelta(seconds=-time.timezone)
            out_tzinfo = datetime_mod.timezone(_delta)
        elif tzinfo == 'utc':
            out_tzinfo = datetime_mod.timezone.utc
        else:
            if allow_dateutil:
                from dateutil import tz as tz_mod
                out_tzinfo = tz_mod.gettz(tzinfo)
                if out_tzinfo is None:
                    raise KeyError(tzinfo)
            else:
                raise ValueError((
                    'Unrecognized timezone: {!r}, and '
                    'dateutil is not allowed').format(tzinfo))
    elif isinstance(tzinfo, datetime_mod.timezone):
        out_tzinfo = tzinfo
    else:
        raise TypeError(
            'Unknown type: {!r} for tzinfo'.format(
                type(tzinfo))
        )
    return out_tzinfo


class Timer(object):
    """
    Measures time elapsed between a start and end point. Can be used as a
    with-statement context manager, or using the tic/toc api.

    Args:
        label (str, default=''):
            identifier for printing

        verbose (int, default=None):
            verbosity flag, defaults to True if label is given, otherwise 0.

        newline (bool, default=True):
            if False and verbose, print tic and toc on the same line.

        ns (bool, default=False):
            if True, a nano-second resolution timer to avoid precision loss
            caused by the float type.

    Attributes:
        elapsed (float): number of seconds measured by the context manager
        tstart (float): time of last `tic` reported by `self._time()`

    Example:
        >>> # Create and start the timer using the context manager
        >>> import math
        >>> import ubelt as ub
        >>> timer = ub.Timer('Timer test!', verbose=1)
        >>> with timer:
        >>>     math.factorial(10)
        >>> assert timer.elapsed > 0
        tic('Timer test!')
        ...toc('Timer test!')=...

    Example:
        >>> # Create and start the timer using the tic/toc interface
        >>> import ubelt as ub
        >>> timer = ub.Timer().tic()
        >>> elapsed1 = timer.toc()
        >>> elapsed2 = timer.toc()
        >>> elapsed3 = timer.toc()
        >>> assert elapsed1 <= elapsed2
        >>> assert elapsed2 <= elapsed3

    Example:
        >>> # In Python 3.7+ nanosecond resolution can be enabled
        >>> import ubelt as ub
        >>> import sys
        >>> if sys.version_info[0:2] <= (3, 6):
        >>>     import pytest
        >>>     pytest.skip()
        >>> # xdoctest +REQUIRES(Python>=3.7)  # fixme directive doesnt exist yet
        >>> timer = ub.Timer(label='perf_counter_ns', ns=True).tic()
        >>> elapsed1 = timer.toc()
        >>> elapsed2 = timer.toc()
        >>> assert elapsed1 <= elapsed2
        >>> assert isinstance(elapsed1, int)
    """
    _default_time = time.perf_counter

    def __init__(self, label='', verbose=None, newline=True, ns=False):
        if verbose is None:
            verbose = bool(label)
        self.label = label
        self.verbose = verbose
        self.newline = newline
        self.tstart = -1
        self.elapsed = -1
        self.write = sys.stdout.write
        self.flush = sys.stdout.flush
        self.ns = ns
        if self.ns:
            self._time = time.perf_counter_ns
        else:
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
            if self.ns:
                self.write('...toc(%r)=%.4fs\n' % (self.label, elapsed / 1e9))
            else:
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


# class Time:
#     """
#     Stub for potential future time object
#     """
#     def __init__(cls, datetime):
#         ...
#     @classmethod
#     def coerce(cls, data):
#         ...
#     @classmethod
#     def parse(cls, stamp):
#         ...
#
# class TimeDelta:
#     ...
