# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ubelt as ub
import numpy as np
import itertools as it

from ubelt.util_hash import _hashable_sequence
hash_sequence = _hashable_sequence

def _benchmark():
    """
    On 64-bit processors sha512 may be faster than sha256

    References:
        https://crypto.stackexchange.com/questions/26336/sha512-faster-than-sha256
    """
    from ubelt.util_hash import _rectify_hasher
    result = ub.AutoOrderedDict()
    algos = ['sha1', 'sha256', 'sha512']
    for n in ub.ProgIter([1, 10, 100, 1000, 10000, 100000], desc='time'):
        # for key in hashlib.algorithms_guaranteed:
        for key in algos:
            hashtype = _rectify_hasher(key)
            t1 = ub.Timerit(100, bestof=10, label=key, verbose=0)
            for timer in t1:
                data = b'8' * n
                with timer:
                    hasher = hashtype()
                    hasher.update(data)
            result[key][n] = t1.min()
    import pandas as pd
    print(pd.DataFrame(result))

    result = ub.AutoOrderedDict()
    for n in ub.ProgIter([1, 10, 100, 1000, 10000, 100000], desc='time'):
        # for key in hashlib.algorithms_guaranteed:
        for key in algos:
            hashtype = _rectify_hasher(key)
            t1 = ub.Timerit(100, bestof=10, label=key, verbose=0)
            for timer in t1:
                data = b'8' * n
                hasher = hashtype()
                hasher.update(data)
                with timer:
                    hasher.hexdigest()
            result[key][n] = t1.min()
    import pandas as pd
    print(pd.DataFrame(result))
    """
    CommandLine:
        python -m test_hash _benchmark

    Example:
        >>> # DISABLE_DOCTEST
        >>> from test_hash import *  # NOQA
        >>> result = _benchmark()
        >>> print(result)
    %timeit hashlib.sha256().update(b'8' * 1000)
    3.62 µs per loop
    %timeit hashlib.sha512().update(b'8' * 1000)
    2.5 µs per loop

    %timeit hashlib.sha256().update(b'8' * 1)
    318 ns
    %timeit hashlib.sha512().update(b'8' * 1)
    342 ns

    %timeit hashlib.sha256().update(b'8' * 100000)
    306 µs
    %timeit hashlib.sha512().update(b'8' * 100000)
    213 µs
    """


def test_hash_data():
    counter = [0]
    failed = []
    def check_hash(want, input_):
        count = counter[0] = counter[0] + 1
        got = ub.hash_data(input_)
        # assert got.startswith(want), 'want={}, got={}'.format(want, got)
        print('check_hash({!r}, {!r})'.format(got, input_))
        if want is not None and not got.startswith(want):
            item = (got, input_, count, want)
            failed.append(item)

    check_hash('egexcbwgdtmjrzafljtjwqpgfhmfetjs', '1')
    check_hash('hjvebphzylxgtxncyphclsjglvmstsbq', ['1'])
    check_hash('hjvebphzylxgtxncyphclsjglvmstsbq', tuple(['1']))
    check_hash('ftzqivzayzivmobwymodjnnzzxzrvvjz', b'12')
    check_hash('jiwjkgkffldfoysfqblsemzkailyridf', [b'1', b'2'])
    check_hash('foevisahdffoxfasicvyklrmuuwqnfcc', ['1', '2', '3'])
    check_hash('qasnkfhlewxsgsocddkybvvkxttdmzqn', ['1', np.array([1, 2, 3], dtype=np.int64), '3'])
    check_hash('lxssoxdkstvccsyqaybaokehclyctgmn', '123')
    check_hash('ektrgalbjkljglbwhqosfovyefmsadkd', zip([1, 2, 3], [4, 5, 6]))

    print(ub.repr2(failed, nl=1))
    assert len(failed) == 0


def test_numpy_object_array():
    """
    _HASHABLE_EXTENSIONS = ub.util_hash._HASHABLE_EXTENSIONS
    """
    # An object array should have the same repr as a list of a tuple of data
    data = np.array([1, 2, 3], dtype=object)
    objhash = ub.hash_data(data)
    assert ub.hash_data([1, 2, 3]) == objhash
    assert ub.hash_data((1, 2, 3)) == objhash

    # Ensure this works when the object array is nested
    data = [np.array([1, 2, 3], dtype=object)]
    objhash = ub.hash_data(data)
    assert ub.hash_data([[1, 2, 3]]) == objhash
    assert ub.hash_data([(1, 2, 3)]) == objhash
    assert ub.hash_data(([1, 2, 3],)) == objhash


def test_ndarray_int_object_convert():
    data_list = [[1, 2, 3], [4, 5, 6]]

    data = np.array(data_list, dtype=np.int64)

    s1 = b''.join(hash_sequence(data.astype(object)))
    s2 = b''.join(hash_sequence(data_list))
    s3 = b''.join(hash_sequence(data.tolist()))
    s4 = b''.join(hash_sequence(data.astype(np.uint8).astype(object)))

    assert s1 == s4
    assert s2 == s4
    assert s3 == s4


def test_ndarray_zeros():
    data = np.zeros((3, 3), dtype=np.int64)
    hashid = ub.hash_data(data)
    assert hashid != ub.hash_data(data.ravel()), (
        'shape should influence data')
    assert hashid != ub.hash_data(data.astype(np.float32))
    assert hashid != ub.hash_data(data.astype(np.int32))
    assert hashid != ub.hash_data(data.astype(np.int8))


