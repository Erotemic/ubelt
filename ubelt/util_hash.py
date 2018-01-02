# -*- coding: utf-8 -*-
"""
Wrappers around hashlib functions to generate hash signatures for common data.

The hashes should be determenistic across platforms.

NOTE:
    The exact hashes generated for data object and files may change in the
    future and should not be relied on between versions. Eventually we plan to
    change this policy and gaurentee a stable hashing scheme across future
    versions.

TODO: Before we merge this... should we:
    [ ] Change default base to 16?
    [ ] Remove hashlen?
    [ ] How is the custom hashing scheme different or better than simply using
    pickle. Perhaps its not, and it should be using pickle.
        * Reason1: compatibility between python 2 and 3. We dont differentiate
        between bytes and unicode, whereas pickle would.
        * Reason2: safety: this will complain about unordered things such as
            dicts.
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import hashlib
import six
import uuid
from six.moves import zip

__all__ = ['hash_data', 'hash_file']

HASH_VERSION = 1  # incremented when we make a change that modifies hashes

_ALPHABET_16 = list('0123456789abcdef')

_ALPHABET_26 = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


_HASH_LEN = 32

if six.PY2:
    _stringlike = (basestring, bytes)  # NOQA
    _intlike = (int, long)  # NOQA
else:
    _stringlike = (str, bytes)  # NOQA
    _intlike = (int,)

# Default to 512 because it is often faster than 256 on 64bit systems:
# Reference: https://crypto.stackexchange.com/questions/26336/faster
DEFAULT_HASHER = hashlib.sha512


if six.PY2:
    import codecs
    def _py2_to_bytes(int_, length, byteorder='big'):
        h = '%x' % int_
        s = ('0' * (len(h) % 2) + h).zfill(length * 2).decode('hex')
        bytes_ =  s if byteorder == 'big' else s[::-1]
        return bytes_

    def _int_to_bytes(int_):
        length = max(4, int_.bit_length())
        bytes_ = _py2_to_bytes(int_, length, 'big')
        return bytes_

    def _bytes_to_int(bytes_):
        int_ = int(codecs.encode(bytes_, 'hex'), 16)
        return int_
else:
    codecs = None
    def _int_to_bytes(int_):
        r"""
        Converts an integer into its byte representation
        assumes int32 by default, but dynamically handles larger ints

        Example:
            >>> int_ = 1
            >>> assert _bytes_to_int((_int_to_bytes(int_))) == int_
            >>> assert _int_to_bytes(int_) == b'\x00\x00\x00\x01'
        """
        length = max(4, int_.bit_length())
        bytes_ = int_.to_bytes(length, byteorder='big')
        return bytes_

    def _bytes_to_int(bytes_):
        r"""
        Converts a string of bytes into its integer representation (big-endian)

        Example:
            >>> bytes_ = b'\x00\x00\x00\x01'
            >>> assert _int_to_bytes((_bytes_to_int(bytes_))) == bytes_
            >>> assert _bytes_to_int(bytes_) == 1
        """
        int_ = int.from_bytes(bytes_, 'big')
        return int_


def _rectify_hasher(hasher):
    """
    Convert a string-based key into a hasher class

    Example:
        >>> assert _rectify_hasher(None) is DEFAULT_HASHER
        >>> assert _rectify_hasher('sha1') is hashlib.sha1
        >>> assert _rectify_hasher('sha256') is hashlib.sha256
        >>> assert _rectify_hasher('sha512') is hashlib.sha512
        >>> assert _rectify_hasher('md5') is hashlib.md5
        >>> assert _rectify_hasher(hashlib.sha1) is hashlib.sha1
        >>> #assert _rectify_hasher(hashlib.sha1())
        >>> import pytest
        >>> assert pytest.raises(KeyError, _rectify_hasher, '42')
        >>> #assert pytest.raises(TypeError, _rectify_hasher, object)
    """
    if hasher is None:
        hasher = DEFAULT_HASHER
    elif isinstance(hasher, six.string_types):
        if hasher not in hashlib.algorithms_available:
            raise KeyError('unknown hasher: {}'.format(hasher))
        else:
            hasher = getattr(hashlib, hasher)
    return hasher


def _rectify_alphabet(alphabet):
    """
    Example:
        >>> assert _rectify_alphabet(None) is _ALPHABET_26
        >>> assert _rectify_alphabet(['1', '2']) == ['1', '2']
    """
    if alphabet is None:
        return _ALPHABET_26
    else:
        return alphabet


def _rectify_hashlen(hashlen):
    """
    Example:
        >>> assert _rectify_hashlen(None) is _HASH_LEN
        >>> assert _rectify_hashlen(8) == 8
    """
    if hashlen is None:
        return _HASH_LEN
    else:
        return hashlen


class HashableExtensions():
    """
    Singleton helper class for managing non-builtin (e.g. numpy) hash types
    """
    def __init__(self):
        self.keyed_extensions = {}
        self.iterable_checks = []

    def register(self, hash_types):
        # ensure iterable
        if not isinstance(hash_types, (list, tuple)):
            hash_types = [hash_types]
        def _wrap(hash_func):
            for hash_type in hash_types:
                key = (hash_type.__module__, hash_type.__name__)
                self.keyed_extensions[key] = (hash_type, hash_func)
                # self.extensions.append((hash_type, hash_func))
            return hash_func
        return _wrap

    def add_iterable_check(self, func):
        """
        Registers a function that detects when a type is iterable
        """
        self.iterable_checks.append(func)
        return func

    def lookup(self, data):
        """
        Returns an appropriate function to hash `data` if one has been
        registered.

        Raises:
            TypeError : if data has no registered hash methods

        Example:
            >>> self = HashableExtensions()
            >>> self._register_numpy_extensions()
            >>> self._register_builtin_class_extensions()

            >>> data = np.array([1, 2, 3])
            >>> self.lookup(data[0])

            >>> class Foo(object):
            >>>     def __init__(f):
            >>>         f.attr = 1
            >>> data = Foo()
            >>> import pytest
            >>> assert pytest.raises(TypeError, self.lookup, data)

            >>> # If ub.hash_data doesnt support your object,
            >>> # then you can register it.
            >>> @self.register(Foo)
            >>> def _hashfoo(data):
            >>>     return b'FOO', data.attr
            >>> func = self.lookup(data)
            >>> assert func(data)[1] == 1

            >>> data = uuid.uuid4()
            >>> self.lookup(data)
        """
        # Maybe try using functools.singledispatch instead?
        # First try fast O(1) lookup
        query_hash_type = data.__class__
        key = (query_hash_type.__module__, query_hash_type.__name__)
        try:
            hash_type, hash_func = self.keyed_extensions[key]
        except KeyError:
            raise TypeError('No registered hash func for hashable type=%r' % (
                    query_hash_type))
        return hash_func

    def _register_numpy_extensions(self):
        """
        Numpy extensions are builtin
        """
        # system checks
        numpy_floating_types = (np.float16, np.float32, np.float64)
        if hasattr(np, 'float128'):  # nocover
            numpy_floating_types = numpy_floating_types + (np.float128,)

        @self.add_iterable_check
        def is_object_ndarray(data):
            # ndarrays of objects cannot be hashed directly.
            return isinstance(data, np.ndarray) and data.dtype.kind == 'O'

        @self.register(np.ndarray)
        def hash_numpy_array(data):
            """
            Example:
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
                header = b''.join(_hashable_sequence((len(data.shape), data.shape)))
                dtype = b''.join(_hashable_sequence(data.dtype.descr))
                hashable = header + dtype + data.tobytes()
            prefix = b'NDARR'
            return prefix, hashable

        @self.register((np.int64, np.int32, np.int16, np.int8) +
                       (np.uint64, np.uint32, np.uint16, np.uint8))
        def _hash_numpy_int(data):
            return _convert_to_hashable(int(data))

        @self.register(numpy_floating_types)
        def _hash_numpy_float(data):
            return _convert_to_hashable(float(data))

        @self.register(np.random.RandomState)
        def _hash_numpy_random_state(data):
            """
            Example:
                >>> rng = np.random.RandomState(0)
                >>> _hashable_sequence(rng, types=True)
            """
            ver, ints, pos, has_gauss, cached = data.get_state()
            hashable = b''.join(_hashable_sequence(data.get_state()))
            # hashable = (_convert_to_hashable(ver)[1] +
            #             _convert_to_hashable(ints)[1] +
            #             _convert_to_hashable(pos)[1] +
            #             _convert_to_hashable(has_gauss)[1] +
            #             _convert_to_hashable(cached)[1])
            prefix = b'RNG'
            return prefix, hashable

    def _register_builtin_class_extensions(self):
        """
        Register hashing extensions for a selection of classes included in
        python stdlib.
        """
        @self.register(uuid.UUID)
        def _hash_uuid(data):
            hashable = data.bytes
            prefix = b'UUID'
            return prefix, hashable

