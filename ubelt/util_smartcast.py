"""
Goal is to handle:
    simple scalar types (int, float, complex, str)
    simple container types (list, tuples, sets) (requires pyparsing)

# TODO: parse nesting for a list
"""
import six
import types

if six.PY2:
    BooleanType = types.BooleanType
else:
    BooleanType = bool

NoneType = type(None)

__all__ = ['smartcast']


def smartcast(item, astype=None, strict=False):
    r"""
    Converts a string into a standard python type.

    In many cases this is a simple alternative to `eval`. However, the syntax
    rules use here are more permissive and forgiving.

    The `astype` can be specified to provide a type hint, otherwise we try to
    cast to the following types in this order: int, float, complex, bool, none

    Args:
        item (str): represents some data of another type.
        astype (type): if None, try infer what the best type is, if
            astype == 'eval' then try to return `eval(item)`, Otherwise, try to
            cast to this type.
        strict (bool): if True raises a TypeError if conversion fails

    Returns:
        object: some item

    Raises:
        TypeError: if we cannot determine the type

    CommandLine:
        python -m ubelt.util_smartcast smartcast

    Example:
        >>> assert smartcast('?') == '?'
        >>> assert smartcast('1') == 1
        >>> assert smartcast('1.0') == 1.0
        >>> assert smartcast('1.2') == 1.2
        >>> assert smartcast('True') is True
        >>> assert smartcast('false') is False
        >>> assert smartcast('None') is None
        >>> assert smartcast('1', str) == '1'
        >>> assert smartcast('1', eval) == 1
        >>> assert smartcast('1', bool) is True
        >>> assert smartcast('[1,2]', eval) == [1, 2]

    Example:
        >>> def check_typed_value(item, want, astype=None):
        >>>     got = smartcast(item, astype)
        >>>     assert got == want and isinstance(got, type(want)), (
        >>>         'Cast {!r} to {!r}, but got {!r}'.format(item, want, got))
        >>> check_typed_value('?', '?')
        >>> check_typed_value('1', 1)
        >>> check_typed_value('1.0', 1.0)
        >>> check_typed_value('1.2', 1.2)
        >>> check_typed_value('True', True)
        >>> check_typed_value('None', None)
        >>> check_typed_value('1', 1, int)
        >>> check_typed_value('1', True, bool)
        >>> check_typed_value('1', 1.0, float)
        >>> check_typed_value('1', 1.0+0j, complex)

    # Example:
    #     >>> smartcast(1)
    #     TypeError: item must be a string
    """
    if not isinstance(item, six.string_types):
        raise TypeError('item must be a string')
    if astype is None:
        type_list = [int, float, complex, bool, NoneType]
        for astype in type_list:
            try:
                return _as_smart_type(item, astype)
            except (TypeError, ValueError):
                pass
        if strict:
            raise TypeError('Could not smartcast item={!r}'.format(item))
        else:
            return item
    else:
        return _as_smart_type(item, astype)


def _as_smart_type(item, astype):
    """
    casts item to type, and tries to be clever when item is a string, otherwise
    it simply calls `astype(item)`.

    Args:
        item (str): represents some data of another type.
        astype (type or str): type to attempt to cast to

    Returns:
        object:

    CommandLine:
        python -m ubelt.util_smartcast _as_smart_type

    Example:
        >>> from ubelt.util_smartcast import *  # NOQA
        >>> assert _as_smart_type('1', int) == 1
        >>> assert _as_smart_type('1', str) == '1'
        >>> assert _as_smart_type('1', bool) is True
        >>> assert _as_smart_type('0', bool) is False
        >>> assert _as_smart_type('1', float) == 1.0
        >>> assert _as_smart_type('(1,3)', 'eval') == (1, 3)
        >>> assert _as_smart_type('(1,3)', eval) == (1, 3)
        >>> assert _as_smart_type('1::3', slice) == slice(1, None, 3)
    """
    # try:
    #     if issubclass(astype, NoneType):
    #         return item
    # except TypeError:
    #     pass
    if not isinstance(item, six.string_types):
        raise TypeError('item must be a string')

    if astype is NoneType:
        return _smartcast_none(item)
    elif astype is bool:
        return _smartcast_bool(item)
    elif astype is slice:
        return _smartcast_slice(item)
    elif astype in [int, float, complex]:
        return astype(item)
    elif astype is str:
        return item
    elif astype is eval:
        return eval(item, {}, {})
    # TODO:
    #    use parse_nestings to smartcast lists/tuples/sets
    elif isinstance(astype, six.string_types):
        # allow types to be given as strings
        astype = {
            'bool': bool,
            'int': int,
            'float': float,
            'complex': complex,
            'str': str,
            'eval': eval,
            'none': NoneType,
        }[astype.lower()]
        return _as_smart_type(item, astype)
    raise NotImplementedError('Unknown smart astype=%r' % (astype,))


def _smartcast_slice(item):
    args = [int(p) if p else None for p in item.split(':')]
    return slice(*args)


def _smartcast_none(item):
    """
    Casts a string to None.
    """
    if item.lower() == 'none':
        return None
    else:
        raise TypeError('string does not represent none')


def _smartcast_bool(item):
    """
    Casts a string to a boolean.
    Setting strict=False allows '0' and '1' to be used as a bool
    """
    lower = item.lower()
    if lower == 'true':
        return True
    elif lower == 'false':
        return False
    else:
        try:
            return bool(int(item))
        except TypeError:
            pass
        raise TypeError('item does not represent boolean')


