"""
Defines the function :func:`urepr`, which allows for a bit more customization
than :func:`repr` or :func:`pprint`. See the docstring for more details.


Two main goals of urepr are to provide nice string representations of nested
data structures and make those "eval-able" whenever possible. As an example
take the value ``float('inf')``, which normally has a non-evalable repr of
``inf``:

>>> import ubelt as ub
>>> ub.urepr(float('inf'))
"float('inf')"

The ``newline`` (or ``nl``) keyword argument can control how deep in the
nesting newlines are allowed.

>>> print(ub.urepr({1: float('nan'), 2: float('inf'), 3: 3.0}))
{
    1: float('nan'),
    2: float('inf'),
    3: 3.0,
}

>>> print(ub.urepr({1: float('nan'), 2: float('inf'), 3: 3.0}, nl=0))
{1: float('nan'), 2: float('inf'), 3: 3.0}


You can also define or overwrite how representations for different types are
created. You can either create your own extension object, or you can
monkey-patch `ub.util_format._FORMATTER_EXTENSIONS` without specifying the
extensions keyword argument (although this will be a global change).

>>> extensions = ub.util_format.FormatterExtensions()
>>> @extensions.register(float)
>>> def my_float_formater(data, **kw):
>>>     return "monkey({})".format(data)
>>> print(ub.urepr({1: float('nan'), 2: float('inf'), 3: 3.0}, nl=0, extensions=extensions))
{1: monkey(nan), 2: monkey(inf), 3: monkey(3.0)}

As of ubelt 1.1.0 you can now access and update the default extensions via the
urepr function itself.

>>> # xdoctest: +SKIP
>>> # We skip this at test time to not modify global state
>>> @ub.urepr.EXTENSIONS.register(float)
>>> def my_float_formater(data, **kw):
>>>     return "monkey2({})".format(data)
>>> print(ub.urepr({1: float('nan'), 2: float('inf'), 3: 3.0}, nl=0))
"""
import collections
from ubelt import util_str
from ubelt import util_list

__all__ = ['repr2', 'urepr', 'FormatterExtensions']


