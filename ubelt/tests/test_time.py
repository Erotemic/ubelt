# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest
import ubelt as ub
import re
from xdoctest.utils import CaptureStdout


def test_timer_nonewline():
    with CaptureStdout() as cap:
        timer = ub.Timer(newline=False, verbose=1)
        timer.tic()
        timer.toc()
    assert cap.text.replace('u', '').startswith("\ntic('')...toc('')")


def test_timestamp():
    stamp = ub.timestamp()
    assert re.match(r'\d+-\d+-\d+T\d+[\+\-]\d+', stamp)


def test_timer_default_verbosity():
    with CaptureStdout() as cap:
        ub.Timer('').tic().toc()
    assert cap.text == '', 'should be quiet by default when label is not given'

    with CaptureStdout() as cap:
        ub.Timer('a label').tic().toc()
    assert cap.text != '', 'should be verbose by default when label is given'


def test_timerit_default_verbosity():
    with CaptureStdout() as cap:
        ub.Timerit(10, '').call(lambda: None)
    assert cap.text == '', 'should be quiet by default when label is not given'

    with CaptureStdout() as cap:
        ub.Timerit(10, 'alabel').call(lambda: None)
    assert cap.text != '', 'should be verbose by default when label is given'


def test_timer_error():
    try:
        with ub.Timer() as timer:
            raise Exception()
    except Exception as ex:
        pass
    assert timer.elapsed > 0


def timestamp_badmethod():
    with pytest.raises(ValueError):
        ub.timestamp(method='not real')

if __name__ == '__main__':
    r"""
    CommandLine:
        python ubelt/tests/test_time.py test_timer_nonewline
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
