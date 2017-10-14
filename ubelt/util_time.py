# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
# import datetime
import time
import sys

__all__ = ['Timer', 'Timerit', 'timestamp']

# Use time.clock in win32
default_timer = time.clock if sys.platform.startswith('win32') else time.time


class Timer(object):
    r"""
    Timer with-statment context object.

    Example:
        >>> import ubelt as ub
        >>> timer = ub.Timer('Timer test!', verbose=1)
        >>> with timer:
        >>>     prime = ub.find_nth_prime(40)
        >>> assert timer.ellapsed > 0
    """
    DEFAULT_VERBOSE = True

    def __init__(self, label='', verbose=None, newline=True):
        if verbose is None:
            verbose = self.DEFAULT_VERBOSE  # nocover
        self.label = label
        self.verbose = verbose
        self.newline = newline
        self.tstart = -1
        self.ellapsed = -1
        self.write = sys.stdout.write
        self.flush = sys.stdout.flush

    def tic(self):
        """ starts the timer """
        if self.verbose:
            self.flush()
            self.write('\ntic(%r)' % self.label)
            if self.newline:
                self.write('\n')
            self.flush()
        self.tstart = default_timer()

    def toc(self):
        """ stops the timer """
        ellapsed = default_timer() - self.tstart
        if self.verbose:
            self.write('...toc(%r)=%.4fs\n' % (self.label, ellapsed))
            self.flush()
        return ellapsed

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, type_, value, trace):
        self.ellapsed = self.toc()
        if trace is not None:
            # return False on error
            return False  # nocover


class Timerit(object):
    r"""
    Reports the average time to run a block of code.

    Unlike `timeit`, `Timerit` can handle multiline blocks of code

    Args:
        num (int): number of times to run the loop
        label (str): identifier for printing
        bestof (int): takes the max over this number of trials
        verbose (int): verbosity level

    CommandLine:
        python -m utool.util_time Timerit
        python -m utool.util_time Timerit:0
        python -m utool.util_time Timerit:1

    Example:
        >>> import ubelt as ub
        >>> num = 15
        >>> t1 = ub.Timerit(num, verbose=2)
        >>> for timer in t1:
        >>>     # <write untimed setup code here> this example has no setup
        >>>     with timer:
        >>>         # <write code to time here> for example...
        >>>         ub.find_nth_prime(100)
        >>> # <you can now access Timerit attributes>
        >>> print('t1.total_time = %r' % (t1.total_time,))
        >>> assert t1.total_time > 0
        >>> assert t1.n_loops == t1.num
        >>> assert t1.n_loops == num

    Example:
        >>> import ubelt as ub
        >>> num = 10
        >>> n = 50
        >>> # If the timer object is unused, time will still be recoreded,
        >>> # but with less precision.
        >>> for _ in ub.Timerit(num, 'inprecise'):
        >>>     ub.find_nth_prime(n)
        >>> # Using the timer object results in the most precise timeings
        >>> for timer in ub.Timerit(num, 'precise'):
        >>>     with timer:
        >>>         ub.find_nth_prime(n)
    """
    DEFAULT_VERBOSE = True

    def __init__(self, num, label=None, bestof=3, verbose=None):
        if verbose is None:
            verbose = self.DEFAULT_VERBOSE
        self.num = num
        self.label = label
        self.times = []
        self.verbose = verbose
        self.total_time = None
        self.n_loops = None
        self.bestof = bestof

    def call(self, func, *args, **kwargs):
        """
        Alternative way to time a simple function call using condensed syntax

        Example:
            >>> import ubelt as ub
            >>> ave_sec = ub.Timerit(num=10, verbose=0).call(ub.find_nth_prime, 50)
            >>> assert ave_sec > 0
        """
        for timer in self:
            with timer:
                func(*args, **kwargs)
        return self.ave_secs

    def __iter__(self):
        if self.verbose >= 2:
            if self.label is None:
                print('Timing for %d loops' % self.num)
            else:
                print('Timing %s for %d loops.' % (self.label, self.num,))
        self.n_loops = 0
        self.total_time = 0
        # Create a foreground and background timer
        bg_timer = Timer(verbose=0)   # (ideally this is unused)
        fg_timer = Timer(verbose=0)   # (used directly by user)
        # Core timing loop
        for i in range(self.num):
            # Start background timer (in case the user doesnt use fg_timer)
            # Yield foreground timer to let the user run a block of code
            # When we return from yield the user code will have just finishec
            # Then record background time + loop overhead
            bg_timer.tic()
            yield fg_timer
            bg_time = bg_timer.toc()
            # Check if the fg_timer object was used, but fallback on bg_timer
            if fg_timer.ellapsed >= 0:
                block_time = fg_timer.ellapsed  # high precision
            else:
                block_time = bg_time  # low precision
            # record timeings
            self.times.append(block_time)
            self.total_time += block_time
            self.n_loops += 1
        # Timeing complete, print results
        assert len(self.times) == self.num, 'incorrectly recorded times'
        if self.verbose > 0:
            self._print_report(self.verbose)

    @property
    def ave_secs(self):
        # Takes the best of each trial
        import ubelt as ub
        chunks = list(ub.chunks(self.times, self.bestof))
        seconds = sum(map(min, chunks)) / len(chunks)
        return seconds
        # return self.total_time / self.n_loops

    def _seconds_str(self):
        units = [
            ('s', 1e0),
            ('ms', 1e-3),
            ('µs', 1e-6),
            ('ns', 1e-9),
        ]
        seconds = self.ave_secs
        for unit, mag in units:
            if seconds > mag:
                break
        unit_sec = seconds / mag
        precision = 4
        fmtstr = '{:.%d} {}' % (precision,)
        unit_str = fmtstr.format(unit_sec, unit)
        return unit_str

    def _print_report(self, verbose=1):
        # ave_secs = self.ave_secs
        if self.label is None:
            print('Timing complete, %d loops, best of %d' % (
                self.n_loops, min(self.n_loops, self.bestof)))
        else:
            print('Timing complete for: %s, %d loops, best of %d' % (
                self.label, self.n_loops, min(self.n_loops, self.bestof)))
        if verbose > 2:
            print('    body took: %s seconds' % self.total_time)
        print('    time per loop : %s seconds' % (self._seconds_str(),))


def timestamp(method='iso8601'):
    """ make an iso8601 timestamp """
    if method == 'iso8601':
        # ISO 8601
        # datetime.datetime.utcnow().isoformat()
        # datetime.datetime.now().isoformat()
        # utcnow
        tz_hour = time.timezone // 3600
        utc_offset = '-' + str(tz_hour) if tz_hour < 0 else '+' + str(tz_hour)
        stamp = time.strftime('%Y-%m-%dT%H%M%S') + utc_offset
        return stamp
    else:
        raise ValueError('only iso8601 is accepted for now')


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_time
        python -m ubelt.util_time all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