def urepr(data, **kwargs):
    """
    Makes a pretty string representation of ``data``.

    Makes a pretty and easy-to-doctest string representation. Has nice handling
    of common nested datatypes. This is an alternative to repr, and
    :func:`pprint.pformat`.

    This output of this function are configurable. By default it aims to
    produce strings that are consistent, compact, and executable.  This makes
    them great for doctests.

    Note:
        This function has many keyword arguments that can be used to customize
        the final representation. For convenience some of the more frequently
        used kwargs have short aliases. See "Kwargs" for more details.

    Args:
        data (object):
            an arbitrary python object to form the string "representation" of

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
            By default this is True if there are any ``nl > 0``.

        explicit (bool, default=False):
            changes dict representation from ``{k1: v1, ...}`` to
            ``dict(k1=v1, ...)``.

            Modifies:
                default kvsep is modified to  ``'='``
                dict braces from `{}` to `dict()`.

        compact (bool, default=False):
            Produces values more suitable for space constrianed environments

            Modifies:
                default kvsep is modified to ``'='``
                default itemsep is modified to  ``''``
                default nobraces is modified to ``1``.
                default newlines is modified to ``0``.
                default strkeys to ``True``
                default strvals to ``True``

        precision (int, default=None):
            if specified floats are formatted with this precision

        kvsep (str, default=': '):
            separator between keys and values

        itemsep (str, default=' '):
            separator between items. This separator is placed after commas,
            which are currently not configurable. This may be modified in the
            future.

        sort (bool | callable, default='auto'):
            if 'auto', then sort unordered collections, but keep the ordering
            of ordered collections. This option attempts to be deterministic in
            most cases.

            if True, then ALL collections will be sorted in the returned text.

        suppress_small (bool):
            passed to :func:`numpy.array2string` for ndarrays

        max_line_width (int):
            passed to :func:`numpy.array2string` for ndarrays

        with_dtype (bool):
            only relevant to numpy.ndarrays. if True includes the dtype.
            Defaults to `not strvals`.

        align (bool | str, default=False):
            if True, will align multi-line dictionaries by the kvsep

        extensions (FormatterExtensions):
            a custom :class:`FormatterExtensions` instance that can overwrite
            or define how different types of objects are formatted.

    Returns:
        str: outstr - output string

    Note:
        There are also internal kwargs, which should not be used:

            _return_info (bool):  return information about child context

            _root_info (depth): information about parent context

    RelatedWork:
        :func:`rich.pretty.pretty_repr`
        :func:`pprint.pformat`

    Example:
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
        ...     'odict': ub.odict([(2, '1'), (1, '2')]),
        ... }
        >>> # In the interest of saving space we are only going to show the
        >>> # output for the first example.
        >>> result = ub.urepr(dict_, nl=1, precision=2)
        >>> import pytest
        >>> import sys
        >>> if sys.version_info[0:2] <= (3, 6):
        >>>     # dictionary order is not guaranteed in 3.6 use repr2 instead
        >>>     pytest.skip()
        >>> print(result)
        {
            'custom_types': [slice(0, 1, None), 0.33],
            'nest_dict': {'k1': [1, 2, {3: {4, 5}}], 'key2': [1, 2, {3: {4, 5}}], 'key3': [1, 2, {3: {4, 5}}]},
            'nest_dict2': {'k': [1, 2, {3: {4, 5}}]},
            'nested_tuples': [(1,), (2, 3), {4, 5, 6}],
            'one_tup': (1,),
            'simple_dict': {'spam': 'eggs', 'ham': 'jam'},
            'simple_list': [1, 2, 'red', 'blue'],
            'odict': {2: '1', 1: '2'},
        }
        >>> # You can try the rest yourself.
        >>> result = ub.urepr(dict_, nl=3, precision=2); print(result)
        >>> result = ub.urepr(dict_, nl=2, precision=2); print(result)
        >>> result = ub.urepr(dict_, nl=1, precision=2, itemsep='', explicit=True); print(result)
        >>> result = ub.urepr(dict_, nl=1, precision=2, nobr=1, itemsep='', explicit=True); print(result)
        >>> result = ub.urepr(dict_, nl=3, precision=2, cbr=True); print(result)
        >>> result = ub.urepr(dict_, nl=3, precision=2, si=True); print(result)
        >>> result = ub.urepr(dict_, nl=3, sort=True); print(result)
        >>> result = ub.urepr(dict_, nl=3, sort=False, trailing_sep=False); print(result)
        >>> result = ub.urepr(dict_, nl=3, sort=False, trailing_sep=False, nobr=True); print(result)

    Example:
        >>> import ubelt as ub
        >>> def _nest(d, w):
        ...     if d == 0:
        ...         return {}
        ...     else:
        ...         return {'n{}'.format(d): _nest(d - 1, w + 1), 'm{}'.format(d): _nest(d - 1, w + 1)}
        >>> dict_ = _nest(d=4, w=1)
        >>> result = ub.urepr(dict_, nl=6, precision=2, cbr=1)
        >>> print('---')
        >>> print(result)
        >>> result = ub.urepr(dict_, nl=-1, precision=2)
        >>> print('---')
        >>> print(result)

    Example:
        >>> import ubelt as ub
        >>> data = {'a': 100, 'b': [1, '2', 3], 'c': {20:30, 40: 'five'}}
        >>> print(ub.urepr(data, nl=1))
        {
            'a': 100,
            'b': [1, '2', 3],
            'c': {20: 30, 40: 'five'},
        }
        >>> # Compact is useful for things like timerit.Timerit labels
        >>> print(ub.urepr(data, compact=True))
        a=100,b=[1,2,3],c={20=30,40=five}
        >>> print(ub.urepr(data, compact=True, nobr=False))
        {a=100,b=[1,2,3],c={20=30,40=five}}
    """
    custom_extensions = kwargs.get('extensions', None)

    _return_info = kwargs.get('_return_info', False)
    kwargs['_root_info'] = _rectify_root_info(kwargs.get('_root_info', None))

    if kwargs.get('compact', False):
        # Compact profile defaults
        kwargs['newlines'] = kwargs.get('newlines', 0)
        kwargs['strkeys'] = kwargs.get('strkeys', True)
        kwargs['strvals'] = kwargs.get('strvals', True)
        kwargs['nobraces'] = kwargs.get('nobraces', 1)
        kwargs['itemsep'] = kwargs.get('itemsep', '')
        kwargs['kvsep'] = kwargs.get('kvsep', '=')

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


