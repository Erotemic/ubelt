# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser
import sys

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')


def get_resource_dir():
    """
    Returns a directory which should be writable for any application
    """
    #resource_prefix = '~'
    if WIN32:
        dpath_ = '~/AppData/Roaming'
    elif LINUX:
        dpath_ = '~/.config'
    elif DARWIN:
        dpath_  = '~/Library/Application Support'
    else:
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath
