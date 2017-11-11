import six
import math
import collections

# __all__ = [
#     'repr2',
#     '_format_list',
#     '_format_dict',
# ]


def repr2(val, **kwargs):
    """
    Constructs a "pretty" string representation.

    This is an alternative to repr, and `pprint.pformat` that attempts to be
    more both configurable and generate output that is consistent between
    python versions.

    Args:
        val (object): an arbitrary python object
        **kwargs: si, stritems, strkeys, strvals, sk, sv, nl, newlines, nobr,
                  nobraces, cbr, compact_brace, trailsep, trailing_sep,
                  explicit, itemsep, precision, kvsep, sort

    Returns:
        str: output string

    CommandLine:
        python -m ubelt.util_format repr2:0
        python -m ubelt.util_format repr2:1

    Example:
        >>> from ubelt.util_format import *
        >>> import ubelt as ub
        >>> dict_ = {
        ...     'custom_types': [slice(0, 1, None), 1/3],
        ...     'nest_dict': {'k1': [1, 2, {3: {4, 5}}],
        ...                   'key2': [1, 2, {3: {4, 5}}],
        ...                   'key3': [1, 2, {3: {4, 5}}],
        ...                   },
        ...     'nest_dict2': {'k': [1, 2, {3: {4, 5}}]},
        ...     'nested_tuples': [tuple([1]), tuple([2, 3]), frozenset([4, 5, 6])],
        ...     'one_tup': tuple([1]),
        ...     'simple_dict': {'spam': 'eggs', 'ham': 'jam'},
        ...     'simple_list': [1, 2, 'red', 'blue'],
        ...     'odict': ub.odict([(1, '1'), (2, '2')]),
        ... }
        >>> result = repr2(dict_, nl=3, precision=2); print(result)
        >>> result = repr2(dict_, nl=2, precision=2); print(result)
        >>> result = repr2(dict_, nl=1, precision=2); print(result)
        >>> result = repr2(dict_, nl=1, precision=2, itemsep='', explicit=True); print(result)
        >>> result = repr2(dict_, nl=1, precision=2, nobr=1, itemsep='', explicit=True); print(result)
        >>> result = repr2(dict_, nl=3, precision=2, cbr=True); print(result)
        >>> result = repr2(dict_, nl=3, precision=2, si=True); print(result)
        >>> result = repr2(dict_, nl=3, sort=True); print(result)
        >>> result = repr2(dict_, nl=3, sort=False, trailing_sep=False); print(result)
        >>> result = repr2(dict_, nl=3, sort=False, trailing_sep=False, nobr=True); print(result)

    Example:
        >>> from ubelt.util_format import *
        >>> def _nest(d, w):
        ...     if d == 0:
        ...         return {}
        ...     else:
        ...         return {'n{}'.format(d): _nest(d - 1, w + 1), 'm{}'.format(d): _nest(d - 1, w + 1)}
        >>> dict_ = _nest(d=4, w=1)
        >>> result = repr2(dict_, nl=6, precision=2, cbr=1)
        >>> print('---')
        >>> print(result)
    """
    if isinstance(val, dict):
        return _format_dict(val, **kwargs)
    elif isinstance(val, (list, tuple, set, frozenset)):
        return _format_list(val, **kwargs)
    # check any registered functions for special formatters
    for type, func in _Formatters.func_registry.items():
        if isinstance(val, type):
            return func(val, **kwargs)
    # base case
    return _format_object(val, **kwargs)


class _Formatters(object):
    # set_types = [set, frozenset]
    # list_types = [list, tuple]
    # dict_types = [dict]
    # custom_types = {
    #     'numpy': [],
    #     'pandas': [],
    # }
    # @classmethod
    # def sequence_types(cls):
    #     return cls.list_types + cls.set_types
    # TODO: register numpy and pandas by default if available
    func_registry = {}

    @classmethod
    def register(cls, type):
        """
        Registers a custom formatting function with ub.repr2
        """
        def _decorator(func):
            cls.func_registry[type] = func
            return func
        return _decorator


