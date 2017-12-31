# -*- coding: utf-8 -*-
"""
Handles parsing of information out of google style docstrings

CommaneLine:
    # Run the doctests
    python -m ubelt.meta.docscrape_google all
"""
from __future__ import absolute_import, division, print_function, unicode_literals


def parse_google_args(docstr):
    r"""
    Generates dictionaries of argument hints based on a google docstring

    Args:
        docstr (str): a google-style docstring

    Yields:
        dict: dictionaries of parameter hints

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> docstr = parse_google_args.__doc__
        >>> argdict_list = list(parse_google_args(docstr))
        >>> print([sorted(d.items()) for d in argdict_list])
        [[('desc', 'a google-style docstring'), ('name', 'docstr'), ('type', 'str')]]
    """
    from xdoctest.docscrape_google import parse_google_args
    return parse_google_args(docstr)


def parse_google_returns(docstr, return_annot=None):
    r"""
    Generates dictionaries of possible return hints based on a google docstring

    Args:
        docstr (str): a google-style docstring
        return_annot (str): the return type annotation (if one exists)

    Yields:
        dict: dictionaries of return value hints

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> docstr = parse_google_returns.__doc__
        >>> retdict_list = list(parse_google_returns(docstr))
        >>> print([sorted(d.items()) for d in retdict_list])
        [[('desc', 'dictionaries of return value hints'), ('type', 'dict')]]

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> docstr = split_google_docblocks.__doc__
        >>> retdict_list = list(parse_google_returns(docstr))
        >>> print([sorted(d.items())[1] for d in retdict_list])
        [('type', 'list')]
    """
    from xdoctest.docscrape_google import parse_google_returns
    return parse_google_returns(docstr, return_annot)


def parse_google_retblock(lines, return_annot=None):
    r"""
    Args:
        lines (str): unindented lines from a Returns or Yields section
        return_annot (str): the return type annotation (if one exists)

    Yeilds:
        dict: each dict specifies the return type and its description

    CommandLine:
        python -m ubelt.meta.docscrape_google parse_google_retblock

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> # Test various ways that retlines can be written
        >>> assert len(list(parse_google_retblock('list: a desc'))) == 1
        >>> assert len(list(parse_google_retblock('no type, just desc'))) == 0
        >>> # ---
        >>> hints = list(parse_google_retblock('\n'.join([
        ...     'entire line can be desc',
        ...     ' ',
        ...     ' if a return type annotation is given',
        ... ]), return_annot='int'))
        >>> assert len(hints) == 1
        >>> # ---
        >>> hints = list(parse_google_retblock('\n'.join([
        ...     'bool: a description',
        ...     ' with a newline',
        ... ])))
        >>> assert len(hints) == 1
        >>> # ---
        >>> hints = list(parse_google_retblock('\n'.join([
        ...     'int or bool: a description',
        ...     ' ',
        ...     ' with a separated newline',
        ...     ' ',
        ... ])))
        >>> assert len(hints) == 1
        >>> # ---
        >>> hints = list(parse_google_retblock('\n'.join([
        ...     # Multiple types can be specified
        ...     'threading.Thread: a description',
        ...     '(int, str): a tuple of int and str',
        ...     'tuple: a tuple of int and str',
        ...     'Tuple[int, str]: a tuple of int and str',
        ... ])))
        >>> assert len(hints) == 4
        >>> # ---
        >>> hints = list(parse_google_retblock('\n'.join([
        ...     # If the colon is not specified nothing will be parsed
        ...     'list',
        ...     'Tuple[int, str]',
        ... ])))
        >>> assert len(hints) == 0
    """
    from xdoctest.docscrape_google import parse_google_retblock
    return parse_google_retblock(lines, return_annot)


def parse_google_argblock(lines):
    r"""
    Args:
        lines (str): the unindented lines from an Args docstring section

    References:
        # It is not clear which of these is *the* standard or if there is one
        https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html#example-google
        http://www.sphinx-doc.org/en/stable/ext/example_google.html#example-google

    CommandLine:
        python -m ubelt.meta.docscrape_google parse_google_argblock

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> # Test various ways that arglines can be written
        >>> line_list = [
        ...     '',
        ...     'foo1 (int): a description',
        ...     'foo2: a description\n    with a newline',
        ...     'foo3 (int or str): a description',
        ...     'foo4 (int or threading.Thread): a description',
        ...     #
        ...     # this is sphynx-like typing style
        ...     'param1 (:obj:`str`, optional): ',
        ...     'param2 (:obj:`list` of :obj:`str`):',
        ...     #
        ...     # the Type[type] syntax is defined by the python typeing module
        ...     'attr1 (Optional[int]): Description of `attr1`.',
        ...     'attr2 (List[str]): Description of `attr2`.',
        ...     'attr3 (Dict[str, str]): Description of `attr3`.',
        ... ]
        >>> lines = '\n'.join(line_list)
        >>> argdict_list = list(parse_google_argblock(lines))
        >>> # All lines except the first should be accepted
        >>> assert len(argdict_list) == len(line_list) - 1
        >>> assert argdict_list[1]['desc'] == 'a description with a newline'
    """
    from xdoctest.docscrape_google import parse_google_argblock
    return parse_google_argblock(lines)


def split_google_docblocks(docstr):
    r"""
    Args:
        docstr (str): a docstring

    Returns:
        list: list of 2-tuples where the first item is a google style docstring
            tag and the second item is the bock corresponding to that tag.

    Example:
        >>> from ubelt.meta.docscrape_google import *  # NOQA
        >>> docstr = split_google_docblocks.__doc__
        >>> groups = split_google_docblocks(docstr)
        >>> #print('groups = %s' % (groups,))
        >>> assert len(groups) == 3
        >>> print([k for k, v in groups])
        ['Args', 'Returns', 'Example']
    """
    from xdoctest.docscrape_google import split_google_docblocks
    return split_google_docblocks(docstr)


if __name__ == '__main__':
    import xdoctest as xdoc
    xdoc.doctest_module()
