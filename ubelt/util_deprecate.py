"""
Currently this module provides one utility
:func:`ubelt.util_deprecate.schedule_deprecation` which allows a developer to
easily mark features in their libraries as deprecated.
"""


def schedule_deprecation(modname, name='?', type='?', migration='',
                         deprecate=None, error=None, remove=None,
                         warncls=DeprecationWarning):
    """
    Deprecation machinery to help provide users with a smoother transition.

    This function provides a concise way to mark a feature as deprecated by
    providing a description of the deprecated feature, documentation on how to
    migrate away from the deprecated feature, and the versions that the feature
    is scheduled for deprecation and eventual removal. Based on the version of
    the library and the specified schedule this function will either do
    nothing, emit a warning, or raise an error with helpful messages for both
    users and developers.

    Args:
        modname (str):
            The name of the underlying module associated with the feature to be
            deprecated. The module must already be imported and have a passable
            ``__version__`` attribute.

        name (str):
            The name of the feature to deprecate. This is usually a function or
            argument name.

        type (str):
            A description of what the feature is. This is not a formal type,
            but rather a prose description: e.g. "argument to my_func".

        migration (str):
            A description that lets users know what they should do instead of
            using the deprecated feature.

        deprecate (str | None):
            The version when the feature is officially deprecated and this
            function should start to emit a deprecation warning.

        error (str | None):
            The version when the feature is officially no longer supported, and
            will start to raise a RuntimeError.

        remove (str | None):
            The version when the feature is completely removed. An
            AssertionError will be raised if this function is still present
            reminding the developer to remove the feature (or extend the remove
            version).

        warncls (type):
            This is the category of warning to use. Defaults to
            :class:`DeprecationWarning`.

    Note:
        The :class:`DeprecationWarning` is not visible by default.
        https://docs.python.org/3/library/warnings.html

    Example:
        >>> from ubelt import schedule_deprecation
        >>> import sys
        >>> import types
        >>> import pytest
        >>> dummy_module = sys.modules['dummy_module'] = types.ModuleType('dummy_module')
        >>> # When less than the deprecated version this does nothing
        >>> dummy_module.__version__ = '1.0.0'
        >>> schedule_deprecation(
        ...     'dummy_module', 'myfunc', 'function', 'do something else',
        ...     deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # Now this raises warning
        >>> with pytest.warns(DeprecationWarning):
        ...     dummy_module.__version__ = '1.1.0'
        ...     schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # Now this raises an error for the user
        >>> with pytest.raises(RuntimeError):
        ...     dummy_module.__version__ = '1.2.0'
        ...     schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # Now this raises an error for the developer
        >>> with pytest.raises(AssertionError):
        ...     dummy_module.__version__ = '1.3.0'
        ...     schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # When no versions are specified, it simply emits the warning
        >>> with pytest.warns(DeprecationWarning):
        ...     dummy_module.__version__ = '1.1.0'
        ...     schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else')
    """
    import sys
    import warnings
    from packaging.version import parse as parse_version
    module = sys.modules[modname]
    current = parse_version(module.__version__)
    deprecate_str = ''
    if deprecate is not None:
        deprecate = parse_version(deprecate)
        deprecate_str = ' in {}'.format(deprecate)
    remove_str = ''
    if remove is not None:
        remove = parse_version(remove)
        remove_str = ' in {}'.format(remove)
    error_str = ''
    if error is not None:
        error = parse_version(error)
        error_str = ' in {}'.format(error)
    if deprecate is None or current >= deprecate:
        msg = (
            'The "{name}" {type} was deprecated{deprecate_str}, will cause '
            'an error{error_str} and will be removed{remove_str}. The current '
            'version is {current}. {migration}'
        ).format(**locals()).strip()
        if remove is not None and current >= remove:
            raise AssertionError(
                'Forgot to remove deprecated: ' + msg + ' ' +
                'Remove the function, or extend the scheduled remove version.'
            )
        if error is not None and current >= error:
            raise RuntimeError(msg)
        else:
            warnings.warn(msg, warncls)
