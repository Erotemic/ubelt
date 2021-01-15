"""
Tests the difference between importing something globally versus locally
"""


def bench_local_versus_global_import():
    """
    Write two python files that loop over a test function that uses some
    external module.

    One version imports the dependency globally at startup, the other does a
    lazy import of the module inside the function.

    We time how long this takes over several tests where we varry the number of
    times this inner function is looped over (and thus the number of times we
    will run over the lazy import versus accessing the global import).

    It should be noted that startup time of the interpreter will play a
    considerable role in these measurements. Any ideas for mitigating that
    would be appreciated.
    """
    import ubelt as ub
    from os.path import join

    import timerit
    ti = timerit.Timerit(30, bestof=3, verbose=2)

    for num in [0, 1, 10, 1000, 1000, 10000]:
        fmtkw = {
            # 'modname': 'numpy',
            # 'attrname': 'array',
            # 'modname': 'ubelt',
            # 'attrname': 'take',
            'modname': 'networkx',
            'attrname': 'Graph',
            'num': 100000,
        }

        global_codeblock = ub.codeblock(
            '''
            import {modname}


            def testfunc():
                return {modname}.{attrname}

            def main():
                for _ in range({num}):
                    testfunc()

            if __name__ == '__main__':
                testfunc()
            ''').format(**fmtkw)

        local_codeblock = ub.codeblock(
            '''

            def testfunc():
                import {modname}
                return {modname}.{attrname}

            def main():
                for _ in range({num}):
                    testfunc()

            if __name__ == '__main__':
                testfunc()
            ''').format(**fmtkw)

        dpath = ub.ensure_app_cache_dir('ubelt/bench')

        local_modpath = join(dpath, 'local_import_test.py')
        global_modpath = join(dpath, 'global_import_test.py')

        ub.writeto(local_modpath, local_codeblock)
        ub.writeto(global_modpath, global_codeblock)

        ub.cmd('python ' + global_modpath)

        for timer in ti.reset('local imports @ {}'.format(num)):
            with timer:
                ub.cmd('python ' + local_modpath)

        for timer in ti.reset('global imports @ {}'.format(num)):
            with timer:
                ub.cmd('python ' + global_modpath)

    print('ti.rankings = {}'.format(ub.repr2(ti.rankings, nl=2, precision=4, align=':')))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_local_import.py
    """
    bench_local_versus_global_import()
