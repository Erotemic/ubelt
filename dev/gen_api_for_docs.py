
def count_ubelt_usage():
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
