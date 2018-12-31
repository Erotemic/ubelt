import ubelt as ub


def test_newlines():
    import ubelt as ub
    dict_ = {
        'k1': [[1, 2, 3], [4, 5, 6]],
        'k2': [[1, 2, 3], [4, 5, 6]],
    }
    assert ub.repr2(dict_, nl=1) != ub.repr2(dict_, nl=2)
    assert ub.repr2(dict_, nl=2) != ub.repr2(dict_, nl=3)
    assert ub.repr2(dict_, nl=3) == ub.repr2(dict_, nl=4)
    assert ub.repr2(dict_, nl=1) == ub.codeblock(
        '''
        {
            'k1': [[1, 2, 3], [4, 5, 6]],
            'k2': [[1, 2, 3], [4, 5, 6]],
        }
        ''')
    assert ub.repr2(dict_, nl=2) == ub.codeblock(
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


def test_compact_brace():
    import ubelt as ub
    def _nest(d, w):
        if d == 0:
            return {}
        else:
            return {'n{}'.format(d): _nest(d - 1, w + 1),
                    'mm{}'.format(d): _nest(d - 1, w + 1)}

    dict_ = _nest(d=3, w=1)
    result = ub.repr2(dict_, nl=4, precision=2, compact_brace=0)
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

    result = ub.repr2(dict_, nl=4, precision=2, compact_brace=1)
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
    assert ub.repr2(list()) == '[]'
    assert ub.repr2(dict()) == '{}'
    assert ub.repr2(set()) == '{}'
    assert ub.repr2(tuple()) == '()'
    assert ub.repr2(dict(), explicit=1) == 'dict()'
    # Even when no braces are no, still include them when input is empty
    assert ub.repr2(list(), nobr=1) == '[]'
    assert ub.repr2(dict(), nobr=1) == '{}'
    assert ub.repr2(set(), nobr=1) == '{}'
    assert ub.repr2(tuple(), nobr=1) == '()'
    assert ub.repr2(dict(), nobr=1, explicit=1) == 'dict()'


def test_list_of_numpy():
    import numpy as np
    import ubelt as ub

    data = [
        np.zeros((3, 3), dtype=np.int32),
        np.zeros((3, 10), dtype=np.int32),
        np.zeros((3, 20), dtype=np.int32),
        np.zeros((3, 30), dtype=np.int32),
    ]
    string = ub.repr2(data, nl=2)
    print(string)
    assert repr(data) == repr(eval(string)), 'should produce eval-able code'
    assert string == ub.codeblock(
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
    string = ub.repr2(data, max_line_width=10000, nl=2)
    print(string)
    assert string == ub.codeblock(
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
    string = ub.repr2(data, nl=1)
    print(string)
    assert string == ub.codeblock(
        '''
        [
            np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32),
        ]
        '''
    )
    string = ub.repr2(data, nl=0)
    print(string)
    assert string == ub.codeblock(
        '''
        [np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32), np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.int32)]
        '''
    )


def test_dict_of_numpy():
    import numpy as np
    data = ub.odict(zip(
        ['one', 'two', 'three', 'four'],
        [
            np.zeros((3, 3), dtype=np.int32),
            np.zeros((3, 10), dtype=np.int32),
            np.zeros((3, 20), dtype=np.int32),
            np.zeros((3, 30), dtype=np.int32),
        ]))

    string = ub.repr2(data, nl=2)
    print(string)
    assert string == ub.codeblock(
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
    import numpy as np
    text = ub.repr2(np.float32(3.333333), precision=2)
    assert text == '3.33'


def test_repr2_tuple_keys():
    data = {
        ('one', 'two'): 100,
        ('three', 'four'): 200,
    }
    string = ub.repr2(data)
    print(string)
    string == ub.codeblock(
        '''
        {
            (
                'one',
                'two',
            ): 100,
            (
                'three',
                'four',
            ): 200,
        }
        ''')

    data = {
        ('one', 'two'): 100,
        ('three', 'four'): 200,
    }
    string = ub.repr2(data, sk=1)
    print(string)
    string == ub.codeblock(
        '''
        {
            ('one', 'two'): 100,
            ('three', 'four'): 200,
        }
        ''')

if __name__ == '__main__':
    """
    CommandLine:
        pytest ~/code/ubelt/ubelt/tests/test_format.py  --verbose -s
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
