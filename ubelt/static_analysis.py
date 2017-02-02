# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ast
from collections import defaultdict


class TopLevelDocstrVisitor(ast.NodeVisitor):
    """
    Other visit_<classname> values:
        http://greentreesnakes.readthedocs.io/en/latest/nodes.html
    """
    def __init__(self):
        super(TopLevelDocstrVisitor, self).__init__()
        self.func_docstrs = defaultdict(list)
        self.class_docstrs = defaultdict(list)
        self.method_docstrs = defaultdict(lambda: defaultdict(list))
        self._current_classname = None

    def visit_FunctionDef(self, node):
        funcname = node.name
        docstr = ast.get_docstring(node)
        if self._current_classname is None:
            self.func_docstrs[funcname].append(docstr)
        else:
            self.method_docstrs[self._current_classname][funcname].append(docstr)

    def visit_ClassDef(self, node):
        classname = node.name
        docstr = ast.get_docstring(node)
        self.class_docstrs[classname].append(docstr)
        self._current_classname = classname
        self.generic_visit(node)
        self._current_classname = None

    def visit_Assign(self, node):
        # print('VISIT FunctionDef node = %r' % (node,))
        # print('VISIT FunctionDef node = %r' % (node.__dict__,))
        # for target in node.targets:
        #     print('target.id = %r' % (target.id,))
        # print('node.value = %r' % (node.value,))
        # TODO: assign constants to
        # self.const_lookup
        ast.NodeVisitor.generic_visit(self, node)


def parse_toplevel(source):
    r"""
    Args:
        source (?):

    CommandLine:
        python -m ubelt.static_analysis parse_toplevel

    Example:
        >>> # DISABLE_DOCTEST
        >>> from ubelt.static_analysis import *  # NOQA
        >>> import ubelt.static_analysis
        >>> fpath = ubelt.static_analysis.__file__.replace('.pyc', '.py')
        >>> import utool as ut
        >>> source = ut.readfrom(fpath)
        >>> parse_toplevel(source)
    """
    pt = ast.parse(source.encode('utf-8'))
    self = TopLevelDocstrVisitor()
    self.visit(pt)
    import utool as ut
    print('self.func_docstrs = %s' % (ut.repr4(self.func_docstrs),))
    print('self.class_docstrs = %s' % (ut.repr4(self.class_docstrs),))
    print('self.method_docstrs = %s' % (ut.repr4(self.method_docstrs),))


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.static_analysis
        python -m ubelt.static_analysis --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