_HASHABLE_EXTENSIONS = HashableExtensions()


try:
    import numpy as np
    _HASHABLE_EXTENSIONS._register_numpy_extensions()
except ImportError:  # nocover
    pass

_HASHABLE_EXTENSIONS._register_builtin_class_extensions()


def _hashable_sequence(data, types=True):
    """
    Extracts the sequence of bytes that would be hashed by hash_data

    >>> data = [2, (3, 4)]
    >>> _hashable_sequence(data, types=False)
    >>> _hashable_sequence(data, types=True)
    """
    class HashTracer(object):
        def __init__(self):
            self.sequence = []
        def update(self, bytes):
            self.sequence.append(bytes)
    hasher = HashTracer()
    _update_hasher(hasher, data, types=types)
    return hasher.sequence


def _convert_to_hashable(data, types=True):
    r"""
    Converts `data` into a hashable byte representation if an appropriate
    hashing function is known.

    Args:
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash

    Returns:
        tuple(bytes, bytes): prefix, hashable:
            a prefix hinting the original data type and the byte representation
            of `data`.

    Raises:
        TypeError : if data has no registered hash methods

    Example:
        >>> assert _convert_to_hashable(None) == (b'NULL', b'NONE')
        >>> assert _convert_to_hashable('string') == (b'TXT', b'string')
        >>> assert _convert_to_hashable(1) == (b'INT', b'\x00\x00\x00\x01')
        >>> assert _convert_to_hashable(1.0) == (b'FLT', b'\x00\x00\x00\x01/\x00\x00\x00\x01')
        >>> assert _convert_to_hashable(_intlike[-1](1)) == (b'INT', b'\x00\x00\x00\x01')
    """
    # HANDLE MOST COMMON TYPES FIRST
    if data is None:
        hashable = b'NONE'
        prefix = b'NULL'
    elif isinstance(data, six.binary_type):
        hashable = data
        prefix = b'TXT'
    elif isinstance(data, six.text_type):
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
        # hashable = repr(data).encode('utf8')
        # prefix = b'FLT'
    else:
        # Then dynamically look up any other type
        hash_func = _HASHABLE_EXTENSIONS.lookup(data)
        prefix, hashable = hash_func(data)
    if types:
        return prefix, hashable
    else:
        return b'', hashable


