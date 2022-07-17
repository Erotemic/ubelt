
def test_compatible_keywords():
    import ubelt as ub
    def func(a, e, f, *args, **kwargs):
        return a * e * f

    config = {
        'a': 2, 'b': 3, 'c': 7,
        'd': 11, 'e': 13, 'f': 17,
    }

    assert ub.compatible(config, func, keywords=True) is config
    assert ub.compatible(config, func, keywords=1) is config
    assert ub.compatible(config, func, keywords='truthy') is config

    assert ub.compatible(config, func, keywords=['iterable']) is not config
    assert ub.compatible(config, func, keywords=0) is not config
    assert ub.compatible(config, func, keywords={'b'}) == {'a': 2, 'e': 13, 'f': 17, 'b': 3}


def test_positional_only_args():
    import ubelt as ub
    import sys
    import pytest
    if sys.version_info[0:2] <= (3, 7):
        pytest.skip('position only arguments syntax requires Python >= 3.8')

    # Define via an exec, so this test does not raise a syntax error
    # in other versions of python and skips gracefully
    pos_only_code = ub.codeblock(
        '''
        import ubelt as ub
        def func(a, e, /,  f):
            return a * e * f
        ''')
    ns = {}
    exec(pos_only_code, ns, ns)
    func = ns['func']
    config = {
        'a': 2, 'b': 3, 'c': 7,
        'd': 11, 'e': 13, 'f': 17,
    }
    pos_only = ub.compatible(config, func)
    assert sorted(pos_only) == ['f']
