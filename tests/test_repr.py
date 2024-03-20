import ubelt as ub


def test_newlines():
    import ubelt as ub
    dict_ = {
        'k1': [[1, 2, 3], [4, 5, 6]],
        'k2': [[1, 2, 3], [4, 5, 6]],
    }
    assert ub.urepr(dict_, nl=1) != ub.urepr(dict_, nl=2)
    assert ub.urepr(dict_, nl=2) != ub.urepr(dict_, nl=3)
    assert ub.urepr(dict_, nl=3) == ub.urepr(dict_, nl=4)
    assert ub.urepr(dict_, nl=1) == ub.codeblock(
        '''
        {
            'k1': [[1, 2, 3], [4, 5, 6]],
            'k2': [[1, 2, 3], [4, 5, 6]],
        }
        ''')
    assert ub.urepr(dict_, nl=2) == ub.codeblock(
        '''
        {
            'k1': [
                [1, 2, 3],
                [4, 5, 6],
            ],
            'k2': [
                [1, 2, 3],
                [4, 5, 6],
            ],
        }
        ''')


def test_negative_newlines():
    import ubelt as ub
    dict_ = {
        'k1': [[1, 2, 3], [4, 5, 6]],
        'k2': [[[1, 2, [1, 2, 3]], [1, 2, 3], 3], [4, 5, 6]],
        'k3': [1, 2, 3],
        'k4': [[[1, 2, 3], 2, 3], [4, 5, 6]],
    }
    text = ub.urepr(dict_, nl=-1)
    print(text)
    assert text == ub.codeblock(
        '''
        {
            'k1': [
                [1, 2, 3],
                [4, 5, 6]
            ],
            'k2': [
                [
                    [
                        1,
                        2,
                        [1, 2, 3]
                    ],
                    [1, 2, 3],
                    3
                ],
                [4, 5, 6]
            ],
            'k3': [1, 2, 3],
            'k4': [
                [
                    [1, 2, 3],
                    2,
                    3
                ],
                [4, 5, 6]
            ]
        }
        ''')


def test_compact_brace():
    import ubelt as ub
    def _nest(d, w):
        if d == 0:
            return {}
        else:
            return {'n{}'.format(d): _nest(d - 1, w + 1),
                    'mm{}'.format(d): _nest(d - 1, w + 1)}

    dict_ = _nest(d=3, w=1)
    result = ub.urepr(dict_, nl=4, precision=2, compact_brace=0, sort=1)
    print(result)
    assert result == ub.codeblock(
        '''
        {
            'mm3': {
                'mm2': {
                    'mm1': {},
                    'n1': {},
                },
                'n2': {
                    'mm1': {},
                    'n1': {},
                },
            },
            'n3': {
                'mm2': {
                    'mm1': {},
                    'n1': {},
                },
                'n2': {
                    'mm1': {},
                    'n1': {},
                },
            },
        }
        ''')

    result = ub.urepr(dict_, nl=4, precision=2, compact_brace=1, sort=1)
    print(result)
    assert result == ub.codeblock(
        '''
        {'mm3': {'mm2': {'mm1': {},
                         'n1': {},},
                 'n2': {'mm1': {},
                        'n1': {},},},
         'n3': {'mm2': {'mm1': {},
                        'n1': {},},
                'n2': {'mm1': {},
                       'n1': {},},},}
        ''')


def test_empty():
    import ubelt as ub
    assert ub.urepr(list()) == '[]'
    assert ub.urepr(dict()) == '{}'
    assert ub.urepr(set()) == '{}'
    assert ub.urepr(tuple()) == '()'
    assert ub.urepr(dict(), explicit=1) == 'dict()'
    # Even when no braces are no, still include them when input is empty
    assert ub.urepr(list(), nobr=1) == '[]'
    assert ub.urepr(dict(), nobr=1) == '{}'
    assert ub.urepr(set(), nobr=1) == '{}'
    assert ub.urepr(tuple(), nobr=1) == '()'
    assert ub.urepr(dict(), nobr=1, explicit=1) == 'dict()'


def test_list_of_numpy():
    try:
        import numpy as np
    except ImportError:
        import pytest
        pytest.skip('numpy is optional')

    import ubelt as ub

    data = [
        np.zeros((3, 3), dtype=np.int32),
        np.zeros((3, 10), dtype=np.int32),
        np.zeros((3, 20), dtype=np.int32),
        np.zeros((3, 30), dtype=np.int32),
    ]
    text = ub.urepr(data, nl=2)
    print(text)
    assert repr(data) == repr(eval(text)), 'should produce eval-able code'
    assert text == ub.codeblock(
        '''
        [
            np.array([[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
        ]
        ''')
    text = ub.urepr(data, max_line_width=10000, nl=2)
    print(text)
    assert text == ub.codeblock(
        '''
        [
            np.array([[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
        ]
        ''')
    text = ub.urepr(data, nl=1)
    print(text)
    assert text == ub.codeblock(
        '''
        [
            np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
        ]
        '''
    )
    text = ub.urepr(data, nl=0)
    print(text)
    assert text == ub.codeblock(
        '''
        [np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32)]
        '''
    )


