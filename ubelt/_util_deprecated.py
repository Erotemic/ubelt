"""
This file contains functions to be deprecated, but are still accessible.
"""
import warnings

# __all__ = []


DEP_SCHEDULE_1 = dict(deprecate='0.9.6', remove='1.0.0')


def schedule_deprecation(deprecate=None, error=None, remove=None):  # nocover
    """
    Deprecation machinery to help provide users with a smoother transition
    """
    import ubelt as ub
    from distutils.version import LooseVersion
    current = LooseVersion(ub.__version__)
    deprecate = None if deprecate is None else LooseVersion(deprecate)
    remove = None if remove is None else LooseVersion(remove)
    error = None if error is None else LooseVersion(error)

    if deprecate is None or current >= deprecate:
        import inspect
        prev_frame = inspect.currentframe().f_back
        # the_class = prev_frame.f_locals["self"].__class__
        caller = prev_frame.f_code.co_name
        # the_method = prev_frame.f_code.co_name
        # stack = inspect.stack()
        # the_class = stack[1][0].f_locals["self"].__class__.__name__
        # the_method = stack[1][0].f_code.co_name
        # caller = str(str(inspect.currentframe())).split(' ')[-1][:-1]
        msg = ub.paragraph(
            '''
            The "{caller}" function was deprecated in {deprecate}, will cause
            an error in {error} and will be removed in {remove}. The current
            version is {current}.
            ''').format(**locals())
        if remove is not None and current >= remove:
            raise AssertionError('forgot to remove a deprecated function')
        if error is not None and current >= error:
            raise DeprecationWarning(msg)
        else:
            warnings.warn(msg, DeprecationWarning)


def schedule_deprecation2(migration='', name='?', type='?', deprecate=None, error=None, remove=None):  # nocover
    """
    Deprecation machinery to help provide users with a smoother transition.

    New version for kwargs, todo: rectify with function version
    """
    import ubelt as ub
    from distutils.version import LooseVersion
    current = LooseVersion(ub.__version__)
    deprecate = None if deprecate is None else LooseVersion(deprecate)
    remove = None if remove is None else LooseVersion(remove)
    error = None if error is None else LooseVersion(error)
    if deprecate is None or current >= deprecate:
        if migration is None:
            migration = ''
        msg = ub.paragraph(
            '''
            The "{name}" {type} was deprecated in {deprecate}, will cause
            an error in {error} and will be removed in {remove}. The current
            version is {current}. {migration}
            ''').format(**locals()).strip()
        if remove is not None and current >= remove:
            raise AssertionError('forgot to remove a deprecated function')
        if error is not None and current >= error:
            raise DeprecationWarning(msg)
        else:
            # print(msg)
            warnings.warn(msg, DeprecationWarning)


# DEPRECATED:
# put dep functions here
