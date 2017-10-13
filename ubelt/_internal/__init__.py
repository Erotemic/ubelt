"""
python -c "import ubelt._internal as a; a.autogen_init('ubelt._internal')"
"""
# flake8: noqa
from __future__ import absolute_import, division, print_function, unicode_literals
from ubelt._internal import static_autogen
from ubelt._internal import dynamic_make_init
from ubelt._internal.static_autogen import (autogen_init,)
from ubelt._internal.dynamic_make_init import (dynamic_import,)