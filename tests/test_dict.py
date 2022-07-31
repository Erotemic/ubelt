import ubelt as ub
import pytest


def test_auto_dict():
    auto = ub.AutoDict()
    assert 0 not in auto
    auto[0][10][100] = None
    assert 0 in auto
    assert isinstance(auto[0], ub.AutoDict)


def test_auto_dict_to_dict():
    from ubelt.util_dict import AutoDict
    auto = AutoDict()
    auto[1] = 1
    auto['n1'] = AutoDict()
    auto['n1']['n2'] = AutoDict()
    auto['n1']['n2'][2] = 2
    auto['n1']['n2'][3] = 3
    auto['dict'] = {}
    auto['dict']['n3'] = AutoDict()
    auto['dict']['n3']['n4'] = AutoDict()
    print('auto = {!r}'.format(auto))
    static = auto.to_dict()
    print('static = {!r}'.format(static))
    assert not isinstance(static, AutoDict), '{}'.format(type(static))
    assert not isinstance(static['n1'], AutoDict), '{}'.format(type(static['n1']))
    assert not isinstance(static['n1']['n2'], AutoDict)
    assert isinstance(static['dict']['n3'], AutoDict)
    assert isinstance(static['dict']['n3']['n4'], AutoDict)


def test_auto_dict_ordered():
    # To Dict should repsect ordering
    from ubelt.util_dict import AutoOrderedDict, AutoDict
    auto = AutoOrderedDict()
    auto[0][3] = 3
    auto[0][2] = 2
    auto[0][1] = 1
    auto[0][4] = AutoDict()
    assert isinstance(auto, AutoDict)
    print('auto = {!r}'.format(auto))
    static = auto.to_dict()
    print('static = {!r}'.format(static))
    assert not isinstance(static, AutoDict), 'bad cast {}'.format(type(static))
    assert not isinstance(static[0][4], AutoDict), 'bad cast {}'.format(type(static[0][4]))
    assert list(auto[0].values())[0:3] == [3, 2, 1], 'maintain order'


def test_dzip_errors():
    with pytest.raises(TypeError):
        ub.dzip([1], 2)
    with pytest.raises(TypeError):
        ub.dzip(1, [2])
    with pytest.raises(ValueError):
        ub.dzip([1, 2, 3], [])
    with pytest.raises(ValueError):
        ub.dzip([], [4, 5, 6])
    with pytest.raises(ValueError):
        ub.dzip([1, 2, 3], [4, 5])


def test_group_items_callable():
    pairs = [
        ('ham', 'protein'),
        ('jam', 'fruit'),
        ('spam', 'protein'),
        ('eggs', 'protein'),
        ('cheese', 'dairy'),
        ('banana', 'fruit'),
    ]
    items, groupids = zip(*pairs)
    lut = dict(zip(items, groupids))

    result1 = ub.group_items(items, groupids)
    result2 = ub.group_items(items, lut.__getitem__)

    result1 = ub.map_values(set, result1)
    result2 = ub.map_values(set, result2)
    assert result1 == result2


def test_dict_hist_ordered():
    import random
    import string
    import ubelt as ub
    rng = random.Random(0)
    items = [rng.choice(string.ascii_letters) for _ in range(100)]
    # Ensure that the ordered=True bug is fixed
    a = sorted(ub.dict_hist(items, ordered=True).items())
    b = sorted(ub.dict_hist(items, ordered=False).items())
    assert a == b


def test_dict_subset_iterable():
    """
    CommandLine:
        xdoctest -m ~/code/ubelt/tests/test_dict.py test_dict_subset_iterable
    """
    # There was a bug in 0.7.0 where iterable keys would be exhausted too soon
    keys_list = list(range(10))
    dict_ = {k: k for k in keys_list}
    got = ub.dict_subset(dict_, iter(keys_list))
    assert dict(got) == dict_


# def _benchmark_groupid_sorted():
#     import random
#     import ubelt as ub

#     ydata = ub.ddict(list)
#     xdata = []

#     ti = ub.Timerit(100, bestof=10, verbose=True)

#     num = 10
#     for gamma in [0.01, .1, .5]:
#         for num in [10, 100, 1000, 10000, 100000]:
#             items = [random.random() for _ in range(num)]
#             groupids = [random.randint(0, int(num ** gamma)) for _ in range(num)]

#             xdata.append(num)

#             for timer in ti.reset(label='sort_g{}'.format(gamma)):
#                 with timer:
#                     ub.group_items(items, groupids, sorted_=True)
#             ydata[ti.label].append(ti.min())

#             for timer in ti.reset(label='nosort_g{}'.format(gamma)):
#                 with timer:
#                     ub.group_items(items, groupids, sorted_=False)
#             ydata[ti.label].append(ti.min())

#     ydata = ub.odict(sorted(ydata.items(), key=lambda t: t[1][-1])[::-1])
#     import netharn as nh
#     nh.util.autompl()
#     nh.util.multi_plot(xdata, ydata)