def repr2(data, **kwargs):
    """
    Deprecated for urepr

    Example:
        >>> # Test that repr2 remains backwards compatible
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
        ...     'odict': ub.odict([(2, '1'), (1, '2')]),
        ... }
        >>> result = ub.repr2(dict_, nl=1, precision=2)
        >>> print(result)
        {
            'custom_types': [slice(0, 1, None), 0.33],
            'nest_dict': {'k1': [1, 2, {3: {4, 5}}], 'key2': [1, 2, {3: {4, 5}}], 'key3': [1, 2, {3: {4, 5}}]},
            'nest_dict2': {'k': [1, 2, {3: {4, 5}}]},
            'nested_tuples': [(1,), (2, 3), {4, 5, 6}],
            'odict': {2: '1', 1: '2'},
            'one_tup': (1,),
            'simple_dict': {'ham': 'jam', 'spam': 'eggs'},
            'simple_list': [1, 2, 'red', 'blue'],
        }
    """
    kwargs['_dict_sort_behavior'] = kwargs.get('_dict_sort_behavior', 'old')
    return urepr(data, **kwargs)


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

    This module (:mod:`ubelt.util_format`) maintains a global set of basic
    extensions, but it is also possible to create a locally scoped set of
    extensions and explicitly pass it to urepr. The following example
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
        >>> print(ub.urepr(data, nl=-1, precision=1, extensions=extensions))
        {
            'a': [1, 2.2, I can do anything here],
            'b': I can do anything here
        }
        >>> # Overload the formatter for float and int
        >>> @extensions.register((float, int))
        >>> def format_myobject(data, **kwargs):
        >>>     return str((data + 10) // 2)
        >>> print(ub.urepr(data, nl=-1, precision=1, extensions=extensions))
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
        self._type_registry = {}      # type: Dict[Type, Callable]  # NOQA
        self._typename_registry = {}  # type: Dict[str, Callable]  # NOQA
        self._lazy_queue = []         # type: List[Callable]  # NOQA
        # self._lazy_registrations = [
        #     self._register_numpy_extensions,
        #     self._register_builtin_extensions,
        # ]

    def register(self, key):
        """
        Registers a custom formatting function with ub.urepr

        Args:
            key (Type | Tuple[Type] | str): indicator of the type

        Returns:
            Callable: decorator function
        """
        def _decorator(func):
            if isinstance(key, tuple):
                for t in key:
                    self._type_registry[t] = func
            if isinstance(key, str):
                self._typename_registry[key] = func
            else:
                self._type_registry[key] = func
            return func
        return _decorator

    def lookup(self, data):
        """
        Returns an appropriate function to format ``data`` if one has been
        registered.
        """
        # Evaluate the lazy queue if anything is in it
        if self._lazy_queue:
            for func in self._lazy_queue:
                func()
            self._lazy_queue = []

        for type_, func in self._type_registry.items():
            if isinstance(data, type_):
                return func

        # Fallback to registered typenames.
        # If we cannot find a formatter for this type, then return None
        typename = type(data).__name__
        func = self._typename_registry.get(typename, None)
        return func

    def _register_pandas_extensions(self):
        """
        Example:
            >>> # xdoctest: +REQUIRES(module:pandas)
            >>> # xdoctest: +IGNORE_WHITESPACE
            >>> import pandas as pd
            >>> import numpy as np
            >>> import ubelt as ub
            >>> rng = np.random.RandomState(0)
            >>> data = pd.DataFrame(rng.rand(3, 3))
            >>> print(ub.repr2(data))
            >>> print(ub.urepr(data, precision=2))
            >>> print(ub.urepr({'akeyfdfj': data}, precision=2))
        """
        @self.register('DataFrame')
        def format_pandas(data, **kwargs):  # nocover
            precision = kwargs.get('precision', None)
            float_format = (None if precision is None
                            else '%.{}f'.format(precision))
            formatted = data.to_string(float_format=float_format)
            return formatted

    # def _register_torch_extensions(self):
    #     @self.register('Tensor')
    #     def format_tensor(data, **kwargs):
    #         """
    #         Example:
    #             >>> # xdoctest: +REQUIRES(module:torch)
    #             >>> # xdoctest: +IGNORE_WHITESPACE
    #             >>> import torch
    #             >>> import numpy as np
    #             >>> data = np.array([[.2, 42, 5], [21.2, 3, .4]])
    #             >>> data = torch.from_numpy(data)
    #             >>> data = torch.rand(100, 100)
    #             >>> print('data = {}'.format(ub.urepr(data, nl=1)))
    #             >>> print(ub.urepr(data))

    #         """
    #         import numpy as np
    #         func = self._type_registry[np.ndarray]
    #         npdata = data.data.cpu().numpy()
    #         # kwargs['strvals'] = True
    #         kwargs['with_dtype'] = False
    #         formatted = func(npdata, **kwargs)
    #         # hack for prefix class
    #         formatted = formatted.replace('np.array', '__Tensor')
    #         # import ubelt as ub
    #         # formatted = ub.hzcat('Tensor(' + formatted + ')')
    #         return formatted

    def _register_numpy_extensions(self):
        """
        Example:
            >>> # xdoctest: +REQUIRES(module:numpy)
            >>> import sys
            >>> import pytest
            >>> import ubelt as ub
            >>> if not ub.modname_to_modpath('numpy'):
            ...     raise pytest.skip()
            >>> # xdoctest: +IGNORE_WHITESPACE
            >>> import numpy as np
            >>> data = np.array([[.2, 42, 5], [21.2, 3, .4]])
            >>> print(ub.urepr(data))
            np.array([[ 0.2, 42. ,  5. ],
                      [21.2,  3. ,  0.4]], dtype=np.float64)
            >>> print(ub.urepr(data, with_dtype=False))
            np.array([[ 0.2, 42. ,  5. ],
                      [21.2,  3. ,  0.4]])
            >>> print(ub.urepr(data, strvals=True))
            [[ 0.2, 42. ,  5. ],
             [21.2,  3. ,  0.4]]
            >>> data = np.empty((0, 10), dtype=np.float64)
            >>> print(ub.urepr(data, strvals=False))
            np.empty((0, 10), dtype=np.float64)
            >>> print(ub.urepr(data, strvals=True))
            []
            >>> data = np.ma.empty((0, 10), dtype=np.float64)
            >>> print(ub.urepr(data, strvals=False))
            np.ma.empty((0, 10), dtype=np.float64)
        """

        # TODO: should we register numpy using the new string method?
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

            if not strvals:
                # Handle special float values inf / nan
                body = re.sub('\\binf\\b', np_nice + '.inf', body)
                body = re.sub('\\bnan\\b', np_nice + '.nan', body)

            if not newlines:
                # remove newlines if we need to
                body = re.sub('\n *', '', body)
            formatted = prefix + body + suffix
            return formatted

        # Hack, make sure we also register numpy floats
        self.register(np.float32)(self._type_registry[float])

    def _register_builtin_extensions(self):
        @self.register(float)
        def format_float(data, **kwargs):
            precision = kwargs.get('precision', None)
            strvals = kwargs.get('sv', kwargs.get('strvals', False))

            if precision is None:
                text = str(data)
            else:
                text = ('{:.%df}' % precision).format(data)

            if not strvals:
                # Ensure the representation of inf and nan is evaluatable
                # NOTE: sometimes this function is used to make json objects
                # how can we ensure that this doesn't break things?
                # Turns out json, never handled these cases. In the future we
                # may want to add a json flag to urepr to encourage it to
                # output json-like representations.
                # json.loads("[0, 1, 2, nan]")
                # json.loads("[Infinity, NaN]")
                # json.dumps([float('inf'), float('nan')])
                import math
                if math.isinf(data) or math.isnan(data):
                    text = "float('{}')".format(text)

            return text

        @self.register(slice)
        def format_slice(data, **kwargs):
            if kwargs.get('itemsep', ' ') == '':
                return 'slice(%r,%r,%r)' % (data.start, data.stop, data.step)
            else:
                return _format_object(data, **kwargs)

_FORMATTER_EXTENSIONS = FormatterExtensions()
_FORMATTER_EXTENSIONS._register_builtin_extensions()


def _lazy_init():
    """
    Only called in the case where we encounter an unknown type that a commonly
    used external library might have. For now this is just numpy. Numpy is
    ubiquitous.
    """
    try:
        # TODO: can we use lazy loading to prevent trying to import numpy until
        # some attribute of _FORMATTER_EXTENSIONS is used?
        _FORMATTER_EXTENSIONS._register_numpy_extensions()
        _FORMATTER_EXTENSIONS._register_pandas_extensions()
        # _FORMATTER_EXTENSIONS._register_torch_extensions()
    except ImportError:  # nocover
        pass

_FORMATTER_EXTENSIONS._lazy_queue.append(_lazy_init)


def _format_object(val, **kwargs):
    stritems = kwargs.get('si', kwargs.get('stritems', False))
    strvals = stritems or kwargs.get('sv', kwargs.get('strvals', False))
    base_valfunc = str if strvals else repr
    itemstr = base_valfunc(val)
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
    kwargs['nobraces'] = _rectify_countdown_or_bool(nobraces)

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
        sort (None, default=None):
            if True, sorts ALL collections and subcollections,
            note, collections with undefined orders (e.g. dicts, sets) are
            sorted by default.

        nl (int, default=None):
            preferred alias for newline. can be a countdown variable

        explicit (int, default=False):
            can be a countdown variable.
            if True, uses dict(a=b) syntax instead of {'a': b}

        nobr (bool, default=False): removes outer braces

    Returns:
        Tuple[str, Dict] : retstr, _leaf_info

    Example:
        >>> from ubelt.util_format import *  # NOQA
        >>> dict_ = {'a': 'edf', 'bc': 'ghi'}
        >>> print(_format_dict(dict_)[0])
        {
            'a': 'edf',
            'bc': 'ghi',
        }
        >>> print(_format_dict(dict_, align=True)[0])
        >>> print(_format_dict(dict_, align=':')[0])
        {
            'a' : 'edf',
            'bc': 'ghi',
        }
        >>> print(_format_dict(dict_, explicit=True, align=True)[0])
        dict(
            a ='edf',
            bc='ghi',
        )
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
    kwargs['nobraces'] = _rectify_countdown_or_bool(nobraces)

    compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))
    # kwargs['cbr'] = _rectify_countdown_or_bool(compact_brace)

    # Doesn't actually put in trailing comma if on same line
    trailing_sep = kwargs.get('trailsep', kwargs.get('trailing_sep', newlines > 0))
    explicit = kwargs.get('explicit', False)
    itemsep = kwargs.get('itemsep', ' ')

    align = kwargs.get('align', False)
    if align and not isinstance(align, str):
        default_kvsep = ': '
        if explicit:
            default_kvsep = '='
        kvsep = kwargs.get('kvsep', default_kvsep)
        align = kvsep

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
                                trailing_sep, compact_brace, lbr, rbr, align)
    return retstr, _leaf_info