class _FormatFuncs(object):
    """
    Standard custom formatting funcs for non-nested types
    """
    # TODO: add support for custom type for pandas / numpy

    @_Formatters.register(float)
    def format_float(val, **kwargs):
        precision = kwargs.get('precision', None)
        if precision is None:
            return six.text_type(val)
        else:
            return ('{:.%df}' % precision).format(val)

    @_Formatters.register(slice)
    def format_slice(val, **kwargs):
        if kwargs.get('itemsep', ' ') == '':
            return 'slice(%r,%r,%r)' % (val.start, val.stop, val.step)
        else:
            return _format_object(val, **kwargs)


def _format_object(val, **kwargs):
    stritems = kwargs.get('si', kwargs.get('stritems', False))
    strvals = stritems or kwargs.get('sv', kwargs.get('strvals', False))
    base_valfunc = six.text_type if strvals else repr

    itemstr = base_valfunc(val)

    # Remove unicode repr from python2 to agree with python3 output
    if six.PY2 and isinstance(val, six.string_types):  # nocover
        if itemstr.startswith(("u'", 'u"')):
            itemstr = itemstr[1:]
    return itemstr


def _format_list(list_, **kwargs):
    r"""
    Makes a pretty printable / human-readable string representation of a
    sequence. In most cases this string could be evaled.

    Args:
        list_ (list): input list
        **kwargs: nl, newlines, packed, nobr, nobraces, itemsep, trailing_sep,
            strvals indent_, precision, use_numpy, with_dtype, force_dtype,
            stritems, strkeys, align, explicit, sort, key_order, maxlen

    Returns:
        str: retstr

    Example:
        >>> print(_format_list([]))
        []
        >>> print(_format_list([], nobr=True))
        []
        >>> print(_format_list([1], nl=0))
        [1]
        >>> print(_format_list([1], nobr=True))
        1,
    """
    newlines = kwargs.pop('nl', kwargs.pop('newlines', 1))
    kwargs['nl'] = _rectify_countdown_or_bool(newlines)

    nobraces = kwargs.pop('nobr', kwargs.pop('nobraces', False))

    itemsep = kwargs.get('itemsep', ' ')
    # Doesn't actually put in trailing comma if on same line
    compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))

    itemstrs = _list_itemstrs(list_, **kwargs)
    if len(itemstrs) == 0:
        nobraces = False  # force braces to prevent empty output

    is_tuple = isinstance(list_, tuple)
    is_set = isinstance(list_, (set, frozenset,))
    if nobraces:
        lbr, rbr = '', ''
    elif is_tuple:
        lbr, rbr  = '(', ')'
    elif is_set:
        lbr, rbr  = '{', '}'
    else:
        lbr, rbr  = '[', ']'

    trailing_sep = kwargs.get('trailsep', kwargs.get('trailing_sep', newlines > 0 and len(itemstrs)))

    # The trailing separator is always needed for single item tuples
    if is_tuple and len(list_) <= 1:
        trailing_sep = True

    if len(itemstrs) == 0:
        newlines = False

    retstr = _join_itemstrs(itemstrs, itemsep, newlines, nobraces,
                            trailing_sep, compact_brace, lbr, rbr)
    return retstr


