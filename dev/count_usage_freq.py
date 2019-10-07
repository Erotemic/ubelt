
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

    fmt_code = 'https://github.com/Erotemic/ubelt/blob/master/{rel_modpath}#L{lineno}'
    fmt_docs = 'https://ubelt.readthedocs.io/en/latest/{modname}.html#{modname}.{attrname}'

    @ub.memoize
    def static_calldefs(modpath):
        from xdoctest import static_analysis as static
        calldefs = dict(static.parse_calldefs(fpath=modpath))
        return calldefs

    def get_object_lineno(obj):
        try:
            # functions just seem to have this info
            lineno = obj.__code__.co_firstlineno
        except AttributeError:
            # class objects don't seem to have this for whatever reason
            # but we can statically parse it out
            attrname = obj.__name__
            modpath = sys.modules[obj.__module__].__file__
            calldefs = static_calldefs(modpath)
            calldef = calldefs[attrname]
            lineno = calldef.lineno
        return lineno

    import sys
    for attrname in usage:
        if attrname.startswith(('util_', 'progiter', 'timerit', 'orderedset')):
            continue
        if attrname in ['OrderedDict', 'defaultdict', 'NoParam', 'ddict', 'odict']:
            continue
        obj = getattr(ub, attrname)
        if isinstance(obj, (bool, str, set, list, tuple)):
            continue

        lineno = get_object_lineno(obj)
        prefix, rel_modpath = ub.split_modpath(sys.modules[obj.__module__].__file__)

        modname = obj.__module__
        code_text = fmt_code.format(rel_modpath=rel_modpath, lineno=lineno)
        docs_text = fmt_docs.format(modname=modname, attrname=attrname)
        print('attrname = {!r}'.format(attrname))
        print('docs_text = {!r}'.format(docs_text))
        print('code_text = {!r}'.format(code_text))
