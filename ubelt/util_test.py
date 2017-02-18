# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
# from ubelt import util_mixins
import sys

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
    """
    reversed_src_lines = []
    reversed_want_lines = []
    finished_want = False

    # Read the example block backwards to get the want string
    # and then the rest should all be source
    for line in reversed(docsrc.splitlines()):
        if not finished_want:
            if line.startswith('>>> ') or line.startswith('... '):
                finished_want = True
            else:
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
        if isinstance(tree.body[-1], ast.Expr):
            lines = src.splitlines()
            # Hack to insert result variable
            lines[-1] = 'result = ' + lines[-1]
            src = '\n'.join(lines)
    # import redbaron
    # baron = redbaron.RedBaron(src)
    # x = baron[-1]
    return src, want


class ExitTestException(Exception):
    pass


# class DocExample(util_mixins.NiceRepr):
class DocExample(object):
    """
    Holds information necessary to execute and verify a doctest
    """

    def __init__(example, modpath, callname, block, num):
        example.modpath = modpath
        example.callname = callname
        example.block = block
        example.num = num

    def is_disabled(example):
        return example.startswith('>>> # DISABLE_DOCTEST')

    def run_test(example):
        # TODO: break into multiple src and want if more than one is specified
        # print('Running example = %r' % (example,))
        src, want = parse_src_want(example.block)
        # print('Running:')
        # print(src)

        code = compile(src, '<string>', 'exec')
        # Only pass in one dict, otherwise there is weird behavior.
        # There is no difference between locals/globals in exec context.
        # References: https://bugs.python.org/issue13557
        try:
            # IN EXEC CONTEXT THERE IS NO DIFF BETWEEN LOCAL / GLOBALS.  ONLY PASS
            # IN ONE DICT. OTHERWISE TREATED ODDLY
            # References: https://bugs.python.org/issue13557
            #exec(code, test_globals, test_locals)
            test_locals = {}
            exec(code, test_locals)
        except ExitTestException:
            print('Test gracefully exists')

    def __nice__(self):
        return self.callname


class ExampleCollection(object):
    """
    Holds information about multiple doctests
    """
    def __init__(self, examples):
        self.examples = examples


def parse_testables(package_name):
    r"""
    Finds all functions/callables with Google-style example blocks

    Example:
        >>> package_name = 'ubelt'
        >>> testable_examples = parse_testables(package_name)
        >>> #assert 'parse_testables' in testable_examples
    """
    from ubelt.meta import static_analysis
    from ubelt.meta import docscrape_google
    from ubelt import util_io

    modnames = static_analysis.package_modnames(package_name)
    for modname in modnames:
        modpath = static_analysis.modname_to_modpath(modname, hide_init=False)
        source = util_io.readfrom(modpath)
        docstrs = static_analysis.parse_docstrs(source)
        for callname, docstr in docstrs.items():
            if docstr is not None:
                blocks = docscrape_google.split_google_docblocks(docstr)
                example_blocks = (
                    (type_, block) for type_, block in blocks
                    if type_.startswith('Example'))
                for num, (type_, block) in enumerate(example_blocks):
                    example = DocExample(modpath, callname, block, num)
                    test_name = modname + '.' + callname
                    yield example


def doctest_package(package_name=None, command=None):
    """
    Executes requestsed google-style doctests in a package

    Args:
        package_name (str): name of the package
        command (str): determines which doctests to run.
            if command is None, this is determined by parsing sys.argv

    CommandLine:
        python -m util_test doctest_package

    Example:
        >>> # DISABLE_DOCTEST
        >>> from util_test import *  # NOQA
        >>> package_name = None
        >>> result = doctest_package(package_name)
        >>> print(result)
    """
    from ubelt.meta import static_analysis
    from ubelt.meta import dynamic_analysis

    if package_name is None:
        # Determine package name via caller if not specified
        frame_parent = dynamic_analysis.get_parent_frame()
        frame_fpath = frame_parent.f_globals['__file__']
        package_name = static_analysis.modpath_to_modname(frame_fpath)

    if command is None:
        # Determine command via sys.argv if not specified
        argv = sys.argv[1:]
        if len(argv) >= 1:
            command = argv[0]
        else:
            command = None

    # Parse all valid examples
    examples = list(parse_testables(package_name))

    if command is None:
        # Display help if command is not specified
        print('Not testname given. Valid choices are:')
        print(examples)
        return

    for example in examples:
        command_parts = command.split(':')
        request_callname = command_parts[0]
        # modifiers = command_parts[1] if len(command_parts) else 0
        if request_callname == example.callname:
            test_result = example.run_test()

if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_test
        python -m ubelt.util_test --allexamples
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
