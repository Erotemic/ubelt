import ubelt as ub
import numpy as np


def _benchmark():
    """
    On 64-bit processors sha512 may be faster than sha256
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

    References:
        https://crypto.stackexchange.com/questions/26336/sha512-faster-than-sha256
    """


def test_hash_data():
    counter = [0]
    failed = []
    def check_hash(input_, want=None):
        count = counter[0] = counter[0] + 1
        got = ub.hash_data(input_)
        # assert got.startswith(want), 'want={}, got={}'.format(want, got)
        if want is not None and not got.startswith(want):
            item = (got, input_, count, want)
            failed.append(item)
            print(item)

    check_hash('1', 'kjckshvqyxgutulxpqdcbgwqynecikho')
    check_hash(['1'], 'vbppcawudziqinqcuojszzvdayryhhmb')
    check_hash(tuple(['1']), 'vbppcawudziqinqcuojszzvdayryhhmb')
    check_hash(b'12', 'zklkttlbjthzkppeeermruktfmhsefhl')
    check_hash([b'1', b'2'], 'bggphxtjkmeoeoxonlsrfoehmvusfxqu')
    check_hash(['1', '2', '3'], 'rpaokzkayydloniwutxhdqmhsibezowc')
    check_hash(['1', np.array([1, 2, 3]), '3'], 'jihkzpzqgwahderjiblyaklxycdldzpg')
    check_hash('123', 'aheslytcdblfeuxjkurjltxzgsdqkvel')
    check_hash(zip([1, 2, 3], [4, 5, 6]), 'xdfqqqjzzdwitclyighsbhuspgeutuod')
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


class HashTracer(object):
    """ class which extracts the sequence that would be hashed """
    def __init__(self):
        self.sequence = []

    def hexdigest(self):
        return b'00000000'

    def __call__(self):
        return self

    def update(self, data):
        self.sequence.append(data)


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

    hashid = ub.hash_data(data)
    assert hashid == ub.hash_data(data.ravel()), (
        'currently we expect ravel not to matter')
    assert hashid != ub.hash_data(data.astype(np.float32))
    assert hashid != ub.hash_data(data.astype(np.int32))
    assert hashid != ub.hash_data(data.astype(np.int8))


def hash_sequence(data):
    tracer = HashTracer()
    ub.hash_data(data, hasher=tracer)
    return tracer.sequence


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
    assert hash_sequence(np.float128(3.0)) == hash_sequence(3.0)


def test_numpy_random_state():
    data = np.random.RandomState(0)
    assert ub.hash_data(data) == 'pooeuqejltfttjdzsgwzlbffznqctsnq'
    # hash_sequence(data)


def test_uuid():
    import uuid
    data = uuid.UUID('12345678-1234-1234-1234-123456789abc')
    assert hash_sequence(data) == [b'UUID\x124Vx\x124\x124\x124\x124Vx\x9a\xbc']
    assert ub.hash_data(data) == 'tuvnocpbbdgcvnaexwxtqugntcdznjbh'
    assert ub.hash_data(data.bytes) != ub.hash_data(data), (
        'the fact that it is a UUID should reflect in the hash')


def test_hash_data_custom_alphabet():
    data = 1
    hashid_26 = ub.hash_data(data, alphabet=None)
    assert hashid_26 == 'cmhclfgczcydmexhcztydbueglwquqap'
    hashid_16 = ub.hash_data(data, alphabet='hex')
    assert hashid_16 == '8bf2a1f4dbea6e59e5c2ec4077498c44'
    hashid_2 = ub.hash_data(data, alphabet=['0', '1'])
    assert hashid_2 == '01101010010100000001100001101010'


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


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_hash.py
        pytest ~/code/ubelt/ubelt/tests/test_hash.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
