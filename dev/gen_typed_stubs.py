"""
MOVED TO xdev:
    SEE xdev
    xdev doctypes ubelt


Script for auto-generating pyi type extension files from google-style
docstrings

Requirements:
    pip install mypy autoflake yapf

CommandLine:
    # Run script to parse google-style docstrings and write pyi files
    python ~/code/ubelt/dev/gen_typed_stubs.py

    # Run mypy to check that type annotations are correct
    mypy ubelt
"""
from mypy.stubgen import (StubGenerator, find_self_initializers, FUNC, EMPTY, METHODS_WITH_RETURN_VALUE,)
import sys

from typing import (List, Dict, Optional)
from mypy.nodes import (
    # Expression, IntExpr, UnaryExpr, StrExpr, BytesExpr, NameExpr, FloatExpr, MemberExpr,
    # TupleExpr, ListExpr, ComparisonExpr, CallExpr, IndexExpr, EllipsisExpr,
    # ClassDef, MypyFile, Decorator, AssignmentStmt, TypeInfo,
    # IfStmt, ImportAll, ImportFrom, Import,
    FuncDef,
    # FuncBase, Block,
    # Statement, OverloadedFuncDef, ARG_POS,
    ARG_STAR, ARG_STAR2,
    # ARG_NAMED,
)
# from mypy.stubgenc import generate_stub_for_c_module
# from mypy.stubutil import (
#     default_py2_interpreter, CantImport, generate_guarded,
#     walk_packages, find_module_path_and_all_py2, find_module_path_and_all_py3,
#     report_missing, fail_missing, remove_misplaced_type_comments, common_dir_prefix
# )
from mypy.types import (
    # Type, TypeStrVisitor,
    CallableType,
    # UnboundType, NoneType, TupleType, TypeList, Instance,
    AnyType,
    get_proper_type
)
from mypy.traverser import (
    all_yield_expressions,
    has_return_statement,
    has_yield_expression
)


