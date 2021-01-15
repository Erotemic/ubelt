# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ubelt as ub
import itertools as it
import uuid
import pytest
from os.path import join
from ubelt.util_hash import _convert_hexstr_base, _ALPHABET_16
from ubelt.util_hash import _hashable_sequence
from ubelt.util_hash import _rectify_hasher
hash_sequence = _hashable_sequence


try:
    import numpy as np
except ImportError:
    np = None


def _benchmark():
    """
    On 64-bit processors sha512 may be faster than sha256

    References:
        https://crypto.stackexchange.com/questions/26336/sha512-faster-than-sha256
    """
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


def test_hash_data_with_types():
    if np is None:
        pytest.skip('requires numpy')
    counter = [0]
    failed = []
    def check_hash(want, input_):
        count = counter[0] = counter[0] + 1
        got = ub.hash_data(input_, hasher='sha512', base='abc', types=True)
        got = got[0:32]
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
    check_hash('foevisahdffoxfasicvyklrmuuwqnfcc', [b'1', b'2', b'3'])
    check_hash('foevisahdffoxfasicvyklrmuuwqnfcc', ['1', '2', '3'])
    check_hash('rkcnfxkjwkrfejhbpcpopmyubhbvonkt', ['1', np.array([1, 2, 3], dtype=np.int64), '3'])
    check_hash('lxssoxdkstvccsyqaybaokehclyctgmn', '123')
    check_hash('fpvptydigvgjimbzadztgpvjpqrevwcq', zip([1, 2, 3], [4, 5, 6]))

    print(ub.repr2(failed, nl=1))
    assert len(failed) == 0


def test_hash_data_without_types():
    if np is None:
        pytest.skip('requires numpy')
    counter = [0]
    failed = []
    def check_hash(want, input_):
        count = counter[0] = counter[0] + 1
        got = ub.hash_data(input_, hasher='sha1', base='hex', types=False)
        # assert got.startswith(want), 'want={}, got={}'.format(want, got)
        print('check_hash({!r}, {!r})'.format(got, input_))
        if want is not None and not got.startswith(want):
            item = (got, input_, count, want)
            failed.append(item)

    check_hash('356a192b7913b04c54574d18c28d46e6395428ab', '1')
    check_hash('d3bcc889aced30afd8e66ae45b310239d79be3df', ['1'])
    check_hash('d3bcc889aced30afd8e66ae45b310239d79be3df', ('1',))
    check_hash('7b52009b64fd0a2a49e6d8a939753077792b0554', b'12')
    check_hash('6bcab1cebcb44fc5c69faacc0ed661b19eff9fef', [b'1', b'2'])
    check_hash('d6d265a904bc7df97bd54a8c2ff4546e211c3cd8', [b'1', b'2', b'3'])
    check_hash('d6d265a904bc7df97bd54a8c2ff4546e211c3cd8', ['1', '2', '3'])
    check_hash('eff59c7c787bd223a680c9d625f54756be4fdf5b', ['1', np.array([1, 2, 3], dtype=np.int64), '3'])
    check_hash('40bd001563085fc35165329ea1ff5c5ecbdbbeef', '123')
    check_hash('1ba3c4e7f5af2a5f38d624047f422553ead2b5ae', zip([1, 2, 3], [4, 5, 6]))

    print(ub.repr2(failed, nl=1))
    assert len(failed) == 0


def test_numpy_object_array():
    """
    _HASHABLE_EXTENSIONS = ub.util_hash._HASHABLE_EXTENSIONS
    """
    if np is None:
        pytest.skip('requires numpy')
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
    if np is None:
        pytest.skip('requires numpy')
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
    if np is None:
        pytest.skip('requires numpy')
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
    if np is None:
        pytest.skip('requires numpy')
    assert hash_sequence(np.int8(3)) == hash_sequence(3)
    assert hash_sequence(np.int16(3)) == hash_sequence(3)
    assert hash_sequence(np.int32(3)) == hash_sequence(3)
    assert hash_sequence(np.int64(3)) == hash_sequence(3)
    assert hash_sequence(np.uint8(3)) == hash_sequence(3)
    assert hash_sequence(np.uint16(3)) == hash_sequence(3)
    assert hash_sequence(np.uint32(3)) == hash_sequence(3)
    assert hash_sequence(np.uint64(3)) == hash_sequence(3)


def test_numpy_float():
    if np is None:
        pytest.skip('requires numpy')
    assert hash_sequence(np.float16(3.0)) == hash_sequence(3.0)
    assert hash_sequence(np.float32(3.0)) == hash_sequence(3.0)
    assert hash_sequence(np.float64(3.0)) == hash_sequence(3.0)
    try:
        assert hash_sequence(np.float128(3.0)) == hash_sequence(3.0)
    except AttributeError:
        pass


