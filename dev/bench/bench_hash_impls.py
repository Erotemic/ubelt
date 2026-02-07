"""
Check iterative versus recursive implementation of hash_data
"""

from xdev import profile

from ubelt import NoParam
from ubelt.util_hash import (
    _HASHABLE_EXTENSIONS,
    _digest_hasher,
    _int_to_bytes,
    _rectify_base,
    _rectify_hasher,
)

_SEP = b'_,_'
_ITER_PREFIX = b'_[_'
_ITER_SUFFIX = b'_]_'


@profile
def _convert_to_hashable(data, types=True, extensions=None):
    r"""
    Converts ``data`` into a hashable byte representation if an appropriate
    hashing function is known.
    """
    # HANDLE MOST COMMON TYPES FIRST
    if data is None:
        hashable = b'NONE'
        prefix = b'NULL'
    elif isinstance(data, bytes):
        hashable = data
        prefix = b'TXT'
    elif isinstance(data, str):
        # convert unicode into bytes
        hashable = data.encode('utf-8')
        prefix = b'TXT'
    elif isinstance(data, int):
        # warnings.warn('Hashing ints is slow, numpy is preferred')
        hashable = _int_to_bytes(data)
        # hashable = data.to_bytes(8, byteorder='big')
        prefix = b'INT'
    elif isinstance(data, float):
        data_ = float(data)  # convert to a base-float
        try:
            a, b = data_.as_integer_ratio()
        except (ValueError, OverflowError):
            hashable = str(data_).encode('utf-8')  # handle and nan, inf
        else:
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


