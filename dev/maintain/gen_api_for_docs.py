#!/usr/bin/env python

import scriptconfig as scfg


class UsageConfig(scfg.Config):
    default = {
        'print_packages': False,
        'remove_zeros': False,
        'hardcoded_ubelt_hack': True,
        'extra_modnames': [],
    }


def count_package_usage(modname):
    import glob
    import re
    from os.path import join

    import ubelt as ub
    config = UsageConfig(cmdline=True)

    names = [
        'xdoctest', 'netharn', 'xdev', 'xinspect', 'xcookie', 'ndsampler',
        'kwarray', 'kwimage', 'kwplot', 'kwcoco',
        'scriptconfig', 'vimtk',
        'mkinit', 'futures_actors', 'graphid',

        'kwutil', 'git_well', 'line_profiler', 'delayed_image', 'simple_dvc',
        'pypogo', 'cmd_queue'

        'ibeis', 'plottool_ibeis', 'guitool_ibeis', 'utool', 'dtool_ibeis',
        'vtool_ibeis', 'pyhesaff', 'torch_liberator', 'liberator',
        'pyflann_ibeis', 'networkx_algo_common_subtree', 'shitspotter',
        'kwgis', 'geowatch', 'sm64-random-assets', 'bioharn',
    ] + config['extra_modnames']

    names = list(ub.unique(names))

    code_repos = [ub.Path('~/code').expand() / name for name in names]
    repo_dpaths = code_repos + [
        # ub.Path('~/local').expand(),
        ub.Path('~/misc').expand(),
    ]
    all_fpaths = []
    all_tlds = []
    for repo_dpath in repo_dpaths:
        name = repo_dpath.stem
        fpaths = glob.glob(join(repo_dpath, '**', '*.py'), recursive=True)
        for fpath in fpaths:
            if ub.Path(fpath).relative_to(repo_dpath).parts[0] in {'build', 'dist'}:
                continue
            all_tlds.append(repo_dpath / ub.Path(fpath).relative_to(repo_dpath).parts[0])
            all_fpaths.append((name, fpath))
    all_tlds = list(ub.unique(all_tlds))
    print(f'all_tlds = {ub.urepr(all_tlds, nl=1)}')

    pat = re.compile(r'\bub\.(?P<attr>[a-zA-Z_][A-Za-z_0-9]*)\b')

    modname = modname
    module = ub.import_module_from_name(modname)
    package_name = module.__name__
    package_allvar = module.__all__

    pat = re.compile(r'\b' + package_name + r'\.(?P<attr>[a-zA-Z_][A-Za-z_0-9]*)\b')
    pats = [
        re.compile(r'\bub\.(?P<attr>[A-Za-z_][A-Za-z0-9_]*)\b'),
        re.compile(r'\bubelt\.(?P<attr>[A-Za-z_][A-Za-z0-9_]*)\b'),
    ]

    pkg_to_hist = ub.ddict(lambda: ub.ddict(int))
    for name, fpath in ub.ProgIter(all_fpaths):
        with open(fpath, 'r') as file:
            text = file.read()
        for pat in pats:
            for match in pat.finditer(text):
                attr = match.groupdict()['attr']
                if attr in package_allvar:
                    pkg_to_hist[name][attr] += 1

    hist_iter = iter(pkg_to_hist.values())
    usage = next(hist_iter).copy()
    for other in hist_iter:
        for k, v in other.items():
            usage[k] += v
    for attr in package_allvar:
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

    if 1:
        # Renamed Aliases
        try:
            usage['urepr'] += usage.pop('repr2')
            usage['ReprExtensions'] += usage.pop('FormatterExtensions')
        except Exception:
            ...

    usage = ub.udict(usage).sorted_values(reverse=True)

    print(ub.repr2(usage, nl=1))
    return usage


