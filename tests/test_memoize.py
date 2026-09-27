from __future__ import annotations

import ubelt as ub


def test_memoize_method_func_attribute() -> None:
    class Demo:
        @ub.memoize_method
        def method(self, value):
            return value

    # Access through the class exercises the descriptor itself. In particular,
    # __func__ should expose the original wrapped function just like a bound
    # method does.
    descriptor = Demo.method
    assert descriptor.__func__.__name__ == 'method'
    assert descriptor.__func__(Demo(), 3) == 3


def test_memoize_unhashable_argument() -> None:
    calls = []

    @ub.memoize
    def func(data):
        calls.append(data)
        return len(data)

    assert func([1, 2]) == 2
    assert func([1, 2]) == 2
    assert len(calls) == 1
