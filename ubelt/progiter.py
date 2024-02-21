"""
A Progress Iterator

ProgIter lets you measure and print the progress of an iterative process. This
can be done either via an iterable interface or using the manual API. Using the
iterable interface is most common.

The basic usage of ProgIter is simple and intuitive. Just wrap a python
iterable.  The following example wraps a ``range`` iterable and prints reported
progress to stdout as the iterable is consumed.

Example:
    >>> for n in ProgIter(range(1000)):
    >>>     # do some work
    >>>     pass

Note that by default ProgIter reports information about iteration-rate,
fraction-complete, estimated time remaining, time taken so far, and the current
wall time.

Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> def is_prime(n):
    ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
    >>> for n in ProgIter(range(1000), verbose=1):
    >>>     # do some work
    >>>     is_prime(n)
    1000/1000... rate=114326.51 Hz, eta=0:00:00, total=0:00:00


For more complex applications is may sometimes be desirable to
manually use the ProgIter API. This is done as follows:

Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> n = 3
    >>> prog = ProgIter(desc='manual', total=n, verbose=3)
    >>> prog.begin() # Manually begin progress iteration
    >>> for _ in range(n):
    ...     prog.step(inc=1)  # specify the number of steps to increment
    >>> prog.end()  # Manually end progress iteration
    manual 0/3... rate=0 Hz, eta=?, total=0:00:00
    manual 1/3... rate=14454.63 Hz, eta=0:00:00, total=0:00:00
    manual 2/3... rate=17485.42 Hz, eta=0:00:00, total=0:00:00
    manual 3/3... rate=21689.78 Hz, eta=0:00:00, total=0:00:00


When working with ProgIter in either iterable or manual mode you can use the
``prog.ensure_newline`` method to guarantee that the next call you make to
stdout will start on a new line. You can also use the ``prog.set_extra`` method
to update a dynamci "extra" message that is shown in the formatted output. The
following example demonstrates this.

Example:
    >>> # xdoctest: +IGNORE_WANT
    >>> def is_prime(n):
    ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
    >>> _iter = range(1000)
    >>> prog = ProgIter(_iter, desc='check primes', verbose=2, show_wall=True)
    >>> for n in prog:
    >>>     if n == 97:
    >>>         print('!!! Special print at n=97 !!!')
    >>>     if is_prime(n):
    >>>         prog.set_extra('Biggest prime so far: {}'.format(n))
    >>>         prog.ensure_newline()
    check primes    0/1000... rate=0 Hz, eta=?, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes    1/1000... rate=95547.49 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes    4/1000...Biggest prime so far: 3 rate=41062.28 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes   16/1000...Biggest prime so far: 13 rate=85340.61 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes   64/1000...Biggest prime so far: 61 rate=164739.98 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    !!! Special print at n=97 !!!
    check primes  256/1000...Biggest prime so far: 251 rate=206287.91 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes  512/1000...Biggest prime so far: 509 rate=165271.92 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes  768/1000...Biggest prime so far: 761 rate=136480.12 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
    check primes 1000/1000...Biggest prime so far: 997 rate=115214.95 Hz, eta=0:00:00, total=0:00:00, wall=2020-10-23 17:27 EST
"""
import sys
import time
import collections
from itertools import islice

__all__ = [
    'ProgIter',
]

default_timer = time.perf_counter  # type: Callable

# A measurment takes place at a given iteration and posixtime.
Measurement = collections.namedtuple('Measurement', ['idx', 'time'])


CLEAR_BEFORE = '\r'
AT_END = '\n'


def _infer_length(iterable):
    """
    Try and infer the length using the PEP 424 length hint if available.

    adapted from click implementation

    Args:
        iterable (Iterable):

    Returns:
        int | None
    """
    try:
        return len(iterable)
    except (AttributeError, TypeError):  # nocover
        try:
            get_hint = type(iterable).__length_hint__
        except AttributeError:
            return None
        try:
            hint = get_hint(iterable)
        except TypeError:
            return None
        if (hint is NotImplemented or
             not isinstance(hint, int) or
             hint < 0):
            return None
        return hint


