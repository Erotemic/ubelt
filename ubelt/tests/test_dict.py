import ubelt as ub


def test_auto_dict():
    auto = ub.AutoDict()
    assert 0 not in auto
    auto[0][10][100] = None
    assert 0 in auto
    assert isinstance(auto[0], ub.AutoDict)


def auto_dict_to_dict():
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


def auto_dict_ordered():
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
