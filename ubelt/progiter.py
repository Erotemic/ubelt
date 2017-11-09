# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import time
import datetime
import collections
from math import log10, floor
import six

__all__ = [
    'ProgIter',
]

# VT100 ANSI definitions
# https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes
CLEARLINE_EL0 = '\33[0K'  # clear line to right
CLEARLINE_EL1 = '\33[1K'  # clear line to left
CLEARLINE_EL2 = '\33[2K'  # clear line
DECTCEM_HIDE = '\033[?25l'  # hide cursor
DECTCEM_SHOW = '\033[?25h'  # show cursor

WIN32 = sys.platform.startswith('win32')
WITH_ANSI = not WIN32

if WIN32:  # nocover
    # Use time.clock in win32
    default_timer = time.clock
else:  # nocover
    default_timer = time.time

if WITH_ANSI:  # pragma: nobranch
    CLEAR_BEFORE = '\r'
    AT_END = '\n'
    CLEAR_AFTER = ''
else:  # nocover
    CLEAR_BEFORE = '\r' + CLEARLINE_EL2 + DECTCEM_HIDE
    CLEAR_AFTER = CLEARLINE_EL0
    AT_END = DECTCEM_SHOW + '\n'


def _infer_length(sequence):
    """
    Try and infer the length using the PEP 424 length hint if available.

    adapted from click implementation
    """
    try:
        return len(sequence)
    except (AttributeError, TypeError):  # nocover
        try:
            get_hint = type(sequence).__length_hint__
        except AttributeError:
            return None
        try:
            hint = get_hint(sequence)
        except TypeError:
            return None
        if (hint is NotImplemented or
             not isinstance(hint, int) or
             hint < 0):
            return None
        return hint


