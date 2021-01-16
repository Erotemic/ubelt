# -*- coding: utf-8 -*-
"""
First, :class:`Timer` is a context manager that times a block of indented
code. Also has `tic` and `toc` methods for a more matlab like feel.

Next, :class:`Timerit` is an alternative to the builtin timeit module. I think
its better at least, maybe Tim Peters can show me otherwise. Perhaps there's a
reason it has to work on strings and can't be placed around existing code like
a with statement.


Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> #
    >>> # The Timerit class allows for robust benchmarking based
    >>> # It can be used in normal scripts by simply adjusting the indentation
    >>> import math
    >>> for timer in Timerit(num=12, verbose=3):
    >>>     with timer:
    >>>         math.factorial(100)
    Timing for: 200 loops, best of 3
    Timed for: 200 loops, best of 3
        body took: 331.840 µs
        time per loop: best=1.569 µs, mean=1.615 ± 0.0 µs

    >>> # xdoctest: +SKIP
    >>> # In Contrast, timeit is similar, but not having to worry about setup
    >>> # and inputing the program as a string, is nice.
    >>> import timeit
    >>> timeit.timeit(stmt='math.factorial(100)', setup='import math')
    1.12695...


Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> #
    >>> # The Timer class can also be useful for quick checks
    >>> #
    >>> import math
    >>> timer = Timer('Timer demo!', verbose=1)
    >>> x = 100000  # the input for example output
    >>> x = 10      # the input for test speed considerations
    >>> with timer:
    >>>     math.factorial(x)
    tic('Timer demo!')
    ...toc('Timer demo!')=0.1959s



"""
from __future__ import absolute_import, division, print_function, unicode_literals
import time
import sys
import itertools as it
from collections import defaultdict, OrderedDict

__all__ = ['Timer', 'Timerit']


if sys.version_info.major == 2:  # nocover
    default_time = time.clock if sys.platform.startswith('win32') else time.time
else:
    # TODO: If sys.version >= 3.7, then use time.perf_counter_ns
    default_time = time.perf_counter


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

    _default_time = default_time

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


