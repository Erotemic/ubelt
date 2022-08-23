"""
Functions for working with text and strings.

The :func:`ensure_unicode` function does its best to coerce Python 2/3 bytes
and text into a consistent unicode text representation.

The :func:`codeblock` and :func:`paragraph` wrap multiline strings to help
write text blocks without hindering the surrounding code indentation.

The :func:`hzcat` function horizontally concatenates multiline text.

The :func:`indent` prefixes all lines in a text block with a given prefix. By
default that prefix is 4 spaces.
"""

__all__ = [
    'indent',
    'codeblock',
    'paragraph',
    'hzcat',
    'ensure_unicode',
]


def indent(text, prefix='    '):
    """
    Indents a block of text

    Args:
        text (str): text to indent
        prefix (str, default = '    '): prefix to add to each line

    Returns:
        str: indented text

    Example:
        >>> import ubelt as ub
        >>> NL = chr(10)  # newline character
        >>> text = 'Lorem ipsum' + NL + 'dolor sit amet'
        >>> prefix = '    '
        >>> result = ub.indent(text, prefix)
        >>> assert all(t.startswith(prefix) for t in result.split(NL))
    """
    return prefix + text.replace('\n', '\n' + prefix)


def codeblock(text):
    """
    Create a block of text that preserves all newlines and relative indentation

    Wraps multiline string blocks and returns unindented code.
    Useful for templated code defined in indented parts of code.

    Args:
        text (str): typically a multiline string

    Returns:
        str: the unindented string

    Example:
        >>> import ubelt as ub
        >>> # Simulate an indented part of code
        >>> if True:
        >>>     # notice the indentation on this will be normal
        >>>     codeblock_version = ub.codeblock(
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
    return textwrap.dedent(text).strip('\n')


def paragraph(text):
    r"""
    Wraps multi-line strings and restructures the text to remove all newlines,
    heading, trailing, and double spaces.

    Useful for writing log messages

    Args:
        text (str): typically a multiline string

    Returns:
        str: the reduced text block

    Example:
        >>> import ubelt as ub
        >>> text = (
        >>>     '''
        >>>     Lorem ipsum dolor sit amet, consectetur adipiscing
        >>>     elit, sed do eiusmod tempor incididunt ut labore et
        >>>     dolore magna aliqua.
        >>>     ''')
        >>> out = ub.paragraph(text)
        >>> assert chr(10) in text
        >>> assert chr(10) not in out
        >>> print('text = {!r}'.format(text))
        >>> print('out = {!r}'.format(out))
    """
    import re
    out = re.sub(r'\s\s*', ' ', text).strip()
    return out


def hzcat(args, sep=''):
    """
    Horizontally concatenates strings preserving indentation

    Concatenates a list of objects ensuring that the next item in the list is
    all the way to the right of any previous items.

    Args:
        args (List[str]): strings to concatenate
        sep (str, default=''): separator

    Example1:
        >>> import ubelt as ub
        >>> B = ub.repr2([[1, 2], [3, 457]], nl=1, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 8]], nl=1, cbr=True, trailsep=False)
        >>> args = ['A = ', B, ' * ', C]
        >>> print(ub.hzcat(args))
        A = [[1, 2],   * [[5, 6],
             [3, 457]]    [7, 8]]

    Example2:
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
    # args = [unicodedata.normalize('NFC', ensure_unicode(val)) for val in args]
    args = [unicodedata.normalize('NFC', val) for val in args]
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

    Args:
        text (str | bytes):
            text to ensure is decoded as unicode

    Returns:
        str

    References:
        [SO_12561063] http://stackoverflow.com/questions/12561063/extract-data-from-file

    Example:
        >>> from ubelt.util_str import *
        >>> import codecs  # NOQA
        >>> assert ensure_unicode('my ünicôdé strįng') == 'my ünicôdé strįng'
        >>> assert ensure_unicode('text1') == 'text1'
        >>> assert ensure_unicode('text1'.encode('utf8')) == 'text1'
        >>> assert ensure_unicode('ï»¿text1'.encode('utf8')) == 'ï»¿text1'
        >>> assert (codecs.BOM_UTF8 + 'text»¿'.encode('utf8')).decode('utf8')
    """
    import ubelt as ub
    ub.schedule_deprecation(
        modname='ubelt', name='ensure_unicode', type='function',
        migration='This should not be needed in Python 3',
        deprecate='1.2.0', error='2.0.0', remove='2.1.0')
    if isinstance(text, str):
        return text
    elif isinstance(text, bytes):
        return text.decode('utf8')
    else:  # nocover
        raise ValueError('unknown input type {!r}'.format(text))
    # if something with the above code goes wrong, refer to this
    # except UnicodeDecodeError:
    #     if text.startswith(codecs.BOM_UTF8):
    #         # Can safely remove the utf8 marker
    #         text = text[len(codecs.BOM_UTF8):]
    #     return text.decode('utf-8')
