# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest
import ubelt as ub
import re


def test_timestamp():
    stamp = ub.timestamp()
    assert re.match('\d+-\d+-\d+T\d+\+\d+', stamp)


def test_timestamp_value_error():
    with pytest.raises(ValueError):
        ub.timestamp(method='bad-method')
