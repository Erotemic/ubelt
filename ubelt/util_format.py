"""
Warning:

    This module is deprecated. Use :mod:`ubelt.util_repr` instead.
"""
from .util_repr import urepr, ReprExtensions, _REPR_EXTENSIONS


def repr2(data, **kwargs):
    """
    Alias of :func:`ubelt.util_repr.urepr`.

    Warning:
        Deprecated for urepr

    Example:
        >>> # Test that repr2 remains backwards compatible
        >>> import ubelt as ub
        >>> dict_ = {
        ...     'custom_types': [slice(0, 1, None), 1/3],
        ...     'nest_dict': {'k1': [1, 2, {3: {4, 5}}],
        ...                   'key2': [1, 2, {3: {4, 5}}],
        ...                   'key3': [1, 2, {3: {4, 5}}],
        ...                   },
        ...     'nest_dict2': {'k': [1, 2, {3: {4, 5}}]},
        ...     'nested_tuples': [tuple([1]), tuple([2, 3]), frozenset([4, 5, 6])],
        ...     'one_tup': tuple([1]),
        ...     'simple_dict': {'spam': 'eggs', 'ham': 'jam'},
        ...     'simple_list': [1, 2, 'red', 'blue'],
        ...     'odict': ub.odict([(2, '1'), (1, '2')]),
        ... }
        >>> import pytest
        >>> with pytest.warns(DeprecationWarning):
        >>>     result = ub.repr2(dict_, nl=1, precision=2)
        >>> print(result)
        {
            'custom_types': [slice(0, 1, None), 0.33],
            'nest_dict': {'k1': [1, 2, {3: {4, 5}}], 'key2': [1, 2, {3: {4, 5}}], 'key3': [1, 2, {3: {4, 5}}]},
            'nest_dict2': {'k': [1, 2, {3: {4, 5}}]},
            'nested_tuples': [(1,), (2, 3), {4, 5, 6}],
            'odict': {2: '1', 1: '2'},
            'one_tup': (1,),
            'simple_dict': {'ham': 'jam', 'spam': 'eggs'},
            'simple_list': [1, 2, 'red', 'blue'],
        }
    """
    from ubelt.util_deprecate import schedule_deprecation
    schedule_deprecation(
        modname='ubelt', name='repr2', type='function',
        migration='use urepr instead',
        deprecate='1.2.5', error='2.0.0', remove='2.1.0',
    )
    kwargs['_dict_sort_behavior'] = kwargs.get('_dict_sort_behavior', 'old')
    return urepr(data, **kwargs)


repr2.extensions = urepr.extensions
repr2.register = urepr.register


# Deprecated aliases
FormatterExtensions = ReprExtensions
_FORMATTER_EXTENSIONS = _REPR_EXTENSIONS


__all__ = ['repr2', 'urepr', 'FormatterExtensions']
