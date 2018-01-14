# -*- coding: utf-8 -*-
"""
New static version of dynamic_make_init.py

Usage:
    To autogenerate a module on demand, its useful to keep a doctr comment
    in the __init__ file like this:
        python -c "import ubelt._internal as a; a.autogen_init('<your_module_path_or_name>')"


TODO:
    - [ ] Move to ubelt.tools, rename to autoinit
    - [ ] Add profiler to ubelt.tools
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import ast
import sys
import textwrap
from collections import OrderedDict, defaultdict
from os.path import join, exists, isfile, splitext, basename, dirname
from six.moves import builtins


class GlobalNameVisitor(ast.NodeVisitor):
    """
    Parses global function class and variable names

    References:
        # For other visit_<classname> values see
        http://greentreesnakes.readthedocs.io/en/latest/nodes.html

    Notes:
        adapted from my static_analysis library

    TODO:
        - [ ] handle names defined in all branches of conditional statements
        - [ ] handle deleted names

    CommandLine:
        python -m ubelt._internal.static_autogen GlobalNameVisitor

    Example:
        >>> import ubelt as ub
        >>> source = ub.codeblock(
        ...    '''
        ...    a = 3
        ...    def foo():
        ...        def subfunc():
        ...            pass
        ...    def bar():
        ...        pass
        ...    class Spam(object):
        ...        def eggs():
        ...            pass
        ...    ''')
        >>> self = GlobalNameVisitor.parse(source)
        >>> assert self.global_types['func'] == ['foo', 'bar']
        >>> assert self.global_types['class'] == ['Spam']
        >>> assert self.global_types['assign'] == ['a']
        >>> assert self.global_types['method'] == ['Spam.eggs']
    """
    def __init__(self):
        super(GlobalNameVisitor, self).__init__()
        self.global_nodes = OrderedDict()
        self.global_types = defaultdict(list)

        # book keeping
        self._current_classname = None

    @classmethod
    def parse(GlobalNameVisitor, source):
        self = GlobalNameVisitor()

        source_utf8 = source.encode('utf8')
        pt = ast.parse(source_utf8)

        self.visit(pt)
        return self

    def register_global(self, name, type, node):
        self.global_nodes[name] = node
        self.global_types[type].append(name)

    def visit_FunctionDef(self, node):
        if self._current_classname is None:
            callname = node.name
            self.register_global(callname, 'func', node)
        else:
            callname = self._current_classname + '.' + node.name
            self.register_global(callname, 'method', node)

    def visit_ClassDef(self, node):
        if self._current_classname is None:
            callname = node.name
            self._current_classname = callname
            self.register_global(callname, 'class', node)

            self.generic_visit(node)
            self._current_classname = None

    def visit_Assign(self, node):
        if self._current_classname is None:
            for target in node.targets:
                if hasattr(target, 'id'):
                    self.register_global(target.id, 'assign', node)
        self.generic_visit(node)

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare):  # pragma: nobranch
            try:
                if all([
                    isinstance(node.test.ops[0], ast.Eq),
                    node.test.left.id == '__name__',
                    node.test.comparators[0].s == '__main__',
                ]):
                    # Ignore main block
                    return
            except Exception:  # nocover
                pass
        self.generic_visit(node)  # nocover

    # def visit_Module(self, node):
    #     self.generic_visit(node)

    # def visit_ExceptHandler(self, node):
    #     pass

    # def visit_TryFinally(self, node):
    #     pass

    # def visit_TryExcept(self, node):
    #     pass

    # def visit_Try(self, node):
    #     TODO: parse a node only if it is visible in all cases
    #     pass
    #     # self.generic_visit(node)  # nocover


def _parse_static_node_value(node):
    """
    Extract a constant value from a node if possible

    Notes:
        taken from my static_analysis library
    """
    if isinstance(node, ast.Num):
        value = node.n
    elif isinstance(node, ast.Str):
        value = node.s
    elif isinstance(node, ast.List):
        value = list(map(_parse_static_node_value, node.elts))
    elif isinstance(node, ast.Tuple):
        value = tuple(map(_parse_static_node_value, node.elts))
    elif isinstance(node, (ast.Dict)):
        keys = map(_parse_static_node_value, node.keys)
        values = map(_parse_static_node_value, node.values)
        value = OrderedDict(zip(keys, values))
    else:
        raise TypeError('Cannot parse a static value from non-static node '
                        'of type: {!r}'.format(type(node)))
    return value


def parse_static_value(key, source=None, fpath=None):
    """
    Statically parse a constant variable's value from python code.

    Notes:
        taken from my static_analysis library

    Args:
        key (str): name of the variable
        source (str): python text
        fpath (str): filepath to read if source is not specified

    Example:
        >>> key = 'foo'
        >>> source = 'foo = 123'
        >>> assert parse_static_value(key, source=source) == 123
        >>> source = 'foo = "123"'
        >>> assert parse_static_value(key, source=source) == '123'
        >>> source = 'foo = [1, 2, 3]'
        >>> assert parse_static_value(key, source=source) == [1, 2, 3]
        >>> source = 'foo = (1, 2, "3")'
        >>> assert parse_static_value(key, source=source) == (1, 2, "3")
        >>> source = 'foo = {1: 2, 3: 4}'
        >>> assert parse_static_value(key, source=source) == {1: 2, 3: 4}
        >>> #parse_static_value('bar', source=source)
        >>> #parse_static_value('bar', source='foo=1; bar = [1, foo]')
    """
    if source is None:  # pragma: no branch
        with open(fpath, 'rb') as file_:
            source = file_.read().decode('utf-8')
    pt = ast.parse(source)

    class AssignentVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if getattr(target, 'id', None) == key:
                    self.value = _parse_static_node_value(node.value)

    sentinal = object()
    visitor = AssignentVisitor()
    visitor.value = sentinal
    visitor.visit(pt)
    if visitor.value is sentinal:
        raise NameError('No static variable named {!r}'.format(key))
    return visitor.value


def _platform_pylib_ext():  # nocover
    if sys.platform.startswith('linux'):
        pylib_ext = '.so'
    elif sys.platform.startswith('win32'):
        pylib_ext = '.pyd'
    elif sys.platform.startswith('darwin'):
        pylib_ext = '.dylib'
    else:
        pylib_ext = '.so'
    return pylib_ext


def package_modpaths(pkgpath, with_pkg=False, with_mod=True, followlinks=True,
                     recursive=True):
    r"""
    Finds sub-packages and sub-modules belonging to a package.

    Notes:
        taken from my static_analysis library

    Args:
        pkgpath (str): path to a module or package
        with_pkg (bool): includes package __init__ files (default = False)
        with_mod (bool): if True includes module files (default = True)
        exclude (list): ignores any module that matches any of these patterns
        recursive (bool): if False, then only child modules are included

    Yields:
        str: module names belonging to the package

    References:
        http://stackoverflow.com/questions/1707709/list-modules-in-py-package

    Example:
        >>> from ubelt.util_import import modname_to_modpath, modpath_to_modname
        >>> pkgpath = modname_to_modpath('xdoctest')
        >>> paths = list(package_modpaths(pkgpath))
        >>> names = list(map(modpath_to_modname, paths))
        >>> assert 'xdoctest.core' in names
        >>> assert 'xdoctest.__main__' in names
        >>> assert 'xdoctest' not in names
        >>> print('\n'.join(names))
    """
    if isfile(pkgpath):
        # If input is a file, just return it
        yield pkgpath
    else:
        if with_pkg:
            root_path = join(pkgpath, '__init__.py')
            if exists(root_path):
                yield root_path

        valid_exts = ['.py', _platform_pylib_ext()]
        for dpath, dnames, fnames in os.walk(pkgpath, followlinks=followlinks):
            ispkg = exists(join(dpath, '__init__.py'))
            if ispkg:
                if with_mod:
                    for fname in fnames:
                        if splitext(fname)[1] in valid_exts:
                            # dont yield inits. Handled in pkg loop.
                            if fname != '__init__.py':
                                path = join(dpath, fname)
                                yield path
                if with_pkg:
                    for dname in dnames:
                        path = join(dpath, dname, '__init__.py')
                        if exists(path):
                            yield path
            else:
                # Stop recursing when we are out of the package
                del dnames[:]
            if not recursive:
                break


def autogen_init(modpath_or_name, imports=None, attrs=True, use_all=True,
                 dry=False):
    """
    Autogenerates imports for a package __init__.py file.

    Args:
        modpath_or_name (str):
            path to or name of a package module.  The path should reference the
            dirname not the __init__.py file.  If specified by name, must be
            findable from the PYTHONPATH.

        imports (list):
            if specified, then only these specific submodules are used in
            package generation. Otherwise, all non underscore prefixed modules
            are used.

        attrs (bool):
            if False, then module attributes will not be imported.

        use_all (bool):
            if False the `__all__` attribute is ignored.

        dry (bool):
            if True, the autogenerated string is not written

    Notes:
        This will partially override the __init__ file!

        By default everything up to the last comment / __future__ import is
        preserved, and everything after is overriden.  For more fine grained
        control, you can specify XML-like `# <AUTOGEN_INIT>` and `#
        </AUTOGEN_INIT>` comments around the volitle area. If specified only
        the area between these tags will be overwritten.

        To autogenerate a module on demand, its useful to keep a doctr comment
        in the __init__ file like this:
            python -c "import ubelt._internal as a; a.autogen_init('<your_module_path_or_name>')"
    """
    from ubelt.util_import import modname_to_modpath
    if exists(modpath_or_name):
        modpath = modpath_or_name
    else:
        modpath = modname_to_modpath(modpath_or_name)
        if modpath is None:
            raise ValueError('Invalid module {}'.format(modpath_or_name))
    modpath = _normalize_modpath(modpath)
    print('modpath = {!r}'.format(modpath))
    initstr = init_execstr(modpath, imports=imports, attrs=attrs,
                               use_all=use_all)
    if dry:
        print(initstr)
    else:
        _autogen_init_write(modpath, initstr)


def _normalize_modpath(modpath):
    """
    Returns the directory of the package if modpath is an __init__ file
    """
    if isfile(modpath):
        if basename(modpath).startswith('__init__.'):
            modpath = dirname(modpath)
    return modpath


def init_execstr(modpath, imports=None, attrs=True, use_all=True):
    """
    Creates an executable string to be placed in an __init__ file

    SeeAlso:
        autogen_init
    """
    # from xdoctest import static_analysis as static
    modpath = _normalize_modpath(modpath)
    if imports is None:
        # the __init__ file may have a variable describing the correct imports
        # should imports specify the name of this variable or should it always
        # be GLOBAL_MODULES?
        with open(join(modpath, '__init__.py'), 'r') as file:
            source = file.read()
        varname = 'GLOBAL_MODULES'
        try:
            imports = static.parse_static_value(varname, source)
        except NameError:
            pass

    modname, imports, from_imports = _static_parse_imports(modpath,
                                                           imports=imports,
                                                           use_all=use_all)
    if not attrs:
        from_imports = []
    initstr = _initstr(modname, imports, from_imports, withheader=False)
    return initstr


def _static_parse_imports(modpath, imports=None, use_all=True):
    # from ubelt.meta import static_analysis as static
    # TODO: port some of this functionality over
    # from xdoctest import static_analysis as static
    from ubelt.util_import import modname_to_modpath, modpath_to_modname
    modname = modpath_to_modname(modpath)
    if imports is not None:
        import_paths = {
            m: modname_to_modpath(modname + '.' + m, hide_init=False)
            for m in imports
        }
    else:
        imports = []
        import_paths = {}
        for sub_modpath in package_modpaths(modpath, with_pkg=True,
                                            recursive=False):
            # print('sub_modpath = {!r}'.format(sub_modpath))
            sub_modname = modpath_to_modname(sub_modpath)
            rel_modname = sub_modname[len(modname) + 1:]
            if rel_modname.startswith('_'):
                continue
            if not rel_modname:
                continue
            import_paths[rel_modname] = sub_modpath
            imports.append(rel_modname)
        imports = sorted(imports)

    from_imports = []
    for rel_modname in imports:
        sub_modpath = import_paths[rel_modname]
        with open(sub_modpath, 'r') as file:
            source = file.read()
        valid_callnames = None
        if use_all:
            try:
                valid_callnames = parse_static_value('__all__', source)
            except NameError:
                pass
        if valid_callnames is None:
            # The __all__ variable is not specified or we dont care
            top_level = GlobalNameVisitor.parse(source)
            attrnames = (top_level.global_types['assign'] +
                         top_level.global_types['class'] +
                         top_level.global_types['func'])
            # list of names we wont export by default
            invalid_callnames = dir(builtins)
            valid_callnames = []
            for attr in attrnames:
                if '.' in attr or attr.startswith('_'):
                    continue
                if attr in invalid_callnames:
                    continue
                valid_callnames.append(attr)
        from_imports.append((rel_modname, sorted(valid_callnames)))
    return modname, imports, from_imports


def _autogen_init_write(modpath, initstr):
    from ubelt import util_str
    from os.path import join, exists
    #print(new_else)
    # Get path to init file so we can overwrite it
    init_fpath = join(modpath, '__init__.py')
    print('attempting to update: %r' % init_fpath)
    assert exists(init_fpath)
    with open(init_fpath, 'r') as file_:
        lines = file_.readlines()

    # write after the last multiline comment, unless explicit tags are defined
    startline = 0
    endline = len(lines)
    explicit = False
    init_indent = ''
    for lineno, line in enumerate(lines):
        if not explicit and line.strip() in ['"""', "'''"]:
            startline = lineno + 1
        if not explicit and line.strip().startswith('from __future__'):
            startline = lineno + 1
        if not explicit and line.strip().startswith('#'):
            startline = lineno + 1
        if line.strip().startswith('# <AUTOGEN_INIT>'):  # allow tags too
            init_indent = line[:line.find('#')]
            explicit = True
            startline = lineno + 1
        if explicit and line.strip().startswith('# </AUTOGEN_INIT>'):
            endline = lineno
    initstr_ = util_str.indent(initstr, init_indent) + '\n'

    assert startline <= endline
    new_lines = lines[:startline] + [initstr_] + lines[endline:]
    print('startline = {!r}'.format(startline))
    print('endline = {!r}'.format(endline))

    print('writing updated file: %r' % init_fpath)
    new_text = ''.join(new_lines).rstrip()
    print(new_text)
    with open(init_fpath, 'w') as file_:
        file_.write(new_text)