def _update_hasher(hasher, data, types=True):
    """
    Converts `data` into a byte representation and calls update on the hasher
    `hashlib.HASH` algorithm.

    Args:
        hasher (HASH): instance of a hashlib algorithm
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash

    Example:
        >>> hasher = hashlib.sha512()
        >>> data = [1, 2, ['a', 2, 'c']]
        >>> _update_hasher(hasher, data)
        >>> print(hasher.hexdigest()[0:8])
        2ba8d82b
    """
    # Determine if the data should be hashed directly or iterated through
    if isinstance(data, (tuple, list, zip)):
        needs_iteration = True
    else:
        needs_iteration = any(check(data) for check in
                              _HASHABLE_EXTENSIONS.iterable_checks)

    if needs_iteration:
        # Denote that we are hashing over an iterable
        # SEP = b'SEP'
        # ITER_PREFIX = b'ITER'
        # SEP = b','
        # ITER_PREFIX = b'['
        # ITER_SUFFIX = b']'
        # Multiple structure bytes makes it harder accidently make conflicts
        SEP = b'_,_'
        ITER_PREFIX = b'_[_'
        ITER_SUFFIX = b'_]_'

        iter_ = iter(data)
        hasher.update(ITER_PREFIX)
        # first, try to nest quickly without recursive calls
        # (this works if all data in the sequence is a non-iterable)
        try:
            for item in iter_:
                prefix, hashable = _convert_to_hashable(item, types)
                binary_data = prefix + hashable + SEP
                hasher.update(binary_data)
        except TypeError:
            # need to use recursive calls
            # Update based on current item
            _update_hasher(hasher, item, types)
            for item in iter_:
                # Ensure the items have a spacer between them
                _update_hasher(hasher, item, types)
                hasher.update(SEP)
        hasher.update(ITER_SUFFIX)
    else:
        prefix, hashable = _convert_to_hashable(data, types)
        binary_data = prefix + hashable
        hasher.update(binary_data)


