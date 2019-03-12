# -*- coding: utf-8 -*-
"""
Functions for working with text strings.
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import six

__all__ = [
    'indent',
    'codeblock',
    'hzcat',
    'ensure_unicode',
]


def indent(text, prefix='    '):
    """
    Indents a block of text

    Args:
        text (str): text to indent
        prefix (str): prefix to add to each line (default = '    ')

    Returns:
        str: indented text

    CommandLine:
        python -m util_str indent

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> NL = chr(10)  # newline character
        >>> text = 'Lorem ipsum' + NL + 'dolor sit amet'
        >>> prefix = '    '
        >>> result = indent(text, prefix)
        >>> assert all(t.startswith(prefix) for t in result.split(NL))
    """
    return prefix + text.replace('\n', '\n' + prefix)


def codeblock(block_str):
    """
    Wraps multiline string blocks and returns unindented code.
    Useful for templated code defined in indented parts of code.

    Args:
        block_str (str): typically in the form of a multiline string

    Returns:
        str: the unindented string

    CommandLine:
        python -m ubelt.util_str codeblock

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> # Simulate an indented part of code
        >>> if True:
        >>>     # notice the indentation on this will be normal
        >>>     codeblock_version = codeblock(
        ...             '''
        ...             def foo():
        ...                 return 'bar'
        ...             '''
        ...         )
        >>>     # notice the indentation and newlines on this will be odd
        >>>     normal_version = ('''
        ...         def foo():
        ...             return 'bar'
        ...     ''')
        >>> assert normal_version != codeblock_version
        >>> print('Without codeblock')
        >>> print(normal_version)
        >>> print('With codeblock')
        >>> print(codeblock_version)
    """
    import textwrap  # this is a slow import, do it lazy
    return textwrap.dedent(block_str).strip('\n')


def hzcat(args, sep=''):
    """
    Horizontally concatenates strings preserving indentation

    Concatenates a list of objects ensuring that the next item in the list is
    all the way to the right of any previous items.

    Args:
        args (List[str]): strings to concatenate
        sep (str): separator (defaults to '')

    CommandLine:
        python -m ubelt.util_str hzcat

    Example1:
        >>> import ubelt as ub
        >>> B = ub.repr2([[1, 2], [3, 457]], nl=1, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
        >>> args = ['A = ', B, ' * ', C]
        >>> print(ub.hzcat(args))
        A = [[1, 2],   * [[5, 6],
             [3, 457]]    [7, 8]]

    Example2:
        >>> from ubelt.util_str import *
        >>> import ubelt as ub
        >>> import unicodedata
        >>> aa = unicodedata.normalize('NFD', 'á')  # a unicode char with len2
        >>> B = ub.repr2([['θ', aa], [aa, aa, aa]], nl=1, si=True, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 'θ']], nl=1, si=True, cbr=True, trailsep=False)
        >>> args = ['A', '=', B, '*', C]
        >>> print(ub.hzcat(args, sep='｜'))
        A｜=｜[[θ, á],   ｜*｜[[5, 6],
         ｜ ｜ [á, á, á]]｜ ｜ [7, θ]]
    """
    import unicodedata
    if '\n' in sep or '\r' in sep:
        raise ValueError('`sep` cannot contain newline characters')

    # TODO: ensure unicode data works correctly for python2
    args = [unicodedata.normalize('NFC', ensure_unicode(val)) for val in args]
    arglines = [a.split('\n') for a in args]
    height = max(map(len, arglines))
    # Do vertical padding
    arglines = [lines + [''] * (height - len(lines)) for lines in arglines]
    # Initialize output
    all_lines = ['' for _ in range(height)]
    width = 0
    n_args = len(args)
    for sx, lines in enumerate(arglines):
        # Concatenate the new string
        for lx, line in enumerate(lines):
            all_lines[lx] += line
        # Find the new maximum horizontal width
        width = max(width, max(map(len, all_lines)))
        if sx < n_args - 1:
            # Horizontal padding on all but last iter
            for lx, line in list(enumerate(all_lines)):
                residual = width - len(line)
                all_lines[lx] = line + (' ' * residual) + sep
            width += len(sep)
    # Clean up trailing whitespace
    all_lines = [line.rstrip(' ') for line in all_lines]
    ret = '\n'.join(all_lines)
    return ret


def ensure_unicode(text):
    r"""
    Casts bytes into utf8 (mostly for python2 compatibility)

    References:
        http://stackoverflow.com/questions/12561063/extract-data-from-file

    Example:
        >>> from ubelt.util_str import *
        >>> import codecs  # NOQA
        >>> assert ensure_unicode('my ünicôdé strįng') == 'my ünicôdé strįng'
        >>> assert ensure_unicode('text1') == 'text1'
        >>> assert ensure_unicode('text1'.encode('utf8')) == 'text1'
        >>> assert ensure_unicode('ï»¿text1'.encode('utf8')) == 'ï»¿text1'
        >>> assert (codecs.BOM_UTF8 + 'text»¿'.encode('utf8')).decode('utf8')
    """
    if isinstance(text, six.text_type):
        return text
    elif isinstance(text, six.binary_type):
        return text.decode('utf8')
    else:  # nocover
        raise ValueError('unknown input type {!r}'.format(text))
    # if something with the above code goes wrong, refer to this
    # except UnicodeDecodeError:
    #     if text.startswith(codecs.BOM_UTF8):
    #         # Can safely remove the utf8 marker
    #         text = text[len(codecs.BOM_UTF8):]
    #     return text.decode('utf-8')
