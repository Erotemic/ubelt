import random
import ubelt as ub
import itertools as it
import pickle
import pytest
import collections
import sys
from ubelt import OrderedSet


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
        print('result1 = {!r}'.format(result1))
        print('result2 = {!r}'.format(result2))
        print('result3 = {!r}'.format(result3))
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


# def test_extend():
#     self = ub.oset()
#     self.extend([3, 1, 2, 3])
#     assert self == [3, 1, 2]


def eq_(item1, item2):
    # replacement for a nosetest util
    assert item1 == item2


def test_pickle():
    set1 = OrderedSet('abracadabra')
    roundtrip = pickle.loads(pickle.dumps(set1))
    assert roundtrip == set1


def test_empty_pickle():
    empty_oset = OrderedSet()
    empty_roundtrip = pickle.loads(pickle.dumps(empty_oset))
    assert empty_roundtrip == empty_oset


def test_order():
    set1 = OrderedSet('abracadabra')
    eq_(len(set1), 5)
    eq_(set1, OrderedSet(['a', 'b', 'r', 'c', 'd']))
    eq_(list(reversed(set1)), ['d', 'c', 'r', 'b', 'a'])


def test_binary_operations():
    set1 = OrderedSet('abracadabra')
    set2 = OrderedSet('simsalabim')
    assert set1 != set2

    eq_(set1 & set2, OrderedSet(['a', 'b']))
    eq_(set1 | set2, OrderedSet(['a', 'b', 'r', 'c', 'd', 's', 'i', 'm', 'l']))
    eq_(set1 - set2, OrderedSet(['r', 'c', 'd']))


def test_indexing():
    set1 = OrderedSet('abracadabra')
    eq_(set1[:], set1)
    eq_(set1.copy(), set1)
    assert set1 is set1
    assert set1[:] is not set1
    assert set1.copy() is not set1

    eq_(set1[[1, 2]], OrderedSet(['b', 'r']))
    eq_(set1[1:3], OrderedSet(['b', 'r']))
    eq_(set1.index('b'), 1)
    eq_(set1.index(['b', 'r']), [1, 2])
    try:
        set1.index('br')
        assert False, "Looking up a nonexistent key should be a KeyError"
    except KeyError:
        pass


def test_tuples():
    set1 = OrderedSet()
    tup = ('tuple', 1)
    set1.add(tup)
    eq_(set1.index(tup), 0)
    eq_(set1[0], tup)


def test_remove():
    set1 = OrderedSet('abracadabra')

    set1.remove('a')
    set1.remove('b')

    assert set1 == OrderedSet('rcd')
    assert set1[0] == 'r'
    assert set1[1] == 'c'
    assert set1[2] == 'd'

    assert set1.index('r') == 0
    assert set1.index('c') == 1
    assert set1.index('d') == 2

    assert 'a' not in set1
    assert 'b' not in set1
    assert 'r' in set1

    # Make sure we can .discard() something that's already gone, plus
    # something that was never there
    set1.discard('a')
    set1.discard('a')


def test_remove_error():
    # If we .remove() an element that's not there, we get a KeyError
    set1 = OrderedSet('abracadabra')
    with pytest.raises(KeyError):
        set1.remove('z')


def test_clear():
    set1 = OrderedSet('abracadabra')
    set1.clear()

    assert len(set1) == 0
    assert set1 == OrderedSet()


def test_update():
    set1 = OrderedSet('abcd')
    result = set1.update('efgh')

    assert result == 7
    assert len(set1) == 8
    assert ''.join(set1) == 'abcdefgh'

    set2 = OrderedSet('abcd')
    result = set2.update('cdef')
    assert result == 5
    assert len(set2) == 6
    assert ''.join(set2) == 'abcdef'


def test_pop():
    set1 = OrderedSet('ab')
    elem = set1.pop()

    assert elem == 'b'
    elem = set1.pop()

    assert elem == 'a'

    pytest.raises(KeyError, set1.pop)


def test_getitem_type_error():
    set1 = OrderedSet('ab')
    with pytest.raises(TypeError):
        set1['a']


def test_update_value_error():
    set1 = OrderedSet('ab')
    with pytest.raises(ValueError):
        set1.update(3)


def test_empty_repr():
    set1 = OrderedSet()
    assert repr(set1) == 'OrderedSet()'


def test_eq_wrong_type():
    set1 = OrderedSet()
    assert set1 != 2


def test_ordered_equality():
    # Ordered set checks order against sequences.
    assert OrderedSet([1, 2]) == OrderedSet([1, 2])
    assert OrderedSet([1, 2]) == [1, 2]
    assert OrderedSet([1, 2]) == (1, 2)
    assert OrderedSet([1, 2]) == collections.deque([1, 2])