class ProgIter(object):
    """
    Prints progress as an iterator progresses

    Attributes:
        sequence (iterable): An iterable sequence
        label (int): Maximum length of the process
            (estimated from sequence if not specified)
        label (str): Message to print
        freq (int): How many iterations to wait between messages.
        adjust (bool): if True freq is adjusted based on time_thresh
        eta_window (int): number of previous measurements to use in eta calculation
        clearline (bool): if true messages are printed on the same line
        adjust (bool): if True `freq` is adjusted based on time_thresh
        time_thresh (float): desired amount of time to wait between messages if
            adjust is True otherwise does nothing
        show_times (bool): shows rate, eta, and wall (defaults to True)
        start (int): starting index offset (defaults to 0)
        stream (file): defaults to sys.stdout
        enabled (bool): if False nothing happens.
        verbose (int): verbosity mode
            0 - no verbosity,
            1 - verbosity with clearline=True and adjust=True
            2 - verbosity without clearline=False and adjust=True
            3 - verbosity without clearline=False and adjust=False

    SeeAlso:
        tqdm - https://pypi.python.org/pypi/tqdm

    Reference:
        http://datagenetics.com/blog/february12017/index.html

    Notes:
        Either use ProgIter in a with statement or call prog.end() at the end
        of the computation if there is a possibility that the entire sequence
        may not be exhausted.

    Example:
        >>> # doctest: +SKIP
        >>> import ubelt as ub
        >>> def is_prime(n):
        ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
        >>> for n in ub.ProgIter(range(100), verbose=1):
        >>>     # do some work
        >>>     is_prime(n)
        100/100... rate=301748.49 Hz, total=0:00:00, wall=10:47 EST
    """
    def __init__(self, sequence=None, label=None, length=None, freq=1,
                 start=0, eta_window=64, clearline=True, adjust=True,
                 time_thresh=2.0, show_times=True, enabled=True, verbose=None,
                 stream=None):
        """
        Notes:
            See attributes for arg information
        """
        if label is None:
            label = ''
        if verbose is not None:
            if verbose <= 0:  # nocover
                enabled = False
            elif verbose == 1:  # nocover
                enabled, clearline, adjust = 1, 1, 1
            elif verbose == 2:  # nocover
                enabled, clearline, adjust = 1, 0, 1
            elif verbose >= 3:  # nocover
                enabled, clearline, adjust = 1, 0, 0
        if stream is None:
            stream = sys.stdout

        self.stream = stream
        self.sequence = sequence
        self.label = label
        self.length = length
        self.freq = freq
        self.offset = start
        self.enabled = enabled
        self.adjust = adjust
        self.show_times = show_times
        self.eta_window = eta_window
        self.time_thresh = 1.0
        self.clearline = clearline
        self.extra = ''
        self.started = False
        self.finished = False

    def __call__(self, sequence):
        self.sequence = sequence
        return iter(self)

    def __enter__(self):
        """
        Example:
            >>> import ubelt as ub
            >>> # can be used as a context manager in iter mode
            >>> n = 3
            >>> with ub.ProgIter(label='manual', length=n, verbose=3) as prog:
            ...     list(prog(range(n)))
        """
        self.begin()
        return self

    def __exit__(self, type, value, trace):
        if trace is not None:
            return False
        else:  # nocover
            self.end()

    def __iter__(self):
        if not self.enabled:  # nocover
            return iter(self.sequence)
        else:
            return self.iter_rate()

    def set_extra(self, extra):
        """
        specify a custom info appended to the end of the next message
        TODO: come up with a better name and rename

        Example:
            >>> import ubelt as ub
            >>> prog = ub.ProgIter(range(100, 300, 100), show_times=False, verbose=3)
            >>> for n in prog:
            >>>     prog.set_extra('processesing num {}'.format(n))
            0/2...
            1/2...processesing num 100
            2/2...processesing num 200
        """
        self.extra = extra

    def iter_rate(self):
        if not self.started:
            self.begin()
        # Wrap input sequence in a generator
        for self._iter_idx, item in enumerate(self.sequence, start=self.offset + 1):
            yield item
            if (self._iter_idx) % self.freq == 0:
                # update progress information every so often
                self.update_measurements()
                self.update_estimates()
                self.display_message()
        self.end()

    def step(self, inc=1):
        """
        Manually step progress update, either directly or by an increment.

        Args:
            idx (int): current step index (default None)
                if specified, takes precidence over `inc`
            inc (int): number of steps to increment (defaults to 1)

        Example:
            >>> import ubelt as ub
            >>> n = 3
            >>> prog = ub.ProgIter(label='manual', length=n, verbose=3)
            >>> # Need to manually begin and end in this mode
            >>> prog.begin()
            >>> for _ in range(n):
            ...     prog.step()
            >>> prog.end()

        Example:
            >>> import ubelt as ub
            >>> n = 3
            >>> # can be used as a context manager in manual mode
            >>> with ub.ProgIter(label='manual', length=n, verbose=3) as prog:
            ...     for _ in range(n):
            ...         prog.step()
        """
        self._iter_idx += inc
        self.update_measurements()
        self.update_estimates()
        self.display_message()

    def reset_internals(self):
        # Prepare for iteration
        if self.length is None:
            self.length = _infer_length(self.sequence)
        self._est_seconds_left = None
        self._total_seconds = 0
        self._between_time = 0
        self._iter_idx = self.offset
        self._last_idx = self.offset - 1
        # now time is actually not right now
        # now refers the the most recent measurment
        # last refers to the measurement before that
        self._now_idx = self.offset
        self._now_time = 0
        self._between_count = -1
        self._max_between_time = -1.0
        self._max_between_count = -1.0
        self._iters_per_second = 0.0

    def begin(self):
        """
        Initializes information used to measure progress
        """
        if not self.enabled:
            return
        # Prepare for iteration
        if self.length is None:
            self.length = _infer_length(self.sequence)

        self.reset_internals()
        self._msg_fmtstr = self.build_message_template()

        self.tryflush()
        self.display_message()

        # Time progress was initialized
        self._start_time = default_timer()
        # Last time measures were udpated
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

    def end(self):
        if not self.enabled or self.finished:
            return
        # Write the final progress line if it was not written in the loop
        if self._iter_idx != self._now_idx:
            self.update_measurements()
            self.update_estimates()
            self._est_seconds_left = 0
            self.display_message()
        self.ensure_newline()
        self._cursor_at_newline = True
        self.finished = True

    def adjust_frequency(self):
        # Adjust frequency so the next print will not happen until
        # approximatly `time_thresh` seconds have passed as estimated by
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
        new_freq = max(new_freq, 1)
        # But things are not perfect. So, don't make drastic changes
        factor = 1.5
        max_freq_change_up = max(256, int(self.freq * factor))
        max_freq_change_down = int(self.freq // factor)
        if (new_freq - self.freq) > max_freq_change_up:
            self.freq += max_freq_change_up
        elif (self.freq - new_freq) > max_freq_change_down:
            self.freq -= max_freq_change_down
        else:
            self.freq = new_freq

    def update_measurements(self):
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

    def update_estimates(self):
        # Estimate rate of progress
        if self.eta_window is None:
            self._iters_per_second = self._now_idx / self._total_seconds
        else:
            # Smooth out rate with a window
            self._measured_times.append((self._now_idx, self._now_time))
            prev_idx, prev_time = self._measured_times[0]
            self._iters_per_second =  ((self._now_idx - prev_idx) /
                                       (self._now_time - prev_time))

        if self.length is not None:
            # Estimate time remaining if length is given
            iters_left = self.length - self._now_idx
            est_eta = iters_left / self._iters_per_second
            self._est_seconds_left  = est_eta

        # Adjust frequency if printing too quickly
        # so progress doesnt slow down actual function
        if self.adjust and (self._between_time < self.time_thresh or
                            self._between_time > self.time_thresh * 2.0):
            self.adjust_frequency()

    def build_message_template(self):
        """
        Defines the template for the progress line

        Example:
            >>> # prints an eroteme if length is unknown
            >>> import ubelt as ub
            >>> sequence = (_ for _ in range(0, 10))
            >>> prog = ub.ProgIter(sequence, label='unknown seq', show_times=False, verbose=1)
            >>> for n in prog:
            ...     pass
            unknown seq   10/?...
        """
        tzname = time.tzname[0]
        length_unknown = self.length is None or self.length <= 0
        if length_unknown:
            n_chrs = 4
        else:
            n_chrs = int(floor(log10(float(self.length))) + 1)
        msg_body = [
            (self.label),
            (' {iter_idx:' + str(n_chrs) + 'd}/'),
            ('?' if length_unknown else six.text_type(self.length)),
            ('...'),
        ]

        msg_body += [
            ('{extra} '),
        ]

        if self.show_times:
            msg_body += [
                    ('rate={rate:{rate_format}} Hz,'),
                    (' eta={eta},' if self.length else ''),
                    (' total={total},'),
                    (' wall={wall} ' + tzname),
            ]
        if self.clearline:
            msg_body = [CLEAR_BEFORE] + msg_body + [CLEAR_AFTER]
        else:
            msg_body = msg_body + [AT_END]
        msg_fmtstr_time = ''.join(msg_body)
        return msg_fmtstr_time

    def format_message(self):
        """ formats the progress template with current values """
        if self._est_seconds_left is None:
            eta = '?'
        else:
            eta = six.text_type(datetime.timedelta(
                seconds=int(self._est_seconds_left)))
        total = six.text_type(datetime.timedelta(
            seconds=int(self._total_seconds)))
        msg = self._msg_fmtstr.format(
            iter_idx=self._now_idx,
            rate=self._iters_per_second,
            rate_format='4.2f' if self._iters_per_second > .001 else 'g',
            eta=eta, total=total,
            wall=time.strftime('%H:%M'),
            extra=self.extra,
        )
        return msg

    def ensure_newline(self):
        """
        use before any custom printing when using the progress iter to ensure
        your print statement starts on a new line instead of at the end of a
        progress line

        Example:
            >>> # Unsafe version may write your message on the wrong line
            >>> import ubelt as ub
            >>> prog = ub.ProgIter(range(4), show_times=False, verbose=1)
            >>> for n in prog:
            ...     print('unsafe message')
             0/4...  unsafe message
             1/4...  unsafe message
            unsafe message
            unsafe message
             4/4...
            >>> # apparently the safe version does this too.
            >>> print('---')
            ---
            >>> prog = ub.ProgIter(range(4), show_times=False, verbose=1)
            >>> for n in prog:
            ...     prog.ensure_newline()
            ...     print('safe message')
             0/4...
            safe message
             1/4...
            safe message
            safe message
            safe message
             4/4...
        """
        if not self._cursor_at_newline:
            self.write(AT_END)
            self._cursor_at_newline = True

    def display_message(self):
        """ Writes current progress to the output stream """
        msg = self.format_message()
        self.write(msg)
        self.tryflush()
        self._cursor_at_newline = not self.clearline

    def tryflush(self):
        try:
            # flush sometimes causes issues in IPython notebooks
            self.stream.flush()
        except IOError:  # nocover
            pass

    def write(self, msg):
        self.stream.write(msg)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.progiter
        python -m ubelt.progiter all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