class _TQDMCompat(object):
    """
    Base class for ProgIter that implements a restricted TQDM Compatibility API
    """

    @classmethod
    def write(cls, s, file=None, end='\n', nolock=False):
        """
        simply writes to stdout

        Args:
            s (str): string
            file (None | SupportsWrite):
            end (str): end of line
            nolock (bool):
        """
        fp = file if file is not None else sys.stdout
        fp.write(s)
        fp.write(end)

    def set_description(self, desc=None, refresh=True):
        """
        tqdm api compatibility. Changes the description of progress

        Args:
            desc (str | None): description
        """
        self.desc = desc
        if refresh:
            self.refresh()

    def set_description_str(self, desc=None, refresh=True):
        """
        tqdm api compatibility. Changes the description of progress

        Args:
            desc (str | None): description string
        """
        self.set_description(desc, refresh)

    def update(self, n=1):
        """ alias of `step` for tqdm compatibility """
        self.step(n)

    def close(self):
        """ alias of `end` for tqdm compatibility """
        self.end()

    def unpause(self):
        """ tqdm api compatibility. does nothing """
        pass

    def moveto(self, n):
        """ tqdm api compatibility. does nothing """
        pass

    def clear(self, nolock=False):
        """ tqdm api compatibility. does nothing """
        pass

    def refresh(self, nolock=False):
        """
        tqdm api compatibility. redisplays message
        (can cause a message to print twice)
        """
        if not self.started:
            self.begin()
        self.display_message()

    @property
    def pos(self):
        """
        Returns:
            int
        """
        return 0

    @classmethod
    def set_lock(cls, lock):
        """ tqdm api compatibility. does nothing """
        pass

    @classmethod
    def get_lock(cls):
        """ tqdm api compatibility. does nothing """
        pass

    def set_postfix_dict(self, ordered_dict=None, refresh=True, **kwargs):
        """
        tqdm api compatibility. calls set_extra

        Args:
            ordered_dict (None | dict):
            refresh (bool):
            **kwargs:
        """
        # Sort in alphabetical order to be more deterministic
        postfix = collections.OrderedDict(
            [] if ordered_dict is None else ordered_dict)
        for key in sorted(kwargs.keys()):
            postfix[key] = kwargs[key]
        # Preprocess stats according to datatype
        for key in postfix.keys():
            import numbers
            # Number: limit the length of the string
            if isinstance(postfix[key], numbers.Number):
                postfix[key] = '{0:2.3g}'.format(postfix[key])
            # Else for any other type, try to get the string conversion
            elif not isinstance(postfix[key], str):
                postfix[key] = str(postfix[key])
            # Else if it's a string, don't need to preprocess anything
        # Stitch together to get the final postfix
        postfix = ', '.join(key + '=' + postfix[key].strip()
                                 for key in postfix.keys())
        self.set_postfix_str(postfix, refresh=refresh)

    def set_postfix(self, postfix, **kwargs):
        if isinstance(postfix, str):
            self.set_postfix_str(postfix, **kwargs)
        else:
            self.set_postfix_dict(ordered_dict=postfix, **kwargs)

    def set_postfix_str(self, s='', refresh=True):
        """ tqdm api compatibility. calls set_extra """
        self.set_extra(str(s))
        if refresh:
            self.refresh()


class _BackwardsCompat(object):
    """
    Base class for ProgIter that maintains backwards compatibility with older
    versions of the ProgIter API.
    """

    # Backwards Compatibility API
    @property
    def length(self):
        """ alias of total """
        return self.total

    @property
    def label(self):
        """ alias of desc """
        return self.desc

    def start(self):  # nocover
        """
        Alias of :func:`ProgIter.begin`
        """
        return self.begin()

    def stop(self):  # nocover
        """
        Alias of :func:`ProgIter.end`
        """
        return self.end()