def _join_itemstrs(itemstrs, itemsep, newlines, _leaf_info, nobraces,
                   trailing_sep, compact_brace, lbr, rbr, align=False):
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
                # rest = [util_str.indent(s, prefix) for s in itemstrs[1:]]
                # indented = itemstrs[0:1] + rest
                indented = itemstrs
            else:
                prefix = ' ' * 4
                indented = [util_str.indent(s, prefix) for s in itemstrs]

            if align:
                indented = _align_lines(indented, character=align)

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
        from ubelt.util_format import _dict_itemstrs
        import xinspect
        print(', '.join(xinspect.get_kwargs(_dict_itemstrs, max_depth=0).keys()))

    Example:
        >>> from ubelt.util_format import *
        >>> dict_ =  {'b': .1, 'l': 'st', 'g': 1.0, 's': 10, 'm': 0.9, 'w': .5}
        >>> kwargs = {'strkeys': True, 'sort': True}
        >>> itemstrs, _ = _dict_itemstrs(dict_, **kwargs)
        >>> char_order = [p[0] for p in itemstrs]
        >>> assert char_order == ['b', 'g', 'l', 'm', 's', 'w']
    """
    import ubelt as ub
    explicit = kwargs.get('explicit', False)
    kwargs['explicit'] = _rectify_countdown_or_bool(explicit)
    precision = kwargs.get('precision', None)

    default_kvsep = ': '
    default_strkeys = False
    if explicit:
        default_strkeys = True
        default_kvsep = '='
    kvsep = kwargs.get('kvsep', default_kvsep)

    def make_item_str(key, val):
        if explicit or kwargs.get('strkeys', default_strkeys):
            key_str = str(key)
        else:
            key_str = urepr(key, precision=precision, newlines=0)

        prefix = key_str + kvsep
        kwargs['_return_info'] = True
        val_str, _leaf_info = urepr(val, **kwargs)

        # If the first line does not end with an open nest char
        # (e.g. for ndarrays), otherwise we need to worry about
        # residual indentation.
        pos = val_str.find('\n')
        first_line = val_str if pos == -1 else val_str[:pos]

        compact_brace = kwargs.get('cbr', kwargs.get('compact_brace', False))

        if compact_brace or not first_line.rstrip().endswith(tuple('([{<')):
            rest = '' if pos == -1 else val_str[pos:]
            # val_str = first_line.lstrip() + rest
            val_str = first_line + rest
            if '\n' in prefix:
                # Fix issue with keys that span new lines
                item_str = prefix + val_str
            else:
                item_str = ub.hzcat([prefix, val_str])
        else:
            item_str = prefix + val_str
        return item_str, _leaf_info

    items = list(dict_.items())
    _tups = [make_item_str(key, val) for (key, val) in items]
    itemstrs = [t[0] for t in _tups]
    max_height = max([t[1]['max_height'] for t in _tups]) if _tups else 0
    _leaf_info = {
        'max_height': max_height + 1,
    }

    sort = kwargs.get('sort', None)
    if sort == 'auto':
        sort = None

    dict_sort_behavior = kwargs.get('_dict_sort_behavior', 'new')
    if dict_sort_behavior == 'old':
        if sort is None:
            # if sort is None, force orderings on unordered collections like dicts,
            # but keep ordering of ordered collections like OrderedDicts.
            # NOTE: WE WANT TO CHANGE THIS TO FALSE BY DEFAULT.
            # MIGHT REQUIRE DEPRECATING PYTHON 3.6 SUPPORT
            sort = True  # LEGACY UBELT BEHAVIOR
            # HOW TO WE INTRODUCE A BACKWARDS COMPATIBLE WAY TO MAKE THIS CHANGE?
            # sort = False  # cannot make this change safely

        if isinstance(dict_, collections.OrderedDict):
            # never sort ordered dicts; they are perfect just the way they are!
            sort = False
    else:
        if sort is None:
            # Dictionaries are sorted by default in 3.7+ so never sort dictionaries
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
    """
    items = list(list_)
    kwargs['_return_info'] = True
    _tups = [urepr(item, **kwargs) for item in items]
    itemstrs = [t[0] for t in _tups]
    max_height = max([t[1]['max_height'] for t in _tups]) if _tups else 0
    _leaf_info = {
        'max_height': max_height + 1,
    }

    sort = kwargs.get('sort', None)
    if sort == 'auto':
        sort = None

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
    Equivalent to ``sorted(items)`` except if ``items`` are unorderable, then
    string values are used to define an ordering.
    """
    # First try to sort items by their normal values
    # If that does not work, then sort by their string values
    try:
        # Set ordering is not unique. Sort by strings values instead.
        if len(items) > 0 and isinstance(items[0], (set, frozenset)):
            raise TypeError
        sortx = util_list.argsort(items, key=key)
    except TypeError:
        sortx = util_list.argsort(itemstrs, key=key)
    itemstrs = [itemstrs[x] for x in sortx]
    return itemstrs


def _rectify_countdown_or_bool(count_or_bool):
    """
    used by recursive functions to specify which level to turn a bool on in
    counting down yields True, True, ..., False
    counting up yields False, False, False, ... True

    Args:
        count_or_bool (bool | int): if positive and an integer, it will count
            down, otherwise it will remain the same.

    Returns:
        int or bool: count_or_bool_

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


