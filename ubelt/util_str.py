# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
import re
import codecs
import unicodedata
import textwrap
from six.moves import cStringIO
import six


class CaptureStdout(object):
    r"""
    Context manager that captures stdout and stores it in an internal stream

    Args:
        enabled (bool): (default = True)

    CommandLine:
        python -m ubelt.util_str CaptureStdout

    Example:
        >>> from ubelt.util_str import *  # NOQA
        >>> self = CaptureStdout(enabled=True)
        >>> print('dont capture the table flip (╯°□°）╯︵ ┻━┻')
        >>> with self:
        >>>     print('capture the heart ♥')
        >>> print('dont capture look of disapproval ಠ_ಠ')
        >>> assert isinstance(self.text, six.text_type)
        >>> assert self.text == 'capture the heart ♥\n', 'failed capture text'
    """
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.orig_stdout = sys.stdout
        self.cap_stdout = cStringIO()
        if six.PY2:
            # http://stackoverflow.com/questions/1817695/stringio-accept-utf8
            codecinfo = codecs.lookup('utf8')
            self.cap_stdout = codecs.StreamReaderWriter(
                self.cap_stdout, codecinfo.streamreader,
                codecinfo.streamwriter)
        self.text = None

    def __enter__(self):
        if self.enabled:
            sys.stdout = self.cap_stdout
        return self

    def __exit__(self, type_, value, trace):
        if self.enabled:
            try:
                self.cap_stdout.seek(0)
                self.text = self.cap_stdout.read()
                if six.PY2:
                    self.text = self.text.decode('utf8')
            except Exception:  # nocover
                pass
            finally:
                self.cap_stdout.close()
                sys.stdout = self.orig_stdout
        if trace is not None:
            return False  # return a falsey value on error


def indent(text, prefix='    '):
    r"""
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
        >>> text = 'Lorem ipsum\ndolor sit amet'
        >>> prefix = '    '
        >>> result = indent(text, prefix)
        >>> assert all(t.startswith(prefix) for t in result.split('\n'))
    """
    return prefix + text.replace('\n', '\n' + prefix)


