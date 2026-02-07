"""
Vendor progiter into ubelt.
"""

#!/usr/bin/env python3
import scriptconfig as scfg

import ubelt as ub


class PortProgiterConfig(scfg.DataConfig):
    yes = scfg.Value(False, isflag=True)


def main(cmdline=1, **kwargs):
    """
    Example:
        >>> # xdoctest: +SKIP
        >>> cmdline = 0
        >>> kwargs = dict(
        >>> )
        >>> main(cmdline=cmdline, **kwargs)
    """
    import xdev

    config = PortProgiterConfig.cli(cmdline=cmdline, data=kwargs, strict=True)
    print('config = ' + ub.urepr(dict(config), nl=1))

    fpath1 = ub.Path('~/code/progiter/progiter/progiter.py').expand()
    fpath2 = ub.Path('~/code/ubelt/ubelt/progiter.py').expand()

    text1 = fpath1.read_text()
    text2 = fpath2.read_text()

    print(xdev.difftext(text2, text1, colored=1))

    import rich.prompt

    ans = config.yes or rich.prompt.Confirm.ask('do write?')
    if ans:
        fpath2.write_text(text1)

    fpath1 = ub.Path('~/code/progiter/tests/test_progiter.py').expand()
    fpath2 = ub.Path('~/code/ubelt/tests/test_progiter.py').expand()
    text1 = fpath1.read_text()

    text1 = text1.replace('from progiter import ProgIter', 'from ubelt import ProgIter')
    text2 = fpath2.read_text()
    print(xdev.difftext(text2, text1, colored=1))

    import rich.prompt
    ans = config.yes or rich.prompt.Confirm.ask('do write?')
    if ans:
        fpath2.write_text(text1)


if __name__ == '__main__':
    """

    CommandLine:
        python ~/code/ubelt/dev/maintain/port_progiter.py
        python -m port_progiter
    """
    main()
