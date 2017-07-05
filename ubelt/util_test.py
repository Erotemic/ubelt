# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import warnings
import sys
import six
from ubelt import util_mixins
from ubelt import util_str


# prevents doctest import * from working
# __all__ = [
#     'doctest_package'
# ]


def parse_src_want(docsrc):
    """
    Breaks into sections of source code and result checks

    Args:
        docsrc (str):

    CommandLine:
        python -m util_test parse_src_want

    Example:
        >>> from ubelt.util_test import *  # NOQA
        >>> from ubelt.meta import docscrape_google
        >>> import inspect
        >>> docstr = inspect.getdoc(parse_src_want)
        >>> blocks = dict(docscrape_google.split_google_docblocks(docstr))
        >>> docsrc = blocks['Example']
        >>> src, want = parse_src_want(docsrc)
        >>> 'I want to see this str'
        I want to see this str

    DisableExample:
        >>> from ubelt.util_test import *  # NOQA
        >>> from ubelt.meta import docscrape_google
        >>> import inspect
        >>> docstr = inspect.getdoc(parse_src_want)
        >>> blocks = dict(docscrape_google.split_google_docblocks(docstr))
        >>> str = (
            '''
            TODO: be able to parse docstrings like this.
            ''')
        >>> print('Intermediate want')
        Intermediate want
        >>> docsrc = blocks['Example']
        >>> src, want = parse_src_want(docsrc)
        >>> 'I want to see this str'
        I want to see this str
    """
    reversed_src_lines = []
    reversed_want_lines = []
    finished_want = False

    # Read the example block backwards to get the want string
    # and then the rest should all be source.
    # TODO: be able to parse intermedidate want strings
    # as well as deal with unbalanced strings.
    for line in reversed(docsrc.splitlines()):
        if not finished_want:
            if line.startswith('>>> ') or line.startswith('... '):
                finished_want = True
            else:  # nocover
                reversed_want_lines.append(line)
                if len(line.strip()) == 0:
                    reversed_want_lines = []
                continue
        reversed_src_lines.append(line[4:])
    src = '\n'.join(reversed_src_lines[::-1])
    if len(reversed_want_lines):
        want = '\n'.join(reversed_want_lines[::-1])
    else:
        want = None

    # FIXME: hacks src to make output lines assign
    # to a special result variable instead
    if want is not None and 'result = ' not in src:
        # Check if the last line has a "want"
        import ast
        tree = ast.parse(src)
        if isinstance(tree.body[-1], ast.Expr):  # pragma: no branch
            lines = src.splitlines()
            # Hack to insert result variable
            lines[-1] = 'result = ' + lines[-1]
            src = '\n'.join(lines)
    return src, want


class ExitTestException(Exception):
    pass


