import ubelt as ub
import itertools as it
import uuid
import pytest
from ubelt.util_hash import _convert_hexstr_base, _ALPHABET_16
from ubelt.util_hash import _hashable_sequence
from ubelt.util_hash import _rectify_hasher


try:
    import numpy as np
except ImportError:
    np = None


def _benchmark():
    """
    On 64-bit processors sha512 may be faster than sha256

    References:
        .. [SE26336] https://crypto.stackexchange.com/questions/26336/sha512-faster-than-sha256
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

    print(ub.urepr(failed, nl=1))
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

    print(ub.urepr(failed, nl=1))
    assert len(failed) == 0


def test_available():
    assert 'sha1' in ub.util_hash._HASHERS.available()


def test_idempotency():
    # When we disable types and join sequence items, the hashable
    # sequence should be idempotent
    nested_data = ['fds', [3, 2, 3], {3: 2, '3': [3, 2, {3}]}, {1, 2, 3}]
    hashable1 = b''.join(_hashable_sequence(nested_data))
    hashable2 = b''.join(_hashable_sequence(hashable1, types=False))
    assert hashable1 == hashable2


def test_special_floats():
    # Tests a fix from version 0.10.3 for inf/nan floats
    # standard_floats = [0.0, 0.1, 0.2]
    data = [
        float('inf'), float('nan'), float('-inf'),
        -0., 0., -1., 1., 0.3, 0.1 + 0.2,
    ]
    expected_encoding = [
        b'_[_',
        b'FLTinf_,_',
        b'FLTnan_,_',
        b'FLT-inf_,_',
        b'FLT\x00/\x01_,_',
        b'FLT\x00/\x01_,_',
        b'FLT\xff/\x01_,_',
        b'FLT\x01/\x01_,_',
        b'FLT\x13333333/@\x00\x00\x00\x00\x00\x00_,_',
        b'FLT\x04\xcc\xcc\xcc\xcc\xcc\xcd/\x10\x00\x00\x00\x00\x00\x00_,_',
        b'_]_']
    exepcted_prefix = '3196f80e17de93565f0fc57d98922a44'

    hasher = 'sha512'
    encoded = _hashable_sequence(data, types=True)
    hashed = ub.hash_data(data, hasher=hasher, types=True)[0:32]
    print('expected_encoding = {!r}'.format(expected_encoding))
    print('encoded           = {!r}'.format(encoded))
    print('hashed          = {!r}'.format(hashed))
    print('exepcted_prefix = {!r}'.format(exepcted_prefix))
    assert encoded == expected_encoding
    assert hashed == exepcted_prefix
    _sanity_check(data)


def test_hashable_sequence_sanity():
    data = [1, 2, [3.2, 5]]
    # data = [1]
    _sanity_check(data)


def _sanity_check(data):

    hasher_code = 'sha512'
    hasher_type = ub.util_hash._rectify_hasher(hasher_code)

    encoded_seq = _hashable_sequence(data, types=False)
    encoded_byt = b''.join(encoded_seq)
    hashed = ub.hash_data(data, hasher=hasher_code, types=False)
    rehashed = ub.hash_data(encoded_byt, hasher=hasher_code, types=False)

    hash_obj1 = hasher_type()
    hash_obj1.update(encoded_byt)
    hashed1 = hash_obj1.hexdigest()

    hash_obj2 = hasher_type()
    for item in encoded_seq:
        hash_obj2.update(item)
    hashed2 = hash_obj2.hexdigest()

    print('encoded_seq = {!r}'.format(encoded_seq))
    print('encoded_byt = {!r}'.format(encoded_byt))

    print('hashed   = {!r}'.format(hashed))
    print('rehashed = {!r}'.format(rehashed))
    print('hashed1  = {!r}'.format(hashed1))
    print('hashed2  = {!r}'.format(hashed2))

    # Sanity check
    ub.hash_data(encoded_seq, hasher=hasher_code, types=False)

    seq2 = b''.join(_hashable_sequence(encoded_byt, types=False))
    assert encoded_byt == seq2

    tracer1 = ub.util_hash._HashTracer()
    ub.hash_data(encoded_byt, types=False, hasher=tracer1)
    traced_bytes1 = tracer1.hexdigest()
    print('traced_bytes1 = {!r}'.format(traced_bytes1))
    assert traced_bytes1 == encoded_byt

    tracer2 = ub.util_hash._HashTracer()
    ub.hash_data(encoded_byt, types=False, hasher=tracer2)
    traced_bytes2 = tracer1.hexdigest()
    print('traced_bytes2 = {!r}'.format(traced_bytes2))
    assert traced_bytes2 == traced_bytes1


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

    s1 = b''.join(_hashable_sequence(data.astype(object)))
    s2 = b''.join(_hashable_sequence(data_list))
    s3 = b''.join(_hashable_sequence(data.tolist()))
    s4 = b''.join(_hashable_sequence(data.astype(np.uint8).astype(object)))

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
    assert _hashable_sequence([1, 1, 1]) != _hashable_sequence([[1], 1, 1])
    assert _hashable_sequence([[1], 1]) != _hashable_sequence([[1, 1]])
    assert _hashable_sequence([1, [1]]) != _hashable_sequence([[1, 1]])
    assert _hashable_sequence([[[1]]]) != _hashable_sequence([[1]])


def test_numpy_int():
    if np is None:
        pytest.skip('requires numpy')
    assert _hashable_sequence(np.int8(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.int16(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.int32(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.int64(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.uint8(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.uint16(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.uint32(3)) == _hashable_sequence(3)
    assert _hashable_sequence(np.uint64(3)) == _hashable_sequence(3)


def test_numpy_float():
    if np is None:
        pytest.skip('requires numpy')
    assert _hashable_sequence(np.float16(3.0)) == _hashable_sequence(3.0)
    assert _hashable_sequence(np.float32(3.0)) == _hashable_sequence(3.0)
    assert _hashable_sequence(np.float64(3.0)) == _hashable_sequence(3.0)
    try:
        assert _hashable_sequence(np.float128(3.0)) == _hashable_sequence(3.0)
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
    sequence = b''.join(_hashable_sequence(data, types=True))
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
    fpath = ub.Path.appdir('ubelt/tests').ensuredir() / 'tmp.txt'
    fpath.write_text('foobar')
    hashid1_a = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=1)
    hashid2_a = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=1)

    hashid1_b = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=10)
    hashid2_b = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=10)

    assert hashid1_a == hashid1_b
    assert hashid2_a != hashid2_b, 'blocksize matters when stride is > 1'
    assert hashid1_a != hashid2_a

    hashid3_c = ub.hash_file(fpath, hasher='sha512', stride=2, blocksize=10, maxbytes=1000)
    assert hashid3_c == hashid2_b


def test_empty_hash_file():
    fpath = ub.Path.appdir('ubelt/tests').ensuredir() / 'tmp.txt'
    fpath.write_bytes(b'')
    a = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=1)
    b = ub.hash_file(fpath, hasher='sha512', stride=4, blocksize=4)
    c = ub.hash_file(fpath, hasher='sha512', stride=4, blocksize=4, maxbytes=1)
    d = ub.hash_file(fpath, hasher='sha512', stride=1, blocksize=4, maxbytes=0)
    assert a == b == c == d


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


def test_xxhash():
    if 'xxh64' in ub.util_hash._HASHERS.available():
        assert ub.hash_data('foo', hasher='xxh64') == '33bf00a859c4ba3f'
    else:
        pytest.skip('xxhash is not available')


def test_blake3():
    if 'blake3' in ub.util_hash._HASHERS.available():
        assert ub.hash_data('foo', hasher='b3') == '04e0bb39f30b1a3feb89f536c93be15055482df748674b00d26e5a75777702e9'
    else:
        pytest.skip('blake3 is not available')


def test_base32():
    hashstr = ub.hash_data('abc', hasher='sha1', base=32, types=False)
    print(f'hashstr={hashstr}')
    assert hashstr == 'VGMT4NSHA2AWVOR6EVYXQUGCNSONBWE5'


def test_compatible_hash_bases():
    """
    Ubelt ~1.2.3 has a ~bug~ incompatability with non-hex hash bases. Depending
    on leftover amount of data in the byte stream, our hex reencoding may be
    incorrect. It is still correct when the input has correct lengths, but in
    general it can produce issues if you were expecting hashes to conform to
    RFC standards.

    FIXME: THIS ISSUE IS NOT RESOLVED YET. NEED A WAY OF GETTING COMPATIBLE
    BEHAVIOR WITH STANDARD ENCODINGS. THIS ULTIMATELY REQUIRES PROCESSING DATA
    WITH PADDING AND VIA BYTE FORM, NOT INTEGER FORM.

    References:
        .. [SO43920799] https://stackoverflow.com/questions/43920799/convert-byte-to-base64-and-ascii-in-python
        .. [MultiBase] https://github.com/multiformats/multibase
        .. [SO6916805] https://stackoverflow.com/questions/6916805/why-does-a-base64-encoded-string-have-an-sign-at-the-end
        .. [SementeBaseConv] https://github.com/semente/python-baseconv
    """
    import pytest
    pytest.skip('FIXME THIS ISSUE IS NOT RESOLVE YET.')
    if not ub.LINUX:
        pytest.skip('only runs on linux')
    required_programs = [
        'sha256sum', 'cut', 'xxd', 'base32',
    ]
    HAS_PROGS = all(ub.find_exe(p) for p in required_programs)
    if not HAS_PROGS:
        pytest.skip('only runs if required programs exist')

    hasher = 'sha1'
    hasher = 'sha256'
    # hasher = 'sha512'
    text = 'foobar'

    trace = ub.hash_data(text, hasher=ub.util_hash._HashTracer(), types=False)
    print(f'text={text}')
    print(f'trace={trace}')
    print(f'hasher={hasher}')

    hasher_obj = ub.util_hash._rectify_hasher(hasher)()
    hasher_obj.update(trace)
    raw_bytes = hasher_obj.digest()
    print(f'raw_bytes={raw_bytes}')
    import base64
    realb32_encode = base64.b32encode(raw_bytes)

    # base64.b32decode(realb32_encode)

    print(f'realb32_encode=\n{realb32_encode}')
    _ = ub.cmd(fr'printf "{text}" | {hasher}sum | cut -f1 -d\  | xxd -r -p', shell=True, system=True)
    # _ = ub.cmd(fr'printf "{text}" | {hasher}sum | cut -f1 -d\  | xxd -r', shell=True, verbose=3)

    std_result = ub.cmd(fr'printf "{text}" | {hasher}sum', shell=True, verbose=3)['out'].split(' ')[0]
    our_result = ub.hash_data(text, hasher=hasher, types=False)
    print(f'std_result={std_result}')
    print(f'our_result={our_result}')
    assert our_result == std_result

    std_result = ub.cmd(fr'printf "{text}" | {hasher}sum | cut -f1 -d\  | xxd -r -p | base32', shell=True, verbose=3)['out'].strip().replace('\n', '')
    our_result = ub.hash_data(text, hasher=hasher, types=False, base=32)
    std_result_16 = ub.cmd(fr'printf "{text}" | {hasher}sum | cut -f1 -d\ ', shell=True, verbose=3)['out'].strip().replace('\n', '')
    our_result_16 = ub.hash_data(text, hasher=hasher, types=False, base=16)
    print(f'std_result_16={std_result_16}')
    print(f'our_result_16={our_result_16}')

    raw_result = base64.b16decode(our_result_16.upper())
    fix_result = base64.b32encode(raw_result).decode()
    print(f'fix_result={fix_result}')
    print(f'std_result={std_result}')
    print(f'our_result={our_result}')
    assert our_result == std_result

    if 1:

        hexstr = our_result_16
        base = ub.util_hash._ALPHABET_32
        baselen = len(base)
        # Experimental solution for _convert_hexstr_base

        # The alternate code has a bug, but it is concistent so we can't change
        # it. Work towards correct logic is here, which we will eventually
        # introduce as an opt-in change.
        import base64
        raw_bytes = base64.b16decode(hexstr.upper())
        # leftover = len(raw_bytes) % 5
        # # Pad the last quantum with zero bits if necessary
        # if leftover:
        #     raw_bytes = raw_bytes + b'\0' * (5 - leftover)  # Don't use += !
        x = int.from_bytes(raw_bytes, 'big', signed=False)
        r = 0
        digits = []
        while x:
            x, r = divmod(x, baselen)
            digits.append(base[r])
        print(r)
        digits.reverse()
        newbase_str = ''.join(digits)
        print(newbase_str)

        import baseconv
        base32_digits = ''.join(ub.util_hash._ALPHABET_32)
        base16_digits = ''.join(ub.util_hash._ALPHABET_16)
        class MyHexConvertor(baseconv.BaseConverter):
            decimal_digits = base16_digits

        co = MyHexConvertor(base32_digits)
        print(f'hexstr={hexstr}')
        got = co.encode(hexstr)
        print(f'got={got}')

        co = MyHexConvertor(base16_digits)
        co.decimal_digits = base32_digits
        redid = co.encode(got)
        print(f'redid={redid}')

        r"""
        echo "foobar" > test.txt
        ipfs add --only-hash test.txt --cid-version=1

        # https://github.com/multiformats/py-multibase
        pip install py-multibase

        from multibase import encode, decode
        hasher_obj = ub.util_hash._rectify_hasher('sha256')()
        hasher_obj.update(b'foobar')
        raw_bytes = hasher_obj.digest()

        raw_bytes = b'\xc3\xab\x8f\xf17 \xe8\xad\x90G\xdd9Fk<\x89t\xe5\x92\xc2\xfa8=J9`qL\xae\xf0\xc4\xf2'
        encode('base32', raw_bytes).upper()
        encode('base32upper', raw_bytes).upper()

        """
        if base == list(base64._b32alphabet.decode()):
            # NOTE: This code has an incompatability with standard base encodings
            # because it does not pad the bytes. I.e. for base 64 3 bytes are
            # converted into 4 characters, so we need a input string divisible by
            # 3. For base32 5 bytes are converted into 2 characters.
            # in general we have to find lowest N and M such that
            #
            # N = number of characters in the encoding
            # M = number of bytes in the input
            #
            # Usually N > M
            #
            # <base> ** N == (2 ** 8) ** M
            # or
            # <base> ** N == (2 ** (8 * M))
            #
            # e.g. For base=64
            # 64 ** 4 == (2 ** 8) ** 3
            #
            # e.g. For base=32
            # 32 ** 8 == (2 ** 8) ** 5
            #
            # In general need find integer solutions for:
            # M = log(B**N)/(8*log(2))
            # or
            # N = log(256 ** M)/log(B)

            if 0:
                import sympy
                N, M, B = sympy.symbols('N, M, B')
                eqn = sympy.Eq((B ** N), ((2 ** 8) ** M))
                solutions = sympy.solve(eqn, N)
                print('solutions = {}'.format(ub.urepr(solutions, nl=1)))
                b = 64
                for soln in solutions:
                    for m in range(1, 10):
                        ans = soln.subs({M: m, B: b}).evalf()
                        real, imag = ans.as_real_imag()
                        if abs(imag) < 1e-8:
                            fracs = real - int(real)
                            if fracs < 1e-8:
                                print(f'n={m}')
                                print(soln)
                                print(ans)
                                raise Exception

            # There is no integer solution for base 26
            base_size = 26
            import math
            for i in range(0, 100):
                num_input_bytes = i
                num_output_symbols = math.log(256 ** num_input_bytes, base_size)
                print(f'{num_input_bytes} > {num_output_symbols}')

            # check
            # alphabet = base64._b32alphabet
            # s = raw_bytes
            # desired = base64.b32encode(raw_bytes)
            # print(f'desired={desired}')
            # print(f'newbase_str={newbase_str}')

            # leftover = len(s) % 5
            # # Pad the last quantum with zero bits if necessary
            # if leftover:
            #     s = s + b'\0' * (5 - leftover)  # Don't use += !
            # encoded = bytearray()
            # from_bytes = int.from_bytes
            # b32tab2 = base64._b32tab2[alphabet]
            # for i in range(0, len(s), 5):
            # if 1:
            #     i = 0
            #     c = from_bytes(s[i: i + 5], 'big')
            #     first = (b32tab2[c >> 30] +           # bits 1 - 10
            #              b32tab2[(c >> 20) & 0x3ff] + # bits 11 - 20
            #              b32tab2[(c >> 10) & 0x3ff] + # bits 21 - 30
            #              b32tab2[c & 0x3ff]           # bits 31 - 40
            #              )


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_hash.py
        pytest ~/code/ubelt/ubelt/tests/test_hash.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