def test_ordered_inequality():
    # Ordered set checks order against sequences.
    assert OrderedSet([1, 2]) != OrderedSet([2, 1])

    assert OrderedSet([1, 2]) != [2, 1]
    assert OrderedSet([1, 2]) != [2, 1, 1]

    assert OrderedSet([1, 2]) != (2, 1)
    assert OrderedSet([1, 2]) != (2, 1, 1)

    # Note: in Python 2.7 deque does not inherit from Sequence, but __eq__
    # contains an explicit check for this case for python 2/3 compatibility.
    assert OrderedSet([1, 2]) != collections.deque([2, 1])
    assert OrderedSet([1, 2]) != collections.deque([2, 2, 1])


def test_comparisons():
    # Comparison operators on sets actually test for subset and superset.
    assert OrderedSet([1, 2]) < OrderedSet([1, 2, 3])
    assert OrderedSet([1, 2]) > OrderedSet([1])

    # MutableSet subclasses aren't comparable to set on 3.3.
    if tuple(sys.version_info) >= (3, 4):
        assert OrderedSet([1, 2]) > {1}


def test_unordered_equality():
    # Unordered set checks order against non-sequences.
    assert OrderedSet([1, 2]) == set([1, 2])
    assert OrderedSet([1, 2]) == frozenset([2, 1])

    assert OrderedSet([1, 2]) == {1: 'a', 2: 'b'}
    assert OrderedSet([1, 2]) == {1: 1, 2: 2}.keys()
    assert OrderedSet([1, 2]) == {1: 1, 2: 2}.values()

    # Corner case: OrderedDict is not a Sequence, so we don't check for order,
    # even though it does have the concept of order.
    assert OrderedSet([1, 2]) == collections.OrderedDict([(2, 2), (1, 1)])

    # Corner case: We have to treat iterators as unordered because there
    # is nothing to distinguish an ordered and unordered iterator
    assert OrderedSet([1, 2]) == iter([1, 2])
    assert OrderedSet([1, 2]) == iter([2, 1])
    assert OrderedSet([1, 2]) == iter([2, 1, 1])


def test_unordered_inequality():
    assert OrderedSet([1, 2]) != set([])
    assert OrderedSet([1, 2]) != frozenset([2, 1, 3])

    assert OrderedSet([1, 2]) != {2: 'b'}
    assert OrderedSet([1, 2]) != {1: 1, 4: 2}.keys()
    assert OrderedSet([1, 2]) != {1: 1, 2: 3}.values()

    # Corner case: OrderedDict is not a Sequence, so we don't check for order,
    # even though it does have the concept of order.
    assert OrderedSet([1, 2]) != collections.OrderedDict([(2, 2), (3, 1)])


def test_bitwise_and():
    """
    # xdoctest ~/code/ordered-set/test.py test_bitwise_and
    pytest ~/code/ordered-set/test.py -s -k test_bitwise_and
    """
    import operator
    import itertools as it

    def allsame(iterable, eq=operator.eq):
            iter_ = iter(iterable)
            try:
                first = next(iter_)
            except StopIteration:
                return True
            return all(eq(first, item) for item in iter_)

    def check_results(*results, **kw):
        name = kw.get('name', 'set test')
        datas = kw.get('datas', [])
        if not allsame(results):
            raise AssertionError('Not all same {} for {} with datas={}'.format(
                results, name, datas))
        for a, b in it.combinations(results, 2):
            if not isinstance(a, (bool, int)):
                assert a is not b, name + ' should all be different items'

    data1 = OrderedSet([12, 13, 1, 8, 16, 15, 9, 11, 18, 6, 4, 3, 19, 17])
    data2 = OrderedSet([19, 4, 9, 3, 2, 10, 15, 17, 11, 13, 20, 6, 14, 16, 8])
    print('\ndata1 = {!r}'.format(data1))
    print('data2 = {!r}'.format(data2))
    result1 = data1.copy()
    result1.intersection_update(data2)
    # This requires a custom & operation apparently
    result2 = (data1 & data2)
    result3 = (data1.intersection(data2))
    print('result1 = {!r}'.format(result1))
    print('result2 = {!r}'.format(result2))
    print('result3 = {!r}\n'.format(result3))
    # result1 = OrderedSet([13, 8, 16, 15, 9, 11, 6, 4, 3, 19, 17])
    # result2 = OrderedSet([13, 8, 16, 15, 9, 11, 6, 4, 3, 19, 17])
    # result3 = OrderedSet([13, 8, 16, 15, 9, 11, 6, 4, 3, 19, 17])

    check_results(result1, result2, result3, datas=(data1, data2),
                  name='isect')


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/code/ubelt/ubelt/tests/test_oset.py test_equality
        pytest ~/code/ubelt/ubelt/tests/test_oset.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
