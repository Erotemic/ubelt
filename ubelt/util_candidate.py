# -*- coding: utf-8 -*-
"""
Candidate functions
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from collections import defaultdict as ddict
from ubelt.util_const import NoParam
import itertools as it

try:
    from collections.abc import Generator
except Exception:
    Generator = object  # Python <3.4 doesnt have Generator ABC


def basis_product(basis):
    """
    Generates the Cartesian product of the ``basis.values()``, where each
    generated item labeled by ``basis.keys()``.

    In other words, given a dictionary that maps each "axes" (i.e. some
    variable) to its "basis" (i.e. the possible values that it can take),
    generate all possible points in that grid (i.e. unique assignments of
    variables to values).

    Args:
        basis (Dict[K, List[T]]):
            A dictionary where the keys correspond to "columns" and the values
            are a list of possible values that "column" can take.

            I.E. each key corresponds to an "axes", the values are the list of
            possible values for that "axes".

    Yields:
        Dict[K, T] - a "row" in the "longform" data containing a point in the
            Cartesian product.

    Notes:
        This function is similar to :func:`itertools.product`, the only
        difference is that the generated items are a dictionary that retains
        the input keys instead of an tuple.

    TODO:
        - [ ] Does this go in util_dict?

    Example:
        >>> # An example use case is looping over all possible settings in a
        >>> # configuration dictionary for a grid search over parameters.
        >>> basis = {
        >>>     'arg1': [1, 2, 3],
        >>>     'arg2': ['A1', 'B1'],
        >>>     'arg3': [9999, 'Z2'],
        >>>     'arg4': ['always'],
        >>> }
        >>> import ubelt as ub
        >>> # sort input data for older python versions
        >>> basis = ub.odict(sorted(basis.items()))
        >>> got = list(basis_product(basis))
        >>> print(ub.repr2(got, nl=-1))
        [
            {'arg1': 1, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 1, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 2, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'A1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'A1', 'arg3': 'Z2', 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'B1', 'arg3': 9999, 'arg4': 'always'},
            {'arg1': 3, 'arg2': 'B1', 'arg3': 'Z2', 'arg4': 'always'}
        ]
    """
    keys = list(basis.keys())
    for vals in it.product(*basis.values()):
        kw = dict(zip(keys, vals))
        yield kw


def varied_values(longform, min_variations=0, default=NoParam):
    """
    Given a list of dictionaries, find the values that differ between them.

    Args:
        longform (List[Dict]):
            This is longform data, as described in [1]_. It is a list of
            dictionaries.

            Each item in the list - or row - is a dictionary and can be thought
            of as an observation. The keys in each dictionary are the columns.
            The values of the dictionary must be hashable. Lists will be
            converted into tuples.

        min_variations (int, default=0):
            "columns" with fewer than ``min_variations`` unique values are
            removed from the result.

        default (object, default=NoParam):
            if specified, unspecified columns are given this value.

    Returns:
        dict : a mapping from each "column" to the set of unique values it took
            over each "row". If a column is not specified for each row, it is
            assumed to take a `default` value, if it is specified.

    Raises:
        KeyError: If ``default`` is unspecified and all the rows
            do not contain the same columns.

    References:
        .. [1] https://seaborn.pydata.org/tutorial/data_structure.html#long-form-data

    CommandLine:
        xdoctest -m /home/joncrall/code/ubelt/ubelt/util_candidate.py varied_values

    TODO:
        - [ ] Does this go in util_dict?

    Example:
        >>> # An example use case is to determine what values of a
        >>> # configuration dictionary were tried in a random search
        >>> # over a parameter grid.
        >>> from ubelt.util_candidate import *  # NOQA
        >>> import ubelt as ub
        >>> longform = [
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 2, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 3, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 9, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 1, 'col2': 'bar', 'col3': None},
        >>> ]
        >>> varied = varied_values(longform)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1)))
        varied = {
            'col1': {1, 2, 3, 9},
            'col2': {'bar', 'foo'},
            'col3': {None},
        }

    Example:
        >>> from ubelt.util_candidate import *  # NOQA
        >>> import ubelt as ub
        >>> import random
        >>> longform = [
        >>>     {'col1': 1, 'col2': 'foo', 'col3': None},
        >>>     {'col1': 1, 'col2': [1, 2], 'col3': None},
        >>>     {'col1': 2, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 3, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 9, 'col2': 'bar', 'col3': None},
        >>>     {'col1': 1, 'col2': 'bar', 'col3': None, 'extra_col': 3},
        >>> ]
        >>> # Operation fails without a default
        >>> import pytest
        >>> with pytest.raises(KeyError):
        >>>     varied = varied_values(longform)
        >>> #
        >>> # Operation works with a default
        >>> varied = varied_values(longform, default='<unset>')
        >>> expected = {
        >>>     'col1': {1, 2, 3, 9},
        >>>     'col2': {'bar', 'foo', (1, 2)},
        >>>     'col3': set([None]),
        >>>     'extra_col': {'<unset>', 3},
        >>> }
        >>> print('varied = {!r}'.format(varied))
        >>> assert varied == expected

    Example:
        >>> # xdoctest: +REQUIRES(PY3)
        >>> # Random numbers are different in Python2, so skip in that case
        >>> from ubelt.util_candidate import *  # NOQA
        >>> import ubelt as ub
        >>> import random
        >>> num_cols = 11
        >>> num_rows = 17
        >>> rng = random.Random(0)
        >>> # Generate a set of columns
        >>> columns = sorted(ub.hash_data(i)[0:8] for i in range(num_cols))
        >>> # Generate rows for each column
        >>> longform = [
        >>>     {key: ub.hash_data(key)[0:8] for key in columns}
        >>>     for _ in range(num_rows)
        >>> ]
        >>> # Add in some varied values in random positions
        >>> for row in longform:
        >>>     if rng.random() > 0.5:
        >>>         for key in sorted(row.keys()):
        >>>             if rng.random() > 0.95:
        >>>                 row[key] = 'special-' + str(rng.randint(1, 32))
        >>> varied = varied_values(longform, min_variations=1)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1, sort=True)))
        varied = {
            '095f3e44': {'8fb4d4c9', 'special-23'},
            '365d11a1': {'daa409da', 'special-31', 'special-32'},
            '5815087d': {'1b823610', 'special-3'},
            '7b54b668': {'349a782c', 'special-10'},
            'b8244d02': {'d57bca90', 'special-8'},
            'f27b5bf8': {'fa0f90d1', 'special-19'},
        }
    """
    # Enumerate all defined columns
    columns = set()
    for row in longform:
        if default is NoParam and len(row) != len(columns) and len(columns):
            missing = set(columns).symmetric_difference(set(row))
            raise KeyError((
                'No default specified and not every '
                'row contains columns {}').format(missing))
        columns.update(row.keys())

    # Build up the set of unique values for each column
    varied = ddict(set)
    for row in longform:
        for key in columns:
            value = row.get(key, default)
            if isinstance(value, list):
                value = tuple(value)
            varied[key].add(value)

    # Remove any column that does not have enough variation
    if min_variations > 0:
        for key, values in list(varied.items()):
            if len(values) <= min_variations:
                varied.pop(key)
    return varied


class IndexableWalker(Generator):
    """
    Traverses through a nested tree-liked indexable structure.

    Generates a path and value to each node in the structure. The path is a
    list of indexes which if applied in order will reach the value.

    The ``__setitem__`` method can be used to modify a nested value based on the
    path returned by the generator.

    When generating values, you can use "send" to prevent traversal of a
    particular branch.

    TODO:
        - [ ] Does this go in util_dict, util_list, or maybe a new util?

    Example:
        >>> # Given Nested Data
        >>> data = {
        >>>     'foo': {'bar': 1},
        >>>     'baz': [{'biz': 3}, {'buz': [4, 5, 6]}],
        >>> }
        >>> # Create an IndexableWalker
        >>> walker = IndexableWalker(data)
        >>> # We iterate over the data as if it was flat
        >>> # ignore the <want> string due to order issues on older Pythons
        >>> # xdoctest: +IGNORE_WANT
        >>> for path, val in walker:
        >>>     print(path)
        ['foo']
        ['baz']
        ['baz', 0]
        ['baz', 1]
        ['baz', 1, 'buz']
        ['baz', 1, 'buz', 0]
        ['baz', 1, 'buz', 1]
        ['baz', 1, 'buz', 2]
        ['baz', 0, 'biz']
        ['foo', 'bar']
        >>> # We can use "paths" as keys to getitem into the walker
        >>> path = ['baz', 1, 'buz', 2]
        >>> val = walker[path]
        >>> assert val == 6
        >>> # We can use "paths" as keys to setitem into the walker
        >>> assert data['baz'][1]['buz'][2] == 6
        >>> walker[path] = 7
        >>> assert data['baz'][1]['buz'][2] == 7
        >>> # We can use "paths" as keys to delitem into the walker
        >>> assert data['baz'][1]['buz'][1] == 5
        >>> del walker[['baz', 1, 'buz', 1]]
        >>> assert data['baz'][1]['buz'][1] == 7

    Example:
        >>> # Create nested data
        >>> # xdoctest: +REQUIRES(module:numpy)
        >>> import numpy as np
        >>> import ubelt as ub
        >>> data = ub.ddict(lambda: int)
        >>> data['foo'] = ub.ddict(lambda: int)
        >>> data['bar'] = np.array([1, 2, 3])
        >>> data['foo']['a'] = 1
        >>> data['foo']['b'] = np.array([1, 2, 3])
        >>> data['foo']['c'] = [1, 2, 3]
        >>> data['baz'] = 3
        >>> print('data = {}'.format(ub.repr2(data, nl=True)))
        >>> # We can walk through every node in the nested tree
        >>> walker = IndexableWalker(data)
        >>> for path, value in walker:
        >>>     print('walk path = {}'.format(ub.repr2(path, nl=0)))
        >>>     if path[-1] == 'c':
        >>>         # Use send to prevent traversing this branch
        >>>         got = walker.send(False)
        >>>         # We can modify the value based on the returned path
        >>>         walker[path] = 'changed the value of c'
        >>> print('data = {}'.format(ub.repr2(data, nl=True)))
        >>> assert data['foo']['c'] == 'changed the value of c'

    Example:
        >>> # Test sending false for every data item
        >>> # xdoctest: +REQUIRES(module:numpy)
        >>> import ubelt as ub
        >>> import numpy as np
        >>> data = {1: 1}
        >>> walker = IndexableWalker(data)
        >>> for path, value in walker:
        >>>     print('walk path = {}'.format(ub.repr2(path, nl=0)))
        >>>     walker.send(False)
        >>> data = {}
        >>> walker = IndexableWalker(data)
        >>> for path, value in walker:
        >>>     walker.send(False)
    """

    def __init__(self, data, dict_cls=(dict,), list_cls=(list, tuple)):
        self.data = data
        self.dict_cls = dict_cls
        self.list_cls = list_cls
        self.indexable_cls = self.dict_cls + self.list_cls

        self._walk_gen = None

    def __iter__(self):
        """
        Iterates through the indexable ``self.data``

        Can send a False flag to prevent a branch from being traversed

        Yields:
            Tuple[List, Any] :
                path (List): list of index operations to arrive at the value
                value (object): the value at the path
        """
        return self

    def __next__(self):
        """ returns next item from this generator """
        if self._walk_gen is None:
            self._walk_gen = self._walk()
        return next(self._walk_gen)

    def next(self):  # nocover
        # For Python 2.7
        return self.__next__()

    def send(self, arg):
        """
        send(arg) -> send 'arg' into generator,
        return next yielded value or raise StopIteration.
        """
        # Note: this will error if called before __next__
        self._walk_gen.send(arg)

    def throw(self, type=None, value=None, traceback=None):
        """
        throw(typ[,val[,tb]]) -> raise exception in generator,
        return next yielded value or raise StopIteration.
        """
        raise StopIteration

    def __setitem__(self, path, value):
        """
        Set nested value by path

        Args:
            path (List): list of indexes into the nested structure
            value (object): new value
        """
        d = self.data
        prefix, key = path[:-1], path[-1]
        # *prefix, key = path
        for k in prefix:
            d = d[k]
        d[key] = value

    def __getitem__(self, path):
        """
        Get nested value by path

        Args:
            path (List): list of indexes into the nested structure

        Returns:
            value
        """
        d = self.data
        prefix, key = path[:-1], path[-1]
        # *prefix, key = path
        for k in prefix:
            d = d[k]
        return d[key]

    def __delitem__(self, path):
        """
        Remove nested value by path

        Note:
            It can be dangerous to use this while iterating (because we may try
            to descend into a deleted location) or on leaf items that are
            list-like (because the indexes of all subsequent items will be
            modified).

        Args:
            path (List): list of indexes into the nested structure.
                The item at the last index will be removed.
        """
        d = self.data
        prefix, key = path[:-1], path[-1]
        # *prefix, key = path
        for k in prefix:
            d = d[k]
        del d[key]

    def _walk(self, data=None, prefix=[]):
        """
        Defines the underlying generator used by IndexableWalker

        Yields:
            Tuple[List, object] | None:
                path (List) - a "path" through the nested data structure
                value (object) - the value indexed by that "path".

            Can also yield None in the case that `send` is called on the
            generator.
        """
        if data is None:  # pragma: nobranch
            data = self.data
        stack = [(data, prefix)]
        while stack:
            _data, _prefix = stack.pop()
            # Create an items iterable of depending on the indexable data type
            if isinstance(_data, self.list_cls):
                items = enumerate(_data)
            elif isinstance(_data, self.dict_cls):
                items = _data.items()
            else:
                raise TypeError(type(_data))

            for key, value in items:
                # Yield the full path to this position and its value
                path = _prefix + [key]
                message = yield path, value
                # If the value at this path is also indexable, then continue
                # the traversal, unless the False message was explicitly sent
                # by the caller.
                if message is False:
                    # Because the `send` method will return the next value,
                    # we yield a dummy value so we don't clobber the next
                    # item in the traversal.
                    yield None
                else:
                    if isinstance(value, self.indexable_cls):
                        stack.append((value, path))


def compatible(config, func, start=0):
    """
    Take only the items of a dict that can be passed to function as kwargs

    Args:
        config (dict): a flat configuration dictionary
        func (Callable): a function or method
        start (int, default=0): set to 1 if calling with an unbound method

    Returns:
        dict : a subset of ``config`` that only contains items compatible with
            the signature of ``func``.

    TODO:
        - [ ] Does this go in util_dict or util_func?

    Example:
        >>> # An example use case is to select a subset of of a config
        >>> # that can be passed to some function as kwargs
        >>> from ubelt.util_candidate import *  # NOQA
        >>> # Define a function with args that match some keys in a config.
        >>> def func(a, e, f):
        >>>     return a * e * f
        >>> # Define a config that has a superset of items needed by the func
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> # Call the function only with keys that are compatible
        >>> func(**compatible(config, func))
        442

    Example:
        >>> # Test case with kwargs
        >>> from ubelt.util_candidate import *  # NOQA
        >>> def func(a, e, f, *args, **kwargs):
        >>>     return a * e * f
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> func(**compatible(config, func))

    Ignore:
        >>> # xdoctest: +REQUIRES(PY3)
        >>> # Test case with positional only 3.x +
        >>> def func(a, e, /,  f):
        >>>     return a * e * f
        >>> config = {
        ...   'a': 2, 'b': 3, 'c': 7,
        ...   'd': 11, 'e': 13, 'f': 17,
        ... }
        >>> import pytest
        >>> with pytest.raises(ValueError):
        ...     func(**compatible(config, func))
    """
    import inspect
    if hasattr(inspect, 'signature'):  # pragma :nobranch
        sig = inspect.signature(func)
        argnames = []
        has_kwargs = False
        for arg in sig.parameters.values():
            if arg.kind == inspect.Parameter.VAR_KEYWORD:
                has_kwargs = True
            elif arg.kind == inspect.Parameter.VAR_POSITIONAL:
                # Ignore variadic positional args
                pass
            elif arg.kind == inspect.Parameter.POSITIONAL_ONLY:
                raise ValueError('this does not work with positional only')
            elif arg.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD,
                              inspect.Parameter.KEYWORD_ONLY}:
                argnames.append(arg.name)
            else:  # nocover
                raise TypeError(arg.kind)
    else:  # nocover
        # For Python 2.7
        spec = inspect.getargspec(func)
        argnames = spec.args
        has_kwargs = spec.keywords
        if spec.keywords:
            # kwargs could be anything, so keep everything
            return config
    if has_kwargs:
        # kwargs could be anything, so keep everything
        common = config
    else:
        common = {k: config[k] for k in argnames[start:]
                  if k in config}  # dict-isect
    return common