def _initstr(modname, imports, from_imports, withheader=True):
    """ Calls the other string makers """
    header         = _make_module_header() if withheader else ''
    import_str     = _make_imports_str(imports, modname)
    fromimport_str = _make_fromimport_str(from_imports, modname)
    initstr = '\n'.join([str_ for str_ in [
        header,
        import_str,
        fromimport_str,
    ] if len(str_) > 0])
    return initstr


def _make_module_header():
    return '\n'.join([
        '# flake8:' + ' noqa',  # the plus prevents it from triggering on this file
        'from __future__ import absolute_import, division, print_function, unicode_literals'])


def _make_imports_str(imports, rootmodname='.'):
    imports_fmtstr = 'from {rootmodname} import %s'.format(
        rootmodname=rootmodname)
    return '\n'.join([imports_fmtstr % (name,) for name in imports])


def _make_fromimport_str(from_imports, rootmodname='.'):
    if rootmodname == '.':
        # dot is already taken care of in fmtstr
        rootmodname = ''
    def _pack_fromimport(tup):
        name, fromlist = tup[0], tup[1]
        from_module_str = 'from {rootmodname}.{name} import ('.format(
            rootmodname=rootmodname, name=name)
        newline_prefix = (' ' * len(from_module_str))
        if len(fromlist) > 0:
            rawstr = from_module_str + ', '.join(fromlist) + ',)'
        else:
            rawstr = ''

        # not sure why this isn't 76? >= maybe?
        packstr = '\n'.join(textwrap.wrap(rawstr, break_long_words=False,
                                          width=79, initial_indent='',
                                          subsequent_indent=newline_prefix))
        return packstr
    from_str = '\n'.join(map(_pack_fromimport, from_imports))
    return from_str
