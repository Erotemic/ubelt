"""Regression coverage for recent IndexableWalker numeric comparison paths."""

import ubelt as ub


def test_indexable_python_float_does_not_use_numpy_isclose():
    """Python float comparisons should not depend on NumPy behavior."""
    import unittest.mock

    import pytest

    np = pytest.importorskip('numpy')

    lhs = ub.IndexableWalker({'value': 1.0})
    rhs = {'value': 1.0 + 1e-10}
    with unittest.mock.patch.object(
        np, 'isclose', side_effect=AssertionError('unexpected NumPy call')
    ):
        assert lhs.allclose(rhs)
        info = ub.IndexableWalker({'value': 1.0}).diff(rhs)
        assert info['num_approximations'] == 1
        assert info['num_differences'] == 0


def test_indexable_numpy_float_scalars_use_numpy_isclose():
    """NumPy floating scalars should use NumPy's scalar comparison path."""
    import pytest

    np = pytest.importorskip('numpy')

    lhs = {'value': np.float32(1.0)}
    rhs = {'value': np.float32(1.0 + 1e-6)}
    assert ub.IndexableWalker(lhs).allclose(rhs, rel_tol=1e-5)

    info = ub.IndexableWalker(lhs).diff(rhs, rel_tol=1e-5)
    assert info['num_approximations'] == 1
    assert info['num_differences'] == 0


def test_indexable_python_nan_does_not_use_numpy_isclose():
    """Python NaNs use the standard-library path even when NumPy is present."""
    import unittest.mock

    import pytest

    np = pytest.importorskip('numpy')

    lhs = ub.IndexableWalker({'value': float('nan')})
    rhs = {'value': float('nan')}
    with unittest.mock.patch.object(
        np, 'isclose', side_effect=AssertionError('unexpected NumPy call')
    ):
        assert lhs.allclose(rhs, equal_nan=True)
        info = ub.IndexableWalker({'value': float('nan')}).diff(
            rhs, equal_nan=True
        )
        assert info['num_approximations'] == 1
        assert info['num_differences'] == 0
