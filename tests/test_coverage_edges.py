"""Regression cases for ZIP imports, NaN comparisons, and descriptors."""

from __future__ import annotations

import sys
import zipfile

import pytest

import ubelt as ub


def test_zip_import_discard_partially_initialized_module(tmp_path) -> None:
    """A SystemExit during ZIP loading must not poison ``sys.modules``."""
    modname = 'ubelt_zip_import_interrupted_for_test'
    archive_path = tmp_path / 'interrupted.zip'
    with zipfile.ZipFile(archive_path, 'w') as archive:
        archive.writestr(f'{modname}.py', "raise SystemExit('zip import stopped')\n")

    assert modname not in sys.modules
    with pytest.raises(SystemExit, match='zip import stopped'):
        ub.import_module_from_path(f'{archive_path}:{modname}.py')
    assert modname not in sys.modules


def test_indexable_diff_python_float_nan() -> None:
    """The non-NumPy float comparison respects equal_nan."""
    left = {'value': float('nan')}
    right = {'value': float('nan')}

    different = ub.IndexableWalker(left).diff(right, equal_nan=False)
    assert different['num_differences'] == 1
    assert different['num_similarities'] == 0

    equivalent = ub.IndexableWalker(left).diff(right, equal_nan=True)
    assert equivalent['num_differences'] == 0
    assert equivalent['num_similarities'] == 1
    assert equivalent['passlist'] == [('value',)]
    assert equivalent['num_approximations'] == 1


def test_memoize_method_class_descriptor_and_wrapped_function() -> None:
    """Class access returns the descriptor and exposes its original method."""
    class Worker:
        def __init__(self) -> None:
            self.calls = 0

        @ub.memoize_method
        def twice(self, value: int) -> int:
            self.calls += 1
            return 2 * value

    descriptor = Worker.twice
    assert descriptor is Worker.__dict__['twice']
    assert descriptor.__func__.__name__ == 'twice'

    instance = Worker()
    assert instance.twice(7) == 14
    assert instance.twice(7) == 14
    assert instance.calls == 1
