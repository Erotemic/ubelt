import random
import ubelt as ub
import itertools as it


def test_operators():
    """
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_oset.py test_operators
    """
    rng = random.Random(0)

    def random_oset(rng, a=20, b=20):
        return ub.OrderedSet(rng.randint(0, a) for _ in range(b))

    def check_results(*results, **kw):
        name = kw.get('name', 'set test')
        datas = kw.get('datas', [])
        if not ub.allsame(results):
            raise AssertionError('Not all same {} for {} with datas={}'.format(
                results, name, datas))
        for a, b in it.combinations(results, 2):
            if not isinstance(a, (bool, int)):
                assert a is not b, name + ' should all be different items'

    def operator_tests(data1, data2):
        result1 = data1.copy()
        print('====')
        print('data1 = {!r}'.format(data1))
        print('data2 = {!r}'.format(data2))
        result1.intersection_update(data2)
        result2 = (data1 & data2)
        result3 = (data1.intersection(data2))
        print('result1 = {!r} result1.intersection_update(data2)'.format(result1))
        print('result2 = {!r} (data1 & data2) '.format(result2))
        print('result3 = {!r} (data1.intersection(data2))'.format(result3))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='isect')

        result1 = data1.copy()
        result1.difference_update(data2)
        result2 = (data1 - data2)
        result3 = (data1.difference(data2))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='-')

        result1 = data1.copy()
        result1.symmetric_difference_update(data2)
        result2 = (data1 ^ data2)
        result3 = (data1.symmetric_difference(data2))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='xor')

        result1 = data1.copy()
        result1.update(data2)
        result2 = (data1 | data2)
        result3 = (data1.union(data2))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='union')

        result1 = data1 <= data2
        result2 = data1.issubset(data2)
        result3 = set(data1).issubset(set(data2))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='subset')

        result1 = data1 >= data2
        result2 = data1.issuperset(data2)
        result3 = set(data1).issuperset(set(data2))
        check_results(result1, result2, result3, datas=(data1, data2),
                      name='superset')

        result1 = data1.isdisjoint(data2)
        result2 = len(data1.intersection(data2)) == 0
        check_results(result1, result2, datas=(data1, data2),
                      name='disjoint')

    # run tests on standard test cases
    data1 = ub.OrderedSet([5, 3, 1, 4])
    data2 = ub.OrderedSet([1, 4])
    operator_tests(data1, data2)
    operator_tests(data2, data1)

    data1 = ub.OrderedSet([])
    data2 = ub.OrderedSet([])
    operator_tests(data1, data2)

    data1 = ub.OrderedSet([3, 1, 2])
    data2 = ub.OrderedSet([])
    operator_tests(data1, data2)
    operator_tests(data2, data1)

    # run tests on random test cases
    for _ in range(10):
        data1 = random_oset(rng)
        data2 = random_oset(rng)

        operator_tests(data1, data2)
        operator_tests(data2, data1)


def test_equality():

    def check(a, b):
        # Self checks
        assert a == a
        assert a >= a
        assert a <= a
        assert not a < a
        assert not a > a
        assert not a != a

        # Lesser checks
        assert a < b
        assert a <= b
        assert a != b
        assert not a == b

        # Greater checks
        assert b > a
        assert b >= a
        assert b != a
        assert not b == a

    a = ub.oset([])
    b = ub.oset([1])
    c = ub.oset([1, 2])
    d = ub.oset([1, 2, 3])

    check(a, b)
    check(b, c)
    check(c, d)
    check(a, d)
    check(a, d)


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_oset.py test_equality
        pytest ~/code/ubelt/ubelt/tests/test_oset.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