@profile
def _update_hasher_recursive(hasher, data, types=True, extensions=None):
    """
    Converts ``data`` into a byte representation and calls update on the hasher
    :class:`hashlib._hashlib.HASH` algorithm.

    Args:
        hasher (Hasher): instance of a hashlib algorithm
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash
        extensions (HashableExtensions | None): overrides global extensions

    Example:
        >>> hasher = hashlib.sha512()
        >>> data = [1, 2, ['a', 2, 'c']]
        >>> _update_hasher_recursive(hasher, data)
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
        # Multiple structure bytes make it harder to accidentally introduce
        # conflicts, but this is not perfect.
        # SEP = b'_,_'
        # ITER_PREFIX = b'_[_'
        # ITER_SUFFIX = b'_]_'

        iter_ = iter(data)
        hasher.update(_ITER_PREFIX)
        # first, try to nest quickly without recursive calls
        # (this works if all data in the sequence is a non-iterable)
        try:
            for item in iter_:
                prefix, hashable = _convert_to_hashable(item, types,
                                                        extensions=extensions)
                binary_data = prefix + hashable + _SEP
                hasher.update(binary_data)
            hasher.update(_ITER_SUFFIX)
        except TypeError:
            # need to use recursive calls
            # Update based on current item
            _update_hasher_recursive(hasher, item, types, extensions=extensions)
            # !>> WHOOPS: THIS IS A BUG. THERE SHOULD BE A
            # !>> hasher.update(_SEP)
            # !>> SEPARATOR HERE.
            # !>> BUT FIXING IT WILL BREAK BACKWARDS COMPAT.
            # !>> We will need to expose versions of the hasher that can be
            # configured, and ideally new versions will have speed improvements.
            for item in iter_:
                # Ensure the items have a spacer between them
                _update_hasher_recursive(hasher, item, types, extensions=extensions)
                hasher.update(_SEP)
            hasher.update(_ITER_SUFFIX)
    else:
        prefix, hashable = _convert_to_hashable(data, types,
                                                extensions=extensions)
        binary_data = prefix + hashable
        hasher.update(binary_data)


# EXPERIMENTAL VARIANT to attempt to speedup update_hasher
@profile
def _update_hasher_iterative(hasher, data, types=True, extensions=None):
    """
    Converts ``data`` into a byte representation and calls update on the hasher
    :class:`hashlib._hashlib.HASH` algorithm.

    Args:
        hasher (Hasher): instance of a hashlib algorithm
        data (object): ordered data with structure
        types (bool): include type prefixes in the hash
        extensions (HashableExtensions | None): overrides global extensions

    Example:
        >>> hasher = hashlib.sha512()
        >>> data = [1, 2, ['a', 2, 'c']]
        >>> _update_hasher_iterative(hasher, data)
        >>> print(hasher.hexdigest()[0:8])
        e2c67675
    """
    if extensions is None:
        extensions = _HASHABLE_EXTENSIONS

    DAT_TYPE = 1
    SEP_TYPE = 2

    stack = [(DAT_TYPE, data)]

    while stack:
        _type, data = stack.pop()
        if _type is SEP_TYPE:
            hasher.update(data)
            continue

        # Determine if the data should be hashed directly or iterated through
        if isinstance(data, (tuple, list, zip)):
            needs_iteration = True
        else:
            needs_iteration = any(check(data) for check in
                                  extensions.iterable_checks)

        if needs_iteration:
            # Denote that we are hashing over an iterable
            # Multiple structure bytes make it harder to accidentally introduce
            # conflicts, but this is not perfect.

            iter_ = iter(data)
            hasher.update(_ITER_PREFIX)
            # first, try to nest quickly without recursive calls
            # (this works if all data in the sequence is a non-iterable)
            try:
                for item in iter_:
                    prefix, hashable = _convert_to_hashable(item, types,
                                                            extensions=extensions)
                    binary_data = prefix + hashable + _SEP
                    hasher.update(binary_data)
                hasher.update(_ITER_SUFFIX)
            except TypeError:
                # need to recurse into the iterable.
                stack.append((SEP_TYPE, _ITER_SUFFIX))
                for subitem in reversed(list(iter_)):
                    stack.append((SEP_TYPE, _SEP))
                    stack.append((DAT_TYPE, subitem))
                # BUG: should have a _SEP here.
                # !>> WHOOPS: THIS IS A BUG. THERE SHOULD BE A
                # !>> hasher.update(_SEP)
                # !>> SEPARATOR HERE.
                # !>> BUT FIXING IT WILL BREAK BACKWARDS COMPAT.
                # !>> We will need to expose versions of the hasher that can be
                stack.append((DAT_TYPE, item))
        else:
            prefix, hashable = _convert_to_hashable(data, types,
                                                    extensions=extensions)
            binary_data = prefix + hashable
            hasher.update(binary_data)


@profile
def hash_data_iterative(data, hasher=NoParam, base=NoParam, types=False,
                        convert=False, extensions=None):
    """
    """
    if convert and not isinstance(data, str):  # nocover
        import json
        try:
            data = json.dumps(data)
        except TypeError:
            # import warnings
            # warnings.warn('Unable to encode input as json due to: {!r}'.format(ex))
            pass

    base = _rectify_base(base)
    hasher = _rectify_hasher(hasher)()
    # Feed the data into the hasher
    _update_hasher_iterative(hasher, data, types=types, extensions=extensions)
    # Get the hashed representation
    text = _digest_hasher(hasher, base)
    return text


@profile
def hash_data_recursive(data, hasher=NoParam, base=NoParam, types=False,
                        convert=False, extensions=None):
    """
    """
    if convert and not isinstance(data, str):  # nocover
        import json
        try:
            data = json.dumps(data)
        except TypeError:
            # import warnings
            # warnings.warn('Unable to encode input as json due to: {!r}'.format(ex))
            pass

    base = _rectify_base(base)
    hasher = _rectify_hasher(hasher)()
    # Feed the data into the hasher
    _update_hasher_recursive(hasher, data, types=types, extensions=extensions)
    # Get the hashed representation
    text = _digest_hasher(hasher, base)
    return text


def main():
    import random
    import string

    import numpy as np
    np_data = np.empty((1, 1))
    data = [1, 2, ['a', 2, 'c'], [1] * 100, [[[], np_data]], {'a': [1, 2, [3, 4, [5, 6]]]}]

    def make_nested_data(leaf_width=10, branch_width=10, depth=0):
        data = {}
        for i in range(leaf_width):
            key = ''.join(random.choices(string.printable, k=16))
            value = ''.join(random.choices(string.printable, k=16))
            data[key] = value

        if depth > 0:
            for i in range(branch_width):
                key = ''.join(random.choices(string.printable, k=16))
                value = make_nested_data(
                    leaf_width=leaf_width, branch_width=branch_width, depth=depth - 1)
                data[key] = value
        return data

    data = make_nested_data(leaf_width=10, branch_width=2, depth=8)

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)
    for timer in ti.reset('recursive'):
        with timer:
            result1 = hash_data_recursive(data)

    for timer in ti.reset('iterative'):
        with timer:
            result2 = hash_data_iterative(data)

    print(f'result1={result1}')
    print(f'result2={result2}')
    assert result1 == result2


if __name__ == '__main__':
    """
    CommandLine:
        XDEV_PROFILE=1 python ~/code/ubelt/dev/bench/bench_hash_impls.py
        python ~/code/ubelt/dev/bench/bench_hash_impls.py
    """
    main()
