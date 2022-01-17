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
    print('data = {}'.format(ub.repr2(data, nl=1)))
    print('mapped_v1 = {}'.format(ub.repr2(mapped_v1, nl=1)))
    print('mapped_v2 = {}'.format(ub.repr2(mapped_v2, nl=1)))
    assert ub.indexable_allclose(mapped_v1, mapped_v2)

    self = ub.IndexableWalker(data)
    self_v1 = _indexable_walker_map_v1(self, ub.identity)
    self_v2 = _indexable_walker_map_v2(self, ub.identity)

    # change auto-dict into lists when appropriate
    fixup = ub.IndexableWalker(self_v1)
    for path, value in fixup:
        if isinstance(value, dict) and isinstance(self[path], list):
            fixup[path] = [v for k, v in sorted(value.items())]

    assert ub.indexable_allclose(self.data, self_v2)
    assert ub.indexable_allclose(self.data, self_v1)
    assert not ub.indexable_allclose(self.data, mapped_v1)