def gen_api_for_docs(modname):
    """
    import sys, ubelt
    sys.path.append(ubelt.expandpath('~/code/ubelt/dev/maintain'))
    from gen_api_for_docs import *  # NOQA
    """
    import ubelt as ub

    usage = count_package_usage(modname)

    module = ub.import_module_from_name(modname)
    attrnames = module.__all__
    if hasattr(module, '__protected__'):
        # Hack for lazy imports
        for subattr in module.__protected__:
            submod = ub.import_module_from_name(modname + '.' + subattr)
            setattr(module, subattr, submod)
        attrnames += module.__protected__

    # Reorgnaize data to contain more information
    rows = []
    unseen = usage.copy()
    for attrname in attrnames:
        member = getattr(module, attrname)
        submembers = getattr(member, '__all__', None)
        if attrname.startswith('util_'):
            if not submembers:
                from mkinit.static_mkinit import _extract_attributes
                submembers = _extract_attributes(member.__file__)
        if submembers:
            for subname in submembers:
                parent_module = f'{modname}.{attrname}'
                short_name = '{modname}.{subname}'.format(**locals())
                full_name = '{parent_module}.{subname}'.format(**locals())
                url = 'https://{modname}.readthedocs.io/en/latest/{parent_module}.html#{full_name}'.format(**locals())
                rst_ref = ':func:`{short_name}<{full_name}>`'.format(**locals())
                url_ref = '`{short_name} <{url}>`__'.format(**locals())
                rows.append({
                    'attr': subname,
                    'parent_module': parent_module,
                    'usage': unseen.pop(subname, 0),
                    'short_name': short_name,
                    'full_name': full_name,
                    'url': url,
                    'rst_ref': rst_ref,
                    'url_ref': url_ref,
                })

    attr_to_infos = ub.group_items(rows, lambda x: x['attr'])

    if 'urepr' in attr_to_infos:
        urepr2_infos = attr_to_infos['urepr']
        cannon_urepr2_infos = [d for d in urepr2_infos if 'repr' in d['parent_module']]
        cannon_urepr2_info = cannon_urepr2_infos[0]
        attr_to_infos['urepr'] = [cannon_urepr2_info]

    import kwarray
    import numpy as np

    if ub.argflag('--url-mode'):
        ref_key = 'url_ref'
    else:
        ref_key = 'rst_ref'

    name_len = max(len(row[ref_key]) for row in rows) + 1
    num_len = 16

    guard = ('=' * name_len + ' ' + '=' * num_len)
    print(guard)
    column_fmt = '{:<' + str(name_len) + '} {:>' + str(num_len) + '}'
    print(column_fmt.format(' Function name ', 'Usefulness'))
    print(guard)
    for key, value in usage.items():
        infos = attr_to_infos[key]
        if len(infos) == 0:
            print(column_fmt.format(f':func:`{modname}.' + key + '`', value))
        else:
            if len(infos) != 1:
                print('infos = {}'.format(ub.urepr(infos, nl=1)))
                raise AssertionError
            info = infos[0]
            print(column_fmt.format(info[ref_key], value))
    print(guard)

    raw_scores = np.array(list(usage.values()))

    print('\n.. code:: python\n')
    print(ub.indent('usage stats = ' + ub.repr2(kwarray.stats_dict(
        raw_scores, median=True, sum=True), nl=1)))

    for attrname in attrnames:
        member = getattr(module, attrname)

        submembers = getattr(member, '__all__', None)

        # if attrname.startswith('util_'):
        if not submembers:
            from mkinit.static_mkinit import _extract_attributes

            try:
                submembers = _extract_attributes(member.__file__)
            except AttributeError:
                pass

        if submembers:
            parent_module = f'{modname}.{attrname}'

            title = ':mod:`{}`'.format(parent_module)
            print('\n' + title)
            print('-' * len(title))
            for subname in submembers:
                if not subname.startswith('_'):
                    rst_ref = (
                        f':func:`<{modname}.{subname}><{parent_module}.{subname}>`'
                    )
                    print(rst_ref)
            submembers = dir(member)


if __name__ == '__main__':
    """
    For Me:
        ~/internal/dev/ubelt_stats_update.sh
        ~/internal/dev/pkg_usage_stats_update.sh

    CommandLine:
        # For index.rst
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py

        # For README
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --url-mode
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --extra_modnames=bioharn,geowatch --remove_zeros=False --url-mode

        # First run and copy the table:
        python ~/code/ubelt/dev/maintain/count_usage_freq.py
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --extra_modnames=bioharn,geowatch --remove_zeros=False

        # Then edit: TODO make less manual
        ~/code/ubelt/docs/source/manual/function_usefulness.rst
    """
    gen_api_for_docs('ubelt')
