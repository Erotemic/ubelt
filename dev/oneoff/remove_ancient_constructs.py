def remove_old_python2_headers():
    """
    Helper to modernize the code
    """
    import re

    from xdev import patterns, search_replace

    import ubelt as ub

    repo_dpath = ub.Path('.')
    # fpaths = set(ub.Path('~/code/watch/').expand().glob('**/*.py'))
    fpaths = set(repo_dpath.glob('**/*.py'))

    lines_to_remove = [
        patterns.Pattern.from_regex(
            re.escape('from __future__ import absolute_import, ') + '.*',
            dotall=True,
        ),
        patterns.Pattern.from_regex(
            re.escape('# -*- coding: utf-8 -*-') + '.*', dotall=True
        ),
    ]

    fpaths = {f for f in fpaths if 'remove_ancient_constructs' not in str(f)}
    # fpaths = fpaths - {ub.Path('~/code/ubelt/dev/remove_ancient_constructs.py').expand()}

    dry = 0
    for fpath in fpaths:
        # x = fpath.read_text().split('\n')[0:1][0]
        for pat in lines_to_remove:
            search_replace.sedfile(
                fpath, regexpr=pat, repl='', dry=dry, verbose=3
            )
