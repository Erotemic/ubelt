import typing


def test_compatible_keywords() -> None:
    import ubelt as ub

    def func(a: int, e: int, f: int, *args: object, **kwargs: object) -> int:
        return a * e * f

    config = {
        'a': 2,
        'b': 3,
        'c': 7,
        'd': 11,
        'e': 13,
        'f': 17,
    }

    assert ub.compatible(config, func, keywords=True) is config
    assert ub.compatible(config, func, keywords=True) is config
    assert ub.compatible(config, func, keywords='truthy') is config

    assert ub.compatible(config, func, keywords=['iterable']) is not config
    assert ub.compatible(config, func, keywords=False) is not config
    assert ub.compatible(config, func, keywords={'b'}) == {
        'a': 2,
        'e': 13,
        'f': 17,
        'b': 3,
    }


def test_positional_only_args() -> None:
    import sys

    import pytest

    import ubelt as ub

    if sys.version_info[0:2] <= (3, 7):
        pytest.skip('position only arguments syntax requires Python >= 3.8')

    # Define via an exec, so this test does not raise a syntax error
    # in other versions of python and skips gracefully
    pos_only_code = ub.codeblock(
        """
        import ubelt as ub
        def func(a, e, /,  f):
            return a * e * f
        """
    )
    ns: dict[str, object] = {}
    exec(pos_only_code, ns, ns)
    func = typing.cast(typing.Callable[..., object], ns['func'])
    config = {
        'a': 2,
        'b': 3,
        'c': 7,
        'd': 11,
        'e': 13,
        'f': 17,
    }
    pos_only = ub.compatible(config, func)
    assert sorted(pos_only) == ['f']