def test_nesting():
    assert hash_sequence([1, 1, 1]) != hash_sequence([[1], 1, 1])
    assert hash_sequence([[1], 1]) != hash_sequence([[1, 1]])
    assert hash_sequence([1, [1]]) != hash_sequence([[1, 1]])
    assert hash_sequence([[[1]]]) != hash_sequence([[1]])


def test_numpy_int():
    assert hash_sequence(np.int8(3)) == hash_sequence(3)
    assert hash_sequence(np.int16(3)) == hash_sequence(3)
    assert hash_sequence(np.int32(3)) == hash_sequence(3)
    assert hash_sequence(np.int64(3)) == hash_sequence(3)
    assert hash_sequence(np.uint8(3)) == hash_sequence(3)
    assert hash_sequence(np.uint16(3)) == hash_sequence(3)
    assert hash_sequence(np.uint32(3)) == hash_sequence(3)
    assert hash_sequence(np.uint64(3)) == hash_sequence(3)


def test_numpy_float():
    assert hash_sequence(np.float16(3.0)) == hash_sequence(3.0)
    assert hash_sequence(np.float32(3.0)) == hash_sequence(3.0)
    assert hash_sequence(np.float64(3.0)) == hash_sequence(3.0)
    try:
        assert hash_sequence(np.float128(3.0)) == hash_sequence(3.0)
    except AttributeError:
        pass


def test_numpy_random_state():
    data = np.random.RandomState(0)
    assert ub.hash_data(data).startswith('ckukrhjsraipjyrwddcvqsvvmuuxztld')
    # hash_sequence(data)


def test_uuid():
    import uuid
    data = uuid.UUID('12345678-1234-1234-1234-123456789abc')
    sequence = b''.join(hash_sequence(data))
    assert sequence == b'UUID\x124Vx\x124\x124\x124\x124Vx\x9a\xbc'
    assert ub.hash_data(data).startswith('nkklelnjzqbi')
    assert ub.hash_data(data.bytes) != ub.hash_data(data), (
        'the fact that it is a UUID should reflect in the hash')


def test_hash_data_custom_alphabet():
    data = 1
    # A larger alphabet means the string can be shorter
    hashid_26 = ub.hash_data(data, alphabet='default')
    assert len(hashid_26) == 109
    assert hashid_26.startswith('lejivmqndqzp')
    hashid_16 = ub.hash_data(data, alphabet='hex')
    assert hashid_16.startswith('8bf2a1f4dbea6e59e5c2ec4077498c44')
    assert len(hashid_16) == 128
    # Binary should have len 512 because the default hasher is sha512
    hashid_2 = ub.hash_data(data, alphabet=['0', '1'])
    assert len(hashid_2) == 512
    assert hashid_2.startswith('10001011111100101010000111110100')


def test_hash_file():
    from os.path import join
    fpath = join(ub.ensure_app_cache_dir('ubelt'), 'tmp.txt')
    ub.writeto(fpath, 'foobar')
    hashid1_a = ub.hash_file(fpath, hasher='sha512', hashlen=8, stride=1, blocksize=1)
    hashid2_a = ub.hash_file(fpath, hasher='sha512', hashlen=8, stride=2, blocksize=1)

    hashid1_b = ub.hash_file(fpath, hasher='sha512', hashlen=8, stride=1, blocksize=10)
    hashid2_b = ub.hash_file(fpath, hasher='sha512', hashlen=8, stride=2, blocksize=10)

    assert hashid1_a == hashid1_b
    assert hashid2_a != hashid2_b, 'blocksize matters when stride is > 1'
    assert hashid1_a != hashid2_a


def test_convert_base_hex():
    from ubelt.util_hash import _convert_hexstr_base, _ALPHABET_16
    # Test that hex values are unchanged
    for i in it.chain(range(-10, 10), range(-1000, 1000, 7)):
        text = hex(i).replace('0x', '')
        assert _convert_hexstr_base(text, _ALPHABET_16) == text, (
            'should not change hex')


def test_convert_base_decimal():
    from ubelt.util_hash import _convert_hexstr_base
    alphabet_10 = list(map(str, range(10)))
    # Test that decimal values agree with python conversion
    for i in it.chain(range(-10, 10), range(-1000, 1000, 7)):
        text_16 = hex(i).replace('0x', '')
        text_10 = _convert_hexstr_base(text_16, alphabet_10)
        assert int(text_16, 16) == int(text_10, 10)


def test_convert_base_simple():
    from ubelt.util_hash import _convert_hexstr_base, _ALPHABET_16
    # Quick one-of tests
    assert _convert_hexstr_base('aaa0111', _ALPHABET_16) == 'aaa0111'

    assert _convert_hexstr_base('aaa0111', list('01')) == '1010101010100000000100010001'
    assert _convert_hexstr_base('aaa0111', list('012')) == '110110122202020220'
    assert _convert_hexstr_base('aaa0111', list('0123')) == '22222200010101'

    alphabet_10 = list(map(str, range(10)))
    assert _convert_hexstr_base('aaa0111', alphabet_10) == '178913553'


def test_no_prefix():
    full = b''.join(_hashable_sequence(1, use_prefix=True))
    part = b''.join(_hashable_sequence(1, use_prefix=False))
    assert full == b'INT\x00\x00\x00\x01'
    assert part == b'\x00\x00\x00\x01'


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_hash.py
        pytest ~/code/ubelt/ubelt/tests/test_hash.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
