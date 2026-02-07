"""
The ubelt.schedule_deprecation function is pretty useful, but it could be
generalized and would probably work better as a class.

As a design / UX goal we need to ensure:

    1. There is a concise way of getting minimal behavior where raise a
    deprecation warning when we go into a deprecated codepath.

    2. There is a way of controlling details in a readable way that is natural,
       expressive, but not burdensome.

Such a basic API might look like:

.. code:: python

    # Hacking
    import ubelt as ub
    import sys, os
    experiment_dpath = ub.Path('~/code/ubelt/dev/experimental').expand()
    sys.path.append(os.fspath(experiment_dpath))
    from better_deprecation import *  # NOQA

    Deprecation.schedule(
        '''
        This is marking a feature that is deprecated and the first positional
        argument gives the user nearly complete control over the message.
        By default the warning emits now.
        Perhaps some extra context is added by trying to introspect which
        module you are currently in.
        ''')


And perhaps the expressive API looks like

.. code:: python

    # Hacking
    import ubelt as ub
    import sys, os
    experiment_dpath = ub.Path('~/code/ubelt/dev/experimental').expand()
    sys.path.append(os.fspath(experiment_dpath))

    from better_deprecation import *  # NOQA

    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('ensure this prints for the test')

    import rich

    self = Deprecation(
        warn='1.1.0',
        error='1.2.0',
        remove='1.3.0',
        message='The foobar is deprecated.',
        migration=ub.paragraph(
            '''
            This text should explain the way to migrate to non-deprecated behavior.
            '''),
        warncls=DeprecationWarning,
        logger=logger,
        print=rich.print,
    )
    print(f'self.__dict__ = {ub.urepr(self.__dict__, nl=1)}')

    def foo():
        self.emit()
    foo()

We should also have a decorator API:

.. code:: python

    # Hacking
    import ubelt as ub
    import sys, os
    experiment_dpath = ub.Path('~/code/ubelt/dev/experimental').expand()
    sys.path.append(os.fspath(experiment_dpath))

    @Deprecation('', module_name='ubelt', print=True)
    def old_function():
        ...
    old_function()


What should the class be called?

* Deprecation?

* Deprecator?

* Deprecate?


"""


class Deprecation:
    """
    """

    def __init__(
        self,
        message=None,
        name=None,
        type=None,
        migration=None,
        deprecate='now',
        warn='soon',
        error='soon',
        remove='soon',
        module_name=None,
        module_version=None,
        logger=None,
        print=None,
        warncls=DeprecationWarning,
    ):
        self.message = message
        self.name = name
        self.type = type
        self.migration = migration
        self.deprecate = deprecate
        self.warn = warn
        self.error = error
        self.remove = remove
        self.module_name = module_name
        self.module_version = module_version
        self.warncls = warncls

        self.logger = logger

        if print is True:
            import builtins

            print = builtins.print

        self.print = print
        self.loud = False

        self._modname_str = None
        self._current_module_version = None
        self._deprecate_now = None
        self._remove_now = None
        self._error_now = None
        self._deprecate_str = None
        self._remove_str = None
        self._error_str = None
        self._full_message = None

    @classmethod
    def schedule(
        cls,
        message=None,
        name=None,
        type=None,
        migration=None,
        deprecate='now',
        error='soon',
        remove='soon',
        module_name=None,
        module_version=None,
        warncls=DeprecationWarning,
        stacklevel=1,
    ):
        """
        Concise classmethod to construct and emit the deprecation warning.
        """
        self = cls(
            message=message,
            name=name,
            type=type,
            migration=migration,
            deprecate=deprecate,
            error=error,
            remove=remove,
            module_name=module_name,
            module_version=module_version,
            warncls=warncls,
        )
        self.emit(stacklevel=1 + stacklevel)
        return self

    def _resolve_module_version(self):
        import sys

        from packaging.version import parse as Version

        if self.module_name is not None:
            module = sys.modules[self.module_name]
            self._current_module_version = Version(module.__version__)
        else:
            # TODO: use the inspect module to get the function / module this was
            # called from and fill in unspecified values.
            self._current_module_version = 'unknown'

        if self.module_name is None:
            self._modname_str = ''
        else:
            self._modname_str = f'{self.module_name} '

    def _handle_when(self, when, default):
        from packaging.version import parse as Version

        if when is None:
            is_now = default
            when_str = ''
        elif isinstance(when, str):
            if when in {'soon', 'now'}:
                when_str = ' {}{}'.format(self._modname_str, when)
                is_now = when == 'now'
            else:
                when = Version(when)
                when_str = ' in {}{}'.format(self._modname_str, when)
                if self._current_module_version == 'unknown':
                    is_now = default
                else:
                    is_now = self._current_module_version >= when
        else:
            is_now = bool(when)
            when_str = ''
        return is_now, when_str

    def _resolve_timeline(self):
        self._deprecate_now, self._deprecate_str = self._handle_when(
            self.deprecate, default=True
        )
        self._remove_now, self._remove_str = self._handle_when(
            self.remove, default=False
        )
        self._error_now, self._error_str = self._handle_when(self.error, default=False)

    def _build_full_message(self):
        self._resolve_module_version()
        self._resolve_timeline()

        parts = []
        if self.message:
            parts.append(self.message)

        if self.name is not None:
            _name = self.name or ""
            _type = self.type or ""
            what_str = f'The "{_name}" {_type}'
        else:
            what_str = 'This'

        parts.append(
            f'{what_str} was deprecated{self._deprecate_str}, will cause '
            f'an error{self._error_str} and will be removed{self._remove_str}. '
        )
        parts.append(
            f'The current {self._modname_str}version is {self._current_module_version}. '
        )
        if self.migration:
            parts.append(self.migration)

        # TODO: make the message more customizable.
        self._full_message = ' '.join(parts).strip()

    def emit(self, stacklevel=1):
        """
        Emit the deprecation message via the requested channels.
        """
        import warnings

        self._build_full_message()

        if self._remove_now:
            error_message = (
                'Forgot to remove deprecated: '
                + self._full_message
                + ' '
                + 'Remove the function, or extend the scheduled remove version.'
            )
            if self.logger is not None:
                self.logger.error(error_message, stacklevel=1 + stacklevel)
            if self.print:
                self.print(error_message)
            raise AssertionError(error_message)
        if self._error_now:
            if self.logger is not None:
                self.logger.error(self._full_message, stacklevel=1 + stacklevel)
            if self.print:
                self.print(self._full_message)
            raise RuntimeError(self._full_message)

        if self._deprecate_now:
            if self.logger is not None:
                self.logger.warn(self._full_message, stacklevel=1 + stacklevel)
            if self.print:
                self.print(self._full_message)
            warnings.warn(self._full_message, self.warncls, stacklevel=1 + stacklevel)
        return self

    def decorator(self, func):
        import functools

        if self.name is None:
            self.name = func.__name__

        if self.type is None:
            self.type = type(func).__name__

        @functools.wraps(func)
        def _deprecated_func(*args, **kwargs):
            self.emit()
            result = func(*args, **kwargs)
            return result

        _deprecated_func._deprecation = self
        return _deprecated_func

    def __call__(self, func):
        return self.decorator(func)
