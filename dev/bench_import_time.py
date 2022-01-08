
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
    import ubelt as ub
    measurements = []
    for i in ub.ProgIter(range(300), desc='measure import time'):
        row = {}
        info = ub.cmd('python -X importtime -c "import ubelt"')
        final_line = info['err'].rstrip().split('\n')[-1]
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
    print(stats)

if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_import_time.py
    """
    benchmark_import_time()
    benchmark_ubelt_import_time_robust()
    # benchmark_multi_or_combined_import()
