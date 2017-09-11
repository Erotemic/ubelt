

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
        }
        ''')

    result = ub.repr2(dict_, nl=4, precision=2, compact_brace=1)
    print(result)
    assert result == ub.codeblock(
        '''
        {'n3': {'mm2': {'mm1': {},
                        'n1': {},},
                'n2': {'mm1': {},
                       'n1': {},},},
         'mm3': {'mm2': {'mm1': {},
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