# class DocExample(object):
class DocExample(util_mixins.NiceRepr):
    """
    Holds information necessary to execute and verify a doctest

    Example:
        >>> from ubelt.util_test import *  # NOQA
        >>> package_name = 'ubelt'
        >>> testable_examples = parse_testables(package_name)
        >>> example = next(testable_examples)
        >>> print(example.want)
        >>> print(example.want)
        >>> print(example.valid_testnames)
    """

    def __init__(example, modpath, callname, block, num):
        from ubelt.meta import static_analysis as static
        example.modpath = modpath
        example.modname = static.modpath_to_modname(modpath)
        example.callname = callname
        example.block = block
        example.num = num
        example._src = None
        example._want = None

    @property
    def src(example):
        if example._src is None:
            example._parse()
        return example._src

    @property
    def want(example):
        if example._want is None:
            example._parse()
        return example._want

    def _parse(example):
        example._src, example._want = parse_src_want(example.block)

    def is_disabled(example):
        return example.block.startswith('>>> # DISABLE_DOCTEST')

    @property
    def cmdline(example):
        return 'python -m ' + example.modname + ' ' + example.unique_callname

    @property
    def unique_callname(example):
        return example.callname + ':' + str(example.num)

    @property
    def valid_testnames(example):
        return {
            example.callname,
            example.unique_callname,
        }

    def format_src(example, linenums=True, colored=True):
        """
        Adds prefix and line numbers to a doctest

        Example:
            >>> from ubelt.util_test import *  # NOQA
            >>> package_name = 'ubelt'
            >>> testable_examples = parse_testables(package_name)
            >>> example = next(testable_examples)
            >>> print(example.format_src())
            >>> print(example.format_src(linenums=False, colored=False))
            >>> assert not example.is_disabled()
        """
        doctest_src = example.src
        doctest_src = util_str.indent(doctest_src, '>>> ')
        if linenums:
            doctest_src = '\n'.join([
                '%3d %s' % (count, line)
                for count, line in enumerate(doctest_src.splitlines(), start=1)])
        if colored:
            doctest_src = util_str.highlight_code(doctest_src, 'python')
        return doctest_src

    def run_example(example, verbose=None):
        """
        Executes the doctest

        TODO:
            * break src and want into multiple parts

        Notes:
            * There is no difference between locals/globals in exec context
            Only pass in one dict, otherwise there is weird behavior
            References: https://bugs.python.org/issue13557
        """
        if verbose is None:
            verbose = 2
        example._parse()
        failed = False
        if verbose >= 1:
            print('============')
            print('* BEGIN EXAMPLE : {}'.format(example.callname))
            print(example.cmdline)
            if verbose >= 2:
                print(example.format_src())
        else:  # nocover
            sys.stdout.write('.')
            sys.stdout.flush()
        # Prepare for actual test run
        test_locals = {}
        code = compile(example.src, '<string>', 'exec')
        cap = util_str.CaptureStdout(enabled=verbose <= 1)
        try:
            with cap:
                exec(code, test_locals)
        # Handle anything that could go wrong
        except ExitTestException:  # nocover
            if verbose > 0:
                print('Test gracefully exists')
        except Exception as ex:  # nocover
            if verbose > 0:
                # TODO: print out nice line number
                print('')
                print('report failure')
                print(example.cmdline)
                print(example.format_src())
            failed = True
            # import utool
            # utool.embed()
            print('* FAILURE: {}, {}'.format(example.callname, type(ex)))
            print(cap.text)
            # TODO: remove appropriate amount of traceback
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # exc_traceback = exc_traceback.tb_next
            # six.reraise(exc_type, exc_value, exc_traceback)
            raise

        if not failed and verbose >= 1:
            if cap.text is not None:  # nocover
                assert isinstance(cap.text, six.text_type), 'do not use ascii'
            try:
                print(cap.text)
            except UnicodeEncodeError:  # nocover
                print('Weird travis bug')
                print('type(cap.text) = %r' % (type(cap.text),))
                print('cap.text = %r' % (cap.text,))
            print('* SUCCESS: {}'.format(example.callname))
        summary = {
            'passed': not failed
        }
        return summary

    def __nice__(self):
        return self.modname + ' ' + self.callname


def parse_docstr_examples(docstr, callname=None, modpath=None):
    """
    Parses Google-style doctests from a docstr and generates example objects
    """
    try:
        from ubelt.meta import docscrape_google
        blocks = docscrape_google.split_google_docblocks(docstr)
        example_blocks = []
        for type_, block in blocks:
            if type_.startswith('Example'):
                example_blocks.append((type_, block))
            if type_.startswith('Doctest'):
                example_blocks.append((type_, block))
        for num, (type_, block) in enumerate(example_blocks):
            example = DocExample(modpath, callname, block, num)
            yield example
    except Exception as ex:  # nocover
        msg = ('Cannot scrape callname={} in modpath={}.\n'
               'Caused by={}')
        msg = msg.format(callname, modpath, ex)
        raise Exception(msg)


def parse_testables(package_name, ignore_patterns=[], strict=False, verbose=False):
    r"""
    Finds all functions/callables with Google-style example blocks

    CommandLine:
        python -m ubelt.util_test parse_testables

    Example:
        >>> from ubelt.util_test import *  # NOQA
        >>> package_name = 'ubelt'
        >>> testable_examples = list(parse_testables(package_name, verbose=True))
        >>> this_example = None
        >>> for example in testable_examples:
        >>>     print(example)
        >>>     if example.callname == 'parse_testables':
        >>>         this_example = example
        >>> assert this_example is not None
        >>> assert this_example.callname == 'parse_testables'
    """
    from ubelt.meta import static_analysis as static
    from os.path import exists

    modnames = static.package_modnames(package_name,
                                       ignore_patterns=ignore_patterns)
    for modname in modnames:
        modpath = static.modname_to_modpath(modname, hide_init=False)
        if not exists(modpath):  # nocover
            warnings.warn(
                'Module {} does not exist. '
                'Is it an old pyc file?'.format(modname))
            continue
        if verbose:  # nocover
            print('Parsing module={} at path={}'.format(modname, modpath))

        try:
            docstrs = static.parse_docstrs(fpath=modpath)
        except Exception as ex:  # nocover
            msg = 'Cannot parse module={} at path={}.\nCaused by={}'
            msg = msg.format(modname, modpath, ex)
            if strict:
                raise Exception(msg)
            else:
                warnings.warn(msg)
                continue

        for callname, docstr in docstrs.items():
            if docstr is not None:
                for example in parse_docstr_examples(docstr, callname, modpath):
                    yield example


