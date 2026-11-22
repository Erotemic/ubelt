from __future__ import annotations

import pathlib
import typing

import ubelt as ub

try:
    from typing import assert_type
except ImportError:  # pragma: no cover
    from typing_extensions import assert_type


def consumer_typing_contract(variable_flag: bool) -> None:
    """Static assertions for common caller-facing inference."""
    walker = ub.IndexableWalker({'value': 1.0})
    assert_type(walker.allclose({'value': 1.0}), bool)
    assert_type(
        walker.allclose({'value': 1.0}, return_info=True),
        tuple[bool, dict],
    )
    assert_type(
        walker.allclose({'value': 1.0}, return_info=variable_flag),
        bool | tuple[bool, dict],
    )

    assert_type(ub.indexable_allclose({}, {}), bool)
    assert_type(
        ub.indexable_allclose({}, {}, return_info=True),
        tuple[bool, dict],
    )

    assert_type(ub.find_exe('python'), str | None)
    assert_type(ub.find_exe('python', multi=True), list[str])
    assert_type(
        ub.find_exe('python', multi=variable_flag),
        str | list[str] | None,
    )

    source = {'a': 1, 'b': 2}
    assert_type(ub.invert_dict(source), dict[int, str])
    assert_type(
        ub.invert_dict(source, unique_vals=False),
        dict[int, set[str]],
    )

    assert_type(ub.readfrom('data.txt'), str)
    assert_type(ub.readfrom('data.txt', aslines=True), list[str])
    assert_type(
        ub.readfrom('data.txt', aslines=variable_flag),
        str | list[str],
    )

    assert_type(
        ub.compress([1, 2, 3], [True, False, True]),
        typing.Iterator[int],
    )

    path = pathlib.Path('demo')
    assert_type(ub.touch(path), pathlib.Path)
    assert_type(ub.ensuredir(path), pathlib.Path)
    assert_type(ub.ensuredir(('demo', 'subdir')), str)
    assert_type(ub.symlink(path, path), str)


def dictionary_subclass_typing_contract(fallback: str) -> None:
    """Static contracts for the generic dictionary subclasses and aliases."""
    raw_items: list[dict[str, int]] = [
        {'alpha': 1},
        {'beta': 2},
    ]

    # ty currently loses generic return types through higher-order calls such
    # as map, even for plain generic functions. Keep the real consumer pattern
    # as a no-diagnostic regression, but assert exact types on direct calls.
    items = list(map(ub.udict, raw_items))
    _ = items[0] | items[1]
    exact_items = [ub.udict(item) for item in raw_items]
    assert_type(exact_items, list[ub.UDict[str, int]])

    direct = ub.udict({'gamma': 3})
    assert_type(direct, ub.UDict[str, int])
    assert_type(ub.UDict({'gamma': 3}), ub.UDict[str, int])
    assert_type(ub.udict([('gamma', 3)]), ub.UDict[str, int])
    assert_type(direct.copy(), ub.UDict[str, int])

    # Union-like operations may widen both keys and values.
    widened = direct | {1: 'one'}
    assert_type(widened, ub.UDict[str | int, int | str])
    # For a built-in dict on the left, ty currently follows dict.__or__ and
    # materializes a plain dict even though runtime reflected dispatch returns
    # UDict. Exercise the expression without asserting checker-specific output.
    reverse_widened = {1: 'one'} | direct
    _ = reverse_widened.items()
    assert_type(direct ^ {1: 'one'}, ub.UDict[str | int, int | str])
    assert_type(
        direct.union({1: 'one'}),
        ub.UDict[str | int, int | str],
    )
    assert_type(
        direct.symmetric_difference({1: 'one'}),
        ub.UDict[str | int, int | str],
    )

    # Subtractive operations preserve the left operand's item types.
    assert_type(direct & {'gamma'}, ub.UDict[str, int])
    assert_type(direct - {'missing'}, ub.UDict[str, int])
    assert_type(direct.intersection({'gamma'}), ub.UDict[str, int])
    assert_type(direct.difference({'missing'}), ub.UDict[str, int])
    assert_type({'gamma': 4} & direct, ub.UDict[str, int])

    assert_type(direct.subdict(['gamma']), ub.UDict[str, int])
    assert_type(
        direct.subdict(['gamma', 'missing'], default=fallback),
        ub.UDict[str, int | str],
    )
    assert_type(
        direct.take(['gamma']),
        typing.Generator[int, None, None],
    )
    assert_type(
        direct.take(['gamma', 'missing'], default=fallback),
        typing.Generator[int | str, None, None],
    )

    assert_type(direct.invert(), ub.UDict[int, str])
    assert_type(direct.invert(unique_vals=False), ub.UDict[int, set[str]])
    assert_type(direct.map_keys(len), ub.UDict[int, int])
    assert_type(direct.map_values(str), ub.UDict[str, str])
    assert_type(direct.sorted_keys(), typing.OrderedDict[str, int])
    assert_type(direct.sorted_values(), typing.OrderedDict[str, int])

    assert_type(ub.udict.fromkeys(['a', 'b'], 1), ub.UDict[str, int])
    assert_type(ub.UDict.fromkeys(['a', 'b'], 1), ub.UDict[str, int])

    base = ub.sdict({'gamma': 3})
    assert_type(base, ub.SetDict[str, int])
    assert_type(base.copy(), ub.SetDict[str, int])
    assert_type(base | {1: 'one'}, ub.SetDict[str | int, int | str])
    assert_type(
        base.union({1: 'one'}),
        ub.SetDict[str | int, int | str],
    )
    assert_type(base.intersection({'gamma'}), ub.SetDict[str, int])

    # The aliases remain classes, not factory objects.
    assert isinstance(direct, ub.udict)
    assert isinstance(direct, ub.UDict)