def _align_text(text, character='=', replchar=None, pos=0):
    r"""
    Left justifies text on the left side of character

    Args:
        text (str): text to align
        character (str): character to align at
        replchar (str): replacement character (default=None)

    Returns:
        str: new_text

    Example:
        >>> character = '='
        >>> text = 'a = b=\none = two\nthree = fish\n'
        >>> print(text)
        >>> result = (_align_text(text, '='))
        >>> print(result)
        a     = b=
        one   = two
        three = fish
    """
    line_list = text.splitlines()
    new_lines = _align_lines(line_list, character, replchar, pos=pos)
    new_text = '\n'.join(new_lines)
    return new_text


def _align_lines(line_list, character='=', replchar=None, pos=0):
    r"""
    Left justifies text on the left side of character

    Args:
        line_list (list of strs):
        character (str):
        pos (int or list or None): does one alignment for all chars beyond this
            column position. If pos is None, then all chars are aligned.

    Returns:
        list: new_lines

    Example:
        >>> line_list = 'a = b\none = two\nthree = fish'.split('\n')
        >>> character = '='
        >>> new_lines = _align_lines(line_list, character)
        >>> result = ('\n'.join(new_lines))
        >>> print(result)
        a     = b
        one   = two
        three = fish

    Example:
        >>> line_list = 'foofish:\n    a = b\n    one    = two\n    three    = fish'.split('\n')
        >>> character = '='
        >>> new_lines = _align_lines(line_list, character)
        >>> result = ('\n'.join(new_lines))
        >>> print(result)
        foofish:
            a        = b
            one      = two
            three    = fish

    Example:
        >>> import ubelt as ub
        >>> character = ':'
        >>> text = ub.codeblock('''
            {'max': '1970/01/01 02:30:13',
             'mean': '1970/01/01 01:10:15',
             'min': '1970/01/01 00:01:41',
             'range': '2:28:32',
             'std': '1:13:57',}''').split('\n')
        >>> new_lines = _align_lines(text, ':', ' :')
        >>> result = '\n'.join(new_lines)
        >>> print(result)
        {'max'   : '1970/01/01 02:30:13',
         'mean'  : '1970/01/01 01:10:15',
         'min'   : '1970/01/01 00:01:41',
         'range' : '2:28:32',
         'std'   : '1:13:57',}

    Example:
        >>> line_list = 'foofish:\n a = b = c\n one = two = three\nthree=4= fish'.split('\n')
        >>> character = '='
        >>> # align the second occurrence of a character
        >>> new_lines = _align_lines(line_list, character, pos=None)
        >>> print(('\n'.join(line_list)))
        >>> result = ('\n'.join(new_lines))
        >>> print(result)
        foofish:
         a   = b   = c
         one = two = three
        three=4    = fish
    """
    import re

    # FIXME: continue to fix ansi
    if pos is None:
        # Align all occurrences
        num_pos = max([line.count(character) for line in line_list])
        pos = list(range(num_pos))

    # Allow multiple alignments
    if isinstance(pos, list):
        pos_list = pos
        # recursive calls
        new_lines = line_list
        for pos in pos_list:
            new_lines = _align_lines(new_lines, character=character,
                                     replchar=replchar, pos=pos)
        return new_lines

    # base case
    if replchar is None:
        replchar = character

    # the pos-th character to align
    lpos = pos
    rpos = lpos + 1

    tup_list = [line.split(character) for line in line_list]

    handle_ansi = True
    if handle_ansi:  # nocover
        # Remove ansi from length calculation
        # References: http://stackoverflow.com/questions/14693701remove-ansi
        ansi_escape = re.compile(r'\x1b[^m]*m')

    # Find how much padding is needed
    maxlen = 0
    for tup in tup_list:
        if len(tup) >= rpos + 1:
            if handle_ansi:  # nocover
                tup = [ansi_escape.sub('', x) for x in tup]
            left_lenlist = list(map(len, tup[0:rpos]))
            left_len = sum(left_lenlist) + lpos * len(replchar)
            maxlen = max(maxlen, left_len)

    # Pad each line to align the pos-th occurrence of the chosen character
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


# Give the urepr function itself a reference to the default extensions
# register method so the user can modify them without accessing this module
urepr.extensions = _FORMATTER_EXTENSIONS
urepr.register = _FORMATTER_EXTENSIONS.register

repr2.extensions = urepr.extensions
repr2.register = urepr.register
