
def benchmark_import_time():
    import ubelt as ub
    info = ub.cmd('python -X importtime -c "import ubelt"')
    print(info['err'])
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "from concurrent import futures"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import numpy"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import hashlib"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import typing"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import json"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import uuid"')
    print(info['err'].rstrip().split('\n')[-1])

    info = ub.cmd('python -X importtime -c "import xxhash"')
    print(info['err'].rstrip().split('\n')[-1])


def benchmark_multi_or_combined_import():
    """
    Combining all imports into a single line is slightly faster
    """
    import ubelt as ub
    attr_names = [
        'altsep', 'basename', 'commonpath', 'commonprefix', 'curdir',
        'defpath', 'devnull', 'dirname', 'exists', 'expanduser', 'expandvars',
        'extsep', 'genericpath', 'getatime', 'getctime', 'getmtime', 'getsize',
        'isabs', 'isdir', 'isfile', 'islink', 'ismount', 'join', 'lexists',
        'normcase', 'normpath', 'os', 'pardir', 'pathsep', 'realpath',
        'relpath', 'samefile',
    ]

    combined_lines = 'from os.path import ' + ', '.join(attr_names)

    multi_lines = '; '.join(['from os.path import ' + name for name in attr_names])

    import timerit
    ti = timerit.Timerit(10, bestof=3, verbose=2)
    for timer in ti.reset('combined_lines'):
        with timer:
            ub.cmd('python -c "{}"'.format(combined_lines), check=True)

    for timer in ti.reset('multi_lines'):
        with timer:
            info = ub.cmd('python -c "{}"'.format(multi_lines))


def benchmark_ubelt_import_time_robust():
    import pandas as pd
    import ubelt as ub
    import kwplot
    sns = kwplot.autosns(force='Qt5Agg')

    prog = ub.codeblock(
        r'''
        def _main():
            import subprocess
            import ubelt as ub
            measurements = []
            for i in range(200):
                row = {}
                # info = ub.cmd('python -X importtime -c "import ubelt"')
                # text = info['err']
                prog = subprocess.Popen('python -X importtime -c "import ubelt"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, text = prog.communicate()
                text = text.decode()
                final_line = text.rstrip().split('\n')[-1]
                partial = final_line.split(':')[1].split('|')
                row['self_us'] = float(partial[0].strip())
                row['cummulative'] = float(partial[1].strip())
                measurements.append(row)
            import pandas as pd
            df = pd.DataFrame(measurements)
            stats = pd.DataFrame({
                'mean': df.mean(),
                'std': df.std(),
                'min': df.min(),
                'max': df.max(),
                'total': df.sum(),
            })
            info = stats.to_dict()
            info['version'] = ub.__version__
            print(info)
            # print(stats)
        _main()
        ''')

    dpath = ub.Path(ub.ensure_app_cache_dir('ubelt/tests/test_version_import'))
    fpath = dpath / 'do_test.py'
    fpath.write_text(prog)

    repo_root = ub.Path('$HOME/code/ubelt').expand()

    info = ub.cmd('git tag', cwd=repo_root)

    versions = [p for p in info['out'].split('\n') if p]
    branches = ['dev/1.0.2', 'main'] + versions

    fig = kwplot.figure(doclf=True)
    ax = fig.gca()

    bname_to_info = {}
    rows = []
    for bname in branches:
        print('bname = {!r}'.format(bname))
        ub.cmd('git checkout {}'.format(bname), cwd=repo_root, verbose=3, check=True)
        info = ub.cmd('python {}'.format(fpath), verbose=2)
        dict_info = eval(info['out'])
        bname_to_info[bname] = dict_info
        for stat in ['mean', 'min', 'max']:
            for type in ['self_us', 'cummulative']:
                rows.append({
                    'version': dict_info['version'],
                    'stat': stat,
                    'type': type,
                    'time': dict_info[stat][type],
                })
        df = pd.DataFrame(rows[-1:])
        print(df)
        # ax.cla()
        # sns.lineplot(data=df, x='version', y='time', hue='stat', style='type', ax=ax)

    ub.cmd('git checkout {}'.format('dev/1.0.2'), cwd=repo_root)
    df = pd.DataFrame(rows)
    from distutils.version import LooseVersion
    unique_versions = list(map(str, sorted(map(LooseVersion, df['version'].unique()))))
    df['release_index'] = df['version'].apply(lambda x: unique_versions.index(x))
    ax.cla()
    kwplot.figure(fnum=2, pnum=(2, 1, 1), doclf=True)
    ax = sns.lineplot(data=df[df['type'] == 'cummulative'], x='release_index', y='time', hue='stat', style='type', marker='o')
    ax.set_title('Ubelt import time over release history')
    kwplot.figure(fnum=2, pnum=(2, 1, 2))
    sns.lineplot(data=df[df['type'] == 'self_us'], x='release_index', y='time', hue='stat', style='type', marker='o')

    kwplot.show_if_requested()



if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench/bench_import_time.py --show
    """
    # benchmark_import_time()
    benchmark_ubelt_import_time_robust()
    # benchmark_multi_or_combined_import()
