def remove_old_python2_headers():
    import re
    import ubelt as ub
    from xdev import search_replace
    from xdev import patterns

    lines_to_remove = [
        patterns.Pattern.from_regex(re.escape('from __future__ import absolute_import, ') + '.*', dotall=True),
        patterns.Pattern.from_regex(re.escape('# -*- coding: utf-8 -*-') + '.*', dotall=True),
    ]

    fpaths = set(ub.Path('~/code/ubelt/').expand().glob('**/*.py'))
    fpaths = fpaths - {ub.Path('~/code/ubelt/dev/remove_ancient_constructs.py').expand()}

    for fpath in fpaths:
        # x = fpath.read_text().split('\n')[0:1][0]
        for pat in lines_to_remove:
            search_replace.sedfile(fpath, regexpr=pat, repl='', dry=False, verbose=3)
