import typing

import pytest

import ubelt as ub

if typing.TYPE_CHECKING:
    try:
        from typing import assert_type
    except ImportError:  # pragma: no cover
        from typing_extensions import assert_type

    _chunk_iter1 = ub.chunks([1, 2, 3], chunksize=2, bordermode='cycle')
    assert_type(next(iter(_chunk_iter1)), list[int])
    _items2: typing.Iterator[int] = iter([1, 2, 3])
    _chunk_iter2 = ub.chunks(_items2, nchunks=2, total=3)
    assert_type(next(iter(_chunk_iter2)), list[int])


def test_chunk_errors() -> None:
    with pytest.raises(ValueError):
        typing.cast(typing.Any, ub.chunks)(range(9))

    with pytest.raises(ValueError):
        typing.cast(typing.Any, ub.chunks)(range(9), chunksize=2, nchunks=2)

    with pytest.raises(ValueError):
        len(typing.cast(typing.Any, ub.chunks)((_ for _ in range(2)), nchunks=2))


def test_chunk_total_chunksize() -> None:
    gen: ub.chunks[typing.Any] = ub.chunks([], total=10, chunksize=4)
    assert len(gen) == 3


def test_chunk_total_nchunks() -> None:
    gen: ub.chunks[typing.Any] = ub.chunks([], total=10, nchunks=4)
    assert len(gen) == 4


def test_chunk_len() -> None:
    gen = ub.chunks([1] * 6, chunksize=3)
    assert len(gen) == 2


if __name__ == '__main__':
    r"""
    CommandLine:
        pytest tests/test_list.py
    """
    import xdoctest

    xdoctest.doctest_module(__file__)