def _format_dict(dict_, **kwargs):
    r"""
    Makes a pretty printable / human-readable string representation of a
    dictionary. In most cases this string could be evaled.

    Args:
        dict_ (dict_):  a dictionary
        **kwargs: si, stritems, strkeys, strvals, sk, sv, nl, newlines, nobr,
                  nobraces, cbr, compact_brace, trailing_sep,
                  explicit, itemsep, precision, kvsep, sort

    Kwargs:
        sort (None): returns str sorted by a metric (default = None)
        nl (int): prefered alias for newline. can be a coundown variable
            (default = None)
        explicit (int): can be a countdown variable. if True, uses
            dict(a=b) syntax instead of {'a': b}
        nobr (bool): removes outer braces (default = False)
    """
    stritems = kwargs.pop('si', kwargs.pop('stritems', False))
    if stritems:
        kwargs['strkeys'] = True
        kwargs['strvals'] = True

    kwargs['strkeys'] = kwargs.pop('sk', kwargs.pop('strkeys', False))
    kwargs['strvals'] = kwargs.pop('sv', kwargs.pop('strvals', False))

    newlines = kwargs.pop('nl', kwargs.pop('newlines', True))
    kwargs['nl'] = _rectify_countdown_or_bool(newlines)

    nobraces = kwargs.pop('nobr', kwargs.pop('nobraces', False))

    # Doesn't actually put in trailing comma if on same line
    compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))
    trailing_sep = kwargs.get('trailsep', kwargs.get('trailing_sep', newlines > 0))
    explicit = kwargs.get('explicit', False)
    itemsep = kwargs.get('itemsep', ' ')

    if len(dict_) == 0:
        return 'dict()' if explicit else '{}'

    itemstrs = _dict_itemstrs(dict_, **kwargs)

    if nobraces:
        lbr, rbr = '', ''
    elif explicit:
        lbr, rbr = 'dict(', ')'
    else:
        lbr, rbr = '{', '}'

    retstr = _join_itemstrs(itemstrs, itemsep, newlines, nobraces,
                            trailing_sep, compact_brace, lbr, rbr)
    return retstr


def _join_itemstrs(itemstrs, itemsep, newlines, nobraces, trailing_sep,
                   compact_brace, lbr, rbr):
    """
    Joins stringified items with separators newlines and container-braces.
    """
    import ubelt as ub

    if newlines > 0:
        sep = ',\n'
        if nobraces:
            body_str = sep.join(itemstrs)
            if trailing_sep and len(itemstrs) > 0:
                body_str += ','
            retstr = body_str
        else:
            if compact_brace:
                # Why must we modify the indentation below and not here?
                # prefix = ''
                # rest = [ub.indent(s, prefix) for s in itemstrs[1:]]
                # indented = itemstrs[0:1] + rest
                indented = itemstrs
            else:
                prefix = ' ' * 4
                indented = [ub.indent(s, prefix) for s in itemstrs]

            body_str = sep.join(indented)
            if trailing_sep and len(itemstrs) > 0:
                body_str += ','
            if compact_brace:
                # Why can we modify the indentation here but not above?
                braced_body_str = (lbr + body_str.replace('\n', '\n ') + rbr)
            else:
                braced_body_str = (lbr + '\n' + body_str + '\n' + rbr)
            retstr = braced_body_str
    else:
        sep = ',' + itemsep
        body_str = sep.join(itemstrs)
        if trailing_sep and len(itemstrs) > 0:
            body_str += ','
        retstr  = (lbr + body_str +  rbr)
    return retstr


