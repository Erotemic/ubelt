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
