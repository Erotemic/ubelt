"""
Candidate functions
"""
from collections import defaultdict as ddict
from ubelt.util_const import NoParam
from collections.abc import Generator


def basis_product(basis):
    """
    Args:
        basis (Dict[str, List[T]]): list of values for each axes

    Yields:
        Dict[str, T] - points in the grid

    Example:
        >>> basis = {
        >>>     'arg1': [1, 2, 3],
        >>>     'arg2': ['A1', 'B1'],
        >>>     'arg3': [9999, 'Z2'],
        >>>     'arg4': ['always'],
        >>> }
        >>> got = list(basis_product(basis))
        >>> import ubelt as ub
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
    import itertools as it
    keys = list(basis.keys())
    for vals in it.product(*basis.values()):
        kw = dict(zip(keys, vals))
        yield kw


def varied_values(dict_list, min_variations=1):
    """
    Given a list of dictionaries, find the values that differ between them

    Args:
        dict_list (List[Dict]):
            The values of the dictionary must be hashable. Lists will be
            converted into tuples.

        min_variations (int, default=1): minimum number of variations to return

    TODO:
        - [ ] Is this a ubelt function?

    Example:
        >>> num_keys = 10
        >>> num_dicts = 10
        >>> all_keys = {ub.hash_data(i)[0:16] for i in range(num_keys)}
        >>> dict_list = [
        >>>     {key: ub.hash_data(key)[0:16] for key in all_keys}
        >>>     for _ in range(num_dicts)
        >>> ]
        >>> import random
        >>> rng = random.Random(0)
        >>> for data in dict_list:
        >>>     if rng.random() > 0.5:
        >>>         for key in list(data):
        >>>             if rng.random() > 0.9:
        >>>                 data[key] = rng.randint(1, 32)
        >>> varied = varied_values(dict_list)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1)))
    """
    all_keys = set()
    for data in dict_list:
        all_keys.update(data.keys())

    varied = ddict(set)
    for data in dict_list:
        for key in all_keys:
            value = data.get(key, NoParam)
            if isinstance(value, list):
                value = tuple(value)
            varied[key].add(value)

    for key, values in list(varied.items()):
        if len(values) <= min_variations:
            del varied[key]
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

    Example:
        >>> # Create nested data
        >>> import numpy as np
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
        *prefix, key = path
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
        *prefix, key = path
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
        *prefix, key = path
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
        if data is None:
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