def generate_typed_stubs():
    """
    Attempt to use google-style docstrings, xdoctest, and mypy to generate
    typed stub files.

    pyfile mypy.stubgen
    # Delete compiled verisons so we can hack it

    # THIS DOES NOT WORK
    # MYPY_DPTH=$(python -c "import mypy, pathlib; print(pathlib.Path(mypy.__file__).parent)")
    # echo $MYPY_DPTH
    # ls $MYPY_DPTH/*.so
    # rm $MYPY_DPTH/*.so

    # ls $VIRTUAL_ENV/lib/*/site-packages/mypy/*.so
    # rm $VIRTUAL_ENV/lib/*/site-packages/mypy/*.so
    # rm ~/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/mypy/*.cpython-38-x86_64-linux-gnu.so

    # This works I think?
    if [[ ! -e "$HOME/code/mypy" ]];  then
        git clone https://github.com/python/mypy.git $HOME/code/mypy
    fi
    (cd $HOME/code/mypy && git pull)
    pip install -e $HOME/code/mypy


    pip install MonkeyType

    monkeytype run run_tests.py
    monkeytype stub ubelt.util_dict

    from typing import TypeVar
    from mypy.applytype import get_target_type
    z = TypeVar('Iterable')
    get_target_type(z)

    from mypy.expandtype import expand_type
    expand_type(z, env={})

    from mypy.types import get_proper_type
    get_proper_type(z)
    get_proper_type(dict)
    import typing
    get_proper_type(typing.Iterable)

    from mypy.types import deserialize_type, UnboundType
    import mypy.types as mypy_types
    z = UnboundType('Iterable')
    get_proper_type(dict)

    from mypy.fastparse import parse_type_string
    parse_type_string('dict', 'dict', 0, 0)
    z = parse_type_string('typing.Iterator', 'Any', 0, 0)
    get_proper_type(z)

    """
    import pathlib
    import ubelt
    import os
    import autoflake
    import yapf
    from mypy import stubgen
    from mypy import defaults
    from xdoctest import static_analysis
    from os.path import dirname, join
    ubelt_dpath = dirname(ubelt.__file__)

    for p in pathlib.Path(ubelt_dpath).glob('*.pyi'):
        p.unlink()
    files = list(static_analysis.package_modpaths(ubelt_dpath, recursive=True, with_libs=1, with_pkg=0))
    files = [f for f in files if 'deprecated' not in f]
    # files = [join(ubelt_dpath, 'util_dict.py')]

    options = stubgen.Options(
        pyversion=defaults.PYTHON3_VERSION,
        no_import=True,
        doc_dir='',
        search_path=[],
        interpreter=sys.executable,
        ignore_errors=False,
        parse_only=True,
        include_private=False,
        output_dir=dirname(ubelt_dpath),
        modules=[],
        packages=[],
        files=files,
        verbose=False,
        quiet=False,
        export_less=True)
    # generate_stubs(options)

    mypy_opts = stubgen.mypy_options(options)
    py_modules, c_modules = stubgen.collect_build_targets(options, mypy_opts)

    # Collect info from docs (if given):
    sigs = class_sigs = None  # type: Optional[Dict[str, str]]
    if options.doc_dir:
        sigs, class_sigs = stubgen.collect_docs_signatures(options.doc_dir)

    # Use parsed sources to generate stubs for Python modules.
    stubgen.generate_asts_for_modules(py_modules, options.parse_only, mypy_opts, options.verbose)

    for mod in py_modules:
        assert mod.path is not None, "Not found module was not skipped"
        target = mod.module.replace('.', '/')
        if os.path.basename(mod.path) == '__init__.py':
            target += '/__init__.pyi'
        else:
            target += '.pyi'
        target = join(options.output_dir, target)
        files.append(target)
        with stubgen.generate_guarded(mod.module, target, options.ignore_errors, options.verbose):
            stubgen.generate_stub_from_ast(mod, target, options.parse_only,
                                           options.pyversion,
                                           options.include_private,
                                           options.export_less)

            gen = ExtendedStubGenerator(mod.runtime_all, pyversion=options.pyversion,
                                        include_private=options.include_private,
                                        analyzed=not options.parse_only,
                                        export_less=options.export_less)
            assert mod.ast is not None, "This function must be used only with analyzed modules"
            mod.ast.accept(gen)
            # print('gen.import_tracker.required_names = {!r}'.format(gen.import_tracker.required_names))
            # print(gen.import_tracker.import_lines())

            print('mod.path = {!r}'.format(mod.path))

            known_one_letter_types = {
                # 'T', 'K', 'A', 'B', 'C', 'V',
                'DT', 'KT', 'VT', 'T'
            }
            for type_var_name in set(gen.import_tracker.required_names) & set(known_one_letter_types):
                gen.add_typing_import('TypeVar')
                # gen.add_import_line('from typing import {}\n'.format('TypeVar'))
                gen._output = ['{} = TypeVar("{}")\n'.format(type_var_name, type_var_name)] + gen._output

            custom_types = {'Hasher'}
            for type_var_name in set(gen.import_tracker.required_names) & set(custom_types):
                gen.add_typing_import('TypeVar')
                # gen.add_import_line('from typing import {}\n'.format('TypeVar'))
                gen._output = ['{} = TypeVar("{}")\n'.format(type_var_name, type_var_name)] + gen._output

            # Hack for specific module
            # if mod.path.endswith('util_path.py'):
            #     gen.add_typing_import('TypeVar')
            #     # hack for variable inheritence
            #     gen._output = ['import pathlib\nimport os\n', "_PathBase = pathlib.WindowsPath if os.name == 'nt' else pathlib.PosixPath\n"] + gen._output

            text = ''.join(gen.output())
            # Hack to remove lines caused by Py2 compat
            text = text.replace('Generator = object\n', '')
            text = text.replace('select = NotImplemented\n', '')
            text = text.replace('iteritems: Any\n', '')
            text = text.replace('text_type = str\n', '')
            text = text.replace('text_type: Any\n', '')
            text = text.replace('string_types: Any\n', '')
            text = text.replace('PY2: Any\n', '')
            text = text.replace('__win32_can_symlink__: Any\n', '')
            # text = text.replace('odict = OrderedDict', '')
            # text = text.replace('ddict = defaultdict', '')

            if mod.path.endswith('util_path.py'):
                # hack for forward reference
                text = text.replace(' -> Path:', " -> 'Path':")
                text = text.replace('class Path(_PathBase)', "class Path")

            # Format the PYI file nicely
            text = autoflake.fix_code(text, remove_unused_variables=True,
                                      remove_all_unused_imports=True)

            # import autopep8
            # text = autopep8.fix_code(text, options={
            #     'aggressive': 0,
            #     'experimental': 0,
            # })

            style = yapf.yapf_api.style.CreatePEP8Style()
            text, _ = yapf.yapf_api.FormatCode(
                text,
                filename='<stdin>',
                style_config=style,
                lines=None,
                verify=False)

            # print(text)

            # Write output to file.
            subdir = dirname(target)
            if subdir and not os.path.isdir(subdir):
                os.makedirs(subdir)
            with open(target, 'w') as file:
                file.write(text)


def hack_annotated_type_from_docstring():
    pass


