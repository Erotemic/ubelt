# -*- coding: utf-8 -*-
from os.path import join
import ubelt as ub
import sys


def test_import_modpath_basic():
    assert 'testmod' not in sys.modules

    with ub.TempDir() as temp:
        modpath = join(temp.dpath, 'testmod.py')
        text = ub.codeblock(
            '''
            a = 'value'
            ''')
        ub.writeto(modpath, text)
        assert temp.dpath not in sys.path
        module = ub.import_module_from_path(modpath)
        assert temp.dpath not in sys.path, 'pythonpath should remain clean'
        assert module.a == 'value'
        assert module.__file__ == modpath
        assert module.__name__ == 'testmod'
        assert 'testmod' in sys.modules


def test_import_modpath_package():
    assert '_tmproot.sub1.sub2.testmod' not in sys.modules

    temp = ub.TempDir().start()
    # with ub.TempDir() as temp:
    if True:
        dpath = temp.dpath

        # Create a dummy package heirachy
        root = ub.ensuredir((dpath, '_tmproot'))
        sub1 = ub.ensuredir((root, 'sub1'))
        sub2 = ub.ensuredir((sub1, 'sub2'))

        ub.touch(join(root, '__init__.py'))
        ub.touch(join(sub1, '__init__.py'))
        ub.touch(join(sub2, '__init__.py'))

        modpath = join(sub2, 'testmod.py')
        text = ub.codeblock(
            '''
            a = 'value'
            ''')
        ub.writeto(modpath, text)
        assert temp.dpath not in sys.path
        module = ub.import_module_from_path(modpath)
        assert temp.dpath not in sys.path, 'pythonpath should remain clean'
        assert module.a == 'value'
        assert module.__file__ == modpath
        assert module.__name__ == '_tmproot.sub1.sub2.testmod'
        assert '_tmproot.sub1.sub2.testmod' in sys.modules
        assert '_tmproot.sub1.sub2' in sys.modules
        assert '_tmproot' in sys.modules


def test_import_modname_builtin():
    module = ub.import_module_from_name('ast')
    import ast
    assert module is ast


if __name__ == '__main__':
    r"""
    CommandLine:
        pytest ubelt/tests/test_import.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