class Timerit(object):
    """
    Reports the average time to run a block of code.

    Unlike `%timeit`, `Timerit` can handle multiline blocks of code. It runs
    inline, and doesn't depend on magic or strings. Just indent your code and
    place in a Timerit block. See https://github.com/Erotemic/vimtk for
    vim functions that will insert one of these in for you (ok that part is a
    little magic).

    Args:
        num (int, default=1): number of times to run the loop
        label (str, default=None): identifier for printing
        bestof (int, default=3): takes the max over this number of trials
        unit (str): what units time is reported in
        verbose (int): verbosity flag, defaults to True if label is given

    Attributes:
        measures - labeled measurements taken by this object
        rankings - ranked measurements (useful if more than one measurement was taken)

    Example:
        >>> import math
        >>> num = 3
        >>> t1 = Timerit(num, label='factorial', verbose=1)
        >>> for timer in t1:
        >>>     # <write untimed setup code here> this example has no setup
        >>>     with timer:
        >>>         # <write code to time here> for example...
        >>>         math.factorial(100)
        Timed best=..., mean=... for factorial
        >>> # <you can now access Timerit attributes>
        >>> assert t1.total_time > 0
        >>> assert t1.n_loops == t1.num
        >>> assert t1.n_loops == num

    Example:
        >>> # xdoc: +IGNORE_WANT
        >>> import math
        >>> num = 4
        >>> # If the timer object is unused, time will still be recorded,
        >>> # but with less precision.
        >>> for _ in Timerit(num, 'concise', bestof=2, verbose=2):
        >>>     math.factorial(100)
        Timed concise for: 4 loops, best of 2
            time per loop: best=1.637 µs, mean=1.935 ± 0.3 µs
        >>> # Using the timer object results in the most precise timings
        >>> for timer in Timerit(num, 'precise', bestof=2, verbose=3):
        >>>     with timer: math.factorial(100)
        Timed precise for: 4 loops, best of 2
            body took: 8.696 µs
            time per loop: best=1.754 µs, mean=1.821 ± 0.1 µs


    """

    _default_timer_cls = Timer
    _default_asciimode = None
    _default_precision = 3
    _default_precision_type = 'f'  # could also be reasonably be 'g' or ''

    def __init__(self, num=1, label=None, bestof=3, unit=None, verbose=None):
        if verbose is None:
            verbose = bool(label)

        self.num = num
        self.label = label
        self.bestof = bestof
        self.unit = unit
        self.verbose = verbose

        self.times = []
        self.n_loops = None
        self.total_time = None

        # Keep track of measures
        self.measures = defaultdict(dict)

        # Internal variables
        self._timer_cls = self._default_timer_cls
        self._asciimode = self._default_asciimode
        self._precision = self._default_precision
        self._precision_type = self._default_precision_type

    def reset(self, label=None, measures=False):
        """
        clears all measurements, allowing the object to be reused

        Args:
            label (str, optional) : change the label if specified
            measures (bool, default=False): if True reset measures

        Example:
            >>> import math
            >>> ti = Timerit(num=10, unit='us', verbose=True)
            >>> _ = ti.reset(label='10!').call(math.factorial, 10)
            Timed best=...s, mean=...s for 10!
            >>> _ = ti.reset(label='20!').call(math.factorial, 20)
            Timed best=...s, mean=...s for 20!
            >>> _ = ti.reset().call(math.factorial, 20)
            Timed best=...s, mean=...s for 20!
            >>> _ = ti.reset(measures=True).call(math.factorial, 20)
        """
        if label:
            self.label = label
        if measures:
            self.measures = defaultdict(dict)
        self.times = []
        self.n_loops = None
        self.total_time = None
        return self

    def call(self, func, *args, **kwargs):
        """
        Alternative way to time a simple function call using condensed syntax.

        Returns:
            self (Timerit): Use `min`, or `mean` to get a scalar. Use
                `print` to output a report to stdout.

        Example:
            >>> import math
            >>> time = Timerit(num=10).call(math.factorial, 50).min()
            >>> assert time > 0
        """
        for timer in self:
            with timer:
                func(*args, **kwargs)
        return self

    def __iter__(self):
        if self.verbose >= 3:
            print(self._status_line(tense='present'))

        self.n_loops = 0
        self.total_time = 0
        # Create a foreground and background timer
        bg_timer = self._timer_cls(verbose=0)   # (ideally this is unused)
        fg_timer = self._timer_cls(verbose=0)   # (used directly by user)
        # give the forground timer a reference to this object, so the user can
        # access this object while still constructing the Timerit object inline
        # with the for loop.
        fg_timer.parent = self
        # disable the garbage collector while timing
        with _ToggleGC(False):
            # Core timing loop
            for _ in it.repeat(None, self.num):
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
        if len(self.times) != self.num:
            raise AssertionError(
                'incorrectly recorded times, need to reset timerit object')

        self._record_measurement()

        if self.verbose > 0:
            self.print(self.verbose)

    def _record_measurement(self):
        """
        Saves the current time measurements for the current labels.
        """
        measures = self.measures
        measures['mean'][self.label] = self.mean()
        measures['min'][self.label] = self.min()
        measures['mean-std'][self.label] = self.mean() - self.std()
        measures['mean+std'][self.label] = self.mean() + self.std()
        return measures

    @property
    def rankings(self):
        """
        Orders each list of measurements by ascending time

        Example:
            >>> import math
            >>> ti = Timerit(num=1)
            >>> _ = ti.reset('a').call(math.factorial, 5)
            >>> _ = ti.reset('b').call(math.factorial, 10)
            >>> _ = ti.reset('c').call(math.factorial, 20)
            >>> ti.rankings
            >>> ti.consistency
        """
        rankings = {
            k: OrderedDict(sorted(d.items(), key=lambda kv: kv[1]))
            for k, d in self.measures.items()
        }
        return rankings

    @property
    def consistency(self):
        """"
        Take the hamming distance between the preference profiles to as a
        measure of consistency.
        """
        rankings = self.rankings

        if len(rankings) == 0:
            raise Exception('no measurements')

        hamming_sum = sum(
            k1 != k2
            for v1, v2 in it.combinations(rankings.values(), 2)
            for k1, k2 in zip(v1.keys(), v2.keys())
        )
        num_labels = len(list(rankings.values())[0])
        num_metrics = len(rankings)
        num_bits = (num_metrics * (num_metrics - 1) // 2) * num_labels
        hamming_ave = hamming_sum / num_bits
        score = 1.0 - hamming_ave
        return score

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

        Returns:
            float: minimum measured seconds over all trials

        Example:
            >>> import math
            >>> self = Timerit(num=10, verbose=0)
            >>> self.call(math.factorial, 50)
            >>> assert self.min() > 0
        """
        return min(self.times)

    def mean(self):
        """
        The mean of the best results of each trial.

        Returns:
            float: mean of measured seconds

        Note:
            This is typically less informative than simply looking at the min.
            It is recommended to use min as the expectation value rather than
            mean in most cases.

        Example:
            >>> import math
            >>> self = Timerit(num=10, verbose=0)
            >>> self.call(math.factorial, 50)
            >>> assert self.mean() > 0
        """
        chunk_iter = _chunks(self.times, self.bestof)
        times = list(map(min, chunk_iter))
        mean = sum(times) / len(times)
        return mean

    def std(self):
        """
        The standard deviation of the best results of each trial.

        Returns:
            float: standard deviation of measured seconds

        Note:
            As mentioned in the timeit source code, the standard deviation is
            not often useful. Typically the minimum value is most informative.

        Example:
            >>> import math
            >>> self = Timerit(num=10, verbose=1)
            >>> self.call(math.factorial, 50)
            >>> assert self.std() >= 0
        """
        import math
        chunk_iter = _chunks(self.times, self.bestof)
        times = list(map(min, chunk_iter))
        mean = sum(times) / len(times)
        std = math.sqrt(sum((t - mean) ** 2 for t in times) / len(times))
        return std

    def _seconds_str(self):
        """
        Returns:
            str: human readable text

        Example:
            >>> self = Timerit(num=100, bestof=10, verbose=0)
            >>> self.call(lambda : sum(range(100)))
            >>> print(self._seconds_str())
            ... 'best=3.423 µs, ave=3.451 ± 0.027 µs'
        """
        mean = self.mean()
        unit, mag = _choose_unit(mean, self.unit, self._asciimode)

        unit_min = self.min() / mag
        unit_mean = mean / mag

        # Is showing the std useful? It probably doesn't hurt.
        std = self.std()
        unit_std = std / mag
        pm = _trychar('±', '+-', self._asciimode)
        fmtstr = ('best={min:.{pr1}{t}} {unit}, '
                  'mean={mean:.{pr1}{t}} {pm} {std:.{pr2}{t}} {unit}')
        pr1 = pr2 = self._precision
        if isinstance(self._precision, int):  # pragma: nobranch
            pr2 = max(self._precision - 2, 1)
        unit_str = fmtstr.format(min=unit_min, unit=unit, mean=unit_mean,
                                 t=self._precision_type, pm=pm, std=unit_std,
                                 pr1=pr1, pr2=pr2)
        return unit_str

    def _status_line(self, tense='past'):
        """
        Text indicating what has been / is being done.

        Example:
            >>> print(Timerit()._status_line(tense='past'))
            Timed for: 1 loops, best of 1
            >>> print(Timerit()._status_line(tense='present'))
            Timing for: 1 loops, best of 1
        """
        action = {'past': 'Timed',  'present': 'Timing'}[tense]
        line = '{action} {label}for: {num:d} loops, best of {bestof:d}'.format(
            label=self.label + ' ' if self.label else '',
            action=action, num=self.num, bestof=min(self.bestof, self.num))
        return line

    def report(self, verbose=1):
        """
        Creates a human readable report

        Args:
            verbose (int): verbosity level. Either 1, 2, or 3.

        Returns:
            str: the report

        SeeAlso:
            :func:`Timerit.print`

        Example:
            >>> import math
            >>> ti = Timerit(num=1).call(math.factorial, 5)
            >>> print(ti.report(verbose=1))
            Timed best=...s, mean=...s
        """
        lines = []
        if verbose >= 2:
            # use a multi-line format for high verbosity
            lines.append(self._status_line(tense='past'))
            if verbose >= 3:
                unit, mag = _choose_unit(self.total_time, self.unit,
                                         self._asciimode)
                lines.append('    body took: {total:.{pr}{t}} {unit}'.format(
                    total=self.total_time / mag,
                    t=self._precision_type,
                    pr=self._precision, unit=unit))
            lines.append('    time per loop: {}'.format(self._seconds_str()))
        else:
            # use a single-line format for low verbosity
            line = 'Timed ' + self._seconds_str()
            if self.label:
                line += ' for ' + self.label
            lines.append(line)
        text = '\n'.join(lines)
        return text

    def print(self, verbose=1):
        """
        Prints human readable report using the print function

        Args:
            verbose (int): verbosity level

        SeeAlso:
            :func:`Timerit.report`

        Example:
            >>> import math
            >>> Timerit(num=10).call(math.factorial, 50).print(verbose=1)
            Timed best=...s, mean=...s
            >>> Timerit(num=10).call(math.factorial, 50).print(verbose=2)
            Timed for: 10 loops, best of 3
                time per loop: best=...s, mean=...s
            >>> Timerit(num=10).call(math.factorial, 50).print(verbose=3)
            Timed for: 10 loops, best of 3
                body took: ...
                time per loop: best=...s, mean=...s
        """
        print(self.report(verbose=verbose))


class _ToggleGC(object):
    """
    Context manager to disable garbage collection.

    Example:
        >>> import gc
        >>> prev = gc.isenabled()
        >>> with _ToggleGC(False):
        >>>     assert not gc.isenabled()
        >>>     with _ToggleGC(True):
        >>>         assert gc.isenabled()
        >>>     assert not gc.isenabled()
        >>> assert gc.isenabled() == prev
    """
    def __init__(self, flag):
        self.flag = flag
        self.prev = None

    def __enter__(self):
        import gc
        self.prev = gc.isenabled()
        if self.flag:
            gc.enable()
        else:
            gc.disable()

    def __exit__(self, ex_type, ex_value, trace):
        import gc
        if self.prev:
            gc.enable()
        else:
            gc.disable()


def _chunks(seq, size):
    """ simple (lighter?) two-line alternative to :func:`ubelt.chunks` """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def _choose_unit(value, unit=None, asciimode=None):
    """
    Finds a good unit to print seconds in

    Args:
        value (float): measured value in seconds
        unit (str): if specified, overrides heuristic decision
        asciimode (bool): if True, forces ascii for microseconds

    Returns:
        tuple[(str, float)]: suffix, mag:
            string suffix and conversion factor

    Example:
        >>> assert _choose_unit(1.1, unit=None)[0] == 's'
        >>> assert _choose_unit(1e-2, unit=None)[0] == 'ms'
        >>> assert _choose_unit(1e-4, unit=None, asciimode=True)[0] == 'us'
        >>> assert _choose_unit(1.1, unit='ns')[0] == 'ns'
    """
    micro = _trychar('µs', 'us', asciimode)
    units = OrderedDict([
        ('s', ('s', 1e0)),
        ('ms', ('ms', 1e-3)),
        ('us', (micro, 1e-6)),
        ('ns', ('ns', 1e-9)),
    ])
    if unit is None:
        for suffix, mag in units.values():  # pragma: nobranch
            if value > mag:
                break
    else:
        suffix, mag = units[unit]
    return suffix, mag


def _trychar(char, fallback, asciimode=None):  # nocover
    """
    Logic from IPython timeit to handle terminals that cant show mu

    Args:
        char (str): character, typically unicode, to try to use
        fallback (str): ascii character to use if stdout cannot encode char
        asciimode (bool): if True, always use fallback

    Example:
        >>> char = _trychar('µs', 'us')
        >>> print('char = {}'.format(char))
        >>> assert _trychar('µs', 'us', asciimode=True) == 'us'

    """
    if asciimode is True:
        # If we request ascii mode simply return it
        return fallback
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:  # pragma: nobranch
        try:
            char.encode(sys.stdout.encoding)
        except Exception:  # nocover
            pass
        else:
            return char
    return fallback  # nocover
