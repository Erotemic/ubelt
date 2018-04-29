# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import time
import math
import sys
import gc
import itertools as it

__all__ = ['Timer', 'Timerit', 'timestamp']

if sys.version_info.major == 2:
    default_timer = time.clock if sys.platform.startswith('win32') else time.time
else:
    default_timer = time.perf_counter


class Timer(object):
    """
    Measures time elapsed between a start and end point. Can be used as a
    with-statement context manager, or using the tic/toc api.

    Args:
        label (str): identifier for printing defaults to ''
        verbose (int): verbosity flag, defaults to True if label is given
        newline (bool): if False and verbose, print tic and toc on the same line

    Attributes:
        elapsed (float): number of seconds measured by the context manager
        tstart (float): time of last `tic` reported by `default_timer()`

    Example:
        >>> # Create and start the timer using the the context manager
        >>> timer = Timer('Timer test!', verbose=1)
        >>> with timer:
        >>>     math.factorial(10000)
        >>> assert timer.elapsed > 0

    Example:
        >>> # Create and start the timer using the tic/toc interface
        >>> timer = Timer().tic()
        >>> elapsed1 = timer.toc()
        >>> elapsed2 = timer.toc()
        >>> elapsed3 = timer.toc()
        >>> assert elapsed1 <= elapsed2
        >>> assert elapsed2 <= elapsed3
    """
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

    def tic(self):
        """ starts the timer """
        if self.verbose:
            self.flush()
            self.write('\ntic(%r)' % self.label)
            if self.newline:
                self.write('\n')
            self.flush()
        self.tstart = default_timer()
        return self

    def toc(self):
        """ stops the timer """
        elapsed = default_timer() - self.tstart
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


