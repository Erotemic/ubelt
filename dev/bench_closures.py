
def bench_closures():
    """
    Is it faster to use a closure or pass in the variables explicitly?
    """
    import ubelt as ub
    import numpy as np

    # Test a nested func with vs without a closure
    def rand_complex(*shape):
        real = np.random.rand(*shape).astype(np.complex)
        imag = np.random.rand(*shape).astype(np.complex) * 1j
        mat = real + imag
        return mat

    s = int(ub.argval('--s', default='1'))
    mat1 = rand_complex(s, s)
    mat2 = rand_complex(s, s)
    N = 1000
    offset = 100

    def nested_closure():
        mat3 = mat1 @ mat2
        for i in range(N):
            mat3 += i + offset

    def nested_explicit(mat1, mat2, N, offset):
        mat3 = mat1 @ mat2
        for i in range(N):
            mat3 += i + offset

    ti = ub.Timerit(int(2 ** 11), bestof=int(2 ** 8), verbose=int(ub.argval('--verbose', default='1')))

    for timer in ti.reset('nested_explicit'):
        with timer:
            nested_explicit(mat1, mat2, N, offset)

    for timer in ti.reset('nested_closure'):
        with timer:
            nested_closure()

    print('rankings = {}'.format(ub.repr2(ti.rankings, precision=9, nl=2)))
    print('consistency = {}'.format(ub.repr2(ti.consistency, precision=9, nl=2)))

    positions = ub.ddict(list)
    for m1, v1 in ti.rankings.items():
        for pos, label in enumerate(ub.argsort(v1), start=0):
            positions[label].append(pos)
    average_position = ub.map_vals(lambda x: sum(x) / len(x), positions)
    print('average_position = {}'.format(ub.repr2(average_position)))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_closures.py
    """
    bench_closures()
