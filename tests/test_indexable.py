import ubelt as ub


def _indexable_walker_map_v1(self, func):
    # This is a one pattern for "mapping" a function over nested data and
    # preserving the structure.
    mapped = ub.AutoDict()
    mapped_walker = ub.IndexableWalker(mapped)
    for path, value in self:
        if isinstance(value, self.list_cls):
            mapped_walker[path] = [ub.AutoDict()] * len(value)
        elif not isinstance(value, self.indexable_cls):
            mapped_walker[path] = func(value)
    return mapped


def _indexable_walker_map_v2(self, func):
    # TODO: might be reasonable to add a map attribute to the indexable walker.
    # This is a another pattern for "mapping" a function over nested data and
    # preserving the structure.
    if isinstance(self.data, self.dict_cls):
        mapped = {}
    elif isinstance(self.data, self.list_cls):
        mapped = []
    else:
        raise NotImplementedError
    mapped_walker = ub.IndexableWalker(mapped)
    for path, value in self:
        if isinstance(value, self.dict_cls):
            mapped_walker[path] = {}
        elif isinstance(value, self.list_cls):
            mapped_walker[path] = [None] * len(value)
        else:
            mapped_walker[path] = func(value)
    return mapped


def _map_vals3(self, func):
    """
    Defines the underlying generator used by IndexableWalker

    Yields:
        Tuple[List, object] | None:
            path (List) - a "path" through the nested data structure
            value (object) - the value indexed by that "path".

        Can also yield None in the case that `send` is called on the
        generator.

    Example:
        data = {
            '1': [2, 3, {4: 5}],
            '3': {
                'foo': 'bar',
                'baz': [1, 2, ['biz']],
            }
        }
        self = ub.IndexableWalker(data)
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/code/ubelt/tests'))
        from test_indexable import *  # NOQA
        from test_indexable import _indexable_walker_map_v1, _indexable_walker_map_v2, _map_vals3
        _map_vals3(self, type)
        _map_vals3(self, str)
    """
    data = self.data
    if isinstance(data, self.dict_cls):
        mapped = {}
    elif isinstance(data, self.list_cls):
        mapped = []
    else:
        raise NotImplementedError
    stack = [(data, mapped)]
    while stack:
        _data, _parent = stack.pop()
        # Create an items iterable of depending on the indexable data type
        if isinstance(_data, self.list_cls):
            items = enumerate(_data)
        elif isinstance(_data, self.dict_cls):
            items = _data.items()
        else:
            raise TypeError(type(_data))
        for key, value in items:
            if isinstance(value, self.indexable_cls):
                if isinstance(value, self.dict_cls):
                    new = _parent[key] = {}
                elif isinstance(value, self.list_cls):
                    new = _parent[key] = [None] * len(value)
                else:
                    raise TypeError(type(value))
                stack.append((value, new))
            else:
                _parent[key] = func(value)
    return mapped


# def _map_vals4(self, func):
#     for key, value, _data in _walk2(self.data):
#         pass


# def _walk2(self, data=None, mapped=None):
#     """
#     Defines the underlying generator used by IndexableWalker

#     Yields:
#         Tuple[List, object] | None:
#             path (List) - a "path" through the nested data structure
#             value (object) - the value indexed by that "path".

#         Can also yield None in the case that `send` is called on the
#         generator.

#     Example:
#         data = {
#             '1': [2, 3, {4: 5}],
#             '3': {
#                 'foo': 'bar',
#                 'baz': [1, 2, ['biz']],
#             }
#         }
#         self = ub.IndexableWalker(data)
#         list(_walk2(self))
#         self = ub.IndexableWalker(data)
#         for key, value, _data, _prefix in _walk2(self):
#             print('key = {!r}'.format(key))
#             print('value = {!r}'.format(value))
#             print('_prefix = {!r}'.format(_prefix))
#             print('_data = {!r}'.format(_data))
#             print('---')
#     """
#     if data is None:  # pragma: nobranch
#         data = self.data
#     key = None
#     if mapped is None:
#         mapped = {None: }
#     stack = [(data, key, mapped)]
#     while stack:
#         _data, _prefix, _mapped = stack.pop()
#         # Create an items iterable of depending on the indexable data type
#         if isinstance(_data, self.list_cls):
#             items = enumerate(_data)
#         elif isinstance(_data, self.dict_cls):
#             items = _data.items()
#         else:
#             raise TypeError(type(_data))

