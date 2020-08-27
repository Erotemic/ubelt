

def count_ubelt_usage():
    """
    import sys, ubelt
    sys.path.append(ubelt.expandpath('~/code/ubelt/dev'))
    from gen_api_for_docs import *  # NOQA
    """
    from count_usage_freq import count_ubelt_usage
    usage = count_ubelt_usage()

    gaurd = ('=' * 64 + ' ' + '=' * 16)
    print(gaurd)
    print('{:<64} {:>8}'.format(' Function name ', 'Usefulness'))
    print(gaurd)
    for key, value in usage.items():
        print('{:<64} {:>16}'.format(':func:`ubelt.' + key + '`', value))
    print(gaurd)

    import ubelt as ub
    for attrname in ub.__all__:
        member = getattr(ub, attrname)

        submembers = getattr(member, '__all__', None)

        if attrname.startswith('util_'):
            if not submembers:
                from mkinit.static_mkinit import _extract_attributes
                submembers = _extract_attributes(member.__file__)

        if submembers:
            print('\n:mod:`ubelt.{}`'.format(attrname))
            print('-------------')
            for subname in submembers:
                if not subname.startswith('_'):
                    print(':func:`ubelt.{}`'.format(subname))
            submembers = dir(member)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/gen_api_for_docs.py

        # First run and copy the table:
        python ~/code/ubelt/dev/count_usage_freq.py

        # Then edit: TODO make less manual
        ~/code/ubelt/docs/source/index.rst
    """
    count_ubelt_usage()
