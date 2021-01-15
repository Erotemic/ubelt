import random
import string
from os.path import join
import ubelt as ub


def hash_file2(fpath, blocksize=65536, hasher='xx64'):
    r"""
    Hashes the data in a file on disk using xxHash

    xxHash is much faster than sha1, bringing computation time down from .57
    seconds to .12 seconds for a 387M file.

    my_weights_fpath_ = ub.truepath('~/tmp/my_weights.pt')


    xdata = 2 ** np.array([8, 12, 14, 16])
    ydatas = ub.ddict(list)
    for blocksize in xdata:
        print('blocksize = {!r}'.format(blocksize))
        ydatas['sha1'].append(ub.Timerit(2).call(ub.hash_file, my_weights_fpath_, hasher='sha1', blocksize=blocksize).min())
        ydatas['sha256'].append(ub.Timerit(2).call(ub.hash_file, my_weights_fpath_, hasher='sha256', blocksize=blocksize).min())
        ydatas['sha512'].append(ub.Timerit(2).call(ub.hash_file, my_weights_fpath_, hasher='sha512', blocksize=blocksize).min())
        ydatas['md5'].append(ub.Timerit(2).call(ub.hash_file, my_weights_fpath_, hasher='md5', blocksize=blocksize).min())
        ydatas['xx32'].append(ub.Timerit(2).call(hash_file2, my_weights_fpath_, hasher='xx32', blocksize=blocksize).min())
        ydatas['xx64'].append(ub.Timerit(2).call(hash_file2, my_weights_fpath_, hasher='xx64', blocksize=blocksize).min())

    import netharn as nh
    nh.util.qtensure()
    nh.util.multi_plot(xdata, ydatas)
    """
    import xxhash
    if hasher == 'xx32':
        hasher = xxhash.xxh32()
    elif hasher == 'xx64':
        hasher = xxhash.xxh64()

    with open(fpath, 'rb') as file:
        buf = file.read(blocksize)
        # otherwise hash the entire file
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(blocksize)
    # Get the hashed representation
    text = ub.util_hash._digest_hasher(hasher, hashlen=None,
                                       base=ub.util_hash.DEFAULT_ALPHABET)
    return text


def _random_data(rng, num):
    return ''.join([rng.choice(string.hexdigits) for _ in range(num)])


def _write_random_file(dpath, part_pool, size_pool, rng):
    namesize = 16
    # Choose 1, 4, or 16 parts of data
    num_parts = rng.choice(size_pool)
    chunks = [rng.choice(part_pool) for _ in range(num_parts)]
    contents = ''.join(chunks)
    fname_noext = _random_data(rng, namesize)
    ext = ub.hash_data(contents)[0:4]
    fname = '{}.{}'.format(fname_noext, ext)
    fpath = join(dpath, fname)
    with open(fpath, 'w') as file:
        file.write(contents)
    return fpath


def bench_hashfile_blocksize():
    """
    Test speed of hashing with various blocksize strategies

    """
    dpath = ub.ensuredir(ub.expandpath('$HOME/raid/data/tmp'))

    size_pool = [10000]

    rng = random.Random(0)
    # Create a pool of random chunks of data
    chunksize = int(2 ** 20)
    pool_size = 8
    part_pool = [_random_data(rng, chunksize) for _ in range(pool_size)]

    # Write a big file (~600 MB)
    fpath = _write_random_file(dpath, part_pool, size_pool, rng)

    import os
    size_mb = os.stat(fpath).st_size / 1e6
    print('file size = {!r} MB'.format(size_mb))

    from ubelt.util_hash import _rectify_hasher

    hasher_algo = 'xx64'

    import timerit
    ti = timerit.Timerit(4, bestof=2, verbose=2)
    # hasher = _rectify_hasher(hash_algo)()
    # with timer:
    #     with open(fpath, 'rb') as file:
    #         buf = file.read(blocksize)
    #         while len(buf) > 0:
    #             hasher.update(buf)
    #             buf = file.read(blocksize)
    # result = hasher.hexdigest()

    results = []

    # Constant blocksize is the winner as long as its chosen right.
    for timer in ti.reset('constant blocksize'):
        blocksize = int(2 ** 20)
        hasher = _rectify_hasher(hasher_algo)()
        with timer:
            with open(fpath, 'rb') as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(blocksize)
        result = hasher.hexdigest()
        results.append(result)

    for timer in ti.reset('double blocksize'):
        blocksize = int(2 ** 20)
        hasher = _rectify_hasher(hasher_algo)()
        with timer:
            with open(fpath, 'rb') as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    blocksize *= 2
                    buf = file.read(blocksize)
        result = hasher.hexdigest()
        results.append(result)

    for timer in ti.reset('double blocksize + limit'):
        max_blocksize = int(2 ** 20) * 16
        blocksize = int(2 ** 20)
        hasher = _rectify_hasher(hasher_algo)()
        with timer:
            with open(fpath, 'rb') as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    hasher.update(buf)
                    blocksize = min(2 * blocksize, max_blocksize)
                    buf = file.read(blocksize)
        result = hasher.hexdigest()
        results.append(result)


