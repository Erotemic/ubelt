# -*- coding: utf-8 -*-
"""
Defines the function `repr2`, which allows for a bit more customization than
`repr` or `pprint`. See the docstring for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import six
import collections


def repr2(data, **kwargs):
    """
    Makes a pretty and easy-to-doctest string representation!

    This is an alternative to repr, and `pprint.pformat` that attempts to be
    both more configurable and generate output that is consistent between
    python versions.

    Notes:
        This function has many keyword arguments that can be used to customize
        the final representation. For convinience some of the more frequently
        used kwargs have short aliases. See `Args` for more details.

    Args:
        data (object): an arbitrary python object
        **kwargs: see `the Kwargs` section

    Kwargs:
        si, stritems, (bool):
            dict/list items use str instead of repr

        strkeys, sk (bool):
            dict keys use str instead of repr

        strvals, sv (bool):
            dict values use str instead of repr

        nl, newlines (int | bool):
            number of top level nestings to place a newline after. If true all
            items are followed by newlines regardless of nesting level.
            Defaults to 1 for lists and True for dicts.

        nobr, nobraces (bool, default=False):
            if True, text will not contain outer braces for containers

        cbr, compact_brace (bool, default=False):
            if True, braces are compactified (i.e. they will not have newlines
            placed directly after them, think java / K&R / 1TBS)

        trailsep, trailing_sep (bool):
            if True, a separator is placed after the last item in a sequence.
            By default this is True if there are any `nl > 0`.

        explicit (bool, default=False):
            changes dict representation from `{k1: v1, ...}` to
            `dict(k1=v1, ...)`.

        precision (int, default=None):
            if specified floats are formatted with this precision

        kvsep (str, default=': '):
            separator between keys and values

        itemsep (str, default=' '):
            separator between items

        sort (bool | callable, default=None):
            if None, then sort unordered collections, but keep the ordering of
            ordered collections. This option attempts to be determenistic in
            most cases.

            New in 0.8.0: if `sort` is callable, it will be used as a
            key-function to sort all collections.

            if False, then nothing will be sorted, and the representation of
            unordered collections will be arbitrary and possibly
            non-determenistic.

            if True, attempts to sort all collections in the returned text.
            Currently if True this WILL sort lists.
            Currently if True this WILL NOT sort OrderedDicts.
            NOTE:
                The previous behavior may not be intuitive, as such the
                behavior of this arg is subject to change.

        suppress_small (bool):
            passed to `numpy.array2string` for ndarrays

        max_line_width (int):
            passed to `numpy.array2string` for ndarrays

        with_dtype (bool):
            only relevant to ndarrays. if True includes the dtype.

        extensions (FormatterExtensions):
            a custom `FormatterExtensions` instance that can overwrite or
            define how different types of objects are formatted.

    Returns:
        str: outstr: output string

    Notes:
        There are also internal kwargs, which should not be used:
            _return_info (bool):  return information about child context
            _root_info (depth): information about parent context

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
        >>> result = repr2(dict_, nl=-1, precision=2)
        >>> print('---')
        >>> print(result)
    """
    custom_extensions = kwargs.get('extensions', None)

    _return_info = kwargs.get('_return_info', False)
    kwargs['_root_info'] = _rectify_root_info(kwargs.get('_root_info', None))

    outstr = None
    _leaf_info = None

    if custom_extensions:
        func = custom_extensions.lookup(data)
        if func is not None:
            outstr = func(data, **kwargs)

    if outstr is None:
        if isinstance(data, dict):
            outstr, _leaf_info = _format_dict(data, **kwargs)
        elif isinstance(data, (list, tuple, set, frozenset)):
            outstr, _leaf_info = _format_list(data, **kwargs)

    if outstr is None:
        # check any globally registered functions for special formatters
        func = _FORMATTER_EXTENSIONS.lookup(data)
        if func is not None:
            outstr = func(data, **kwargs)
        else:
            outstr = _format_object(data, **kwargs)

    if _return_info:
        _leaf_info = _rectify_leaf_info(_leaf_info)
        return outstr, _leaf_info
    else:
        return outstr


def _rectify_root_info(_root_info):
    if _root_info is None:
        _root_info = {
            'depth': 0,
        }
    return _root_info


def _rectify_leaf_info(_leaf_info):
    if _leaf_info is None:
        _leaf_info = {
            'max_height': 0,
            'min_height': 0,
        }
    return _leaf_info


class FormatterExtensions(object):
    """
    Helper class for managing non-builtin (e.g. numpy) format types.

    This module (`ubelt.util_format`) maintains a global set of basic
    extensions, but it is also possible to create a locally scoped set of
    extensions and explicilty pass it to repr2. The following example
    demonstrates this.

    Example:
        >>> import ubelt as ub
        >>> class MyObject(object):
        >>>     pass
        >>> data = {'a': [1, 2.2222, MyObject()], 'b': MyObject()}
        >>> # Create a custom set of extensions
        >>> extensions = ub.FormatterExtensions()
        >>> # Register a function to format your specific type
        >>> @extensions.register(MyObject)
        >>> def format_myobject(data, **kwargs):
        >>>     return 'I can do anything here'
        >>> # Repr2 will now respect the passed custom extensions
        >>> # Note that the global extensions will still be respected
        >>> # unless they are overloaded.
        >>> print(ub.repr2(data, nl=-1, precision=1, extensions=extensions))
        {
            'a': [1, 2.2, I can do anything here],
            'b': I can do anything here
        }
        >>> # Overload the formatter for float and int
        >>> @extensions.register((float, int))
        >>> def format_myobject(data, **kwargs):
        >>>     return str((data + 10) // 2)
        >>> print(ub.repr2(data, nl=-1, precision=1, extensions=extensions))
        {
            'a': [5, 6.0, I can do anything here],
            'b': I can do anything here
        }
    """
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

    def __init__(self):
        self.func_registry = {}
        self.lazy_init = []
        # self._lazy_registrations = [
        #     self._register_numpy_extensions,
        #     self._register_builtin_extensions,
        # ]

    def register(self, type):
        """
        Registers a custom formatting function with ub.repr2
        """
        def _decorator(func):
            if isinstance(type, tuple):
                for t in type:
                    self.func_registry[t] = func
            else:
                self.func_registry[type] = func
            return func
        return _decorator

    def lookup(self, data):
        """
        Returns an appropriate function to format `data` if one has been
        registered.
        """
        for func in self.lazy_init:
            func()

        for type, func in self.func_registry.items():
            if isinstance(data, type):
                return func

    # def _register_pandas_extensions(self):
    #     # import numpy as np
    #     # @self.register(pd.DataFrame)
    #     def format_pandas(data, **kwargs):
    #         precision = kwargs.get('precision', None)
    #         float_format = (None if precision is None
    #                         else '%.{}f'.format(precision))
    #         formatted = data.to_string(float_format=float_format)
    #         return formatted

    def _register_numpy_extensions(self):
        """
        CommandLine:
            python -m ubelt.util_format FormatterExtensions._register_numpy_extensions

        Example:
            >>> import sys
            >>> import pytest
            >>> import ubelt as ub
            >>> if not ub.modname_to_modpath('numpy'):
            ...     raise pytest.skip()
            >>> # xdoctest: +IGNORE_WHITESPACE
            >>> import numpy as np
            >>> data = np.array([[.2, 42, 5], [21.2, 3, .4]])
            >>> print(ub.repr2(data))
            np.array([[ 0.2, 42. ,  5. ],
                      [21.2,  3. ,  0.4]], dtype=np.float64)
            >>> print(ub.repr2(data, with_dtype=False))
            np.array([[ 0.2, 42. ,  5. ],
                      [21.2,  3. ,  0.4]])
            >>> print(ub.repr2(data, strvals=True))
            [[ 0.2, 42. ,  5. ],
             [21.2,  3. ,  0.4]]
            >>> data = np.empty((0, 10), dtype=np.float64)
            >>> print(ub.repr2(data, strvals=False))
            np.empty((0, 10), dtype=np.float64)
            >>> print(ub.repr2(data, strvals=True))
            []
            >>> data = np.ma.empty((0, 10), dtype=np.float64)
            >>> print(ub.repr2(data, strvals=False))
            np.ma.empty((0, 10), dtype=np.float64)
        """
        import numpy as np
        @self.register(np.ndarray)
        def format_ndarray(data, **kwargs):
            import re
            strvals = kwargs.get('sv', kwargs.get('strvals', False))
            itemsep = kwargs.get('itemsep', ' ')
            precision = kwargs.get('precision', None)
            suppress_small = kwargs.get('supress_small', None)
            max_line_width = kwargs.get('max_line_width', None)
            with_dtype = kwargs.get('with_dtype', kwargs.get('dtype', not strvals))
            newlines = kwargs.pop('nl', kwargs.pop('newlines', 1))

            # if with_dtype and strvals:
            #     raise ValueError('cannot format with strvals and dtype')

            separator = ',' + itemsep

            if strvals:
                prefix = ''
                suffix = ''
            else:
                modname = type(data).__module__
                # substitute shorthand for numpy module names
                np_nice = 'np'
                modname = re.sub('\\bnumpy\\b', np_nice, modname)
                modname = re.sub('\\bma.core\\b', 'ma', modname)

                class_name = type(data).__name__
                if class_name == 'ndarray':
                    class_name = 'array'

                prefix = modname + '.' + class_name + '('

                if with_dtype:
                    dtype_repr = data.dtype.name
                    # dtype_repr = np.core.arrayprint.dtype_short_repr(data.dtype)
                    suffix = ',{}dtype={}.{})'.format(itemsep, np_nice, dtype_repr)
                else:
                    suffix = ')'

            if not strvals and data.size == 0 and data.shape != (0,):
                # Special case for displaying empty data
                prefix = modname + '.empty('
                body = repr(tuple(map(int, data.shape)))
            else:
                body = np.array2string(data, precision=precision,
                                       separator=separator,
                                       suppress_small=suppress_small,
                                       prefix=prefix,
                                       max_line_width=max_line_width)
            if not newlines:
                # remove newlines if we need to
                body = re.sub('\n *', '', body)
            formatted = prefix + body + suffix
            return formatted

        # Hack, make sure we also register numpy floats
        self.register(np.float32)(self.func_registry[float])

    def _register_builtin_extensions(self):
        @self.register(float)
        def format_float(data, **kwargs):
            precision = kwargs.get('precision', None)
            if precision is None:
                return six.text_type(data)
            else:
                return ('{:.%df}' % precision).format(data)

        @self.register(slice)
        def format_slice(data, **kwargs):
            if kwargs.get('itemsep', ' ') == '':
                return 'slice(%r,%r,%r)' % (data.start, data.stop, data.step)
            else:
                return _format_object(data, **kwargs)

_FORMATTER_EXTENSIONS = FormatterExtensions()
_FORMATTER_EXTENSIONS._register_builtin_extensions()


@_FORMATTER_EXTENSIONS.lazy_init.append
def _lazy_init():
    try:
        # TODO: can we use lazy loading to prevent trying to import numpy until
        # some attribute of _FORMATTER_EXTENSIONS is used?
        _FORMATTER_EXTENSIONS._register_numpy_extensions()
        # TODO: register pandas by default if available
        pass
    except ImportError:  # nocover
        pass


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
    """
    Makes a pretty printable / human-readable string representation of a
    sequence. In most cases this string could be evaled.

    Args:
        list_ (list): input list
        **kwargs: nl, newlines, packed, nobr, nobraces, itemsep, trailing_sep,
            strvals indent_, precision, use_numpy, with_dtype, force_dtype,
            stritems, strkeys, explicit, sort, key_order, maxlen

    Returns:
        Tuple[str, Dict] : retstr, _leaf_info

    Example:
        >>> print(_format_list([])[0])
        []
        >>> print(_format_list([], nobr=True)[0])
        []
        >>> print(_format_list([1], nl=0)[0])
        [1]
        >>> print(_format_list([1], nobr=True)[0])
        1,
    """
    kwargs['_root_info'] = _rectify_root_info(kwargs.get('_root_info', None))
    kwargs['_root_info']['depth'] += 1

    newlines = kwargs.pop('nl', kwargs.pop('newlines', 1))
    kwargs['nl'] = _rectify_countdown_or_bool(newlines)

    nobraces = kwargs.pop('nobr', kwargs.pop('nobraces', False))

    itemsep = kwargs.get('itemsep', ' ')

    compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))
    # kwargs['cbr'] = _rectify_countdown_or_bool(compact_brace)

    itemstrs, _leaf_info = _list_itemstrs(list_, **kwargs)
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

    # Doesn't actually put in trailing comma if on same line
    trailing_sep = kwargs.get('trailsep', kwargs.get('trailing_sep', newlines > 0 and len(itemstrs)))

    # The trailing separator is always needed for single item tuples
    if is_tuple and len(list_) <= 1:
        trailing_sep = True

    if len(itemstrs) == 0:
        newlines = False

    retstr = _join_itemstrs(itemstrs, itemsep, newlines, _leaf_info, nobraces,
                            trailing_sep, compact_brace, lbr, rbr)
    return retstr, _leaf_info


def _format_dict(dict_, **kwargs):
    """
    Makes a pretty printable / human-readable string representation of a
    dictionary. In most cases this string could be evaled.

    Args:
        dict_ (dict):  a dictionary
        **kwargs: si, stritems, strkeys, strvals, sk, sv, nl, newlines, nobr,
                  nobraces, cbr, compact_brace, trailing_sep,
                  explicit, itemsep, precision, kvsep, sort

    Kwargs:
        sort (None): if True, sorts ALL collections and subcollections,
            note, collections with undefined orders (e.g. dicts, sets) are
            sorted by default. (default = None)
        nl (int): preferred alias for newline. can be a countdown variable
            (default = None)
        explicit (int): can be a countdown variable. if True, uses
            dict(a=b) syntax instead of {'a': b}
        nobr (bool): removes outer braces (default = False)

    Returns:
        Tuple[str, Dict] : retstr, _leaf_info
    """
    kwargs['_root_info'] = _rectify_root_info(kwargs.get('_root_info', None))
    kwargs['_root_info']['depth'] += 1

    stritems = kwargs.pop('si', kwargs.pop('stritems', False))
    if stritems:
        kwargs['strkeys'] = True
        kwargs['strvals'] = True

    kwargs['strkeys'] = kwargs.pop('sk', kwargs.pop('strkeys', False))
    kwargs['strvals'] = kwargs.pop('sv', kwargs.pop('strvals', False))

    newlines = kwargs.pop('nl', kwargs.pop('newlines', True))
    kwargs['nl'] = _rectify_countdown_or_bool(newlines)

    nobraces = kwargs.pop('nobr', kwargs.pop('nobraces', False))

    compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))
    # kwargs['cbr'] = _rectify_countdown_or_bool(compact_brace)

    # Doesn't actually put in trailing comma if on same line
    trailing_sep = kwargs.get('trailsep', kwargs.get('trailing_sep', newlines > 0))
    explicit = kwargs.get('explicit', False)
    itemsep = kwargs.get('itemsep', ' ')

    if len(dict_) == 0:
        retstr = 'dict()' if explicit else '{}'
        _leaf_info = None
    else:
        itemstrs, _leaf_info = _dict_itemstrs(dict_, **kwargs)
        if nobraces:
            lbr, rbr = '', ''
        elif explicit:
            lbr, rbr = 'dict(', ')'
        else:
            lbr, rbr = '{', '}'
        retstr = _join_itemstrs(itemstrs, itemsep, newlines, _leaf_info, nobraces,
                                trailing_sep, compact_brace, lbr, rbr)
    return retstr, _leaf_info


def _join_itemstrs(itemstrs, itemsep, newlines, _leaf_info, nobraces,
                   trailing_sep, compact_brace, lbr, rbr):
    """
    Joins string-ified items with separators newlines and container-braces.
    """
    # positive newlines means start counting from the root
    use_newline = newlines > 0

    # negative countdown values mean start counting from the leafs
    # if compact_brace < 0:
    #     compact_brace = (-compact_brace) >= _leaf_info['max_height']
    if newlines < 0:
        use_newline = (-newlines) < _leaf_info['max_height']

    if use_newline:
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
                import ubelt as ub
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
    Create a string representation for each item in a dict.

    Args:
        dict_ (dict): the dict
        **kwargs: explicit, precision, kvsep, strkeys, _return_info, cbr,
            compact_brace, sort

    Ignore:
        import xinspect
        ', '.join(xinspect.get_kwargs(_dict_itemstrs, max_depth=0).keys())

    Example:
        >>> from ubelt.util_format import *
        >>> dict_ =  {'b': .1, 'l': 'st', 'g': 1.0, 's': 10, 'm': 0.9, 'w': .5}
        >>> kwargs = {'strkeys': True}
        >>> itemstrs, _ = _dict_itemstrs(dict_, **kwargs)
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
            key_str = repr2(key, precision=precision, newlines=0)

        prefix = key_str + kvsep
        kwargs['_return_info'] = True
        val_str, _leaf_info = repr2(val, **kwargs)

        # If the first line does not end with an open nest char
        # (e.g. for ndarrays), otherwise we need to worry about
        # residual indentation.
        pos = val_str.find('\n')
        first_line = val_str if pos == -1 else val_str[:pos]

        compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))

        if compact_brace or not first_line.rstrip().endswith(tuple('([{<')):
            rest = '' if pos == -1 else val_str[pos:]
            val_str = first_line.lstrip() + rest
            if '\n' in prefix:
                # Fix issue with keys that span new lines
                item_str = prefix + val_str
            else:
                item_str = ub.hzcat([prefix, val_str])
        else:
            item_str = prefix + val_str
        return item_str, _leaf_info

    items = list(six.iteritems(dict_))
    _tups = [make_item_str(key, val) for (key, val) in items]
    itemstrs = [t[0] for t in _tups]
    max_height = max([t[1]['max_height'] for t in _tups]) if _tups else 0
    _leaf_info = {
        'max_height': max_height + 1,
    }

    sort = kwargs.get('sort', None)
    if sort is None:
        # if sort is None, force orderings on unordered collections like dicts,
        # but keep ordering of ordered collections like OrderedDicts.
        sort = True
    if isinstance(dict_, collections.OrderedDict):
        # never sort ordered dicts; they are perfect just the way they are!
        sort = False
    if sort:
        key = sort if callable(sort) else None
        itemstrs = _sort_itemstrs(items, itemstrs, key)
    return itemstrs, _leaf_info


def _list_itemstrs(list_, **kwargs):
    """
    Create a string representation for each item in a list.

    Args:
        list_ (Sequence):
        **kwargs: _return_info, sort

    Ignore:
        import xinspect
        ', '.join(xinspect.get_kwargs(_list_itemstrs, max_depth=0).keys())
    """
    items = list(list_)
    kwargs['_return_info'] = True
    _tups = [repr2(item, **kwargs) for item in items]
    itemstrs = [t[0] for t in _tups]
    max_height = max([t[1]['max_height'] for t in _tups]) if _tups else 0
    _leaf_info = {
        'max_height': max_height + 1,
    }

    sort = kwargs.get('sort', None)
    if sort is None:
        # if sort is None, force orderings on unordered collections like sets,
        # but keep ordering of ordered collections like lists.
        sort = isinstance(list_, (set, frozenset))
    if sort:
        key = sort if callable(sort) else None
        itemstrs = _sort_itemstrs(items, itemstrs, key)
    return itemstrs, _leaf_info


def _sort_itemstrs(items, itemstrs, key=None):
    """
    Equivalent to `sorted(items)` except if `items` are unorderable, then
    string values are used to define an ordering.
    """
    # First try to sort items by their normal values
    # If that doesnt work, then sort by their string values
    import ubelt as ub
    try:
        # Set ordering is not unique. Sort by strings values instead.
        if _peek_isinstance(items, (set, frozenset)):
            raise TypeError
        sortx = ub.argsort(items, key=key)
    except TypeError:
        sortx = ub.argsort(itemstrs, key=key)
    itemstrs = [itemstrs[x] for x in sortx]
    return itemstrs


def _peek_isinstance(items, types):
    return len(items) > 0 and isinstance(items[0], types)


def _rectify_countdown_or_bool(count_or_bool):
    """
    used by recursive functions to specify which level to turn a bool on in
    counting down yields True, True, ..., False
    counting up yields False, False, False, ... True

    Args:
        count_or_bool (bool or int): if positive and an integer, it will count
            down, otherwise it will remain the same.

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
        [1, 0, 0, -1, -2, True, False, False]
    """
    if count_or_bool is True or count_or_bool is False:
        count_or_bool_ = count_or_bool
    elif isinstance(count_or_bool, int):
        if count_or_bool == 0:
            return 0
        elif count_or_bool > 0:
            count_or_bool_ = count_or_bool - 1
        else:
            # We dont countup negatives anymore
            count_or_bool_ = count_or_bool
    else:
        count_or_bool_ = False
    return count_or_bool_