def test_numpy_random_state():
    if np is None:
        pytest.skip('requires numpy')
    data = np.random.RandomState(0)
    # assert ub.hash_data(data).startswith('ujsidscotcycsqwnkxgbsxkcedplzvytmfmr')
    assert ub.hash_data(data, hasher='sha512', types=True, base='abc').startswith('snkngbxghabesvowzalqtvdvjtvslmxve')
    # _hashable_sequence(data)


def test_uuid():
    data = uuid.UUID('12345678-1234-1234-1234-123456789abc')
    sequence = b''.join(hash_sequence(data))
    assert sequence == b'UUID\x124Vx\x124\x124\x124\x124Vx\x9a\xbc'
    assert ub.hash_data(data, types=True, base='abc', hasher='sha512').startswith('nkklelnjzqbi')
    assert ub.hash_data(data.bytes, types=True) != ub.hash_data(data, types=True), (
        'the fact that it is a UUID should reflect in the hash')
    assert ub.hash_data(data.bytes, types=False) == ub.hash_data(data, types=False), (
        'the hash should be equal when ignoring types')


def test_hash_data_custom_base():
    data = 1
    # A larger base means the string can be shorter
    hashid_26 = ub.hash_data(data, base='abc', hasher='sha512', types=True)
    assert len(hashid_26) == 109
    # assert hashid_26.startswith('lejivmqndqzp')
    assert hashid_26.startswith('rfsmlqsjsuzllgp')
    hashid_16 = ub.hash_data(data, base='hex', hasher='sha512', types=True)
    # assert hashid_16.startswith('8bf2a1f4dbea6e59e5c2ec4077498c44')
    assert hashid_16.startswith('d7c9cea9373eb7ba20444ec65e0186b')

    assert len(hashid_16) == 128
    # Binary should have len 512 because the default hasher is sha512
    hashid_2 = ub.hash_data(data, base=['0', '1'], hasher='sha512', types=True)
    assert len(hashid_2) == 512
    assert hashid_2.startswith('110101111100100111001110101010010')


def test_hash_file():
    fpath = join(ub.ensure_app_cache_dir('ubelt'), 'tmp.txt')
    ub.writeto(fpath, 'foobar')
    hashid1_a = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=1)
    hashid2_a = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=1)

    hashid1_b = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=10)
    hashid2_b = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=10)

    assert hashid1_a == hashid1_b
    assert hashid2_a != hashid2_b, 'blocksize matters when stride is > 1'
    assert hashid1_a != hashid2_a

    hashid3_c = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=10, maxbytes=1000)
    assert hashid3_c == hashid2_b


def test_convert_base_hex():
    # Test that hex values are unchanged
    for i in it.chain(range(-10, 10), range(-1000, 1000, 7)):
        text = hex(i).replace('0x', '')
        assert _convert_hexstr_base(text, _ALPHABET_16) == text, (
            'should not change hex')


def test_convert_base_decimal():
    base_10 = list(map(str, range(10)))
    # Test that decimal values agree with python conversion
    for i in it.chain(range(-10, 10), range(-1000, 1000, 7)):
        text_16 = hex(i).replace('0x', '')
        text_10 = _convert_hexstr_base(text_16, base_10)
        assert int(text_16, 16) == int(text_10, 10)


def test_convert_base_simple():
    # Quick one-of tests
    assert _convert_hexstr_base('aaa0111', _ALPHABET_16) == 'aaa0111'

    assert _convert_hexstr_base('aaa0111', list('01')) == '1010101010100000000100010001'
    assert _convert_hexstr_base('aaa0111', list('012')) == '110110122202020220'
    assert _convert_hexstr_base('aaa0111', list('0123')) == '22222200010101'

    base_10 = list(map(str, range(10)))
    assert _convert_hexstr_base('aaa0111', base_10) == '178913553'


def test_no_prefix():
    full = b''.join(_hashable_sequence(1, types=True))
    part = b''.join(_hashable_sequence(1, types=False))
    # assert full == b'INT\x00\x00\x00\x01'
    # assert part == b'\x00\x00\x00\x01'
    assert full == b'INT\x01'
    assert part == b'\x01'


def _test_int_bytes():
    assert ub.util_hash._int_to_bytes(0) == b'\x00'
    assert ub.util_hash._int_to_bytes(1) == b'\x01'
    assert ub.util_hash._int_to_bytes(2) == b'\x02'
    assert ub.util_hash._int_to_bytes(-1) == b'\xff'
    assert ub.util_hash._int_to_bytes(-2) == b'\xfe'
    assert ub.util_hash._int_to_bytes(600) == b'\x02X'
    assert ub.util_hash._int_to_bytes(-600) == b'\xfd\xa8'
    assert ub.util_hash._int_to_bytes(2 ** 256) == b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert ub.util_hash._int_to_bytes(-2 ** 256) == b'\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


def _test_xxhash():
    try:
        import xxhash  # NOQA
    except ImportError:
        pass
    else:
        assert ub.hash_data('foo', hasher='xxh64') == '33bf00a859c4ba3f'


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_hash.py
        pytest ~/code/ubelt/ubelt/tests/test_hash.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
