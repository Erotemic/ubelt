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


def _infer_length(iterable):
    # use PEP 424 length hint if available
    # adapted from click implementation
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


class ProgIter(object):
    """
    Attributes:
        iterable : sequence
            A python iterable
        label : int
            Maximum length of the process
                (estimated from iterable if not specified)
        label : str
            Message to print
        freq : int
            How many iterations to wait between messages.
        adjust : bool
            if True freq is adjusted based on time_thresh
        eta_window : int
            number of previous measurements to use in eta calculation
        clearline : bool
            if true messages are printed on the same line
        adjust : bool
            if True `freq` is adjusted based on time_thresh
        time_thresh : float
            desired amount of time to wait between messages if adjust is True
            otherwise does nothing
        stream : file
            defaults to sys.stdout
        enabled : bool
             if False nothing happens.
        verbose : int
            verbosity mode
            0 - no verbosity,
            1 - verbosity with clearline=True and adjust=True
            2 - verbosity without clearline=False and adjust=True
            3 - verbosity without clearline=False and adjust=False

    SeeAlso:
        tqdm - https://pypi.python.org/pypi/tqdm

    Reference:
        http://datagenetics.com/blog/february12017/index.html

    Examples:
        >>> import ubelt as ub
        >>> def is_prime(n):
        ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
        >>> for n in ub.ProgIter(range(100), verbose=2):
        >>>     # do some work
        >>>     is_prime(n)
        10000/10000... rate=13294.94 Hz, eta=0:00:00, total=0:00:00, wall=13:34 EST

    Notes
    ----------
    Either use ProgIter in a with statement or call prog.end() at the end of
    the computation if there is a possibility that the entire iterable may not
    be exhausted.
    """
    def __init__(self, iterable=None, label=None, length=None, freq=1,
                 eta_window=64, clearline=True, adjust=True, time_thresh=2.0,
                 enabled=True, verbose=None, stream=None):
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
        self.iterable = iterable
        self.label = label
        self.length = length
        self.freq = freq
        self.enabled = enabled
        self.adjust = adjust
        self.eta_window = eta_window
        self.time_thresh = 1.0
        self.clearline = clearline
        self.extra = ''
        self.started = False
        self.finished = False

    def __call__(self, iterable):  # nocover
        self.iterable = iterable
        return iter(self)

    def __enter__(self):  # nocover
        return self

    def __exit__(self, type_, value, trace):
        if trace is not None:
            return False
        else:  # nocover
            self.end()

    def __iter__(self):
        if not self.enabled:  # nocover
            return iter(self.iterable)
        else:
            return self.iter_rate()

    def set_extra(self, extra):
        """
        specify a custom info appended to the end of the next message
        TODO: come up with a better name and rename
        """
        self.extra = extra

    def iter_rate(self):
        self.begin()
        # Wrap input iterable in a generator
        for self._iter_idx, item in enumerate(self.iterable, start=1):
            yield item
            if (self._iter_idx) % self.freq == 0:
                # update progress information every so often
                self.update_measurements()
                self.update_estimates()
                self.display_message()
        self.end()

    def mark(self):
        self.update_measurements()
        self.update_estimates()
        self.display_message()

    def reset_internals(self):
        # Prepare for iteration
        if self.length is None:
            self.length = _infer_length(self.iterable)
        self._est_seconds_left = None
        self._total_seconds = 0
        self._between_time = 0
        self._iter_idx = 0
        self._last_idx = -1
        # now time is actually not right now
        # now refers the the most recent measurment
        # last refers to the measurement before that
        self._now_idx = 0
        self._now_time = 0
        self._between_count = -1
        self._max_between_time = -1.0
        self._max_between_count = -1.0
        self._iters_per_second = 0.0

    def begin(self):
        """
        Initializes information used to measure progress
        """
        # Prepare for iteration
        if self.length is None:
            self.length = _infer_length(self.iterable)

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

        self._cursor_at_newline = True
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
        """ Defines the template for the progress line """
        tzname = time.tzname[0]
        if self.length <= 0:
            n_chrs = 4
        else:
            n_chrs = int(floor(log10(float(self.length))) + 1)
        msg_body = [
            (self.label),
            (' {iter_idx:' + str(n_chrs) + 'd}/'),
            ('?' if self.length <= 0 else six.text_type(self.length)),
            ('... '),
            ('rate={rate:4.2f} Hz,'),
            ('' if self.length == 0 else ' eta={eta},'),
            (' total={total},'),
            (' wall={wall} ' + tzname),
            (' {extra}'),
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
    import ubelt as ub  # NOQA
    ub.doctest_package()
