#!/usr/bin/env python

def count_ubelt_usage():
    """
    import sys, ubelt
    sys.path.append(ubelt.expandpath('~/code/ubelt/dev/maintain'))
    from gen_api_for_docs import *  # NOQA
    """
    from count_usage_freq import count_ubelt_usage
    import ubelt as ub
    usage = count_ubelt_usage()

    # Reorgnaize data to contain more information
    rows = []
    unseen = usage.copy()
    for attrname in ub.__all__:
        member = getattr(ub, attrname)
        submembers = getattr(member, '__all__', None)
        if attrname.startswith('util_'):
            if not submembers:
                from mkinit.static_mkinit import _extract_attributes
                submembers = _extract_attributes(member.__file__)
        if submembers:
            for subname in submembers:
                parent_module = 'ubelt.{}'.format(attrname)
                short_name = 'ubelt.{subname}'.format(**locals())
                full_name = '{parent_module}.{subname}'.format(**locals())
                url = 'https://ubelt.readthedocs.io/en/latest/{parent_module}.html#{full_name}'.format(**locals())
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

    import numpy as np
    import kwarray

    if ub.argflag('--url-mode'):
        ref_key = 'url_ref'
    else:
        ref_key = 'rst_ref'

    name_len = max(len(row[ref_key]) for row in rows) + 1
    num_len = 16

    gaurd = ('=' * name_len + ' ' + '=' * num_len)
    print(gaurd)
    column_fmt = '{:<' + str(name_len) + '} {:>' + str(num_len) + '}'
    print(column_fmt.format(' Function name ', 'Usefulness'))
    print(gaurd)
    for key, value in usage.items():
        infos = attr_to_infos[key]
        if len(infos) == 0:
            print(column_fmt.format(':func:`ubelt.' + key + '`', value))
        else:
            if len(infos) != 1:
                print('infos = {}'.format(ub.urepr(infos, nl=1)))
                raise AssertionError
            info = infos[0]
            print(column_fmt.format(info[ref_key], value))
    print(gaurd)

    raw_scores = np.array(list(usage.values()))

    print('\n.. code:: python\n')
    print(ub.indent('usage stats = ' + ub.repr2(kwarray.stats_dict(
        raw_scores, median=True, sum=True), nl=1)))

    for attrname in ub.__all__:
        member = getattr(ub, attrname)

        submembers = getattr(member, '__all__', None)

        if attrname.startswith('util_'):
            if not submembers:
                from mkinit.static_mkinit import _extract_attributes
                submembers = _extract_attributes(member.__file__)

        if submembers:
            parent_module = 'ubelt.{}'.format(attrname)

            title = ':mod:`{}`'.format(parent_module)
            print('\n' + title)
            print('-' * len(title))
            for subname in submembers:
                if not subname.startswith('_'):
                    rst_ref = (
                        ':func:`<ubelt.{subname}><{parent_module}.{subname}>`'
                    ).format(subname=subname, parent_module=parent_module)
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
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --extra_modname=bioharn,watch --remove_zeros=False --url-mode

        # First run and copy the table:
        python ~/code/ubelt/dev/maintain/count_usage_freq.py
        python ~/code/ubelt/dev/maintain/gen_api_for_docs.py --extra_modname=bioharn,watch --remove_zeros=False

        # Then edit: TODO make less manual
        ~/code/ubelt/docs/source/function_usefulness.rst
    """
    count_ubelt_usage()
