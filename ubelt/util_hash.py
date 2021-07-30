# -*- coding: utf-8 -*-
r"""
Wrappers around hashlib functions to generate hash signatures for common data.

The hashes are deterministic across python versions and operating systems.
This is verified by CI testing on Windows, Linux, Python with 2.7, 3.4, and
greater, and on 32 and 64 bit versions.

Use Case #1: You have data that you want to hash. If we assume the data is in
standard python scalars or ordered sequences: e.g.  tuple, list, odict, oset,
int, str, etc..., then the solution is `:func:hash_data`.

Use Case #2: You have a file you want to hash, but your system doesn't have a
sha1sum executable (or you dont want to use Popen). The solution is
`:func:hash_file`

The :func:`ub.hash_data` function recursively hashes most builtin python data
structures.

The :func:`ub.hash_file` function hashes data on disk.  Both of the
aformentioned functions have options for different hashers and alphabets.


Example:
    >>> import ubelt as ub
    >>> data = ub.odict(sorted({
    >>>     'param1': True,
    >>>     'param2': 0,
    >>>     'param3': [None],
    >>>     'param4': ('str', 4.2),
    >>> }.items()))
    >>> # hash_data can hash any ordered builtin object
    >>> ub.hash_data(data, convert=False, hasher='sha512')
    2ff39d0ecbf6ecc740ca7d...

Example:
    >>> import ubelt as ub
    >>> from os.path import join
    >>> fpath = ub.touch(join(ub.ensure_app_cache_dir('ubelt'), 'empty_file'))
    >>> ub.hash_file(fpath, hasher='sha1')
    da39a3ee5e6b4b0d3255bfef95601890afd80709

NOTE:
    The exact hashes generated for data object and files may change in the
    future. When this happens the ``HASH_VERSION`` attribute will be incremented.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import hashlib
import sys
import math
from collections import OrderedDict
# from typing import List, Callable, Type, Dict  # NOQA
# we will use NoParam instead of None because None is a valid hashlen setting
from ubelt.util_const import NoParam

__all__ = ['hash_data', 'hash_file']

HASH_VERSION = 2  # incremented when we make a change that modifies hashes

_ALPHABET_10 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

_ALPHABET_16 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'a', 'b', 'c', 'd', 'e', 'f']

_ALPHABET_26 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z']

_ALPHABET_36 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z']

DEFAULT_ALPHABET = _ALPHABET_16

PY2 = sys.version_info[0] == 2

if PY2:
    import six
    from six.moves import zip
    b = six.b
    string_types = six.string_types
    binary_type = six.binary_type
    text_type = six.text_type
    _stringlike = (basestring, bytes)  # NOQA
    _intlike = (int, long)  # NOQA
else:
    # zip = zip  # hack for editor
    six = None
    def b(s):
        return s.encode("latin-1")
    binary_type = bytes
    text_type = str
    string_types = (str,)
    _stringlike = (str, bytes)  # NOQA
    _intlike = (int,)

# Sensible choices for default hashers are sha1, sha512, and xxh64.

# xxhash.xxh64 is very fast, but non-crypto-grade and not in the standard lib
# Reference: http://cyan4973.github.io/xxHash/
# Reference: https://github.com/Cyan4973/xxHash

# We dont default to sha1 because it has a known collision and other issues
# Reference: https://stackoverflow.com/questions/28159071/more-modern-sha
# Reference: https://security.googleblog.com/2017/02/announcing-first-sha1-collision.html

# Default to 512 because it is often faster than 256 on 64bit systems:
# Reference: https://crypto.stackexchange.com/questions/26336/faster

# DEFAULT_HASHER = xxhash.xxh32
# DEFAULT_HASHER = xxhash.xxh64  # xxh64 is the fastest, but non-standard
# DEFAULT_HASHER = hashlib.sha1  # fast algo, but has a known collision
DEFAULT_HASHER = hashlib.sha512  # most robust algo, but slower than others


if PY2:
    import codecs
    # HASH = type(hashlib.sha1())  # python2 doesn't expose the hash type

    def _py2_to_bytes(int_, length, byteorder='big', signed=True):
        """
        Args:
            length (int) : number of bytes (not bits)

        References:
            https://bugs.python.org/issue16580
        """
        # convert nbytes to nbits
        bit_width = length * 8
        if int_ < 0:
            complement = (1 << bit_width) + int_
        else:
            complement = int_
        h = '%x' % complement
        p = ('0' * (len(h) % 2) + h).zfill(length * 2)
        s = p.decode('hex')
        bytes_ = s if byteorder == 'big' else s[::-1]
        return bytes_

    def _int_to_bytes(int_):
        bit_length = int_.bit_length() + 1
        length = int(math.ceil(bit_length / 8.0))  # bytelength
        bytes_ = _py2_to_bytes(int_, length, byteorder='big', signed=True)
        return bytes_

    def _bytes_to_int(bytes_):
        nbytes = len(bytes_)
        nbits = nbytes * 8
        comp = int(codecs.encode(bytes_, 'hex'), 16)
        if comp > 1 << (nbits - 1):
            int_ = comp - (1 << (nbits))
        else:
            int_ = comp
        return int_
else:
    # try:
    #     HASH = hashlib._hashlib.HASH
    # except AttributeError:  # nocover
    #     # Python seems to have been compiled without OpenSSL
    #     HASH = None

    codecs = None
    def _int_to_bytes(int_):
        r"""
        Converts an integer into its byte representation
        assumes int32 by default, but dynamically handles larger ints

        Example:
            >>> from ubelt.util_hash import _int_to_bytes, _bytes_to_int
            >>> int_ = 1
            >>> assert _bytes_to_int((_int_to_bytes(int_))) == int_
            >>> assert _int_to_bytes(int_) == b'\x01'
            >>> assert _bytes_to_int((_int_to_bytes(0))) == 0
            >>> assert _bytes_to_int((_int_to_bytes(-1))) == -1
            >>> assert _bytes_to_int((_int_to_bytes(-1000000))) == -1000000
            >>> assert _bytes_to_int((_int_to_bytes(1000000))) == 1000000
        """
        bit_length = int_.bit_length() + 1
        length = math.ceil(bit_length / 8.0)  # bytelength
        bytes_ = int_.to_bytes(length, byteorder='big', signed=True)
        return bytes_

    def _bytes_to_int(bytes_):
        r"""
        Converts a string of bytes into its integer representation (big-endian)

        Example:
            >>> bytes_ = b'\x01'
            >>> assert _int_to_bytes((_bytes_to_int(bytes_))) == bytes_
            >>> assert _bytes_to_int(bytes_) == 1
        """
        int_ = int.from_bytes(bytes_, 'big', signed=True)
        return int_


class _Hashers(object):
    """
    We offer hashers beyond what is available in hashlib.
    This class is used to lazy load them.
    """
    def __init__(self):
        self.algos = {}
        self._lazy_queue = [
            self._register_xxhash,
            self._register_blake3,
            self._register_hashlib,
        ]

    def _evaluate_registration_queue(self):
        for func in self._lazy_queue:
            try:
                func()
            except ImportError:  # nocover
                pass
        self._lazy_queue = []

    def __contains__(self, key):  # nocover
        if self._lazy_queue:
            self._evaluate_registration_queue()
        return key in self.algos

    def _register_xxhash(self):  # nocover
        import xxhash
        self.algos['xxh32'] = xxhash.xxh32
        self.algos['xx32'] = xxhash.xxh32
        self.algos['xxh64'] = xxhash.xxh64
        self.algos['xx64'] = xxhash.xxh64
        self.algos['xxhash'] = xxhash.xxh32

    def _register_blake3(self):  # nocover
        import blake3
        self.algos['blake3'] = blake3.blake3
        self.algos['b3'] = blake3.blake3

    def _register_hashlib(self):
        guaranteed = set(hashlib.algorithms_guaranteed)
        for key in guaranteed:  # nocover
            self.algos[key] = getattr(hashlib, key)

        if 0:  # nocover
            # Do we want to expose these hash algos?
            available = set(hashlib.algorithms_available)
            extra = available - guaranteed
            for key in extra:
                self.algos[key] = hashlib.new(key)

    def lookup(self, hasher):
        if hasher is NoParam or hasher == 'default':
            hasher = DEFAULT_HASHER
        elif hasattr(hasher, 'hexdigest'):
            # HASH is not None and isinstance(hasher, HASH):
            # by default the result of this function is a class we will make an
            # instance of, if we already have an instance, wrap it in a
            # callable so the external syntax does not need to change.
            return lambda: hasher
        else:
            # Ensure lazy registration functions have been executed
            if self._lazy_queue:
                self._evaluate_registration_queue()

            if isinstance(hasher, string_types):
                if hasher in self.algos:  # pragma: no cover
                    return self.algos[hasher]
                else:
                    raise KeyError('unknown hasher: {}'.format(hasher))
        return hasher

_HASHERS = _Hashers()


def _rectify_hasher(hasher):
    """
    Convert a string-based key into a hasher class

    Notes:
        In terms of speed on 64bit systems, sha1 is the fastest followed by md5
        and sha512. The slowest algorithm is sha256. If xxhash is installed
        the fastest algorithm is xxh64.

    Example:
        >>> assert _rectify_hasher(NoParam) is DEFAULT_HASHER
        >>> assert _rectify_hasher('sha1') is hashlib.sha1
        >>> assert _rectify_hasher('sha256') is hashlib.sha256
        >>> assert _rectify_hasher('sha512') is hashlib.sha512
        >>> assert _rectify_hasher('md5') is hashlib.md5
        >>> assert _rectify_hasher(hashlib.sha1) is hashlib.sha1
        >>> #if HASH is not None:
        >>> assert _rectify_hasher(hashlib.sha1())().name == 'sha1'
        >>> import pytest
        >>> assert pytest.raises(KeyError, _rectify_hasher, '42')
        >>> #assert pytest.raises(TypeError, _rectify_hasher, object)
        >>> if 'xxh32' in _HASHERS:
        >>>     import xxhash
        >>>     assert _rectify_hasher('xxh64') is xxhash.xxh64
        >>>     assert _rectify_hasher('xxh32') is xxhash.xxh32
        >>> if 'blake3' in _HASHERS:
        >>>     import blake3
        >>>     assert _rectify_hasher('blake3') is blake3.blake3
        >>> if 'whirlpool' in _HASHERS:
        >>>     assert _rectify_hasher('whirlpool') is blake3.blake3
    """
    # Keeping this function for backwards compatability (even though its not
    # part of the public API)
    return _HASHERS.lookup(hasher)


def _rectify_base(base):
    """
    transforms base shorthand into the full list representation

    Example:
        >>> assert _rectify_base(NoParam) is DEFAULT_ALPHABET
        >>> assert _rectify_base('hex') is _ALPHABET_16
        >>> assert _rectify_base('abc') is _ALPHABET_26
        >>> assert _rectify_base('alphanum') is _ALPHABET_36
        >>> assert _rectify_base(10) is _ALPHABET_10
        >>> assert _rectify_base(['1', '2']) == ['1', '2']
        >>> import pytest
        >>> assert pytest.raises(TypeError, _rectify_base, 'uselist')
    """
    if base is NoParam or base == 'default':
        return DEFAULT_ALPHABET
    elif base in [36, 'abc123', 'alphanum']:
        return _ALPHABET_36
    elif base in [26, 'abc', 'alpha']:
        return _ALPHABET_26
    elif base in [16, 'hex']:
        return _ALPHABET_16
    elif base in [10, 'dec']:
        return _ALPHABET_10
    else:
        if not isinstance(base, (list, tuple)):
            raise TypeError(
                'Argument `base` must be a key, list, or tuple; not {}'.format(
                    type(base)))
        return base


def _rectify_hashlen(hashlen):  # nocover
    """
    Example:
        >>> assert _rectify_hashlen(NoParam) is None
        >>> assert _rectify_hashlen(8) == 8
    """
    if hashlen is NoParam:
        return None
    else:  # nocover
        import warnings
        warnings.warn('Specifying hashlen is deprecated and will be removed. '
                      'Use slice syntax instead', DeprecationWarning)
        if hashlen == 'default':  # nocover
            return None
        else:
            return hashlen


class HashableExtensions(object):
    """
    Helper class for managing non-primitive (e.g. numpy) hash types

    Note:
        We are introducing experimental functionality where custom instances of
        this class can be created and passed as arguments to hash_data.
    """
    def __init__(self):
        self.keyed_extensions = {}
        self.iterable_checks = []
        self._lazy_queue = []         # type: List[Callable]

    def register(self, hash_types):
        """
        Registers a function to generate a hash for data of the appropriate
        types. This can be used to register custom classes. Internally this is
        used to define how to hash non-builtin objects like ndarrays and uuids.

        The registered function should return a tuple of bytes. First a small
        prefix hinting at the data type, and second the raw bytes that can be
        hashed.

        Args:
            hash_types (type | Tuple[type]):

        Returns:
            func: closure to be used as the decorator

        Example:
            >>> import ubelt as ub
            >>> import pytest
            >>> class MyType(object):
            ...     def __init__(self, id):
            ...         self.id = id
            >>> data = MyType(1)
            >>> # Custom types wont work with ub.hash_data by default
            >>> with pytest.raises(TypeError):
            ...     ub.hash_data(data)
            >>> # To handle custom types, you can create custom extensions
            >>> # and pass them to hash_data explicitly.
            >>> extensions = ub.util_hash.HashableExtensions()
            >>> @extensions.register(MyType)
            >>> def hash_my_type(data):
            ...     return b'mytype', b(ub.hash_data(data.id))
            >>> my_instance = MyType(1)
            >>> ub.hash_data(my_instance, extensions=extensions)

        Example:
            >>> # xdoctest: +SKIP
            >>> # Skip this doctest because we dont want tests to modify
            >>> # the global state.
            >>> import ubelt as ub
            >>> import pytest
            >>> class MyType(object):
            ...     def __init__(self, id):
            ...         self.id = id
            >>> data = MyType(1)
            >>> # Custom types wont work with ub.hash_data by default
            >>> with pytest.raises(TypeError):
            ...     ub.hash_data(data)
            >>> # You can register your functions with ubelt's internal
            >>> # hashable_extension registry.
            >>> @ub.util_hash._HASHABLE_EXTENSIONS.register(MyType)
            >>> def hash_my_type(data):
            ...     return b'mytype', b(ub.hash_data(data.id))
            >>> my_instance = MyType(1)
            >>> ub.hash_data(my_instance)
        """
        # ensure iterable
        if not isinstance(hash_types, (list, tuple)):
            hash_types = [hash_types]
        def _decor_closure(hash_func):
            for hash_type in hash_types:
                key = (hash_type.__module__, hash_type.__name__)
                self.keyed_extensions[key] = (hash_type, hash_func)
            return hash_func
        return _decor_closure

    def add_iterable_check(self, func):
        """
        Registers a function that detects when a type is iterable
        """
        self.iterable_checks.append(func)
        return func

    def lookup(self, data):
        """
        Returns an appropriate function to hash ``data`` if one has been
        registered.

        Raises:
            TypeError : if data has no registered hash methods

        Example:
            >>> import ubelt as ub
            >>> import pytest
            >>> if not ub.modname_to_modpath('numpy'):
            ...     raise pytest.skip('numpy is optional')
            >>> self = HashableExtensions()
            >>> self._register_numpy_extensions()
            >>> self._register_builtin_class_extensions()

            >>> import numpy as np
            >>> data = np.array([1, 2, 3])
            >>> self.lookup(data[0])

            >>> class Foo(object):
            >>>     def __init__(f):
            >>>         f.attr = 1
            >>> data = Foo()
            >>> assert pytest.raises(TypeError, self.lookup, data)

            >>> # If ub.hash_data doesnt support your object,
            >>> # then you can register it.
            >>> @self.register(Foo)
            >>> def _hashfoo(data):
            >>>     return b'FOO', data.attr
            >>> func = self.lookup(data)
            >>> assert func(data)[1] == 1

            >>> import uuid
            >>> data = uuid.uuid4()
            >>> self.lookup(data)
        """
        # Evaluate the lazy queue if anything is in it
        if self._lazy_queue:
            for func in self._lazy_queue:
                func()
            self._lazy_queue = []

        # Maybe try using functools.singledispatch instead?
        # First try O(1) lookup
        query_hash_type = data.__class__
        key = (query_hash_type.__module__, query_hash_type.__name__)
        try:
            hash_type, hash_func = self.keyed_extensions[key]
        except KeyError:
            # if issubclass(query_hash_type, dict):
            #     # TODO: In Python 3.7+ dicts are ordered by default, so
            #     # perhaps we should allow hashing them by default
            #     import warnings
            #     warnings.warn(
            #         'It looks like you are trying to hash an unordered dict. '
            #         'By default this is not allowed, but if you REALLY need '
            #         'to do this, then call '
            #         'ubelt.util_hash._HASHABLE_EXTENSIONS._register_agressive_extensions() '
            #         'beforehand')
            raise TypeError(
                'No registered hash func for hashable type={!r}'.format(
                    query_hash_type))
        return hash_func

    def _register_numpy_extensions(self):
        """
        Registers custom functions to hash numpy data structures.

        By default ubelt enables numpy extensions
        """
        # system checks
        import numpy as np
        numpy_floating_types = (np.float16, np.float32, np.float64)
        if hasattr(np, 'float128'):  # nocover
            numpy_floating_types = numpy_floating_types + (np.float128,)

        @self.add_iterable_check
        def is_object_ndarray(data):
            # ndarrays of objects cannot be hashed directly.
            return isinstance(data, np.ndarray) and data.dtype.kind == 'O'

        @self.register(np.ndarray)
        def _convert_numpy_array(data):
            """
            Example:
                >>> import ubelt as ub
                >>> if not ub.modname_to_modpath('numpy'):
                ...     raise pytest.skip()
                >>> import numpy as np
                >>> data_f32 = np.zeros((3, 3, 3), dtype=np.float64)
                >>> data_i64 = np.zeros((3, 3, 3), dtype=np.int64)
                >>> data_i32 = np.zeros((3, 3, 3), dtype=np.int32)
                >>> hash_f64 = _hashable_sequence(data_f32, types=True)
                >>> hash_i64 = _hashable_sequence(data_i64, types=True)
                >>> hash_i32 = _hashable_sequence(data_i64, types=True)
                >>> assert hash_i64 != hash_f64
                >>> assert hash_i64 != hash_i32
            """
            if data.dtype.kind == 'O':
                msg = 'directly hashing ndarrays with dtype=object is unstable'
                raise TypeError(msg)
            else:
                # tobytes() views the array in 1D (via ravel())
                # encode the shape as well
                header = b''.join(_hashable_sequence(
                    (len(data.shape), data.shape), extensions=self))
                dtype = b''.join(_hashable_sequence(data.dtype.descr,
                                                    extensions=self))
                hashable = header + dtype + data.tobytes()
            prefix = b'NDARR'
            return prefix, hashable

        @self.register((np.int64, np.int32, np.int16, np.int8,
                        np.uint64, np.uint32, np.uint16, np.uint8))
        def _convert_numpy_int(data):
            return _convert_to_hashable(int(data), extensions=self)

        @self.register(numpy_floating_types)
        def _convert_numpy_float(data):
            return _convert_to_hashable(float(data), extensions=self)

        @self.register(np.random.RandomState)
        def _convert_numpy_random_state(data):
            """
            Example:
                >>> import ubelt as ub
                >>> if not ub.modname_to_modpath('numpy'):
                ...     raise pytest.skip()
                >>> import numpy as np
                >>> rng = np.random.RandomState(0)
                >>> _hashable_sequence(rng, types=True)
            """
            hashable = b''.join(_hashable_sequence(data.get_state(),
                                                   extensions=self))
            prefix = b'RNG'
            return prefix, hashable

    def _register_builtin_class_extensions(self):
        """
        Register hashing extensions for a selection of classes included in
        python stdlib.

        This registers extensions for the following types:
            * uuid.UUID
            * collections.OrderedDict
            * dict (caveat: will be sorted, so must be sortable)

        CommandLine:
            xdoctest -m ubelt.util_hash HashableExtensions._register_builtin_class_extensions:0
            xdoctest -m ubelt.util_hash HashableExtensions._register_builtin_class_extensions:1

        Example:
            >>> import uuid
            >>> data = uuid.UUID('7e9d206b-dc02-4240-8bdb-fffe858121d0')
            >>> print(hash_data(data, base='abc', hasher='sha512', types=True)[0:8])
            cryarepd
            >>> data = OrderedDict([('a', 1), ('b', 2), ('c', [1, 2, 3]),
            >>>                     (4, OrderedDict())])
            >>> print(hash_data(data, base='abc', hasher='sha512', types=True)[0:8])
            qjspicvv

        Example:
            >>> # Ordered dictionaries are hashed differently that builtin dicts
            >>> import ubelt as ub
            >>> from collections import OrderedDict
            >>> datas = {}
            >>> datas['odict_data1'] = OrderedDict([
            >>>     ('4', OrderedDict()),
            >>>     ('a', 1),
            >>>     ('b', 2),
            >>>     ('c', [1, 2, 3]),
            >>> ])
            >>> datas['udict_data1'] = {
            >>>     '4': {},
            >>>     'a': 1,
            >>>     'b': 2,
            >>>     'c': [1, 2, 3],
            >>> }
            >>> datas['odict_data2'] = ub.dict_subset(datas['odict_data1'], ['a', '4', 'c', 'b'])
            >>> datas['udict_data2'] = ub.dict_isect(datas['udict_data1'], ['a', '4', 'c', 'b'])
            >>> datas['odict_data3'] = ub.dict_subset(datas['odict_data1'], ['c', 'b', 'a', '4'])
            >>> datas['udict_data3'] = ub.dict_isect(datas['udict_data1'], ['c', 'b', 'a', '4'])
            >>> # print('datas = {}'.format(ub.repr2(datas, nl=-1)))
            >>> for key, val in sorted(datas.items()):
            >>>     hashstr = ub.hash_data(val, base='abc', hasher='sha512', types=True)[0:8]
            >>>     print('{} = {}'.format(key, hashstr))
            odict_data1 = omnqalbe
            odict_data2 = tjrlsoel
            odict_data3 = cycowefz
            udict_data1 = bvshfmzm
            udict_data2 = bvshfmzm
            udict_data3 = bvshfmzm

        Example:
            >>> # Ordered dictionaries are hashed differently that builtin dicts
            >>> import ubelt as ub
            >>> import six
            >>> print(ub.hash_data({1, 2, 3})[0:8])
            >>> print(ub.hash_data({2, 3, 1})[0:8])
            36fb38a1
            36fb38a1
            >>> # xdoctest: +REQUIRES(PY3):
            >>> print(ub.hash_data({'2', 3, 1})[0:8])
            >>> print(ub.hash_data({3, 1, '2'})[0:8])
            742ae82d
            742ae82d
        """
        import uuid
        @self.register(uuid.UUID)
        def _convert_uuid(data):
            hashable = data.bytes
            prefix = b'UUID'
            return prefix, hashable

        @self.register(set)
        def _convert_set(data):
            try:
                # what raises a TypeError differs between Python 2 and 3
                ordered_ = sorted(data)
            except TypeError:
                import ubelt as ub
                data_ = list(data)
                sortx = ub.argsort(data_, key=str)
                ordered_ = [data_[k] for k in sortx]
            hashable = b''.join(_hashable_sequence(ordered_, extensions=self))
            prefix = b'SET'
            return prefix, hashable

        @self.register(dict)
        def _convert_dict(data):
            try:
                ordered_ = sorted(data.items())
                # what raises a TypeError differs between Python 2 and 3
            except TypeError:
                import ubelt as ub
                sortx = ub.argsort(data, key=str)
                ordered_ = [(k, data[k]) for k in sortx]
            hashable = b''.join(_hashable_sequence(ordered_, extensions=self))
            prefix = b'DICT'
            return prefix, hashable

        @self.register(OrderedDict)
        def _convert_ordered_dict(data):
            """
            Currently ordered dictionaries are considered separately from
            regular dictionaries. I'm not sure what the right thing to do is.
            """
            hashable = b''.join(_hashable_sequence(list(data.items()),
                                                   extensions=self))
            prefix = b'ODICT'
            return prefix, hashable

    def _register_agressive_extensions(self):  # nocover
        """
        Extensions that might be desired, but we do not enable them by default

        This registers extensions for the following types:
            * none right now *
        """
        pass

    def _register_torch_extensions(self):  # nocover
        """
        Experimental. Define a default hash function for torch tensors, but do
        not use it by default. Currently, the user must call this explicitly.
        """
        import torch
        @self.register(torch.Tensor)
        def _convert_torch_tensor(data):
            data_ = data.data.cpu().numpy()
            prefix = b'TORCH_TENSOR'
            return prefix, _convert_to_hashable(data_, extensions=self)[1]

_HASHABLE_EXTENSIONS = HashableExtensions()


def _lazy_init():
    """
    Delay the registration of any external libraries until a hashable extension
    is needed.
    """
    try:
        _HASHABLE_EXTENSIONS._register_builtin_class_extensions()
        _HASHABLE_EXTENSIONS._register_numpy_extensions()
    except ImportError:  # nocover
        pass


_HASHABLE_EXTENSIONS._lazy_queue.append(_lazy_init)


class _HashTracer(object):
    """ helper class to extract hashed sequences """

    def __init__(self):
        self.sequence = []

    def update(self, bytes):
        self.sequence.append(bytes)


def _hashable_sequence(data, types=True, extensions=None):
    r"""
    Extracts the sequence of bytes that would be hashed by hash_data

    Example:
        >>> data = [2, (3, 4)]
        >>> result1 = (b''.join(_hashable_sequence(data, types=False)))
        >>> result2 = (b''.join(_hashable_sequence(data, types=True)))
        >>> assert result1 == b'_[_\x02_,__[_\x03_,_\x04_,__]__]_'
        >>> assert result2 == b'_[_INT\x02_,__[_INT\x03_,_INT\x04_,__]__]_'
    """
    hasher = _HashTracer()
    _update_hasher(hasher, data, types=types, extensions=extensions)
    return hasher.sequence


def _convert_to_hashable(data, types=True, extensions=None):
    r"""
    Converts ``data`` into a hashable byte representation if an appropriate
    hashing function is known.

    Args:
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash

    Returns:
        Tuple[bytes, bytes]: prefix, hashable:
            a prefix hinting the original data type and the byte representation
            of ``data``.

    Raises:
        TypeError : if data has no registered hash methods

    Example:
        >>> assert _convert_to_hashable(None) == (b'NULL', b'NONE')
        >>> assert _convert_to_hashable('string') == (b'TXT', b'string')
        >>> assert _convert_to_hashable(1) == (b'INT', b'\x01')
        >>> assert _convert_to_hashable(1.0) == (b'FLT', b'\x01/\x01')
        >>> assert _convert_to_hashable(_intlike[-1](1)) == (b'INT', b'\x01')
        >>> import uuid
        >>> data = uuid.UUID('7e9d206b-dc02-4240-8bdb-fffe858121d0')
        >>> assert _convert_to_hashable(data) == (b'UUID', b'~\x9d k\xdc\x02B@\x8b\xdb\xff\xfe\x85\x81!\xd0')
    """
    # HANDLE MOST COMMON TYPES FIRST
    if data is None:
        hashable = b'NONE'
        prefix = b'NULL'
    elif isinstance(data, binary_type):
        hashable = data
        prefix = b'TXT'
    elif isinstance(data, text_type):
        # convert unicode into bytes
        hashable = data.encode('utf-8')
        prefix = b'TXT'
    elif isinstance(data, _intlike):
        # warnings.warn('Hashing ints is slow, numpy is prefered')
        hashable = _int_to_bytes(data)
        # hashable = data.to_bytes(8, byteorder='big')
        prefix = b'INT'
    elif isinstance(data, float):
        a, b = float(data).as_integer_ratio()
        hashable = _int_to_bytes(a) + b'/' +  _int_to_bytes(b)
        prefix = b'FLT'
    else:
        if extensions is None:
            extensions = _HASHABLE_EXTENSIONS
        # Then dynamically look up any other type
        hash_func = extensions.lookup(data)
        prefix, hashable = hash_func(data)
    if types:
        return prefix, hashable
    else:
        return b'', hashable


def _update_hasher(hasher, data, types=True, extensions=None):
    """
    Converts ``data`` into a byte representation and calls update on the hasher
    :class:`hashlib.HASH` algorithm.

    Args:
        hasher (hashlib.HASH): instance of a hashlib algorithm
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash

    Example:
        >>> hasher = hashlib.sha512()
        >>> data = [1, 2, ['a', 2, 'c']]
        >>> _update_hasher(hasher, data)
        >>> print(hasher.hexdigest()[0:8])
        e2c67675
    """
    if extensions is None:
        extensions = _HASHABLE_EXTENSIONS

    # Determine if the data should be hashed directly or iterated through
    if isinstance(data, (tuple, list, zip)):
        needs_iteration = True
    else:
        needs_iteration = any(check(data) for check in
                              extensions.iterable_checks)

    if needs_iteration:
        # Denote that we are hashing over an iterable
        # Multiple structure bytes makes it harder accidentally make conflicts
        SEP = b'_,_'
        ITER_PREFIX = b'_[_'
        ITER_SUFFIX = b'_]_'

        iter_ = iter(data)
        hasher.update(ITER_PREFIX)
        # first, try to nest quickly without recursive calls
        # (this works if all data in the sequence is a non-iterable)
        try:
            for item in iter_:
                prefix, hashable = _convert_to_hashable(item, types,
                                                        extensions=extensions)
                binary_data = prefix + hashable + SEP
                hasher.update(binary_data)
        except TypeError:
            # need to use recursive calls
            # Update based on current item
            _update_hasher(hasher, item, types, extensions=extensions)
            for item in iter_:
                # Ensure the items have a spacer between them
                _update_hasher(hasher, item, types, extensions=extensions)
                hasher.update(SEP)
        hasher.update(ITER_SUFFIX)
    else:
        prefix, hashable = _convert_to_hashable(data, types,
                                                extensions=extensions)
        binary_data = prefix + hashable
        hasher.update(binary_data)


def _convert_hexstr_base(hexstr, base):
    r"""
    Packs a long hexstr into a shorter length string with a larger base.

    Args:
        hexstr (str): string of hexidecimal symbols to convert
        base (list): symbols of the conversion base

    Example:
        >>> print(_convert_hexstr_base('ffffffff', _ALPHABET_26))
        nxmrlxv
        >>> print(_convert_hexstr_base('0', _ALPHABET_26))
        0
        >>> print(_convert_hexstr_base('-ffffffff', _ALPHABET_26))
        -nxmrlxv
        >>> print(_convert_hexstr_base('aafffff1', _ALPHABET_16))
        aafffff1

    Sympy:
        >>> import sympy as sy
        >>> # Determine the length savings with lossless conversion
        >>> consts = dict(hexbase=16, hexlen=256, baselen=27)
        >>> symbols = sy.symbols('hexbase, hexlen, baselen, newlen')
        >>> haexbase, hexlen, baselen, newlen = symbols
        >>> eqn = sy.Eq(16 ** hexlen,  baselen ** newlen)
        >>> newlen_ans = sy.solve(eqn, newlen)[0].subs(consts).evalf()
        >>> print('newlen_ans = %r' % (newlen_ans,))
        >>> # for a 26 char base we can get 216
        >>> print('Required length for lossless conversion len2 = %r' % (len2,))
        >>> def info(base, len):
        ...     bits = base ** len
        ...     print('base = %r' % (base,))
        ...     print('len = %r' % (len,))
        ...     print('bits = %r' % (bits,))
        >>> info(16, 256)
        >>> info(27, 16)
        >>> info(27, 64)
        >>> info(27, 216)
    """
    if base is _ALPHABET_16:
        # already in hex, no conversion needed
        return hexstr
    baselen = len(base)
    x = int(hexstr, 16)  # first convert to base 16
    if x == 0:
        return '0'  # bug: should be base[0]
    sign = 1 if x > 0 else -1
    x *= sign
    digits = []
    while x:
        digits.append(base[x % baselen])
        x //= baselen
    if sign < 0:
        digits.append('-')
    digits.reverse()
    newbase_str = ''.join(digits)
    return newbase_str


def _digest_hasher(hasher, hashlen, base):
    """ counterpart to _update_hasher """
    # Get a 128 character hex string
    hex_text = hasher.hexdigest()
    # Shorten length of string (by increasing base)
    base_text = _convert_hexstr_base(hex_text, base)
    # Truncate
    text = base_text[:hashlen]
    return text


def hash_data(data, hasher=NoParam, base=NoParam, types=False,
              hashlen=NoParam, convert=False, extensions=None):
    """
    Get a unique hash depending on the state of the data.

    Args:
        data (object):
            Any sort of loosely organized data

        hasher (str | hashlib.HASH, default='sha512'):
            string code or a hash algorithm from hashlib. Valid hashing
            algorithms are defined by ``hashlib.algorithms_guaranteed`` (e.g.
            'sha1', 'sha512', 'md5') as well as 'xxh32' and 'xxh64' if
            :mod:`xxhash` is installed.

        base (List[str] | str, default='hex'):
            list of symbols or shorthand key.
            Valid keys are 'abc', 'hex', and 'dec'.

        types (bool):
            If True data types are included in the hash, otherwise only the raw
            data is hashed. Defaults to False.

        hashlen (int):
            Maximum number of symbols in the returned hash. If not specified,
            all are returned.  DEPRECATED. Use slice syntax instead.

        convert (bool, default=True):
            if True, try and convert the data to json an the json is hashed
            instead. This can improve runtime in some instances, however the
            hash may differ from the case where convert=False.

        extensions (HashableExtensions):
            a custom :class:`HashableExtensions` instance that can overwrite or
            define how different types of objects are hashed.

    Notes:
        The types allowed are specified by the  HashableExtensions object. By
        default ubelt will register:

        OrderedDict, uuid.UUID, np.random.RandomState, np.int64, np.int32,
        np.int16, np.int8, np.uint64, np.uint32, np.uint16, np.uint8,
        np.float16, np.float32, np.float64, np.float128, np.ndarray, bytes,
        str, int, float, long (in python2), list, tuple, set, and dict

    Returns:
        str: text representing the hashed data

    Notes:
        The alphabet26 base is a pretty nice base, I recommend it.
        However we default to ``base='hex'`` because it is standard.
        You can try the alphabet26 base by setting ``base='abc'``.

    Example:
        >>> import ubelt as ub
        >>> print(ub.hash_data([1, 2, (3, '4')], convert=False))
        60b758587f599663931057e6ebdf185a...
        >>> print(ub.hash_data([1, 2, (3, '4')], base='abc',  hasher='sha512')[:32])
        hsrgqvfiuxvvhcdnypivhhthmrolkzej
    """
    if convert and not isinstance(data, string_types):  # nocover
        import json
        try:
            data = json.dumps(data)
        except TypeError:
            # import warnings
            # warnings.warn('Unable to encode input as json due to: {!r}'.format(ex))
            pass

    base = _rectify_base(base)
    hashlen = _rectify_hashlen(hashlen)
    hasher = _rectify_hasher(hasher)()
    # Feed the data into the hasher
    _update_hasher(hasher, data, types=types, extensions=extensions)
    # Get the hashed representation
    text = _digest_hasher(hasher, hashlen, base)
    return text


def hash_file(fpath, blocksize=1048576, stride=1, maxbytes=None, hasher=NoParam,
              hashlen=NoParam, base=NoParam):
    """
    Hashes the data in a file on disk.

    The results of this function agree with the standard UNIX commands (e.g.
    sha1sum, sha512sum, md5sum, etc...)

    Args:
        fpath (PathLike):
            location of the file to be hashed.

        blocksize (int, default=2 ** 20):
            Amount of data to read and hash at a time. There is a trade off and
            the optimal number will depend on specific hardware. This number
            was chosen to be optimal on a developer system. See
            "dev/bench_hash_file" for methodology to choose this number for
            your use case.

        stride (int, default=1):
            strides > 1 skip data to hash, useful for faster hashing, but less
            accurate, also makes hash dependant on blocksize.

        maxbytes (int | None):
            if specified, only hash the leading `maxbytes` of data in the file.

        hasher (str | hashlib.HASH, default='sha512'):
            string code or a hash algorithm from hashlib. Valid hashing
            algorithms are defined by ``hashlib.algorithms_guaranteed`` (e.g.
            'sha1', 'sha512', 'md5') as well as 'xxh32' and 'xxh64' if
            :mod:`xxhash` is installed.

            TODO: add logic such that you can update an existing hasher

        hashlen (int):
            maximum number of symbols in the returned hash. If not specified,
            all are returned. DEPRECATED. DO NOT USE.

        base (List[str] | str, default='hex'):
            list of symbols or shorthand key.
            Valid keys are 'abc', 'hex', and 'dec'.

    Notes:
        For better hashes keep stride = 1
        For faster hashes set stride > 1
        blocksize matters when stride > 1

    References:
        http://stackoverflow.com/questions/3431825/md5-checksum-of-a-file
        http://stackoverflow.com/questions/5001893/when-to-use-sha-1-vs-sha-2

    Example:
        >>> import ubelt as ub
        >>> from os.path import join
        >>> fpath = join(ub.ensure_app_cache_dir('ubelt'), 'tmp.txt')
        >>> ub.writeto(fpath, 'foobar')
        >>> print(ub.hash_file(fpath, hasher='sha1', base='hex'))
        8843d7f92416211de9ebb963ff4ce28125932878

    Example:
        >>> import ubelt as ub
        >>> from os.path import join
        >>> fpath = join(ub.ensure_app_cache_dir('ubelt'), 'tmp.txt')
        >>> ub.writeto(fpath, 'foobar')
        >>> print(ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=1000))
        8843d7f92416211de9ebb963ff4ce28125932878

        >>> # We have the ability to only hash at most ``maxbytes`` in a file
        >>> ub.writeto(fpath, 'abcdefghijklmnop')
        >>> h0 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=11, blocksize=3)
        >>> h1 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=32, blocksize=3)
        >>> h2 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=32, blocksize=32)
        >>> h3 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=16, blocksize=1)
        >>> h4 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=16, blocksize=18)
        >>> assert h1 == h2 == h3 == h4
        >>> assert h1 != h0

        >>> # Using a stride makes the result dependant on the blocksize
        >>> h0 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=11, blocksize=3, stride=2)
        >>> h1 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=32, blocksize=3, stride=2)
        >>> h2 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=32, blocksize=32, stride=2)
        >>> h3 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=16, blocksize=1, stride=2)
        >>> h4 = ub.hash_file(fpath, hasher='sha1', base='hex', maxbytes=16, blocksize=18, stride=2)
        >>> assert h1 != h2 != h3
        >>> assert h1 == h0
        >>> assert h2 == h4

    Example:
        >>> import ubelt as ub
        >>> from os.path import join
        >>> fpath = ub.touch(join(ub.ensure_app_cache_dir('ubelt'), 'empty_file'))
        >>> # Test that the output is the same as sha1sum
        >>> if ub.find_exe('sha1sum'):
        >>>     want = ub.cmd(['sha1sum', fpath], verbose=2)['out'].split(' ')[0]
        >>>     got = ub.hash_file(fpath, hasher='sha1')
        >>>     print('want = {!r}'.format(want))
        >>>     print('got = {!r}'.format(got))
        >>>     assert want.endswith(got)
        >>> # Do the same for sha512 sum and md5sum
        >>> if ub.find_exe('sha512sum'):
        >>>     want = ub.cmd(['sha512sum', fpath], verbose=2)['out'].split(' ')[0]
        >>>     got = ub.hash_file(fpath, hasher='sha512')
        >>>     print('want = {!r}'.format(want))
        >>>     print('got = {!r}'.format(got))
        >>>     assert want.endswith(got)
        >>> if ub.find_exe('md5sum'):
        >>>     want = ub.cmd(['md5sum', fpath], verbose=2)['out'].split(' ')[0]
        >>>     got = ub.hash_file(fpath, hasher='md5')
        >>>     print('want = {!r}'.format(want))
        >>>     print('got = {!r}'.format(got))
        >>>     assert want.endswith(got)
    """
    base = _rectify_base(base)
    hashlen = _rectify_hashlen(hashlen)
    hasher = _rectify_hasher(hasher)()
    with open(fpath, 'rb') as file:
        buf = file.read(blocksize)
        # We separate implementations for speed. Haven't benchmarked, but the
        # idea is to keep the inner loop extremely tight
        if maxbytes is None:
            if stride > 1:
                # skip blocks when stride is greater than 1
                while len(buf) > 0:
                    hasher.update(buf)
                    file.seek(blocksize * (stride - 1), 1)
                    buf = file.read(blocksize)
            else:
                # otherwise hash the entire file
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(blocksize)
        else:
            # In this case we hash at most ``maxbytes``
            maxremain = maxbytes
            if stride > 1:
                while len(buf) > 0 and maxremain > 0:
                    buf = buf[:maxremain]
                    maxremain -= len(buf)
                    hasher.update(buf)
                    if maxremain > 0:
                        file.seek(blocksize * (stride - 1), 1)
                        buf = file.read(blocksize)
            else:
                while len(buf) > 0 and maxremain > 0:
                    buf = buf[:maxremain]
                    maxremain -= len(buf)
                    hasher.update(buf)
                    if maxremain > 0:
                        buf = file.read(blocksize)

    # Get the hashed representation
    text = _digest_hasher(hasher, hashlen, base)
    return text