class Timerit(object):
    """
    Reports the average time to run a block of code.

    Unlike `timeit`, `Timerit` can handle multiline blocks of code

    Args:
        num (int): number of times to run the loop
        label (str): identifier for printing
        bestof (int): takes the max over this number of trials
        verbose (int): verbosity flag, defaults to True if label is given

    CommandLine:
        python -m utool.util_time Timerit
        python -m utool.util_time Timerit:0
        python -m utool.util_time Timerit:1

    Example:
        >>> num = 15
        >>> t1 = Timerit(num, verbose=2)
        >>> for timer in t1:
        >>>     # <write untimed setup code here> this example has no setup
        >>>     with timer:
        >>>         # <write code to time here> for example...
        >>>         math.factorial(10000)
        >>> # <you can now access Timerit attributes>
        >>> print('t1.total_time = %r' % (t1.total_time,))
        >>> assert t1.total_time > 0
        >>> assert t1.n_loops == t1.num
        >>> assert t1.n_loops == num

    Example:
        >>> num = 10
        >>> # If the timer object is unused, time will still be recorded,
        >>> # but with less precision.
        >>> for _ in Timerit(num, 'imprecise'):
        >>>     math.factorial(10000)
        >>> # Using the timer object results in the most precise timings
        >>> for timer in Timerit(num, 'precise'):
        >>>     with timer: math.factorial(10000)
    """
    def __init__(self, num, label=None, bestof=3, verbose=None):
        if verbose is None:
            verbose = bool(label)
        self.num = num
        self.label = label
        self.times = []
        self.verbose = verbose
        self.total_time = None
        self.n_loops = None
        self.bestof = bestof

    def call(self, func, *args, **kwargs):
        """
        Alternative way to time a simple function call using condensed syntax.

        Returns:
            self (Timerit): Use `ave_secs`, `min`, or `mean` to get a scalar.

        Example:
            >>> ave_sec = Timerit(num=10).call(math.factorial, 50).ave_secs
            >>> assert ave_sec > 0
        """
        for timer in self:
            with timer:
                func(*args, **kwargs)
        return self

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
        # disable the garbage collector while timing
        with ToggleGC(False):
            # Core timing loop
            for i in it.repeat(None, self.num):
                # Start background timer (in case the user doesn't use fg_timer)
                # Yield foreground timer to let the user run a block of code
                # When we return from yield the user code will have just finished
                # Then record background time + loop overhead
                bg_timer.tic()
                yield fg_timer
                bg_time = bg_timer.toc()
                # Check if the fg_timer object was used, but fallback on bg_timer
                if fg_timer.elapsed >= 0:
                    block_time = fg_timer.elapsed  # higher precision
                else:
                    block_time = bg_time  # low precision
                # record timings
                self.times.append(block_time)
                self.total_time += block_time
                self.n_loops += 1
        # Timing complete, print results
        assert len(self.times) == self.num, 'incorrectly recorded times'
        if self.verbose > 0:
            self._print_report(self.verbose)

    @property
    def ave_secs(self):
        """
        The expected execution time of the timed code snippet in seconds.
        This is the minimum value recorded over all runs.

        SeeAlso:
            self.min
            self.mean
            self.std
        """
        return self.min()

    def min(self):
        """
        The best time overall.

        This is typically the best metric to consider when evaluating the
        execution time of a function. To understand why consider this quote
        from the docs of the original timeit module:

        '''
        In a typical case, the lowest value gives a lower bound for how fast
        your machine can run the given code snippet; higher values in the
        result vector are typically not caused by variability in Python's
        speed, but by other processes interfering with your timing accuracy.
        So the min() of the result is probably the only number you should be
        interested in.
        '''

        Example:
            >>> self = Timerit(num=10, verbose=0)
            >>> self.call(math.factorial, 50)
            >>> assert self.min() > 0
        """
        return min(self.times)

    def mean(self):
        """
        The mean of the best results of each trial.

        Note:
            This is typically less informative than simply looking at the min

        Example:
            >>> self = Timerit(num=10, verbose=0)
            >>> self.call(math.factorial, 50)
            >>> assert self.mean() > 0
        """
        from ubelt.util_list import chunks
        chunks = chunks(self.times, self.bestof)
        times = list(map(min, chunks))
        mean = sum(times) / len(times)
        return mean

    def std(self):
        """
        The standard deviation of the best results of each trial.

        Note:
            As mentioned in the timeit source code, the standard deviation is
            not often useful. Typically the minimum value is most informative.

        Example:
            >>> self = Timerit(num=10, verbose=1)
            >>> self.call(math.factorial, 50)
            >>> assert self.std() >= 0
        """
        from ubelt.util_list import chunks
        chunks = chunks(self.times, self.bestof)
        times = list(map(min, chunks))
        mean = sum(times) / len(times)
        std = math.sqrt(sum((t - mean) ** 2 for t in times) / len(times))
        return std

    def _seconds_str(self):
        """
        CommandLine:
            python -m ubelt.util_time Timerit._seconds_str

        Example:
            >>> self = Timerit(num=100, bestof=10, verbose=0)
            >>> self.call(lambda : sum(range(100)))
            >>> print(self._seconds_str())
            ... 'best=3.423 µs, ave=3.451 ± 0.027 µs'
        """

        units = [
            ('s', 1e0),
            ('ms', 1e-3),
            (_trychar('µs', 'us'), 1e-6),
            ('ns', 1e-9),
        ]

        mean = self.mean()

        for unit, mag in units:  # pragma: nobranch
            if mean > mag:
                break

        unit_min = self.min() / mag
        unit_mean = mean / mag
        precision = 4

        # Is showing the std useful? It probably doesn't hurt.
        std = self.std()
        unit_std = std / mag
        pm = _trychar('±', '+-')
        fmtstr = ('best={min:.{pr1}} {unit}, '
                  'mean={mean:.{pr1}} {pm} {std:.{pr2}} {unit}')
        pr1 = precision
        pr2 = max(precision - 2, 1)
        unit_str = fmtstr.format(min=unit_min, unit=unit, mean=unit_mean,
                                 pm=pm, std=unit_std, pr1=pr1, pr2=pr2)
        return unit_str

    def _report(self, verbose=1):
        """
        Creates a human readable report
        """
        report_lines = []
        pline = report_lines.append
        if self.label is None:
            pline('Timed for: %d loops, best of %d' % (
                self.n_loops, min(self.n_loops, self.bestof)))
        else:
            pline('Timed %s for: %d loops, best of %d' % (
                self.label, self.n_loops, min(self.n_loops, self.bestof)))
        if verbose > 2:
            pline('    body took: %s seconds' % self.total_time)
        pline('    time per loop: %s' % (self._seconds_str(),))
        return '\n'.join(report_lines)

    def _print_report(self, verbose=1):
        """
        Prints human readable report using the print function
        """
        print(self._report(verbose=verbose))


class ToggleGC(object):
    """
    Context manager to disable garbage collection.

    Example:
        >>> import gc
        >>> prev = gc.isenabled()
        >>> with ToggleGC(False):
        >>>     assert not gc.isenabled()
        >>>     with ToggleGC(True):
        >>>         assert gc.isenabled()
        >>>     assert not gc.isenabled()
        >>> assert gc.isenabled() == prev
    """
    def __init__(self, flag):
        self.flag = flag
        self.prev = None

    def __enter__(self):
        self.prev = gc.isenabled()
        if self.flag:
            gc.enable()
        else:
            gc.disable()

    def __exit__(self, ex_type, ex_value, trace):
        if self.prev:
            gc.enable()
        else:
            gc.disable()


def timestamp(method='iso8601'):
    """
    make an iso8601 timestamp

    CommandLine:
        python -m ubelt.util_time timestamp

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


def _trychar(char, fallback):  # nocover
    """
    CommandLine:
        python -m ubelt.util_time _trychar
        pytest ubelt/util_time.py::_trychar:0 -s

    Example:
        >>> char = _trychar('µs', 'us')
        >>> print('char = {}'.format(char))
    """
    # Logic from ipython timeit to handle terminals that cant show mu
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:  # pragma: nobranch
        try:
            char.encode(sys.stdout.encoding)
        except Exception:  # nocover
            pass
        else:
            return char
    return fallback  # nocover


if __name__ == '__main__':
    """
    CommandLine:
        python -m ubelt.util_time
        python -m ubelt.util_time all
    """
    import xdoctest as xdoc
    xdoc.doctest_module(__file__)