class ProgIter(_TQDMCompat, _BackwardsCompat):
    """
    Prints progress as an iterator progresses

    ProgIter is an alternative to `tqdm`. ProgIter implements much of the
    tqdm-API.  The main difference between `ProgIter` and `tqdm` is that
    ProgIter does not use threading whereas `tqdm` does.

    Attributes:

    Note:
        Either use ProgIter in a with statement or call prog.end() at the end
        of the computation if there is a possibility that the entire iterable
        may not be exhausted.

    Note:
        ProgIter is an alternative to `tqdm`.  The main difference between
        `ProgIter` and `tqdm` is that ProgIter does not use threading whereas
        `tqdm` does.  `ProgIter` is simpler than `tqdm` and thus more stable in
        certain circumstances.

    SeeAlso:
        tqdm - https://pypi.python.org/pypi/tqdm

    References:
        .. [DatagenProgBars] http://datagenetics.com/blog/february12017/index.html

    Example:
        >>> # doctest: +SKIP
        >>> def is_prime(n):
        ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
        >>> for n in ProgIter(range(100), verbose=1, show_wall=True):
        >>>     # do some work
        >>>     is_prime(n)
        100/100... rate=... Hz, total=..., wall=...
    """
    def __init__(self, iterable=None, desc=None, total=None, freq=1,
                 initial=0, eta_window=64, clearline=True, adjust=True,
                 time_thresh=2.0, show_percent=True, show_times=True,
                 show_rate=True, show_eta=True, show_total=True,
                 show_wall=False, enabled=True, verbose=None, stream=None,
                 chunksize=None, rel_adjust_limit=4.0, homogeneous='auto',
                 timer=None, **kwargs):
        """
        See attributes more arg information

        Args:
            iterable (List | Iterable):
                A list or iterable to loop over

            desc (str | None):
                description label to show with progress

            total (int | None):
                Maximum length of the process. If not specified, we estimate it
                from the iterable, if possible.

            freq (int):
                How many iterations to wait between messages.
                Defaults to 1.

            initial (int):
                starting index offset, default=0

            eta_window (int):
                number of previous measurements to use in eta calculation, default=64

            clearline (bool):
                if True messages are printed on the same line otherwise each new
                progress message is printed on new line.
                default=True

            adjust (bool):
                if True `freq` is adjusted based on time_thresh. This may be
                overwritten depending on the setting of verbose.
                default=True

            time_thresh (float):
                desired amount of time to wait between messages if adjust is True
                otherwise does nothing, default=2.0

            show_percent (bool):
                if True show percent progress. Default=True

            show_times (bool):
                if False do not show rate, eta, or wall time.  default=True
                Deprecated. Use show_rate / show_eta / show_wall instead.

            show_rate (bool):
                show / hide rate, default=True

            show_eta (bool):
                show / hide estimated time of arival (i.e. time to completion),
                default=True

            show_wall (bool):
                show / hide wall time, default=False

            stream (typing.IO):
                stream where progress information is written to, default=sys.stdout

            timer (callable):
                the timer object to use. Defaults to :func:`time.perf_counter`.

            enabled (bool): if False nothing happens. default=True

            chunksize (int | None):
                indicates that each iteration processes a batch of this size.
                Iteration rate is displayed in terms of single-items.

            rel_adjust_limit (float):
                Maximum factor update frequency can be adjusted by in a single
                step. default=4.0

            verbose (int):
                verbosity mode, which controls clearline, adjust, and enabled. The
                following maps the value of `verbose` to its effect.
                0: enabled=False,
                1: enabled=True with clearline=True and adjust=True,
                2: enabled=True with clearline=False and adjust=True,
                3: enabled=True with clearline=False and adjust=False

            homogeneous (bool | str):
                Indicate if the iterable is likely to take a uniform or homogeneous
                amount of time per iteration. When True we can enable a speed
                optimization. When False, the time estimates are more accurate.
                Default to "auto", which attempts to determine if it is safe to use
                True. Has no effect if ``adjust`` is False.

            show_total (bool):
                if True show total time.

            **kwargs: accepts most of the tqdm api
        """
        if desc is None:
            desc = ''
        if verbose is not None:
            if verbose <= 0:  # nocover
                enabled = False
            elif verbose == 1:  # nocover
                enabled, clearline, adjust = 1, 1, 1
            elif verbose == 2:  # nocover
                enabled, clearline, adjust = 1, 0, 1
            elif verbose >= 3:  # nocover
                enabled, clearline, adjust = 1, 0, 0

        # Potential new additions to the API
        self._microseconds = kwargs.pop('microseconds', False)

        # --- Accept the tqdm api ---
        if kwargs:
            stream = kwargs.pop('file', stream)
            enabled = not kwargs.pop('disable', not enabled)
            if kwargs.get('miniters', None) is not None:
                adjust = False
            freq = kwargs.pop('miniters', freq)

            kwargs.pop('position', None)  # API compatibility does nothing
            kwargs.pop('dynamic_ncols', None)  # API compatibility does nothing
            kwargs.pop('leave', True)  # we always leave

            # Accept the old api keywords
            desc = kwargs.pop('label', desc)
            total = kwargs.pop('length', total)
            enabled = kwargs.pop('enabled', enabled)
            initial = kwargs.pop('start', initial)
            time_thresh = kwargs.pop('mininterval', time_thresh)
        if kwargs:
            raise ValueError('ProgIter given unknown kwargs {}'.format(kwargs))
        # ----------------------------

        if stream is None:
            stream = sys.stdout

        self.stream = stream
        self.iterable = iterable
        self.desc = desc
        self.total = total
        self.freq = freq
        self.initial = initial
        self.enabled = enabled
        self.adjust = adjust
        self.show_percent = show_percent
        self.show_times = show_times
        self.show_rate = show_rate
        self.show_eta = show_eta
        self.show_total = show_total
        self.show_wall = show_wall
        self.eta_window = eta_window
        self.time_thresh = time_thresh
        self.clearline = clearline
        self.chunksize = chunksize
        self.rel_adjust_limit = rel_adjust_limit
        self.extra = ''
        self._extra_fn = None
        self.started = False
        self.finished = False

        if timer is None:
            timer = default_timer
        self._timer = timer

        self.homogeneous = homogeneous
        self._likely_homogeneous = None

        # indicates if the cursor is currently at the start of a line (True) or
        # if characters have been written with no newline yet.
        self._cursor_at_newline = True

        self._prev_msg_len = 0  # used to ensure lines are fully cleared

        self._reset_internals()

    def __call__(self, iterable):
        """
        Overwrites the current iterator with iterable and starts iterating on
        it.

        Warning:
            Using this function is not recommended.

        Args:
            iterable (Iterable):

        Returns:
            Iterable
        """
        self.iterable = iterable
        return iter(self)

    def __enter__(self):
        """
        Returns:
            ProgIter

        Example:
            >>> # can be used as a context manager in iter mode
            >>> n = 3
            >>> with ProgIter(desc='manual', total=n, verbose=3) as prog:
            ...     list(prog(range(n)))
        """
        self.begin()
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """
        Args:
            ex_type (Type[BaseException] | None):
            ex_value (BaseException | None):
            ex_traceback (TracebackType | None):

        Returns:
            bool | None
        """
        if ex_traceback is not None:  # nocover
            return False
        else:
            self.end()

    def __iter__(self):
        """
        Returns:
            Iterable
        """
        if not self.enabled:
            return iter(self.iterable)
        else:
            return self._iterate()

    def set_extra(self, extra):
        """
        specify a custom info appended to the end of the next message

        Args:
            extra (str | Callable):
                a constant or dynamically constructed extra message.

        TODO:
            - [ ] extra is a bad name; come up with something better and rename

        Example:
            >>> prog = ProgIter(range(100, 300, 100), show_times=False, verbose=3)
            >>> for n in prog:
            >>>     prog.set_extra('processesing num {}'.format(n))
             0.00% 0/2...
             50.00% 1/2...processesing num 100
             100.00% 2/2...processesing num 200
        """
        if callable(extra):
            self._extra_fn = extra
        else:
            self._extra_fn = None
        self.extra = extra

    def _reset_internals(self):
        """
        Initialize all variables used in the internal state
        """
        # Prepare for iteration
        if self.total is None:
            self.total = _infer_length(self.iterable)

        # Track the total time up to the most recent measurement.
        self._total_seconds = 0

        # Track the current iteration we are on
        self._iter_idx = self.initial

        # Track the last time we displayed a message
        self._display_measurement = Measurement(-1, -1)

        # Track the most recent iteration/time a measurement was made
        self._curr_measurement = Measurement(self.initial, 0)

        # Track the number of iterations and time between the last two measurements
        self._measure_countdelta = -1
        self._measure_timedelta = self.time_thresh
        self._display_timedelta = self.time_thresh
        self._next_measure_idx = self._iter_idx + self.freq

        # Primary estimates
        self._est_seconds_left = None
        self._iters_per_second = 0.0

        # hack flag that should be refactored and removed used to ensure the
        # first message after begin is displayed.
        self._force_next_display = False

        self._update_message_template()

    def begin(self):
        """
        Initializes information used to measure progress

        This only needs to be used if this ProgIter is not wrapping an iterable.
        Does nothing if this ProgIter is disabled.

        Returns:
            ProgIter:
                a chainable self-reference
        """
        if not self.enabled:
            return

        self._reset_internals()

        # Time progress was initialized
        self._start_time = self._timer()
        # Last time measures were updated
        self._curr_measurement = Measurement(self._iter_idx, self._start_time)

        # use last few times to compute a more stable average rate
        if self.eta_window is not None:
            self._measurements = collections.deque([
                self._curr_measurement
            ], maxlen=self.eta_window)
        else:
            self._measurements = collections.deque([
                self._curr_measurement
            ], maxlen=2)

        # self._cursor_at_newline = True
        self._cursor_at_newline = not self.clearline
        self.started = True
        self.finished = False

        self._tryflush()
        self.display_message()

        # The start message isn't very helpful.
        # If we enable this we could force the first iteration.
        self._force_next_display = self.freq == 1
        return self

    def end(self):
        """
        Signals that iteration has ended and displays the final message.

        This only needs to be used if this ProgIter is not wrapping an
        iterable.  Does nothing if this ProgIter object is disabled or has
        already finished.
        """
        if not self.enabled or self.finished:
            return
        # Write the final progress line if it was not written in the loop
        if self._iter_idx != self._display_measurement.idx:
            self._measure_time()
            self._est_seconds_left = 0
            self.display_message()
        self.ensure_newline()
        self._cursor_at_newline = True
        self.finished = True

    def _iterate(self):
        """ iterates with progress """
        if not self.started:
            self.begin()
        # Wrap input sequence in a generator
        gen = enumerate(self.iterable, start=self.initial + 1)
        # Iterating is performance sensitive, so separate both cases - where
        # 'freq' is used and checks can be fast, and where 'adjust' is used and
        # checks need more calculation. This is worth duplicating code for.

        if self.adjust:
            homogeneous = self.homogeneous
            if homogeneous == 'auto':
                yield from self._homogeneous_check(gen)
                homogeneous = self._likely_homogeneous

            if homogeneous:
                use_fast_path = True
            else:
                use_fast_path = False
                # Slow path where we do checks every iteration.
                for self._iter_idx, item in gen:
                    yield item
                    self._slow_path_step_body()
        else:
            use_fast_path = True

        if use_fast_path:
            # In the fast path we only check the time every `freq` iterations.
            for self._iter_idx, item in gen:
                yield item
                if self._force_next_display or self._iter_idx >= self._next_measure_idx:
                    self._measure_time()
                    if self._force_next_display or (self._display_timedelta >= self.time_thresh):
                        self.display_message()

        self.end()

    def _homogeneous_check(self, gen):
        # NOTE: We could have a more complex heuristic with negligable
        # overhead and more robustness that checks every n iterations
        # that such that the time call overhead would be negligable.
        # To do this we would need a semi-fast mode that does the fast
        # mode for a fixed number of iterations and then rechecks the
        # slow mode. Or something like that.
        # NOTE: We could also try to find a pseudo property to check to
        # see if things are changing. Is this faster than a call to
        # time.time?
        # Take a few steps in the slow path and then check to see
        # if we should continue or do go down the fast path.
        num_initial_steps = 5

        # A call to time is 50ns, we can accept the overhead if it
        # is only .01% of the total loop time
        overhead_threshold = 50e-9 * 10_000

        slowest = 0
        for self._iter_idx, item in islice(gen, num_initial_steps):
            yield item
            self._slow_path_step_body()
            slowest = max(slowest, self._measure_timedelta)

        # We are moving fast, take the faster path
        self._likely_homogeneous = (slowest < overhead_threshold)

    def _slow_path_step_body(self, force=False):
        # In the slow path, we don't make any assumption about how long
        # iterations take. So on every iteration we must measure the time
        self._measure_time()
        if force or (self._display_timedelta >= self.time_thresh):
            self.display_message()

    def step(self, inc=1, force=False):
        """
        Manually step progress update, either directly or by an increment.

        Args:
            inc (int): number of steps to increment. Defaults to 1.
            force (bool): if True forces progress display. Defaults to False.

        Example:
            >>> n = 3
            >>> prog = ProgIter(desc='manual', total=n, verbose=3)
            >>> # Need to manually begin and end in this mode
            >>> prog.begin()
            >>> for _ in range(n):
            ...     prog.step()
            >>> prog.end()

        Example:
            >>> n = 3
            >>> # can be used as a context manager in manual mode
            >>> with ProgIter(desc='manual', total=n, verbose=3) as prog:
            ...     for _ in range(n):
            ...         prog.step()
        """
        if not self.enabled:
            return

        self._iter_idx += inc
        self._slow_path_step_body(force=force)

    def _adjust_frequency(self):
        # Adjust frequency so the next print will not happen until
        # approximately `time_thresh` seconds have passed as estimated by
        # iter_idx.

        # If progress was uniform and all time estimates were
        # perfect this would be the new freq to achieve self.time_thresh
        eps = 1E-9
        new_freq = int(self.time_thresh * self._measure_countdelta /
                       max(eps, self._measure_timedelta))
        # But things are not perfect. So, don't make drastic changes
        rel_limit = self.rel_adjust_limit
        max_freq = int(self.freq * rel_limit)
        min_freq = int(self.freq // rel_limit)
        self.freq = max(min(new_freq, max_freq), min_freq, 1)

    def _measure_time(self):
        """
        Measures the current time and update info about how long we've been
        waiting since the last iteration was displayed.
        """
        _prev_measurement = self._measurements[-1]
        if _prev_measurement.idx == self._iter_idx:
            # We already recorded this time measurement
            # raise AssertionError("PROBABLY SHOULD NOT BE HERE")
            return

        _curr_measurement = Measurement(self._iter_idx, self._timer())

        self._curr_measurement = _curr_measurement
        self._measurements.append(_curr_measurement)

        self._measure_timedelta = _curr_measurement.time - _prev_measurement.time
        self._measure_countdelta = _curr_measurement.idx - _prev_measurement.idx
        self._total_seconds = _curr_measurement.time - self._start_time

        self._display_timedelta = (self._curr_measurement.time -
                                   self._display_measurement.time)

        # Estimate rate of progress
        if self.eta_window is None:
            self._iters_per_second = self._curr_measurement.idx / self._total_seconds
        else:
            # Smooth out rate with a window
            oldest_idx, oldest_time = self._measurements[0]
            latest_idx, latest_time = self._measurements[-1]
            self._iters_per_second =  ((latest_idx - oldest_idx) /
                                       (latest_time - oldest_time))

        if self.total is not None:
            # Estimate time remaining if total is given
            iters_left = self.total - self._curr_measurement.idx
            est_eta = iters_left / self._iters_per_second
            self._est_seconds_left = est_eta

        # Adjust frequency to stay within time_thresh
        if self.adjust and (self._measure_timedelta < self.time_thresh or
                            self._measure_timedelta > self.time_thresh * 2.0):
            self._adjust_frequency()

        # Mark when our next measurement should be in "fast mode"
        self._next_measure_idx = self._iter_idx + self.freq

    def _update_message_template(self):
        self._msg_fmtstr = self._build_message_template()

    def _build_message_template(self):
        """
        Defines the template for the progress line

        Returns:
            Tuple[str, str, str]

        Example:
            >>> self = ProgIter()
            >>> print(self._build_message_template()[1].strip())
            {desc} {iter_idx:4d}/?...{extra} rate={rate:{rate_format}} Hz, total={total}...

            >>> self = ProgIter(show_total=False, show_eta=False, show_rate=False)
            >>> print(self._build_message_template()[1].strip())
            {desc} {iter_idx:4d}/?...{extra}

            >>> self = ProgIter(total=0, show_times=True)
            >>> print(self._build_message_template()[1].strip())
            {desc} {percent:03.2f}% {iter_idx:1d}/0...{extra} rate={rate:{rate_format}} Hz, total={total}
        """
        from math import log10, floor
        length_unknown = self.total is None or self.total < 0
        if length_unknown:
            n_chrs = 4
        else:
            if self.total == 0:
                n_chrs = 1
            else:
                n_chrs = int(floor(log10(float(self.total))) + 1)

        if self.chunksize and not length_unknown:
            msg_body = [
                ('{desc}'),
                (' {percent:03.2f}% of ' + str(self.chunksize) + 'x'),
                ('?' if length_unknown else str(self.total)),
                ('...'),
            ]
        else:
            if self.show_percent and not length_unknown:
                msg_body = [
                    ('{desc}'),
                    (' {percent:03.2f}% {iter_idx:' + str(n_chrs) + 'd}/'),
                    ('?' if length_unknown else str(self.total)),
                    ('...'),
                ]
            else:
                msg_body = [
                    ('{desc}'),
                    (' {iter_idx:' + str(n_chrs) + 'd}/'),
                    ('?' if length_unknown else str(self.total)),
                    ('...'),
                ]

        msg_body.append('{extra} ')

        if self.show_times:
            if self.show_rate:
                msg_body.append('rate={rate:{rate_format}} Hz,')

            if self.show_eta:
                msg_body.append(' eta={eta},' if self.total else '')

            if self.show_total:
                msg_body.append(' total={total}')  # this is total time

            if self.show_wall:
                msg_body.append(', wall={wall}')

        if self.clearline:
            parts = (CLEAR_BEFORE, ''.join(msg_body), '')
        else:
            parts = ('', ''.join(msg_body), AT_END)
        return parts

    def format_message(self):
        """
        Exists only for backwards compatibility.

        See `format_message_parts` for more recent API.

        Returns:
            str
        """
        return ''.join(self.format_message_parts())

    def format_message_parts(self):
        r"""
        builds a formatted progress message with the current values.
        This contains the special characters needed to clear lines.

        Returns:
            Tuple[str, str, str]

        Example:
            >>> self = ProgIter(clearline=False, show_times=False)
            >>> print(repr(self.format_message_parts()[1]))
            '    0/?... '
            >>> self.begin()
            >>> self.step()
            >>> print(repr(self.format_message_parts()[1]))
            ' 1/?... '

        Example:
            >>> self = ProgIter(chunksize=10, total=100, clearline=False,
            >>>                 show_times=False, microseconds=True)
            >>> # hack, microseconds=True for coverage, needs real test
            >>> print(repr(self.format_message_parts()[1]))
            ' 0.00% of 10x100... '
            >>> self.begin()
            >>> self.update()  # tqdm alternative to step
            >>> print(repr(self.format_message_parts()[1]))
            ' 1.00% of 10x100... '
        """
        from datetime import timedelta
        if self._est_seconds_left is None:
            eta = '?'
        else:
            if self._microseconds:
                eta = str(timedelta(seconds=self._est_seconds_left))
            else:
                eta = str(timedelta(seconds=int(self._est_seconds_left)))

        if self._microseconds:
            total = str(timedelta(seconds=self._total_seconds))
        else:
            total = str(timedelta(seconds=int(self._total_seconds)))

        before, fmtstr, after = self._msg_fmtstr

        if self._extra_fn is not None:
            # User requested a dynamic extra callback.
            extra = self._extra_fn()
        else:
            extra = self.extra

        fmtkw = {
            'desc': self.desc,
            'iter_idx': self._curr_measurement.idx,
            'eta': eta,
            'total': total,
            'wall': time.strftime('%Y-%m-%d %H:%M ') + time.tzname[0] if self.show_wall else None,
            'extra': extra,
            'percent': '',
        }

        # similar to tqdm.format_meter
        if self.chunksize and self.total:
            fmtkw.update({
                'percent': self._curr_measurement.idx / self.total * 100,
                'rate': self._iters_per_second * self.chunksize,
                'rate_format': '4.2f' if self._iters_per_second * self.chunksize > .001 else 'g',
            })
        else:
            fmtkw.update({
                'percent': self._curr_measurement.idx / self.total * 100 if self.total is not None and self.total > 0 else 0,
                'rate': self._iters_per_second,
                'rate_format': '4.2f' if self._iters_per_second > .001 else 'g',
            })
        msg = fmtstr.format(**fmtkw)

        return before, msg, after

    def ensure_newline(self):
        """
        use before any custom printing when using the progress iter to ensure
        your print statement starts on a new line instead of at the end of a
        progress line

        Example:
            >>> # Unsafe version may write your message on the wrong line
            >>> prog = ProgIter(range(3), show_times=False, freq=2, adjust=False,
            ...                 time_thresh=0)
            >>> for n in prog:
            ...     print('unsafe message')
             0.00% 0/3... unsafe message
            unsafe message
             66.67% 2/3... unsafe message
             100.00% 3/3...
            >>> # apparently the safe version does this too.
            >>> print('---')
            ---
            >>> prog = ProgIter(range(3), show_times=False, freq=2, adjust=False,
            ...                 time_thresh=0)
            >>> for n in prog:
            ...     prog.ensure_newline()
            ...     print('safe message')
             0.00% 0/3...
            safe message
            safe message
             66.67% 2/3...
            safe message
             100.00% 3/3...
        """
        if not self._cursor_at_newline:
            self._write(AT_END)
            self._prev_msg_len = 0
            self._cursor_at_newline = True

    def display_message(self):
        """
        Writes current progress to the output stream
        """
        # When we make a display, ensure need to have a recent time measurement
        if self._curr_measurement.idx != self._iter_idx:
            self._measure_time()

        before, msg, after = self.format_message_parts()
        msg_len = len(msg)  # TODO account for unicode
        if self.clearline:
            padding = self._prev_msg_len - msg_len
            if padding > 0:
                msg = msg + ' ' * padding
        self._write(''.join([before, msg, after]))
        self._prev_msg_len = msg_len
        self._tryflush()
        self._cursor_at_newline = not self.clearline
        self._display_measurement = self._curr_measurement
        self._display_timedelta = 0
        self._force_next_display = False

    def _tryflush(self):
        """ flush to the internal stream """
        try:
            # flush sometimes causes issues in IPython notebooks
            self.stream.flush()
        except IOError:  # nocover
            pass

    def _write(self, msg):
        """
        write to the internal stream

        Args:
            msg (str): message to write
        """
        self.stream.write(msg)
