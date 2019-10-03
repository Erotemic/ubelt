
def count_ubelt_usage():
    import ubelt as ub
    import glob
    from os.path import join
    names = [
        'xdoctest', 'netharn', 'xdev', 'xinspect', 'ndsampler', 'kwil',
        'kwarray', 'kwimage', 'kwplot', 'scriptconfig',
    ]

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

    print(ub.repr2(pkg_to_hist, nl=2))
    print(ub.repr2(usage, nl=1))
