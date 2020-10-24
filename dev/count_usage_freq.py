

import scriptconfig as scfg


class UsageConfig(scfg.Config):
    default = {
        'print_packages': False,
        'remove_zeros': True,
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

    all_fpaths = []
    for name in names:
        repo_fpath = ub.expandpath(join('~/code', name))
        fpaths = glob.glob(join(repo_fpath, '**', '*.py'), recursive=True)
        for fpath in fpaths:
            all_fpaths.append((name, fpath))

    import re
    pat = re.compile(r'\bub\.(?P<attr>[a-zA-Z_][A-Za-z_0-9]*)\b')

    import ubelt as ub

    pkg_to_hist = ub.ddict(lambda: ub.ddict(int))
    for name, fpath in ub.ProgIter(all_fpaths):
        text = open(fpath, 'r').read()
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
        for k in list(usage):
            if k.startswith('util_'):
                usage.pop(k)
            if k.startswith('_util_'):
                usage.pop(k)
            # ub._util_deprecated
            from ubelt import _util_deprecated
            if k in dir(_util_deprecated):
                usage.pop(k)

    print(ub.repr2(usage, nl=1))
    return usage


if __name__ == '__main__':
    """
    For Me:
        ~/internal/dev/ubelt_stats_update.sh

    CommandLine:
        python ~/code/ubelt/dev/count_usage_freq.py --help
        python ~/code/ubelt/dev/count_usage_freq.py
    """
    count_ubelt_usage()
