"""
This module defines the :class:`NiceRepr` mixin class, which defines a
``__repr__`` and ``__str__`` method that only depend on a custom ``__nice__``
method, which you must define. This means you only have to overload one
function instead of two.  Furthermore, if the object defines a ``__len__``
method, then the ``__nice__`` method defaults to something sensible, otherwise
it is treated as abstract and raises ``NotImplementedError``.

To use simply have your object inherit from :class:`NiceRepr`
(multi-inheritance should be ok).

Example:
    >>> # Objects that define __nice__ have a default __str__ and __repr__
    >>> import ubelt as ub
    >>> class Student(ub.NiceRepr):
    ...    def __init__(self, name):
    ...        self.name = name
    ...    def __nice__(self):
    ...        return self.name
    >>> s1 = Student('Alice')
    >>> s2 = Student('Bob')
    >>> # The __str__ representation looks nice
    >>> print('s1 = {}'.format(s1))
    >>> print('s2 = {}'.format(s2))
    s1 = <Student(Alice)>
    s2 = <Student(Bob)>
    >>> # xdoctest: +IGNORE_WANT
    >>> # The __repr__ representation also looks nice
    >>> print('s1 = {!r}'.format(s1))
    >>> print('s2 = {!r}'.format(s2))
    s1 = <Student(Alice) at 0x7f2c5460aad0>
    s2 = <Student(Bob) at 0x7f2c5460ad10>


Example:
    >>> # Objects that define __len__ have a default __nice__
    >>> import ubelt as ub
    >>> class Group(ub.NiceRepr):
    ...    def __init__(self, data):
    ...        self.data = data
    ...    def __len__(self):
    ...        return len(self.data)
    >>> g = Group([1, 2, 3])
    >>> print('g = {}'.format(g))
    g = <Group(3)>

"""
import warnings


class NiceRepr(object):
    """
    Inherit from this class and define ``__nice__`` to "nicely" print your
    objects.

    Defines ``__str__`` and ``__repr__`` in terms of ``__nice__`` function
    Classes that inherit from :class:`NiceRepr` should redefine ``__nice__``.
    If the inheriting class has a ``__len__``, method then the default
    ``__nice__`` method will return its length.

    Example:
        >>> import ubelt as ub
        >>> class Foo(ub.NiceRepr):
        ...    def __nice__(self):
        ...        return 'info'
        >>> foo = Foo()
        >>> assert str(foo) == '<Foo(info)>'
        >>> assert repr(foo).startswith('<Foo(info) at ')

    Example:
        >>> import ubelt as ub
        >>> class Bar(ub.NiceRepr):
        ...    pass
        >>> bar = Bar()
        >>> import pytest
        >>> with pytest.warns(RuntimeWarning) as record:
        >>>     assert 'object at' in str(bar)
        >>>     assert 'object at' in repr(bar)

    Example:
        >>> import ubelt as ub
        >>> class Baz(ub.NiceRepr):
        ...    def __len__(self):
        ...        return 5
        >>> baz = Baz()
        >>> assert str(baz) == '<Baz(5)>'

    Example:
        >>> import ubelt as ub
        >>> # If your nice message has a bug, it shouldn't bring down the house
        >>> class Foo(ub.NiceRepr):
        ...    def __nice__(self):
        ...        assert False
        >>> foo = Foo()
        >>> import pytest
        >>> with pytest.warns(RuntimeWarning) as record:
        >>>     print('foo = {!r}'.format(foo))
        foo = <...Foo ...>

    Example:
        >>> import ubelt as ub
        >>> class Animal(ub.NiceRepr):
        ...    def __init__(self):
        ...        ...
        ...    def __nice__(self):
        ...        return ''
        >>> class Cat(Animal):
        >>>     ...
        >>> class Dog(Animal):
        >>>     ...
        >>> class Beagle(Dog):
        >>>     ...
        >>> class Ragdoll(Cat):
        >>>     ...
        >>> instances = [Animal(), Cat(), Dog(), Beagle(), Ragdoll()]
        >>> for inst in instances:
        >>>     print(str(inst))
        <Animal()>
        <Cat()>
        <Dog()>
        <Beagle()>
        <Ragdoll()>
    """

    def __nice__(self):
        if hasattr(self, '__len__'):
            # It is a common pattern for objects to use __len__ in __nice__
            # As a convenience we define a default __nice__ for these objects
            return str(len(self))
        else:
            # In all other cases force the subclass to overload __nice__
            raise NotImplementedError(
                'Define the __nice__ method for {!r}'.format(self.__class__))

    def __repr__(self):
        try:
            nice = self.__nice__()
            classname = self.__class__.__name__
            return '<{0}({1}) at {2}>'.format(classname, nice, hex(id(self)))
        except Exception as ex:
            warnings.warn(str(ex), category=RuntimeWarning)
            return object.__repr__(self)

    def __str__(self):
        try:
            classname = self.__class__.__name__
            nice = self.__nice__()
            return '<{0}({1})>'.format(classname, nice)
        except Exception as ex:
            warnings.warn(str(ex), category=RuntimeWarning)
            return object.__repr__(self)
