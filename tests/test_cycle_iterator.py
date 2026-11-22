import itertools
import pytest
import ubelt as ub


@pytest.mark.parametrize(
    'length,size', [(5, 3), (2, 7), (7, 3), (6, 3), (0, 3), (3, 1)]
)
@pytest.mark.parametrize('kind', ['iterator', 'generator'])
def test_cycle_chunks_one_shot(length, size, kind):
    values = list(range(length))
    source = iter(values) if kind == 'iterator' else (x for x in values)
    expected = [
        [values[(start + offset) % length] for offset in range(size)]
        for start in range(0, length, size)
    ]
    assert list(ub.chunks(source, size, bordermode='cycle')) == expected


def test_cycle_chunks_does_not_materialize_input():
    consumed = []

    def source():
        for value in itertools.count():
            consumed.append(value)
            if value >= 9:
                raise AssertionError('consumed beyond requested chunks')
            yield value

    chunks = iter(ub.chunks(source(), 3, bordermode='cycle'))
    assert consumed == []
    assert next(chunks) == [0, 1, 2]
    assert consumed == [0, 1, 2]
    assert next(chunks) == [3, 4, 5]
    assert consumed == list(range(6))


@pytest.mark.parametrize('size', [1, 3])
def test_cycle_chunks_yield_independent_lists(size):
    values = list(range(size + 1))
    result = iter(ub.chunks(iter(values), size, bordermode='cycle'))
    first = next(result)
    first[:] = [-1] * size
    expected_last = [
        values[(size + offset) % len(values)] for offset in range(size)
    ]
    assert next(result) == expected_last
    with pytest.raises(StopIteration):
        next(result)


@pytest.mark.parametrize('size', [1, 3])
def test_cycle_chunks_defers_source_error(size):
    error = RuntimeError('source failed after a full chunk')

    def source():
        yield from range(size)
        raise error

    result = iter(ub.chunks(source(), size, bordermode='cycle'))
    assert next(result) == list(range(size))
    with pytest.raises(RuntimeError) as exc_info:
        next(result)
    assert exc_info.value is error
