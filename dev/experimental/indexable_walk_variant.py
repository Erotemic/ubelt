def _walk_iterables(self):
    """
    EXPERIMENTAL

    # TODO: it would likely be helpful to have some method of directly
    # modifying the underlying value without needing to traverse the entire
    # path to get to it.
    # This could be implemented in two ways:
    ##
    # 1. We send the new value to the generator, but this might result in
    # an awkward API with the existing "False" method of controlling
    # iteration.
    ##
    # 2. A new walking method that works more like os.walk where instead
    # of yielding for every item, we yield for every iterable.  This seems
    # like a nicer change and the user could simply modify the returned
    # iterable inplace to both prevent subsequent iteration and modify
    # values.
    ##
    # 3. We can return the parent with the path, value.
    # this is kinda blegh.

    This is the solution for point 2.

    But this might not have advantage over the existing walk if the
    previous walk has access to iterable values anyway...
    In fact this probably isn't worth it.

    This is a new style generator that is more similar to os.walk

    Yields:
        Tuple[List, [Iterable]]:
            path (List) - a "path" through the nested data structure
            level (Iterable) - the iterable at this level.

    Ignore:
        >>> # A somewhat clever way of mapping a filesystem into a dict
        >>> fs_tree = {}
        >>> fs_walker = ub.IndexableWalker(fs_tree)
        >>> root = ub.Path.appdir('ubelt')
        >>> for r, ds, fs in root.walk():
        >>>     p = ['.'] + list(r.relative_to(root).parts)
        >>>     fs_walker[p] = {}
        >>>     fs_walker[p].update({f: None for f in fs})
        >>> # The above gives us some richer demo data
        >>> fs_walker = ub.IndexableWalker(fs_tree)
        >>> for path, nodes, leafs, data in _walk_iterables(fs_walker):
        >>>     print(f'path={path}')
        >>>     print(f'nodes={nodes}')
        >>>     print(f'leafs={leafs}')

        >>> import numpy as np
        >>> import ubelt as ub
        >>> data = ub.ddict(lambda: int)
        >>> data['foo'] = ub.ddict(lambda: int)
        >>> data['bar'] = np.array([1, 2, 3])
        >>> data['foo']['a'] = 1
        >>> data['foo']['b'] = np.array([1, 2, 3])
        >>> data['foo']['c'] = [1, 2, [[1, 1, 1, 1], [], [1, {'a': [[2, 1], [3, 4]]}, 2, [2, 3]]]]
        >>> data['baz'] = 3
        >>> print('data = {}'.format(ub.repr2(data, nl=True)))
        >>> # We can walk through every node in the nested tree
        >>> walker = ub.IndexableWalker(data)
        >>> for path, nodes, leafs, data in _walk_iterables(walker):
        >>>     print(f'path={path}')
        >>>     print(f'leafs={leafs}')
    """
    stack = [([], self.data)]
    while stack:
        path, data = stack.pop()

        # Create an items iterable of depending on the indexable data type
        if isinstance(data, self.list_cls):
            items = enumerate(data)
        elif isinstance(data, self.dict_cls):
            items = data.items()
        else:
            raise TypeError(type(data))

        nodes = []
        leafs = []

        # Iterate through this level and determine which keys are
        # leaf-endpoints and which keys are recursable nodes.
        for key, value in items:
            if isinstance(value, self.indexable_cls):
                nodes.append(key)
            else:
                leafs.append(key)
        # The user is given:
        # * path - where we are in the tree
        # * data - the iterable at this level
        # * nodes - which keys will be descended into
        # * leafs - which keys will not be descended into
        yield path, nodes, leafs, data
        # If the user modifies: "nodes" that will change how we iterate.
        # The user can also modify data at this level without hassle
        for key in nodes:
            stack.append((path + [key], data[key]))