def codeblock(block_str):
    r"""
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
    return textwrap.dedent(block_str).strip('\n')


def hzcat(args, sep=''):
    """
    Horizontally concatenates strings preserving indentation

    Concats a list of objects ensuring that the next item in the list
    is all the way to the right of any previous items.

    Args:
        args (list): strings to concat
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
        >>> aa = unicodedata.normalize('NFD', 'á')  # a unicode char with len2
        >>> B = ub.repr2([['θ', aa], [aa, aa, aa]], nl=1, si=True, cbr=True, trailsep=False)
        >>> C = ub.repr2([[5, 6], [7, 'θ']], nl=1, si=True, cbr=True, trailsep=False)
        >>> args = ['A', '=', B, '*', C]
        >>> print(ub.hzcat(args, sep='｜'))
        A｜=｜[[θ, á],   ｜*｜[[5, 6],
         ｜ ｜ [á, á, á]]｜ ｜ [7, θ]]
    """
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
        # Find the new maximum horiztonal width
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
        http://stackoverflow.com/questions/12561063/python-extract-data-from-file

    Example:
        >>> from ubelt.util_str import *
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


def strip_ansi(text):
    r"""
    Removes all ansi directives from the string.

    References:
        http://stackoverflow.com/questions/14693701/remove-ansi
        https://stackoverflow.com/questions/13506033/filtering-out-ansi

    Examples:
        >>> line = ('\t\u001b[0;35mBlabla\u001b[0m     '
        ...         '\u001b[0;36m172.18.0.2\u001b[0m')
        >>> escaped_line = strip_ansi(line)
        >>> assert escaped_line == '\tBlabla     172.18.0.2'
    """
    ansi_escape3 = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]',
                              flags=re.IGNORECASE)
    text = ansi_escape3.sub('', text)
    return text


def align(text, character='=', replchar=None, pos=0):
    r"""
    Left justifies text on the left side of character

    Args:
        line_list (list of strs): strings to align
        character (str): character to align
        replchar (str): if not None, replace character with this
        pos (int or list or None): does one alignment for all chars beyond this
            column position. If pos is None, then all chars are aligned.

    Returns:
        str: new_text

    SeeAlso:
        ub.align_lines

    Example:
        >>> character = '='
        >>> text = 'a = b=\none = two\nthree = fish\n'
        >>> print(align(text, '='))
        a     = b=
        one   = two
        three = fish
    """
    line_list = text.splitlines()
    new_lines = align_lines(line_list, character, replchar, pos=pos)
    new_text = '\n'.join(new_lines)
    return new_text


def align_lines(line_list, character='=', replchar=None, pos=0):
    r"""
    Left justifies text on the left side of character

    Args:
        line_list (list of strs): strings to align
        character (str): character to align
        replchar (str): if not None, replace character with this
        pos (int or list or None): does one alignment for all chars beyond this
            column position. If pos is None, then all chars are aligned.

    Returns:
        list: new_lines

    SeeAlso:
        ub.align

    Example0:
        >>> line_list = 'a = b\none = two\nthree = fish'.split('\n')
        >>> character = '='
        >>> new_lines = align_lines(line_list, character)
        >>> print('\n'.join(new_lines))
        a     = b
        one   = two
        three = fish

    Example1:
        >>> line_list = 'foofish:\n    a = b\n    one    = two\n    three    = fish'.split('\n')
        >>> character = '='
        >>> new_lines = align_lines(line_list, character)
        >>> print('\n'.join(new_lines))
        foofish:
            a        = b
            one      = two
            three    = fish

    Example2:
        >>> character = ':'
        >>> text = codeblock('''
            {'max': '1970/01/01 02:30:13',
             'mean': '1970/01/01 01:10:15',
             'min': '1970/01/01 00:01:41',
             'range': '2:28:32',
             'std': '1:13:57',}''').split('\n')
        >>> new_lines = align_lines(text, ':', ' :')
        >>> print('\n'.join(new_lines))
        {'max'   : '1970/01/01 02:30:13',
         'mean'  : '1970/01/01 01:10:15',
         'min'   : '1970/01/01 00:01:41',
         'range' : '2:28:32',
         'std'   : '1:13:57',}

    Example3:
        >>> line_list = 'foofish:\n a = b = c\n one = two = three\nthree=4= fish'.split('\n')
        >>> character = '='
        >>> # align the second occurence of a character
        >>> new_lines = align_lines(line_list, character, pos=None)
        >>> print('\n'.join(new_lines))
        foofish:
         a   = b   = c
         one = two = three
        three=4    = fish

    Ignore:
        # use this as test case
        \begin{tabular}{lrrll}
        \toprule
        {} &  Names &  Annots & Annots size & Training Edges \\
        \midrule
        training &    390 &    1164 &   2.98\pm2.83 &           9360 \\
        testing  &    363 &    1119 &   3.08\pm2.82 &              - \\
        \bottomrule
        \end{tabular}

    """
    # def visible_len(str_):
    #     """
    #     returns num printed characters accounting for utf8 and ansi
    #     Returns:
    #         http://stackoverflow.com/questions/2247205/length-special-chars
    #     """
    #     import unicodedata
    #     str_ = ensure_unicode(str_)
    #     str_ = strip_ansi(str_)
    #     str_ = unicodedata.normalize('NFC', str_)
    #     return len(str_)

    # FIXME: continue to fix ansi
    if pos is None:
        # Align all occurences
        num_pos = max([line.count(character) for line in line_list])
        pos = list(range(num_pos))

    # Allow multiple alignments
    if isinstance(pos, list):
        pos_list = pos
        # recursive calls
        new_lines = line_list
        for pos in pos_list:
            new_lines = align_lines(new_lines, character=character,
                                    replchar=replchar, pos=pos)
        return new_lines

    # base case
    if replchar is None:
        replchar = character

    # the pos-th character to align
    lpos = pos
    rpos = lpos + 1

    tup_list = [line.split(character) for line in line_list]

    # Find how much padding is needed
    maxlen = 0
    for tup in tup_list:
        if len(tup) >= rpos + 1:
            tup = [strip_ansi(x) for x in tup]
            left_lenlist = list(map(len, tup[0:rpos]))
            left_len = sum(left_lenlist) + lpos * len(replchar)
            maxlen = max(maxlen, left_len)

    # Pad each line to align the pos-th occurence of the chosen character
    new_lines = []
    for tup in tup_list:
        if len(tup) >= rpos + 1:
            lhs = character.join(tup[0:rpos])
            rhs = character.join(tup[rpos:])
            # pad the new line with requested justification
            newline = lhs.ljust(maxlen) + replchar + rhs
            new_lines.append(newline)
        else:
            new_lines.append(replchar.join(tup))
    return new_lines


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_str
        python -m ubelt.util_str all
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