def parse_nestings(string, nesters=['()', '[]', '{}', '<>', "''", '""'], escape='\\'):
    r"""
    Recursively partitions strings into nested or quoted expressions.

    By default four types of nesters (paren, brak, curly, and angle) are
    recognied along with double and single quotes. Different nesters can be
    specified for custom uses.

    SeeAlso:
        recombine_nestings - takes the result of this function

    Returns:
        list: an abstract syntax tree represented as a list of lists

    References:
        http://stackoverflow.com/questions/4801403/pyparsing-nested-mutiple-opener-clo

    CommandLine:
        python -m ubelt.util_smartcast parse_nestings

    Example:
        >>> from ubelt.util_smartcast import *  # NOQA
        >>> import ubelt as ub
        >>> string = r'lambda u: sign("\"u(\'fdfds\')") * abs(u)**3.0 * greater(u, 0)'
        >>> parse_tree = parse_nestings(string)
        >>> print('parse_tree = {}'.format(ub.repr2(parse_tree, nl=3, si=True)))
        >>> assert recombine_nestings(parse_tree) == string
    """
    import pyparsing as pp

    def as_tagged_tree(parent, doctag=None):
        """Returns the parse results as XML. Tags are created for tokens and lists that have defined results names."""
        namedItems = dict(
            (v[1], k)
            for (k, vlist) in parent._ParseResults__tokdict.items()
            for v in vlist
        )
        # collapse out indents if formatting is not desired
        parentTag = None
        if doctag is not None:
            parentTag = doctag
        else:
            if parent._ParseResults__name:
                parentTag = parent._ParseResults__name
        if not parentTag:
            parentTag = "ITEM"
        out = []
        for i, res in enumerate(parent._ParseResults__toklist):
            if isinstance(res, pp.ParseResults):
                if i in namedItems:
                    child = as_tagged_tree(res, namedItems[i])
                else:
                    child = as_tagged_tree(res, None)
                out.append(child)
            else:
                # individual token, see if there is a name for it
                resTag = None
                if i in namedItems:
                    resTag = namedItems[i]
                if not resTag:
                    resTag = "ITEM"
                child = (resTag, pp._ustr(res))
                out += [child]
        # return out
        return (parentTag, out)

    def combine_nested(opener, closer, content, name=None):
        r"""
        opener, closer, content = '(', ')', nest_body
        """
        ret1 = pp.Forward()
        group = pp.Group(opener + pp.ZeroOrMore(content) + closer)
        ret2 = ret1 << group
        ret3 = ret2
        if name is not None:
            ret3 = ret2.setResultsName(name)
        return ret3

    def regex_or(*patterns):
        """ matches one of the patterns """
        return '{}'.format('|'.join(patterns))

    def nocapture(pat):
        """ A non-capturing version of regular parentheses """
        return '(?:{})'.format(pat)

    # Current Best Grammar
    nest_body = pp.Forward()
    nest_expr_list = []
    for left, right in nesters:
        if left == right:
            # Treat left==right nestings as quoted strings
            q = left
            quote_pat_fmt = (nocapture(regex_or(
                r'[^{quote}\n\r\\]',
                nocapture('{quote}{quote}'),
                nocapture(r'\\' + nocapture(regex_or(
                    '[^x]',
                    'x[0-9a-fA-F]+')
                ))
            )) + '*')
            quote_pat_fmt = r'(?:[^{quote}\n\r\\]|(?:{quote}{quote})|(?:\\(?:[^x]|x[0-9a-fA-F]+)))*'
            quote_pat = quote_pat_fmt.format(quote=q)
            quotedString = pp.Group(q + pp.Regex(quote_pat) + q)
            nest_expr = quotedString.setResultsName('nest' + left + right)
        else:
            nest_expr = combine_nested(left, right, content=nest_body, name='nest' + left + right)
        nest_expr_list.append(nest_expr)

    # quotedString = Combine(Regex(r'"(?:[^"\n\r\\]|(?:"")|(?:\\(?:[^x]|x[0-9a-fA-F]+)))*')+'"'|
    #                        Regex(r"'(?:[^'\n\r\\]|(?:'')|(?:\\(?:[^x]|x[0-9a-fA-F]+)))*")+"'").setName("quotedString using single or double quotes")

    nonBracePrintables = ''.join(c for c in pp.printables if c not in ''.join(nesters)) + ' '
    nonNested = pp.Word(nonBracePrintables).setResultsName('nonNested')
    nonNested = nonNested.leaveWhitespace()

    # The body might be a non-nested set of characters
    nest_body_input = nonNested
    # Allow each type of nested expression to be present in the body
    for nest_expr in nest_expr_list:
        nest_body_input = nest_body_input | nest_expr

    nest_body << nest_body_input

    nest_body = nest_body.leaveWhitespace()
    parser = pp.ZeroOrMore(nest_body)

    if len(string) > 0:
        tokens = parser.parseString(string)
        # parse_tree = tokens.asList()
        parse_tree = as_tagged_tree(tokens)
    else:
        # parse_tree = []
        parse_tree = ('nonNested', [])
    return parse_tree


def recombine_nestings(parse_tree):
    values = parse_tree[1]
    if isinstance(values, list):
        literals = map(recombine_nestings, values)
        recombined = ''.join(literals)
    else:
        recombined = values
    return recombined


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_smartcast all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
