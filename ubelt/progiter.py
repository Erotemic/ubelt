"""
A Progress Iterator

ProgIter lets you measure and print the progress of an iterative process. This
can be done either via an iterable interface or using the manual API. Using the
iterable interface is most common.

ProgIter was originally developed independently of tqdm, but the newer versions
of this library have been designed to be compatible with tqdm-API.
:class:`ProgIter` is now a (mostly) drop-in alternative to :func:`tqdm.tqdm`. The
:mod:`tqdm` library may be more appropriate in some cases. *The main advantage of
:class:`ProgIter` is that it does not use any python threading*, and therefore can
be safer with code that makes heavy use of multiprocessing.
`The reason <https://pybay.com/site_media/slides/raymond2017-keynote/combo.html>`_
for this is that threading before forking may cause locks to be duplicated
across processes, which may lead to deadlocks.

ProgIter is simpler than tqdm, which may be desirable for some applications.
However, this also means ProgIter is not as extensible as tqdm.
If you want a pretty bar or need something fancy, use tqdm;
if you want useful information  about your iteration by default, use progiter.

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

TODO:
    - [ ] Specify callback that occurs whenever progress is written?
"""
import sys
import time
import collections


__all__ = [
    'ProgIter',
]

default_timer = time.perf_counter


CLEAR_BEFORE = '\r'
AT_END = '\n'


