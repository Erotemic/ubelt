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


def test_timer_error():
    try:
        with ub.Timer() as timer:
            raise Exception()
    except Exception:
        pass
    assert timer.elapsed > 0


def test_timestamp_corner_cases():
    from datetime import datetime as datetime_cls
    import datetime as datetime_mod
    datetime = datetime_cls(1, 1, 1, 1, 1, 1, tzinfo=datetime_mod.timezone.utc)
    stamp = ub.timestamp(datetime)
    assert stamp == '0001-01-01T010101+0'


def test_timeparse_minimal():
    # We should always be able to parse these
    good_stamps = [
        '2000-11-22T111111.44444Z',
        '2000-11-22T111111.44444+5',
        '2000-11-22T111111.44444-05',
        '2000-11-22T111111.44444-0500',
        '2000-11-22T111111.44444+0530',
        '2000-11-22T111111Z',
        '2000-11-22T111111+5',
        '2000-11-22T111111+0530',
        '2000-11-22T111111',
    ]
    for stamp in good_stamps:
        result = ub.timeparse(stamp, allow_dateutil=0)
        recon_stamp = ub.timestamp(result, precision=9)
        recon_result = ub.timeparse(recon_stamp, allow_dateutil=0)
        print('----')
        print(f'stamp        = {stamp}')
        print(f'recon_stamp  = {recon_stamp}')
        print(f'result       = {result!r}')
        print(f'recon_result = {recon_result!r}')
        assert recon_result == result


def test_timeparse_with_dateutil():
    import ubelt as ub
    # See Also: https://github.com/dateutil/dateutil/blob/master/tests/test_isoparser.py
    conditional_stamps = [
        'Thu Sep 25 10:36:28 2003',
        'Thu Sep 25 2003',
        '2003-09-25T10:49:41',
        '2003-09-25T10:49',
        '2003-09-25T10',
        # '2003-09-25',
        '20030925T104941',
        '20030925T1049',
        '20030925T10',
        '20030925',
        '2003-09-25 10:49:41,502',
        '199709020908',
        '19970902090807',
        '09-25-2003',
        '25-09-2003',
        '10-09-2003',
        '10-09-03',
        '2003.09.25',
        '09.25.2003',
        '25.09.2003',
        '10.09.2003',
        '10.09.03',
        '2003/09/25',
        '09/25/2003',
        '25/09/2003',
        '10/09/2003',
        '10/09/03',
        '2003 09 25',
        '09 25 2003',
        '25 09 2003',
        '10 09 2003',
        '10 09 03',
        '25 09 03',
        '03 25 Sep',
        '25 03 Sep',
        '  July   4 ,  1976   12:01:02   am  ',
        "Wed, July 10, '96",
        '1996.July.10 AD 12:08 PM',
        'July 4, 1976',
        '7 4 1976',
        '4 jul 1976',
        '4 Jul 1976',
        '7-4-76',
        '19760704',
        '0:01:02 on July 4, 1976',
        'July 4, 1976 12:01:02 am',
        'Mon Jan  2 04:24:27 1995',
        '04.04.95 00:22',
        'Jan 1 1999 11:23:34.578',
        '950404 122212',
        '3rd of May 2001',
        '5th of March 2001',
        '1st of May 2003',
        '0099-01-01T00:00:00',
        '0031-01-01T00:00:00',
        '20080227T21:26:01.123456789',
    ]

    for stamp in conditional_stamps:
        with pytest.raises(ValueError):
            result = ub.timeparse(stamp, allow_dateutil=False)

    have_dateutil = bool(ub.modname_to_modpath('dateutil'))
    if have_dateutil:
        for stamp in conditional_stamps:
            result = ub.timeparse(stamp)
            recon_stamp = ub.timestamp(result, precision=6)
            recon_result = ub.timeparse(recon_stamp)
            print('----')
            print(f'stamp        = {stamp}')
            print(f'recon_stamp  = {recon_stamp}')
            print(f'result       = {result!r}')
            print(f'recon_result = {recon_result!r}')
            assert result == recon_result


def test_timeparse_bad_stamps():
    # We can never parse these types of stamps
    bad_stamps = [
        '',
        'foobar',
        '0000-00-00T00:00:00.0000+05'
    ]
    for stamp in bad_stamps:
        with pytest.raises(ValueError):
            ub.timeparse(stamp)


if __name__ == '__main__':
    r"""
    CommandLine:
        python ubelt/tests/test_time.py test_timer_nonewline
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
