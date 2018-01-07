# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest
import ubelt as ub
import re


def test_timer_nonewline():
    from xdoctest.utils import CaptureStdout
    with CaptureStdout() as cap:
        timer = ub.Timer(newline=False)
        timer.tic()
        timer.toc()
    assert cap.text.replace('u', '').startswith("\ntic('')...toc('')")


def test_timestamp():
    stamp = ub.timestamp()
    assert re.match('\d+-\d+-\d+T\d+\+\d+', stamp)


def test_timerit_verbose():
    from xdoctest.utils import CaptureStdout
    with CaptureStdout() as cap:
        ub.Timerit(3, label='foo', verbose=0).call(lambda: None)
    assert cap.text == ''

    with CaptureStdout() as cap:
        ub.Timerit(3, label='foo', verbose=1).call(lambda: None)
    assert cap.text.count('\n') == 2
    assert cap.text.count('foo') == 1

    with CaptureStdout() as cap:
        ub.Timerit(3, label='foo', verbose=2).call(lambda: None)
    assert cap.text.count('\n') == 3
    assert cap.text.count('foo') == 2

    with CaptureStdout() as cap:
        ub.Timerit(3, label='foo', verbose=3).call(lambda: None)
    assert cap.text.count('\n') == 4
    assert cap.text.count('foo') == 2

    with CaptureStdout() as cap:
        ub.Timerit(3, label='foo', verbose=4).call(lambda: None)
    assert cap.text.count('\n') == 4
    assert cap.text.count('foo') == 2


def test_timestamp_value_error():
    with pytest.raises(ValueError):
        ub.timestamp(method='bad-method')

if __name__ == '__main__':
    r"""
    CommandLine:
        python ubelt/tests/test_time.py test_timer_nonewline
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
