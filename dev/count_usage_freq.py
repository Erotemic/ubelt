

import scriptconfig as scfg


class UsageConfig(scfg.Config):
    default = {
        'print_packages': False,
        'remove_zeros': False,
        'hardcoded_ubelt_hack': True,
        'extra_modnames': [],
    }


def count_ubelt_usage():
    config = UsageConfig(cmdline=True)

    import ubelt as ub
    import glob
    from os.path import join
    names = [
        'xdoctest', 'netharn', 'xdev', 'xinspect', 'ndsampler',
        'kwarray', 'kwimage', 'kwplot', 'kwcoco',
        'scriptconfig', 'vimtk',
        'mkinit', 'futures_actors', 'graphid',

        'ibeis', 'plottool_ibeis', 'guitool_ibeis', 'utool', 'dtool_ibeis',
        'vtool_ibeis', 'hesaff', 'torch_liberator', 'liberator',
    ] + config['extra_modnames']

    code_repos = [ub.Path('~/code').expand() / name for name in names]
    repo_dpaths = code_repos + [
        # ub.Path('~/local').expand(),
        ub.Path('~/misc').expand(),
    ]
    all_fpaths = []
    for repo_dpath in repo_dpaths:
        name = repo_dpath.stem
        fpaths = glob.glob(join(repo_dpath, '**', '*.py'), recursive=True)
        for fpath in fpaths:
            all_fpaths.append((name, fpath))

    import re
    pat = re.compile(r'\bub\.(?P<attr>[a-zA-Z_][A-Za-z_0-9]*)\b')

    import ubelt as ub

    pkg_to_hist = ub.ddict(lambda: ub.ddict(int))
    for name, fpath in ub.ProgIter(all_fpaths):
        with open(fpath, 'r') as file:
            text = file.read()
        for match in pat.finditer(text):
            attr = match.groupdict()['attr']
            if attr in ub.__all__:
                pkg_to_hist[name][attr] += 1

    hist_iter = iter(pkg_to_hist.values())
    usage = next(hist_iter).copy()
    for other in hist_iter:
        for k, v in other.items():
            usage[k] += v
    for attr in ub.__all__:
        usage[attr] += 0

    for name in pkg_to_hist.keys():
        pkg_to_hist[name] = ub.odict(sorted(pkg_to_hist[name].items(), key=lambda t: t[1])[::-1])

    usage = ub.odict(sorted(usage.items(), key=lambda t: t[1])[::-1])

    if config['print_packages']:
        print(ub.repr2(pkg_to_hist, nl=2))

    if config['remove_zeros']:
        for k, v in list(usage.items()):
            if v == 0:
                usage.pop(k)

    if config['hardcoded_ubelt_hack']:
        blocklist = [
            'progiter', 'timerit', 'orderedset',
        ]
        for k in list(usage):
            if k in blocklist:
                usage.pop(k, None)
            elif k.startswith('util_'):
                usage.pop(k, None)
            elif k.startswith('_util_'):
                usage.pop(k, None)
            # ub._util_deprecated
            # from ubelt import _util_deprecated
            # if k in dir(_util_deprecated):
            #     usage.pop(k, None)

    print(ub.repr2(usage, nl=1))
    return usage


if __name__ == '__main__':
    """
    For Me:
        ~/internal/dev/pkg_usage_stats_update.sh

    CommandLine:
        python ~/code/ubelt/dev/count_usage_freq.py --help
        python ~/code/ubelt/dev/count_usage_freq.py --remove_zeros=False --print_packages=True
    """
    count_ubelt_usage()