def bench_find_optimal_blocksize():
    r"""
    This function can help find the optimal blocksize for your usecase:w

    Notes:

        # Usage
        cd ~/code/ubelt/dev
        xdoctest bench_hash_file.py bench_find_optimal_blocksize \
            --dpath <PATH-TO-HDD-OR-SDD> \
            --size <INT-IN-MB> \
            --hash_algo <ALGO_NAME> \

        # Benchmark on an HDD
        xdoctest bench_hash_file.py bench_find_optimal_blocksize \
            --size 500 \
            --dpath $HOME/raid/data/tmp \
            --hash_algo xx64

        # Benchmark on an SSD
        xdoctest bench_hash_file.py bench_find_optimal_blocksize \
            --size 500 \
            --dpath $HOME/.cache/ubelt/tmp \
            --hash_algo xx64


        # Test a small file
        xdoctest bench_hash_file.py bench_find_optimal_blocksize \
            --size 1 \
            --dpath $HOME/.cache/ubelt/tmp \
            --hash_algo xx64

        Throughout our tests on SSDs / HDDs with small and large files
        we are finding a chunksize of 2 ** 20 consistently working best with
        xx64.

        # Test with a slower hash algo
        xdoctest bench_hash_file.py bench_find_optimal_blocksize \
            --size 500 \
            --dpath $HOME/raid/data/tmp \
            --hash_algo sha1

        Even that shows 2 ** 20 working well.
    """
    import os
    import numpy as np
    import timerit

    dpath = ub.argval('--dpath', default=None)

    if dpath is None:
        # dpath = ub.ensuredir(ub.expandpath('$HOME/raid/data/tmp'))
        dpath = ub.ensure_app_cache_dir('ubelt/hash_test')
    else:
        ub.ensuredir(dpath)

    print('dpath = {!r}'.format(dpath))

    target_size = int(ub.argval('--size', default=600))
    hash_algo = ub.argval('--hash_algo', default='xx64')

    print('hash_algo = {!r}'.format(hash_algo))
    print('target_size = {!r}'.format(target_size))

    # Write a big file (~600 MB)
    MB = int(2 ** 20)
    size_pool = [target_size]
    rng = random.Random(0)
    # pool_size = max(target_size // 2, 1)
    # pool_size = max(1, target_size // 10)
    pool_size = 8
    part_pool = [_random_data(rng, MB) for _ in range(pool_size)]
    fpath = _write_random_file(dpath, part_pool, size_pool, rng)
    print('fpath = {!r}'.format(fpath))

    size_mb = os.stat(fpath).st_size / MB
    print('file size = {!r} MB'.format(size_mb))

    ti = timerit.Timerit(4, bestof=2, verbose=2)

    results = []

    # Find an optimal constant blocksize
    min_power = 16
    max_power = 24
    blocksize_candiates = [int(2 ** e) for e in range(min_power, max_power)]

    for blocksize in blocksize_candiates:
        for timer in ti.reset('constant blocksize=2 ** {} = {}'.format(np.log2(float(blocksize)), blocksize)):
            result = ub.hash_file(fpath, blocksize=blocksize, hasher=hash_algo)
            results.append(result)

    print('ti.rankings = {}'.format(ub.repr2(ti.rankings, nl=2, align=':')))
    assert ub.allsame(results)