#         for key, value in items:
#             # Yield the full path to this position and its value
#             path = _prefix + [key]
#             message = yield path, key, value, _data, _prefix
#             # If the value at this path is also indexable, then continue
#             # the traversal, unless the False message was explicitly sent
#             # by the caller.
#             if message is False:
#                 # Because the `send` method will return the next value,
#                 # we yield a dummy value so we don't clobber the next
#                 # item in the traversal.
#                 yield None
#             else:
#                 if isinstance(value, self.indexable_cls):
#                     stack.append((value, key, _mapped[key]))


def test_indexable_walker_map_patterns():
    """
    Check that we can walk through an indexable and make a deep copy
    """
    data = {
        '1': [2, 3, {4: 5}],
        '3': {
            'foo': 'bar',
            'baz': [1, 2, ['biz']],
        }
    }
    self = ub.IndexableWalker(data)
    func = type
    mapped_v1 = _indexable_walker_map_v1(self, func)
    mapped_v2 = _indexable_walker_map_v2(self, func)
    print('data = {}'.format(ub.urepr(data, nl=1)))
    print('mapped_v1 = {}'.format(ub.urepr(mapped_v1, nl=1)))
    print('mapped_v2 = {}'.format(ub.urepr(mapped_v2, nl=1)))

    import pytest
    with pytest.warns(Warning):
        assert ub.indexable_allclose(mapped_v1, mapped_v2)

    self = ub.IndexableWalker(data)
    # import timerit
    # ti = timerit.Timerit(10, bestof=2, verbose=2)
    # for timer in ti.reset('time'):
    #     with timer:
    self_v1 = _indexable_walker_map_v1(self, ub.identity)
    # for timer in ti.reset('time'):
    #     with timer:
    self_v2 = _indexable_walker_map_v2(self, ub.identity)
    # for timer in ti.reset('time'):
    #     with timer:
    self_v3 = _map_vals3(self, ub.identity)  # NOQA

    # change auto-dict into lists when appropriate
    fixup = ub.IndexableWalker(self_v1)
    for path, value in fixup:
        if isinstance(value, dict) and isinstance(self[path], list):
            fixup[path] = [v for k, v in sorted(value.items())]

    import pytest
    with pytest.warns(Warning):
        assert ub.indexable_allclose(self.data, self_v2)
    with pytest.warns(Warning):
        assert ub.indexable_allclose(self.data, self_v1)
    with pytest.warns(Warning):
        assert not ub.indexable_allclose(self.data, mapped_v1)


def test_walk_iter_gen_behavior():
    from itertools import count
    import ubelt as ub
    # from functools import cache
    counter = count()

    @ub.memoize
    def tree(b, d):
        if d == 1:
            return [next(counter) for i in range(b)]
        else:
            return [tree(b, d - 1) for i in range(b)]

    data = tree(3, 3)

    # Order of operations does matter
    walker = ub.IndexableWalker(data)
    # Should use self-iter
    item1 = next(walker)
    item2 = next(walker)
    item3 = next(walker)
    print('item1 = {!r}'.format(item1))
    print('item2 = {!r}'.format(item2))
    print('item3 = {!r}'.format(item3))

    # Should make new iters, and clobber existing ones
    assert list(walker) == list(walker)

    import pytest
    # Exhausing the current iterator will cause StopIteration
    list(walker)
    with pytest.raises(StopIteration):
        item4 = next(walker)  # NOQA

    walker = ub.IndexableWalker(data)
    # Should make new iters, and clobber existing ones
    item1 = next(walker)
    iter(walker)
    item2 = next(walker)
    assert item1 == item2
    assert item1 != next(walker)

    # Should make new iters
    walker = ub.IndexableWalker(data)
    c = 0
    for _ in walker:
        try:
            next(walker)
        except StopIteration:
            pass
        c += 1

    walker = ub.IndexableWalker(data)
    d = 0
    for _ in walker:
        d += 1

    assert d == len(list(walker))
    assert d != c