def _infer_length(iterable):
    """
    Try and infer the length using the PEP 424 length hint if available.

    adapted from click implementation
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
        """ simply writes to stdout """
        fp = file if file is not None else sys.stdout
        fp.write(s)
        fp.write(end)

    def set_description(self, desc=None, refresh=True):
        """ tqdm api compatibility. Changes the description of progress """
        self.desc = desc
        if refresh:
            self.refresh()

    def set_description_str(self, desc=None, refresh=True):
        """ tqdm api compatibility. Changes the description of progress """
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
        return 0

    @classmethod
    def set_lock(cls, lock):
        """ tqdm api compatibility. does nothing """
        pass

    @classmethod
    def get_lock(cls):
        """ tqdm api compatibility. does nothing """
        pass

    def set_postfix(self, ordered_dict=None, refresh=True, **kwargs):
        """ tqdm api compatibility. calls set_extra """
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


class ProgIter(_TQDMCompat, _BackwardsCompat):
    """
    Prints progress as an iterator progresses

    ProgIter is an alternative to `tqdm`. ProgIter implements much of the
    tqdm-API.  The main difference between `ProgIter` and `tqdm` is that
    ProgIter does not use threading where as `tqdm` does.

    Attributes:
        iterable (List | Iterable):
            A list or iterable to loop over

        desc (str):
            description label to show with progress

        total (int):
            Maximum length of the process. If not specified, we estimate it
            from the iterable, if possible.

        freq (int):
            How many iterations to wait between messages.
            Defaults to 1.

        adjust (bool):
            if True freq is adjusted based on time_thresh
            Defaults to True.

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

        show_times (bool):
            shows rate and eta, default=True

        show_wall (bool):
            show wall time, default=False

        initial (int):
            starting index offset, default=0

        stream (typing.IO):
            stream where progress information is written to, default=sys.stdout

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

    Note:
        Either use ProgIter in a with statement or call prog.end() at the end
        of the computation if there is a possibility that the entire iterable
        may not be exhausted.

    Note:
        ProgIter is an alternative to `tqdm`.  The main difference between
        `ProgIter` and `tqdm` is that ProgIter does not use threading where as
        `tqdm` does.  `ProgIter` is simpler than `tqdm` and thus more stable in
        certain circumstances.

    SeeAlso:
        tqdm - https://pypi.python.org/pypi/tqdm

    References:
        http://datagenetics.com/blog/february12017/index.html

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
                 time_thresh=2.0, show_times=True, show_wall=False,
                 enabled=True, verbose=None, stream=None, chunksize=None,
                 rel_adjust_limit=4.0, **kwargs):
        """
        Note:
            See attributes for arg information
            **kwargs accepts most of the tqdm api
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
        self.show_times = show_times
        self.show_wall = show_wall
        self.eta_window = eta_window
        self.time_thresh = time_thresh
        self.clearline = clearline
        self.chunksize = chunksize
        self.rel_adjust_limit = rel_adjust_limit
        self.extra = ''
        self.started = False
        self.finished = False

        # indicates if the cursor is currently at the start of a line (True) or
        # if characters have been written with no newline yet.
        self._cursor_at_newline = True

        self._prev_msg_len = 0  # used to ensure lines are fully cleared

        self._reset_internals()

    def __call__(self, iterable):
        self.iterable = iterable
        return iter(self)

    def __enter__(self):
        """
        Example:
            >>> # can be used as a context manager in iter mode
            >>> n = 3
            >>> with ProgIter(desc='manual', total=n, verbose=3) as prog:
            ...     list(prog(range(n)))
        """
        self.begin()
        return self

    def __exit__(self, type_, value, trace):
        if trace is not None:
            return False
        else:
            self.end()

    def __iter__(self):
        if not self.enabled:
            return iter(self.iterable)
        else:
            return self._iterate()

    def set_extra(self, extra):
        """
        specify a custom info appended to the end of the next message

        TODO:
            - [ ] extra is a bad name; come up with something better and rename

        Example:
            >>> prog = ProgIter(range(100, 300, 100), show_times=False, verbose=3)
            >>> for n in prog:
            >>>     prog.set_extra('processesing num {}'.format(n))
            0/2...
            1/2...processesing num 100
            2/2...processesing num 200
        """
        self.extra = extra

    def _iterate(self):
        """ iterates with progress """
        if not self.started:
            self.begin()
        # Wrap input sequence in a generator
        for self._iter_idx, item in enumerate(self.iterable, start=self.initial + 1):
            yield item
            # Call the body of step to reduce overyead
            # self.step(0)  # inc is 0 because we already updated
            if (self._iter_idx) % self.freq == 0:
                # update progress information every so often
                self._update_measurements()
                self._update_estimates()
                self.display_message()
        self.end()

    def step(self, inc=1, force=False):
        """
        Manually step progress update, either directly or by an increment.

        Args:
            inc (int, default=1): number of steps to increment
            force (bool, default=False): if True forces progress display

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
        _between_idx = (self._iter_idx - self._now_idx)
        if force or _between_idx >= self.freq:
            self._update_measurements()
            self._update_estimates()
            self.display_message()

    def _reset_internals(self):
        """
        Initialize all variables used in the internal state
        """
        # Prepare for iteration
        if self.total is None:
            self.total = _infer_length(self.iterable)
        self._est_seconds_left = None
        self._total_seconds = 0
        self._between_time = 0
        self._iter_idx = self.initial
        self._last_idx = self.initial - 1
        # now time is actually not right now
        # now refers the the most recent measurement
        # last refers to the measurement before that
        self._now_idx = self.initial
        self._now_time = 0
        self._between_count = -1
        self._max_between_time = -1.0
        self._max_between_count = -1.0
        self._iters_per_second = 0.0
        self._update_message_template()

    def start(self):  # nocover
        """
        Alias of :func:`ProgIter.begin`
        """
        return self.begin()

    def begin(self):
        """
        Initializes information used to measure progress

        This only needs to be used if this ProgIter is not wrapping an iterable.
        Does nothing if the this ProgIter is disabled.

        Returns:
            ProgIter:
                a chainable self-reference
        """
        if not self.enabled:
            return

        self._reset_internals()

        self._tryflush()
        self.display_message()

        # Time progress was initialized
        self._start_time = default_timer()
        # Last time measures were updated
        self._last_time  = self._start_time
        self._now_idx = self._iter_idx
        self._now_time = self._start_time

        # use last few times to compute a more stable average rate
        if self.eta_window is not None:
            self._measured_times = collections.deque(
                [], maxlen=self.eta_window)
            self._measured_times.append((self._iter_idx, self._start_time))

        # self._cursor_at_newline = True
        self._cursor_at_newline = not self.clearline
        self.started = True
        self.finished = False
        return self

    def end(self):
        """
        Signals that iteration has ended and displays the final message.

        This only needs to be used if this ProgIter is not wrapping an
        iterable.  Does nothing if the this ProgIter object is disabled or has
        already finished.
        """
        if not self.enabled or self.finished:
            return
        # Write the final progress line if it was not written in the loop
        if self._iter_idx != self._now_idx:
            self._update_measurements()
            self._update_estimates()
            self._est_seconds_left = 0
            self.display_message()
        self.ensure_newline()
        self._cursor_at_newline = True
        self.finished = True

    def _adjust_frequency(self):
        # Adjust frequency so the next print will not happen until
        # approximately `time_thresh` seconds have passed as estimated by
        # iter_idx.
        eps = 1E-9
        self._max_between_time = max(self._max_between_time,
                                     self._between_time)
        self._max_between_time = max(self._max_between_time, eps)
        self._max_between_count = max(self._max_between_count,
                                      self._between_count)

        # If progress was uniform and all time estimates were
        # perfect this would be the new freq to achieve self.time_thresh
        new_freq = int(self.time_thresh * self._max_between_count /
                       self._max_between_time)
        # But things are not perfect. So, don't make drastic changes
        rel_limit = self.rel_adjust_limit
        max_freq = int(self.freq * rel_limit)
        min_freq = int(self.freq // rel_limit)
        self.freq = max(min(new_freq, max_freq), min_freq, 1)

    def _update_measurements(self):
        """
        update current measurements and estimated of time and progress
        """
        self._last_idx = self._now_idx
        self._last_time  = self._now_time

        self._now_idx = self._iter_idx
        self._now_time = default_timer()

        self._between_time = self._now_time - self._last_time
        self._between_count = self._now_idx - self._last_idx
        self._total_seconds = self._now_time - self._start_time

        # Record that measures were updated

    def _update_estimates(self):
        # Estimate rate of progress
        if self.eta_window is None:
            self._iters_per_second = self._now_idx / self._total_seconds
        else:
            # Smooth out rate with a window
            self._measured_times.append((self._now_idx, self._now_time))
            prev_idx, prev_time = self._measured_times[0]
            self._iters_per_second =  ((self._now_idx - prev_idx) /
                                       (self._now_time - prev_time))

        if self.total is not None:
            # Estimate time remaining if total is given
            iters_left = self.total - self._now_idx
            est_eta = iters_left / self._iters_per_second
            self._est_seconds_left  = est_eta

        # Adjust frequency if printing too quickly
        # so progress does not slow down actual function
        if self.adjust and (self._between_time < self.time_thresh or
                            self._between_time > self.time_thresh * 2.0):
            self._adjust_frequency()

    def _update_message_template(self):
        self._msg_fmtstr = self._build_message_template()

    def _build_message_template(self):
        """
        Defines the template for the progress line

        Example:
            >>> self = ProgIter(show_times=True)
            >>> print(self._build_message_template()[1].strip())
            {desc} {iter_idx:4d}/?...{extra} rate={rate:{rate_format}} Hz, total={total}...

            >>> self = ProgIter(show_times=False)
            >>> print(self._build_message_template()[1].strip())
            {desc} {iter_idx:4d}/?...{extra}

            >>> self = ProgIter(total=0, show_times=True)
            >>> print(self._build_message_template()[1].strip())
            {desc} {iter_idx:1d}/0...{extra} rate={rate:{rate_format}} Hz, total={total}...
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
            msg_body = [
                ('{desc}'),
                (' {iter_idx:' + str(n_chrs) + 'd}/'),
                ('?' if length_unknown else str(self.total)),
                ('...'),
            ]

        msg_body += [
            ('{extra} '),
        ]

        if self.show_times:
            msg_body += [
                ('rate={rate:{rate_format}} Hz,'),
                (' eta={eta},' if self.total else ''),
                (' total={total}'),  # this is total time
                # (' wall={wall} ' + tzname),
            ]
        if self.show_wall:

            msg_body += [
                (', wall={wall}'),
            ]

        if self.clearline:
            parts = (CLEAR_BEFORE, ''.join(msg_body), '')
        else:
            parts = ('', ''.join(msg_body), AT_END)
        return parts

    def format_message(self):
        """
        Exists only for backwards compatibility.

        See `format_message_parts` for more recent API.
        """
        return ''.join(self.format_message_parts())

    def format_message_parts(self):
        r"""
        builds a formatted progres message with the current values.
        This contains the special characters needed to clear lines.

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

        # similar to tqdm.format_meter
        if self.chunksize and self.total:
            msg = fmtstr.format(
                desc=self.desc,
                percent=self._now_idx / self.total * 100,
                rate=self._iters_per_second * self.chunksize,
                rate_format='4.2f' if self._iters_per_second * self.chunksize > .001 else 'g',
                eta=eta, total=total,
                wall=time.strftime('%Y-%m-%d %H:%M ') + time.tzname[0] if self.show_wall else None,
                extra=self.extra,
            )
        else:
            msg = fmtstr.format(
                desc=self.desc,
                iter_idx=self._now_idx,
                rate=self._iters_per_second,
                rate_format='4.2f' if self._iters_per_second > .001 else 'g',
                eta=eta, total=total,
                wall=time.strftime('%Y-%m-%d %H:%M ') + time.tzname[0] if self.show_wall else None,
                extra=self.extra,
            )

        return before, msg, after

    def ensure_newline(self):
        """
        use before any custom printing when using the progress iter to ensure
        your print statement starts on a new line instead of at the end of a
        progress line

        Example:
            >>> # Unsafe version may write your message on the wrong line
            >>> prog = ProgIter(range(3), show_times=False, freq=2, adjust=False)
            >>> for n in prog:
            ...     print('unsafe message')
             0/3... unsafe message
            unsafe message
             2/3... unsafe message
             3/3...
            >>> # apparently the safe version does this too.
            >>> print('---')
            ---
            >>> prog = ProgIter(range(3), show_times=False, freq=2, adjust=False)
            >>> for n in prog:
            ...     prog.ensure_newline()
            ...     print('safe message')
             0/3...
            safe message
            safe message
             2/3...
            safe message
             3/3...
        """
        if not self._cursor_at_newline:
            self._write(AT_END)
            self._prev_msg_len = 0
            self._cursor_at_newline = True

    def display_message(self):
        """
        Writes current progress to the output stream
        """
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

    def _tryflush(self):
        """ flush to the internal stream """
        try:
            # flush sometimes causes issues in IPython notebooks
            self.stream.flush()
        except IOError:  # nocover
            pass

    def _write(self, msg):
        """ write to the internal stream """
        self.stream.write(msg)