def test_dict_of_numpy():
    try:
        import numpy as np
    except ImportError:
        import pytest
        pytest.skip('numpy is optional')
    data = ub.odict(zip(
        ['one', 'two', 'three', 'four'],
        [
            np.zeros((3, 3), dtype=np.int32),
            np.zeros((3, 10), dtype=np.int32),
            np.zeros((3, 20), dtype=np.int32),
            np.zeros((3, 30), dtype=np.int32),
        ]))

    text = ub.urepr(data, nl=2)
    print(text)
    assert text == ub.codeblock(
        '''
        {
            'one': np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]], dtype=np.int32),
            'two': np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            'three': np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            'four': np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                               0, 0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                               0, 0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                               0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
        }
        ''')


def test_numpy_scalar_precision():
    try:
        import numpy as np
    except ImportError:
        import pytest
        pytest.skip('numpy is optional')
    text = ub.urepr(np.float32(3.333333), precision=2)
    assert text == '3.33'


def test_urepr_tuple_keys():
    data = {
        ('one', 'two'): 100,
        ('three', 'four'): 200,
    }
    text = ub.urepr(data)
    print(text)
    assert text == ub.codeblock(
        '''
        {
            ('one', 'two'): 100,
            ('three', 'four'): 200,
        }
        ''')

    data = {
        ('one', 'two'): 100,
        ('three', 'four'): 200,
    }
    text = ub.urepr(data, sk=1)
    print(text)
    assert text == ub.codeblock(
        '''
        {
            ('one', 'two'): 100,
            ('three', 'four'): 200,
        }
        ''')


def test_newline_keys():
    import ubelt as ub
    class NLRepr(object):
        def __repr__(self):
            return ub.codeblock(
                '''
                <This repr has newlines, and the first line is long:
                   * line1
                   * line2>
                ''')
    key = NLRepr()
    dict_ =  {key: {key: [1, 2, 3, key]}}
    text = ub.urepr(dict_)
    print(text)
    want = ub.codeblock(
        '''
        {
            <This repr has newlines, and the first line is long:
               * line1
               * line2>: {
                <This repr has newlines, and the first line is long:
                   * line1
                   * line2>: [
                    1,
                    2,
                    3,
                    <This repr has newlines, and the first line is long:
                       * line1
                       * line2>,
                ],
            },
        }
        ''')
    assert text == want

    text = ub.urepr(dict_, cbr=True)
    want = ub.codeblock(
        '''
        {<This repr has newlines, and the first line is long:
            * line1
            * line2>: {<This repr has newlines, and the first line is long:
             * line1
             * line2>: [1,
           2,
           3,
           <This repr has newlines, and the first line is long:
              * line1
              * line2>,],},}
        ''')
    print(text)
    assert text == want


def test_format_inf():
    import ubelt as ub
    ub.urepr(float('inf'))
    ub.urepr({'a': float('inf')})

    try:
        import numpy as np
    except ImportError:
        pass
    else:
        ub.urepr(float(np.inf), sv=1)
        text1 = ub.urepr(np.array([np.inf, 1, 2, np.nan, -np.inf]), sv=0)
        assert 'np.inf' in text1 and 'np.nan' in text1
        text2 = ub.urepr(np.array([np.inf, 1, 2, np.nan, -np.inf]), sv=1)
        assert 'np.inf' not in text2 and 'inf' in text2
        assert 'np.nan' not in text2 and 'nan' in text2


def test_autosort():
    import ubelt as ub
    import sys
    dict_ = {
        'k2': [[9, 2, 3], [4, 5, 2]],
        'k1': [[1, 7, 3], [8, 5, 6]],
    }
    if sys.version_info[0:2] >= (3, 7):
        import pytest
        # with pytest.warns(DeprecationWarning):
        with pytest.deprecated_call():
            assert ub.repr2(dict_, sort='auto', nl=1) == ub.codeblock(
                '''
                {
                    'k1': [[1, 7, 3], [8, 5, 6]],
                    'k2': [[9, 2, 3], [4, 5, 2]],
                }
                ''')

    if sys.version_info[0:2] >= (3, 7):
        from collections import OrderedDict
        dict_ = OrderedDict(sorted(dict_.items())[::-1])
        assert ub.urepr(dict_, sort='auto', nl=1) == ub.codeblock(
            '''
            {
                'k2': [[9, 2, 3], [4, 5, 2]],
                'k1': [[1, 7, 3], [8, 5, 6]],
            }
            ''')


def test_align_with_nobrace():
    data = {'123': 123, '45': 45, '6': 6}
    text = ub.urepr(data, align=':')
    print(text)
    assert text == ub.codeblock(
        '''
        {
            '123': 123,
            '45' : 45,
            '6'  : 6,
        }
        ''')

    text = ub.urepr(data, align=':', nobr=1)
    print(text)
    assert text == ub.codeblock(
        '''
        '123': 123,
        '45' : 45,
        '6'  : 6,
        ''')


if __name__ == '__main__':
    """
    CommandLine:
        pytest ~/code/ubelt/ubelt/tests/test_format.py  --verbose -s
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
