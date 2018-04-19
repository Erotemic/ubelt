# -*- coding: utf-8 -*-
"""
A Progress Iterator:

    The API is compatible with TQDM!

    We have our own ways of running too!
    You can divide the runtime overhead by two as many times as you want.

CommandLine:
    python -m ubelt.progiter __doc__:0

Example:
    >>> # SCRIPT
    >>> import ubelt as ub
    >>> def is_prime(n):
    ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
    >>> for n in ub.ProgIter(range(1000000), verbose=1):
    >>>     # do some work
    >>>     is_prime(n)


"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import time
import datetime
import collections
from math import log10, floor
import six
from collections import OrderedDict
import numbers

__all__ = [
    'ProgIter',
]

if sys.version_info.major == 2:  # nocover
    default_timer = time.clock if sys.platform.startswith('win32') else time.time
else:
    default_timer = time.perf_counter

CLEAR_BEFORE = '\r'
AT_END = '\n'
CLEAR_AFTER = ''

# Turns out we probably dont need all this ansi stuff
# VT100 ANSI definitions
# https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_codes
# CLEARLINE_EL0 = '\33[0K'  # clear line to right
# CLEARLINE_EL1 = '\33[1K'  # clear line to left
# CLEARLINE_EL2 = '\33[2K'  # clear line
# DECTCEM_HIDE = '\033[?25l'  # hide cursor
# DECTCEM_SHOW = '\033[?25h'  # show cursor
# if WITH_ANSI:  # pragma: nobranch
#     CLEAR_BEFORE = '\r' + CLEARLINE_EL2 + DECTCEM_HIDE
#     CLEAR_AFTER = CLEARLINE_EL0
#     AT_END = DECTCEM_SHOW + '\n'


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

    # TQDM Compatibility API
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
        postfix = OrderedDict([] if ordered_dict is None else ordered_dict)
        for key in sorted(kwargs.keys()):
            postfix[key] = kwargs[key]
        # Preprocess stats according to datatype
        for key in postfix.keys():
            # Number: limit the length of the string
            if isinstance(postfix[key], numbers.Number):
                postfix[key] = '{0:2.3g}'.format(postfix[key])
            # Else for any other type, try to get the string conversion
            elif not isinstance(postfix[key], six.string_types):
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

    Note:
        USE `tqdm` INSTEAD.  The main difference between `ProgIter` and `tqdm`
        is that ProgIter does not use threading where as `tqdm` does.
        `ProgIter` is simpler than `tqdm` and thus more stable in certain
        circumstances. However, `tqdm` is recommended for the majority of use
        cases.

    Note:
        The API on `ProgIter` will change to become inter-compatible with
        `tqdm`.

    Attributes:
        iterable (iterable): An iterable iterable
        desc (str): description label to show with progress
        total (int): Maximum length of the process
            (estimated from iterable if not specified)
        freq (int): How many iterations to wait between messages.
        adjust (bool): if True freq is adjusted based on time_thresh
        eta_window (int): number of previous measurements to use in eta calculation
        clearline (bool): if true messages are printed on the same line
        adjust (bool): if True `freq` is adjusted based on time_thresh
        time_thresh (float): desired amount of time to wait between messages if
            adjust is True otherwise does nothing
        show_times (bool): shows rate, eta, and wall (defaults to True)
        initial (int): starting index offset (defaults to 0)
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
        of the computation if there is a possibility that the entire iterable
        may not be exhausted.

    Example:
        >>> # doctest: +SKIP
        >>> import ubelt as ub
        >>> def is_prime(n):
        ...     return n >= 2 and not any(n % i == 0 for i in range(2, n))
        >>> for n in ub.ProgIter(range(100), verbose=1):
        >>>     # do some work
        >>>     is_prime(n)
        100/100... rate=... Hz, total=..., wall=... EST
    """
    def __init__(self, iterable=None, desc=None, total=None, freq=1,
                 initial=0, eta_window=64, clearline=True, adjust=True,
                 time_thresh=2.0, show_times=True, enabled=True, verbose=None,
                 stream=None, **kwargs):
        """
        Notes:
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

        # --- Accept the tqdm api ---
        if kwargs:
            stream = kwargs.pop('file', stream)
            enabled = not kwargs.pop('disable', not enabled)
            if kwargs.get('miniters', None) is not None:
                adjust = False
            freq = kwargs.pop('miniters', freq)

            kwargs.pop('position', None)  # API compatability does nothing
            kwargs.pop('dynamic_ncols', None)  # API compatability does nothing
            kwargs.pop('leave', True)  # we always leave

            # Accept the old api keywords
            desc = kwargs.pop('label', desc)
            total = kwargs.pop('length', total)
            enabled = kwargs.pop('enabled', enabled)
            initial = kwargs.pop('start', initial)
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
        self.eta_window = eta_window
        self.time_thresh = 1.0
        self.clearline = clearline
        self.extra = ''
        self.started = False
        self.finished = False
        self._reset_internals()

    def __call__(self, iterable):
        self.iterable = iterable
        return iter(self)

    def __enter__(self):
        """
        CommandLine:
            python -m ubelt.progiter ProgIter.__enter__

        Example:
            >>> # can be used as a context manager in iter mode
            >>> n = 3
            >>> with ProgIter(desc='manual', total=n, verbose=3) as prog:
            ...     list(prog(range(n)))
        """
        self.begin()
        return self

    def __exit__(self, type, value, trace):
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

    def _iterate(self):
        """ iterates with progress """
        if not self.started:
            self.begin()
        # Wrap input sequence in a generator
        for self._iter_idx, item in enumerate(self.iterable, start=self.initial + 1):
            yield item
            if (self._iter_idx) % self.freq == 0:
                # update progress information every so often
                self._update_measurements()
                self._update_estimates()
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
            >>> prog = ub.ProgIter(desc='manual', total=n, verbose=3)
            >>> # Need to manually begin and end in this mode
            >>> prog.begin()
            >>> for _ in range(n):
            ...     prog.step()
            >>> prog.end()

        Example:
            >>> import ubelt as ub
            >>> n = 3
            >>> # can be used as a context manager in manual mode
            >>> with ub.ProgIter(desc='manual', total=n, verbose=3) as prog:
            ...     for _ in range(n):
            ...         prog.step()
        """
        if not self.enabled:
            return
        self._iter_idx += inc
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
        # now refers the the most recent measurment
        # last refers to the measurement before that
        self._now_idx = self.initial
        self._now_time = 0
        self._between_count = -1
        self._max_between_time = -1.0
        self._max_between_count = -1.0
        self._iters_per_second = 0.0
        self._update_message_template()

    def begin(self):
        """
        Initializes information used to measure progress
        """
        if not self.enabled:
            return

        self._reset_internals()

        self._tryflush()
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
            self._update_measurements()
            self._update_estimates()
            self._est_seconds_left = 0
            self.display_message()
        self.ensure_newline()
        self._cursor_at_newline = True
        self.finished = True

    def _adjust_frequency(self):
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
        # so progress doesnt slow down actual function
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
            >>> print(self._build_message_template().strip())
            {desc} {iter_idx:4d}/?...{extra} rate={rate:{rate_format}} Hz, total={total}, wall={wall} ...
            >>> self = ProgIter(show_times=False)
            >>> print(self._build_message_template().strip())
            {desc} {iter_idx:4d}/?...{extra}
        """
        tzname = time.tzname[0]
        length_unknown = self.total is None or self.total <= 0
        if length_unknown:
            n_chrs = 4
        else:
            n_chrs = int(floor(log10(float(self.total))) + 1)
        msg_body = [
            ('{desc}'),
            (' {iter_idx:' + str(n_chrs) + 'd}/'),
            ('?' if length_unknown else six.text_type(self.total)),
            ('...'),
        ]

        msg_body += [
            ('{extra} '),
        ]

        if self.show_times:
            msg_body += [
                    ('rate={rate:{rate_format}} Hz,'),
                    (' eta={eta},' if self.total else ''),
                    (' total={total},'),  # this is total time
                    (' wall={wall} ' + tzname),
            ]
        if self.clearline:
            msg_body = [CLEAR_BEFORE] + msg_body + [CLEAR_AFTER]
        else:
            msg_body = msg_body + [AT_END]
        msg_fmtstr_time = ''.join(msg_body)
        return msg_fmtstr_time

    def format_message(self):
        r"""
        builds a formatted progres message with the current values.
        This contains the special characters needed to clear lines.

        CommandLine:
            python -m ubelt.progiter ProgIter.format_message

        Example:
            >>> self = ProgIter(clearline=False, show_times=False)
            >>> print(repr(self.format_message()))
            '    0/?... \n'
            >>> self.begin()
            >>> self.step()
            >>> print(repr(self.format_message()))
            ' 1/?... \n'
        """
        if self._est_seconds_left is None:
            eta = '?'
        else:
            eta = six.text_type(datetime.timedelta(
                seconds=int(self._est_seconds_left)))
        total = six.text_type(datetime.timedelta(
            seconds=int(self._total_seconds)))
        # similar to tqdm.format_meter
        msg = self._msg_fmtstr.format(
            desc=self.desc,
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
            self._write(AT_END)
            self._cursor_at_newline = True

    def display_message(self):
        """ Writes current progress to the output stream """
        msg = self.format_message()
        self._write(msg)
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


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.progiter
        python -m ubelt.progiter all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
