# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import inspect


def get_stack_frame(n=0, strict=True):
    """
    Gets the current stack frame or any of its ancestors dynamically

    Args:
        n (int): n=0 means the frame you called this function in.
                 n=1 is the parent frame.
        strict (bool): (default = True)

    Returns:
        frame: frame_cur

    CommandLine:
        python -m dynamic_analysis get_stack_frame

    Example:
        >>> from ubelt.meta.dynamic_analysis import *  # NOQA
        >>> frame_cur = get_stack_frame(n=0)
        >>> print('frame_cur = %r' % (frame_cur,))
        >>> assert frame_cur.f_globals['frame_cur'] is frame_cur
    """
    frame_cur = inspect.currentframe()
    # Use n+1 to always skip the frame of this function
    for ix in range(n + 1):
        frame_next = frame_cur.f_back
        if frame_next is None:  # nocover
            if strict:
                raise AssertionError('Frame level %r is root' % ix)
            else:
                break
        frame_cur = frame_next
    return frame_cur


def get_parent_frame(n=0):
    r"""
    Returns the frame of that called you.
    This is equivalent to `get_stack_frame(n=1)`

    Args:
        n (int): n=0 means the frame you called this function in.
                 n=1 is the parent frame.

    Returns:
        frame: parent_frame

    CommandLine:
        python -m dynamic_analysis get_parent_frame

    Example:
        >>> from ubelt.meta.dynamic_analysis import *  # NOQA
        >>> root0 = get_stack_frame(n=0)
        >>> def foo():
        >>>     child = get_stack_frame(n=0)
        >>>     root1 = get_parent_frame(n=0)
        >>>     root2 = get_stack_frame(n=1)
        >>>     return child, root1, root2
        >>> # Note this wont work in IPython because several
        >>> # frames will be inserted between here and foo
        >>> child, root1, root2 = foo()
        >>> print('root0 = %r' % (root0,))
        >>> print('root1 = %r' % (root1,))
        >>> print('root2 = %r' % (root2,))
        >>> print('child = %r' % (child,))
        >>> assert root0 == root1
        >>> assert root1 == root2
        >>> assert child != root1
    """
    parent_frame = get_stack_frame(n=n + 2)
    return parent_frame


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.meta.dynamic_analysis
        python -m ubelt.meta.dynamic_analysis --allexamples
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