class ExtendedStubGenerator(StubGenerator):

    def visit_func_def(self, o: FuncDef, is_abstract: bool = False,
                       is_overload: bool = False) -> None:
        if (self.is_private_name(o.name, o.fullname)
                or self.is_not_in_all(o.name)
                or (self.is_recorded_name(o.name) and not is_overload)):
            self.clear_decorators()
            return
        if not self._indent and self._state not in (EMPTY, FUNC) and not o.is_awaitable_coroutine:
            self.add('\n')
        if not self.is_top_level():
            self_inits = find_self_initializers(o)
            for init, value in self_inits:
                if init in self.method_names:
                    # Can't have both an attribute and a method/property with the same name.
                    continue
                init_code = self.get_init(init, value)
                if init_code:
                    self.add(init_code)
        # dump decorators, just before "def ..."
        for s in self._decorators:
            self.add(s)
        self.clear_decorators()
        self.add("%s%sdef %s(" % (self._indent, 'async ' if o.is_coroutine else '', o.name))
        self.record_name(o.name)
        # import ubelt as ub
        # if o.name == 'dzip':
        #     import xdev
        #     xdev.embed()

        def _hack_for_info(info):
            if info['type'] is None:
                return
            for typing_arg in ['Iterable', 'Callable', 'Dict',
                               'List', 'Union', 'Type', 'Mapping',
                               'Tuple', 'Optional', 'Sequence',
                               'Iterator', 'Set', 'Dict']:
                if typing_arg in info['type']:
                    self.add_typing_import(typing_arg)
                    self.add_import_line('from typing import {}\n'.format(typing_arg))

            if 'io.' in info['type']:
                self.add_import_line('import io\n')

            if 'datetime.' in info['type']:
                self.add_import_line('import datetime\n')

            if '|' in info['type']:
                self.add_typing_import('Union')
                self.add_import_line('from typing import {}\n'.format('Union'))

            if 'ModuleType' in info['type']:
                self.add_import_line('from types import {}\n'.format('ModuleType'))
                # types.ModuleType

            if 'hashlib._hashlib' in info['type']:
                self.add_import_line('import hashlib._hashlib\n')

            if 'PathLike' in info['type']:
                self.add_import_line('from os import {}\n'.format('PathLike'))

            if 'concurrent.futures.Future' in info['type']:
                self.add_import_line('import concurrent.futures\n')

            if info['type'].startswith('callable'):
                # TODO: generalize, allow the "callable" func to be transformed
                # into the type if given in the docstring
                self.add_typing_import('Callable')
                info['type'] = info['type'].replace('callable', 'Callable')
                self.add_import_line('from typing import {}\n'.format(typing_arg))

        name_to_parsed_docstr_info = {}
        return_parsed_docstr_info = None
        fullname = o.name
        if getattr(self, '_IN_CLASS', None) is not None:
            fullname = self._IN_CLASS + '.' + o.name

        from ubelt import util_import
        curr = util_import.import_module_from_name(self.module)
        # curr = sys.modules.get(self.module)
        # print('o.name = {!r}'.format(o.name))
        # print('fullname = {!r}'.format(fullname))
        for part in fullname.split('.'):
            # print('part = {!r}'.format(part))
            # print('curr = {!r}'.format(curr))
            curr = getattr(curr, part, None)
        # print('curr = {!r}'.format(curr))
        real_func = curr

        # print('real_func = {!r}'.format(real_func))
        # if o.name == 'dict_union':
        #     import xdev
        #     xdev.embed()
        if real_func is not None and real_func.__doc__ is not None:
            from mypy import fastparse
            from xdoctest.docstr import docscrape_google
            parsed_args = None
            # parsed_ret = None

            blocks = docscrape_google.split_google_docblocks(real_func.__doc__)
            for key, block in blocks:
                lines = block[0]
                if key == 'Returns':
                    for retdict in docscrape_google.parse_google_retblock(lines):
                        _hack_for_info(retdict)
                        return_parsed_docstr_info = (key, retdict['type'])
                if key == 'Yields':
                    for retdict in docscrape_google.parse_google_retblock(lines):
                        _hack_for_info(retdict)
                        return_parsed_docstr_info = (key, retdict['type'])
                if key == 'Args':
                    # hack for *args
                    lines = '\n'.join([line.lstrip('*') for line in lines.split('\n')])
                    # print('lines = {!r}'.format(lines))
                    parsed_args = list(docscrape_google.parse_google_argblock(lines))
                    for info in parsed_args:
                        _hack_for_info(info)
                        name = info['name'].replace('*', '')
                        name_to_parsed_docstr_info[name] = info

            parsed_rets = list(docscrape_google.parse_google_returns(real_func.__doc__))
            ret_infos = []
            for info in parsed_rets:
                try:
                    got = fastparse.parse_type_string(info['type'], 'Any', 0, 0)

                    ret_infos.append(got)
                except Exception:
                    pass

        # print('o = {!r}'.format(o))
        # print('o.arguments = {!r}'.format(o.arguments))
        args: List[str] = []
        for i, arg_ in enumerate(o.arguments):
            var = arg_.variable
            kind = arg_.kind
            name = var.name
            annotated_type = (o.unanalyzed_type.arg_types[i]
                              if isinstance(o.unanalyzed_type, CallableType) else None)

            if annotated_type is None:
                if name in name_to_parsed_docstr_info:
                    name = name.replace('*', '')
                    doc_type_str = name_to_parsed_docstr_info[name].get('type', None)
                    if doc_type_str is not None:
                        doc_type_str = doc_type_str.split(', default')[0]
                        # annotated_type = doc_type_str
                        # import mypy.types as mypy_types
                        from mypy import fastparse
                        # globals_ = {**mypy_types.__dict__}
                        try:
                            # # got = mypy_types.deserialize_type(doc_type_str)
                            # got = eval(doc_type_str, globals_)
                            # got = mypy_types.get_proper_type(got)
                            # got = mypy_types.Iterable
                            got = fastparse.parse_type_string(doc_type_str, 'Any', 0, 0)
                        except Exception as ex:
                            print('ex = {!r}'.format(ex))
                            print('Failed to parse doc_type_str = {!r}'.format(doc_type_str))
                        else:
                            annotated_type = got
                            # print('PARSED: annotated_type = {!r}'.format(annotated_type))
                        # print('annotated_type = {!r}'.format(annotated_type))

            # I think the name check is incorrect: there are libraries which
            # name their 0th argument other than self/cls
            is_self_arg = i == 0 and name == 'self'
            is_cls_arg = i == 0 and name == 'cls'
            annotation = ""
            if annotated_type and not is_self_arg and not is_cls_arg:
                # Luckily, an argument explicitly annotated with "Any" has
                # type "UnboundType" and will not match.
                if not isinstance(get_proper_type(annotated_type), AnyType):
                    annotation = ": {}".format(self.print_annotation(annotated_type))
            if arg_.initializer:
                if kind.is_named() and not any(arg.startswith('*') for arg in args):
                    args.append('*')
                if not annotation:
                    typename = self.get_str_type_of_node(arg_.initializer, True, False)
                    if typename == '':
                        annotation = '=...'
                    else:
                        annotation = ': {} = ...'.format(typename)
                else:
                    annotation += ' = ...'
                arg = name + annotation
            elif kind == ARG_STAR:
                arg = '*%s%s' % (name, annotation)
            elif kind == ARG_STAR2:
                arg = '**%s%s' % (name, annotation)
            else:
                arg = name + annotation
            args.append(arg)
        retname = None
        if o.name != '__init__' and isinstance(o.unanalyzed_type, CallableType):
            if isinstance(get_proper_type(o.unanalyzed_type.ret_type), AnyType):
                # Luckily, a return type explicitly annotated with "Any" has
                # type "UnboundType" and will enter the else branch.
                retname = None  # implicit Any
            else:
                retname = self.print_annotation(o.unanalyzed_type.ret_type)
        elif isinstance(o, FuncDef) and (o.is_abstract or o.name in METHODS_WITH_RETURN_VALUE):
            # Always assume abstract methods return Any unless explicitly annotated. Also
            # some dunder methods should not have a None return type.
            retname = None  # implicit Any
        elif has_yield_expression(o):
            self.add_abc_import('Generator')
            yield_name = 'None'
            send_name = 'None'
            return_name = 'None'
            for expr, in_assignment in all_yield_expressions(o):
                if expr.expr is not None and not self.is_none_expr(expr.expr):
                    self.add_typing_import('Any')
                    yield_name = 'Any'
                if in_assignment:
                    self.add_typing_import('Any')
                    send_name = 'Any'
            if has_return_statement(o):
                self.add_typing_import('Any')
                return_name = 'Any'
            generator_name = self.typing_name('Generator')
            if return_parsed_docstr_info is not None:
                yield_name = return_parsed_docstr_info[1]
            retname = f'{generator_name}[{yield_name}, {send_name}, {return_name}]'
            # print('o.name = {}'.format(ub.repr2(o.name, nl=1)))
            # print('retname = {!r}'.format(retname))
            # print('retfield = {!r}'.format(retfield))
        elif not has_return_statement(o) and not is_abstract:
            retname = 'None'

        if retname is None:
            if return_parsed_docstr_info is not None:
                retname = return_parsed_docstr_info[1]

        retfield = ''
        if retname is not None:
            retfield = ' -> ' + retname

        self.add(', '.join(args))
        self.add("){}: ...\n".format(retfield))
        self._state = FUNC

    def visit_class_def(self, o) -> None:
        self._IN_CLASS = o.name
        # print('o.name = {!r}'.format(o.name))
        ret = super().visit_class_def(o)
        self._IN_CLASS = None
        return ret

if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/gen_typed_stubs.py
    """
    generate_typed_stubs()