def _convert_hexstr_base(hexstr, alphabet):
    r"""
    Packs a long hexstr into a shorter length string with a larger base.

    Args:
        hexstr (str): string of hexidecimal symbols to convert
        alphabet (list): symbols of the conversion base

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
        >>> consts = dict(hexbase=16, hexlen=256, bigbase=27)
        >>> symbols = sy.symbols('hexbase, hexlen, bigbase, newlen')
        >>> haexbase, hexlen, bigbase, newlen = symbols
        >>> eqn = sy.Eq(16 ** hexlen,  bigbase ** newlen)
        >>> newlen_ans = sy.solve(eqn, newlen)[0].subs(consts).evalf()
        >>> print('newlen_ans = %r' % (newlen_ans,))
        >>> # for a 27 char alphabet we can get 216
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
    bigbase = len(alphabet)
    x = int(hexstr, 16)  # first convert to base 16
    if x == 0:
        return '0'
    sign = 1 if x > 0 else -1
    x *= sign
    digits = []
    while x:
        digits.append(alphabet[x % bigbase])
        x //= bigbase
    if sign < 0:
        digits.append('-')
    digits.reverse()
    newbase_str = ''.join(digits)
    return newbase_str


def hash_data(data, hasher=None, hashlen=None, alphabet=None):
    r"""
    Get a unique hash depending on the state of the data.

    Args:
        data (object): any sort of loosely organized data
        hashlen (None): maximum number of symbols in the returned hash.
        alphabet (list): alphabet of symbols. If not specified uses base 26.
        hasher (HASH): hash algorithm from hashlib, if None uses
            `DEFAULT_HASHER`.

    Returns:
        str: text -  hash string

    Example:
        >>> print(hash_data([1, 2, (3, '4')], hashlen=8, hasher='sha512'))
        frqkjbsq
    """
    alphabet = _rectify_alphabet(alphabet)
    hashlen = _rectify_hashlen(hashlen)
    hasher = _rectify_hasher(hasher)()
    # Feed the data into the hasher
    _update_hasher(hasher, data)
    # Get a 128 character hex string
    hex_text = hasher.hexdigest()
    if alphabet == 'hex':
        base_text = hex_text
    else:
        # Shorten length of string (by increasing base)
        base_text = _convert_hexstr_base(hex_text, alphabet)
    # Truncate
    text = base_text[:hashlen]
    return text


def hash_file(fpath, blocksize=65536, stride=1, hasher=None, hashlen=None,
              alphabet=None):
    r"""
    Hashes the data in a file on disk.

    Args:
        fpath (str):  file path string
        blocksize (int): 2 ** 16. Affects speed of reading file
        hasher (None):  defaults to sha1 for fast (but non-robust) hashing
        stride (int): strides > 1 skip data to hash, useful for faster
                      hashing, but less accurate, also makes hash dependant on
                      blocksize.

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
        >>> print(ub.hash_file(fpath, hasher='sha512', hashlen=8))
        vkiodmcj
    """
    alphabet = _rectify_alphabet(alphabet)
    hashlen = _rectify_hashlen(hashlen)
    hasher = _rectify_hasher(hasher)()
    with open(fpath, 'rb') as file:
        buf = file.read(blocksize)
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
        hexid = hasher.hexdigest()
        hashid = _convert_hexstr_base(hexid, alphabet)[:hashlen]
        return hashid

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_hash all
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
