# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import inspect


def get_stack_frame(N=0, strict=True):
    """
    Args:
        N (int): N=0 means the frame you called this function in.
                 N=1 is the parent frame.
        strict (bool): (default = True)

    Returns:
        frame: frame_cur

    CommandLine:
        python -m dynamic_analysis get_stack_frame

    Example:
        >>> from ubelt.meta.dynamic_analysis import *  # NOQA
        >>> frame_cur = get_stack_frame(N=0)
        >>> print('frame_cur = %r' % (frame_cur,))
        >>> assert frame_cur.f_globals['frame_cur'] is frame_cur
    """
    frame_cur = inspect.currentframe()
    # Use N+1 to always skip the frame of this function
    for _ix in range(N + 1):
        frame_next = frame_cur.f_back
        if frame_next is None:  # nocover
            if strict:
                raise AssertionError('Frame level %r is root' % _ix)
            else:
                break
        frame_cur = frame_next
    return frame_cur


def get_parent_frame(N=0):
    r"""
    Returns the frame of that called you.
    This is equivalent to `get_stack_frame(N=1)`

    Args:
        N (int): N=0 means the frame you called this function in.
                 N=1 is the parent frame.

    Returns:
        frame: parent_frame

    CommandLine:
        python -m dynamic_analysis get_parent_frame

    Example:
        >>> from ubelt.meta.dynamic_analysis import *  # NOQA
        >>> root0 = get_stack_frame(N=0)
        >>> def foo():
        >>>     child = get_stack_frame(N=0)
        >>>     root1 = get_parent_frame(N=0)
        >>>     root2 = get_stack_frame(N=1)
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
    parent_frame = get_stack_frame(N=N + 2)
    return parent_frame


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.meta.dynamic_analysis
        python -m ubelt.meta.dynamic_analysis --allexamples
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
