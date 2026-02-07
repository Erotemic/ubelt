from __future__ import annotations

"""
Currently this module provides one utility
:func:`ubelt.util_deprecate.schedule_deprecation` which allows a developer to
easily mark features in their libraries as deprecated.
"""


# DEFAULT_WARN_CLASS = DeprecationWarning
DEFAULT_WARN_CLASS = FutureWarning


def schedule_deprecation(
    modname: str | None = None,
    name: str = '?',
    type: str = '?',
    migration: str = '',
    deprecate: str | None = None,
    error: str | None = None,
    remove: str | None = None,
    # TODO: let the user have more control over the message.
    # message=None,
    warncls: type | str = 'default',
    stacklevel: int = 1,
) -> str:
    """
    Raise a deprecation warning or error based on the version of a package.

    This helps provide users with a smoother transition by specifying a version
    when the deprecation warning will start, when it transitions into an error,
    and when the maintainers should remove the feature all together.

    This function provides a concise way to mark a feature as deprecated by
    providing a description of the deprecated feature, documentation on how to
    migrate away from the deprecated feature, and the versions that the feature
    is scheduled for deprecation and eventual removal. Based on the version of
    the library and the specified schedule this function will either do
    nothing, emit a warning, or raise an error with helpful messages for both
    users and developers.

    Args:
        modname (str | None):
            The name of the underlying module associated with the feature to be
            deprecated. The module must already be imported and have a passable
            ``__version__`` attribute. If unspecified, version info cannot be
            used.

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
            Can also be the strings: "soon" or "now" if the timeline
            isnt perfectly defined.

        error (str | None):
            The version when the feature is officially no longer supported, and
            will start to raise a RuntimeError.
            Can also be the strings: "soon" or "now".

        remove (str | None):
            The version when the feature is completely removed. An
            AssertionError will be raised if this function is still present
            reminding the developer to remove the feature (or extend the remove
            version).  Can also be the strings: "soon" or "now".

        warncls (type | str):
            This is the category of warning to use.
            If given as the string "default", it will defaults the global
            ``DEFAULT_WARN_CLASS``, which can be overwritten by an application,
            but is hard coded as :class:`FutureWarning`.

        stacklevel (int):
            The stacklevel can be used by wrapper functions to indicate where
            the warning is occurring.

    Returns:
        str : the constructed message

    Note:
        If deprecate, remove, or error is specified as "now" or a truthy value
        it will force that check to trigger immediately. If the value is
        "soon", then the check will not trigger.

    Note:
        The :class:`DeprecationWarning` is not visible by default.
        https://docs.python.org/3/library/warnings.html which is why we default
        to :class`FutureWarning`.

    Example:
        >>> # xdoctest: +REQUIRES(module:packaging)
        >>> import ubelt as ub
        >>> import sys
        >>> import types
        >>> import pytest
        >>> dummy_module = sys.modules['dummy_module'] = types.ModuleType('dummy_module')
        >>> # When less than the deprecated version this does nothing
        >>> dummy_module.__version__ = '1.0.0'
        >>> ub.schedule_deprecation(
        ...     modname='dummy_module', name='myfunc', type='function',
        ...     migration='do something else',
        ...     deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # But when the module version increases above the threshold,
        >>> # the warning is raised.
        >>> dummy_module.__version__ = '1.1.0'
        >>> with pytest.warns(Warning):
        ...     msg = ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> print(msg)
        The "myfunc" function was deprecated in dummy_module 1.1.0, will cause
        an error in dummy_module 1.2.0 and will be removed in dummy_module
        1.3.0. The current dummy_module version is 1.1.0. do something else

    Example:
        >>> # xdoctest: +REQUIRES(module:packaging)
        >>> # Demo the various cases
        >>> import ubelt as ub
        >>> import sys
        >>> import types
        >>> import pytest
        >>> dummy_module = sys.modules['dummy_module'] = types.ModuleType('dummy_module')
        >>> # When less than the deprecated version this does nothing
        >>> dummy_module.__version__ = '1.1.0'
        >>> # Now this raises warning
        >>> with pytest.warns(Warning):
        ...     dummy_module.__version__ = '1.1.0'
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # Now this raises an error for the user
        >>> with pytest.raises(RuntimeError):
        ...     dummy_module.__version__ = '1.2.0'
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # Now this raises an error for the developer
        >>> with pytest.raises(AssertionError):
        ...     dummy_module.__version__ = '1.3.0'
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='1.1.0', error='1.2.0', remove='1.3.0')
        >>> # When no versions are specified, it simply emits the warning
        >>> with pytest.warns(Warning):
        ...     dummy_module.__version__ = '1.1.0'
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else')
        >>> # Test with soon / now
        >>> with pytest.warns(Warning):
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate='now', error='soon', remove='soon', warncls=Warning)
        >>> # Test with truthy values
        >>> with pytest.raises(RuntimeError):
        ...     ub.schedule_deprecation(
        ...         'dummy_module', 'myfunc', 'function', 'do something else',
        ...         deprecate=True, error=1, remove=False)
        >>> # Test with No module
        >>> with pytest.warns(Warning):
        ...     ub.schedule_deprecation(
        ...         None, 'myfunc', 'function', 'do something else',
        ...         deprecate='now', error='soon', remove='soon', warncls=Warning)
        >>> # Test with No module
        >>> with pytest.warns(Warning):
        ...     ub.schedule_deprecation(
        ...         None, 'myfunc', 'function', 'do something else',
        ...         deprecate='now', error='2.0.0', remove='soon', warncls=Warning)
    """
    import sys
    import warnings

    from packaging.version import parse as Version

    if modname is not None:
        module = sys.modules[modname]
        current = Version(module.__version__)
    else:
        # TODO: use the inspect module to get the function / module this was
        # called from and fill in unspecified values.
        current = 'unknown'

    if warncls == 'default':
        warncls = DEFAULT_WARN_CLASS

    if modname is None:
        modname_str = ''
    else:
        modname_str = f'{modname} '

    def _handle_when(when, default):
        if when is None:
            is_now = default
            when_str = ''
        elif isinstance(when, str):
            if when in {'soon', 'now'}:
                when_str = ' {}{}'.format(modname_str, when)
                is_now = (when == 'now')
            else:
                when = Version(when)
                when_str = ' in {}{}'.format(modname_str, when)
                if current == 'unknown':
                    is_now = default
                else:
                    is_now = current >= when
        else:
            is_now = bool(when)
            when_str = ''
        return is_now, when_str

    deprecate_now, deprecate_str = _handle_when(deprecate, default=True)
    remove_now, remove_str = _handle_when(remove, default=False)
    error_now, error_str = _handle_when(error, default=False)

    # TODO: make the message more customizable.
    msg = (
        'The "{name}" {type} was deprecated{deprecate_str}, will cause '
        'an error{error_str} and will be removed{remove_str}. The current '
        '{modname_str}version is {current}. {migration}'
    ).format(**locals()).strip()
    if remove_now:
        raise AssertionError(
            'Forgot to remove deprecated: ' + msg + ' ' +
            'Remove the function, or extend the scheduled remove version.'
        )
    if error_now:
        raise RuntimeError(msg)

    if deprecate_now:
        warnings.warn(msg, warncls, stacklevel=1 + stacklevel)

    return msg