def doctest_package(package_name=None, command=None, argv=None,
                    check_coverage=None, ignore_patterns=[],
                    verbose=None):  # nocover
    r"""
    Executes requestsed google-style doctests in a package.
    Main entry point into the testing framework.

    Args:
        package_name (str): name of the package
        command (str): determines which doctests to run.
            if command is None, this is determined by parsing sys.argv
        argv (list): if None uses sys.argv
        verbose (bool):  verbosity flag
        ignore_patterns (list): ignores any modname matching any of these
            glob-like patterns
        check_coverage (None): if True outputs coverage report

    CommandLine:
        python -m ubelt.util_test doctest_package

    Example:
        >>> from ubelt.util_test import *  # NOQA
        >>> package_name = 'ubelt.util_test'
        >>> result = doctest_package(package_name, 'list', argv=[''])
    """
    from ubelt.meta import static_analysis as static
    from ubelt.meta import dynamic_analysis
    print('Start doctest_package({})'.format(package_name))

    if package_name is None:
        # Determine package name via caller if not specified
        frame_parent = dynamic_analysis.get_parent_frame()
        frame_fpath = frame_parent.f_globals['__file__']
        package_name = static.modpath_to_modname(frame_fpath)

    if command is None:
        if argv is None:
            argv = sys.argv
        # Determine command via sys.argv if not specified
        argv = argv[1:]
        if len(argv) >= 1:
            command = argv[0]
        else:
            command = None

    # Parse all valid examples
    examples = list(parse_testables(
        package_name, ignore_patterns=ignore_patterns))

    if verbose is None:
        if '--verbose' in sys.argv:
            verbose = 2
        elif '--quiet' in sys.argv:
            verbose = 0
        else:
            verbose = 1 if len(examples) > 1 else 2

    if command == 'list':
        print('Listing tests')

    if command is None:
        # Display help if command is not specified
        print('Not testname given. Use `all` to run everything or')
        print('Pick from a list of valid choices:')
        command = 'list'

    run_all = command == 'all'

    if command == 'list':
        print('\n'.join([example.cmdline for example in examples]))
    else:
        print('gathering tests')
        enabled_examples = []
        for example in examples:
            if run_all or command in example.valid_testnames:
                if run_all and example.is_disabled():
                    continue
                enabled_examples.append(example)

        if check_coverage is None:
            check_coverage = run_all

        if check_coverage:
            import coverage
            modnames = list({e.modname for e in enabled_examples})
            cov = coverage.Coverage(source=modnames)
            exclude_lines = [
                'pragma: no cover',
                '.*  # pragma: no cover',
                '.*  # nocover',
                'def __repr__',
                'raise AssertionError',
                'raise NotImplementedError',
                'if 0:',
                'if trace is not None',
                'verbose = .*',
                'raise',
                'pass',
                'if _debug:',
                'if __name__ == .__main__.:',
                'print(.*)',
                # Exclude this function as well
            ]
            if six.PY2:
                exclude_lines.append('.*if six.PY3:')
            elif six.PY3:
                exclude_lines.append('.*if six.PY2:')
            for line in exclude_lines:
                cov.exclude(line)
            print('Starting coverage')
            cov.start()
            # Dump the coveragerc file for codecov.io
            # Doesn't seem to work :(
            # from os.path import exists
            # rcpath = '.coveragerc'
            # if not exists(rcpath) and not exists('__init__.py'):
            #     import textwrap
            #     rctext = textwrap.dedent(
            #         r'''
            #         [report]
            #         exclude_lines =
            #         '''
            #     )
            #     rctext += util_str.indent('\n'.join(exclude_lines))
            #     from ubelt import util_io
            #     util_io.writeto(rcpath, rctext)
            # Hack to reload modules for coverage
            import imp
            for modname in modnames:
                if modname in sys.modules:
                    # print('realoading modname = %r' % (modname,))
                    imp.reload(sys.modules[modname])

        n_total = len(enabled_examples)
        print('running %d test(s)' % (n_total))
        summaries = []
        for example in enabled_examples:
            summary = example.run_example(verbose=verbose)
            summaries.append(summary)
        if verbose <= 0:
            print('')
        n_passed = sum(s['passed'] for s in summaries)
        print('Finished doctests')
        print('%d / %d passed'  % (n_passed, n_total))

        if check_coverage:
            print('Stoping coverage')
            cov.stop()
            print('Saving coverage for codecov')
            cov.save()
            print('Generating coverage html report')
            cov.html_report()
            from six.moves import cStringIO
            stream = cStringIO()
            cov_percent = cov.report(file=stream)  # NOQA
            stream.seek(0)
            cov_report = stream.read()
            print('Coverage Report:')
            print(cov_report)
        return n_passed == n_total
        # TODO: test summary

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_test
        python -m ubelt.util_test all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