def _dict_itemstrs(dict_, **kwargs):
    """
    Example:
        >>> from ubelt.util_format import *
        >>> dict_ =  {'b': .1, 'l': 'st', 'g': 1.0, 's': 10, 'm': 0.9, 'w': .5}
        >>> kwargs = {'strkeys': True}
        >>> itemstrs = _dict_itemstrs(dict_, **kwargs)
        >>> char_order = [p[0] for p in itemstrs]
        >>> assert char_order == ['b', 'g', 'l', 'm', 's', 'w']
    """
    import ubelt as ub
    explicit = kwargs.get('explicit', False)
    kwargs['explicit'] = _rectify_countdown_or_bool(explicit)
    precision = kwargs.get('precision', None)
    kvsep = kwargs.get('kvsep', ': ')
    if explicit:
        kvsep = '='

    def make_item_str(key, val):
        if explicit or kwargs.get('strkeys', False):
            key_str = six.text_type(key)
        else:
            key_str = repr2(key, precision=precision)

        prefix = key_str + kvsep
        val_str = repr2(val, **kwargs)

        # If the first line does not end with an open nest char
        # (e.g. for ndarrays), otherwise we need to worry about
        # residual indentation.
        pos = val_str.find('\n')
        first_line = val_str if pos == -1 else val_str[:pos]

        compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))

        if compact_brace or not first_line.rstrip().endswith(tuple('([{<')):
            rest = '' if pos == -1 else val_str[pos:]
            val_str = first_line.lstrip() + rest
            item_str = ub.hzcat([prefix, val_str])
        else:
            item_str = prefix + val_str
        return item_str

    items = list(six.iteritems(dict_))
    itemstrs = [make_item_str(key, val) for (key, val) in items]

    sort = kwargs.get('sort', None)
    if sort is None:
        sort = True
    if isinstance(dict_, collections.OrderedDict):
        # never sort ordered dicts; they are perfect just the way they are!
        sort = False
    if sort:
        itemstrs = _sort_itemstrs(items, itemstrs)
    return itemstrs


def _list_itemstrs(list_, **kwargs):
    items = list(list_)
    itemstrs = [repr2(item, **kwargs) for item in items]

    sort = kwargs.get('sort', None)
    if sort is None:
        # Force orderings on sets.
        sort = isinstance(list_, (set, frozenset))
    if sort:
        itemstrs = _sort_itemstrs(items, itemstrs)
    return itemstrs


def _sort_itemstrs(items, itemstrs):
    # First try to sort items by their normal values
    # If that doesnt work, then sort by their string values
    import ubelt as ub
    try:
        # Set ordering is not unique. Sort by strings values instead.
        if _peek_isinstance(items, (set, frozenset)):
            raise TypeError
        sortx = ub.argsort(items)
    except TypeError:
        sortx = ub.argsort(itemstrs)
    itemstrs = list(ub.take(itemstrs, sortx))
    return itemstrs


def _peek_isinstance(items, types):
    return len(items) > 0 and isinstance(items[0], types)


def _rectify_countdown_or_bool(count_or_bool):
    """
    used by recrusive functions to specify which level to turn a bool on in
    counting down yeilds True, True, ..., False
    conting up yeilds False, False, False, ... True

    Args:
        count_or_bool (bool or int): if positive will count down, if negative
            will count up, if bool will remain same

    Returns:
        int or bool: count_or_bool_

    CommandLine:
        python -m utool.util_str --test-_rectify_countdown_or_bool

    Example:
        >>> from ubelt.util_format import _rectify_countdown_or_bool  # NOQA
        >>> count_or_bool = True
        >>> a1 = (_rectify_countdown_or_bool(2))
        >>> a2 = (_rectify_countdown_or_bool(1))
        >>> a3 = (_rectify_countdown_or_bool(0))
        >>> a4 = (_rectify_countdown_or_bool(-1))
        >>> a5 = (_rectify_countdown_or_bool(-2))
        >>> a6 = (_rectify_countdown_or_bool(True))
        >>> a7 = (_rectify_countdown_or_bool(False))
        >>> a8 = (_rectify_countdown_or_bool(None))
        >>> result = [a1, a2, a3, a4, a5, a6, a7, a8]
        >>> print(result)
        [1, 0, 0, 0, -1, True, False, False]
    """
    if count_or_bool is True or count_or_bool is False:
        count_or_bool_ = count_or_bool
    elif isinstance(count_or_bool, int):
        if count_or_bool == 0:
            return 0
        sign_ =  math.copysign(1, count_or_bool)
        count_or_bool_ = int(count_or_bool - sign_)
    else:
        count_or_bool_ = False
    return count_or_bool_


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_format
    """
    import xdoctest as xdoc
    xdoc.doctest_module()
