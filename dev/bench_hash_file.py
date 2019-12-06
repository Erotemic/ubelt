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
