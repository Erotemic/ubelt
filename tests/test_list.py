import pytest
import ubelt as ub


def test_chunk_errors():
    with pytest.raises(ValueError):
        ub.chunks(range(9))

    with pytest.raises(ValueError):
        ub.chunks(range(9), chunksize=2, nchunks=2)

    with pytest.raises(ValueError):
        len(ub.chunks((_ for _ in range(2)), nchunks=2))


def test_chunk_total_chunksize():
    gen = ub.chunks([], total=10, chunksize=4)
    assert len(gen) == 3


def test_chunk_total_nchunks():
    gen = ub.chunks([], total=10, nchunks=4)
    assert len(gen) == 4


def test_chunk_len():
    gen = ub.chunks([1] * 6, chunksize=3)
    assert len(gen) == 2


if __name__ == '__main__':
    r"""
    CommandLine:
        pytest tests/test_list.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
