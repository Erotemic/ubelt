class Simple(object):

    class_attr1 = True

    def __init__(self):
        self.attr1 = True


class SimpleWithSlots(object):
    __slots__ = ['attr1']

    class_attr1 = True

    def __init__(self):
        self.attr1 = True


class Complex(object):

    class_attr1 = True
    class_attr2 = True
    class_attr3 = True
    class_attr4 = True
    class_attr5 = True
    class_attr6 = True
    class_attr7 = True
    class_attr8 = True
    class_attr9 = True

    def __init__(self):
        self.attr1 = True
        self.attr2 = True
        self.attr3 = True
        self.attr4 = True
        self.attr5 = True
        self.attr6 = True
        self.attr7 = True
        self.attr8 = True
        self.attr9 = True


class ComplexWithSlots(object):
    __slots__ = [
        'attr1',
        'attr2',
        'attr3',
        'attr4',
        'attr5',
        'attr6',
        'attr7',
        'attr8',
        'attr9',
    ]

    class_attr1 = True
    class_attr2 = True
    class_attr3 = True
    class_attr4 = True
    class_attr5 = True
    class_attr6 = True
    class_attr7 = True
    class_attr8 = True
    class_attr9 = True

    def __init__(self):
        self.attr1 = True
        self.attr2 = True
        self.attr3 = True
        self.attr4 = True
        self.attr5 = True
        self.attr6 = True
        self.attr7 = True
        self.attr8 = True
        self.attr9 = True


def benchmark_attribute_access():
    """
    How fast are different methods of accessing attributes? Lets find out!
    """

    instances = {
        'simple': Simple(),
        'complex': Complex(),
        'slot_simple': SimpleWithSlots(),
        'slot_complex': ComplexWithSlots(),
    }

    import ubelt as ub

    ti = ub.Timerit(100000, bestof=500, verbose=1, unit='us')

    # Do this twice, but keep the second measure
    data = ub.AutoDict()

    for selfname, self in instances.items():

        print(ub.color_text('--- SELF = {} ---'.format(selfname), 'blue'))

        subdata = data[selfname] = {}

        for timer in ti.reset('self.attr1'):
            with timer:
                self.attr1
        subdata[ti.label] = ti.min()

        for timer in ti.reset('getattr(self, attr1)'):
            with timer:
                getattr(self, 'attr1')
        subdata[ti.label] = ti.min()

        attrs = ['attr1', 'attr2']

        for attrname in attrs:
            for timer in ti.reset('hasattr(self, {})'.format(attrname)):
                with timer:
                    hasattr(self, attrname)
            subdata[ti.label] = ti.min()

            for timer in ti.reset('getattr(self, {}, None)'.format(attrname)):
                with timer:
                    getattr(self, attrname, None)
            subdata[ti.label] = ti.min()

            if 'slot' not in selfname.lower():
                for timer in ti.reset('self.__dict__.get({}, None)'.format(attrname)):
                    with timer:
                        self.__dict__.get(attrname, None)
                subdata[ti.label] = ti.min()

        for timer in ti.reset('try/except: self.attr2'):
            with timer:
                try:
                    x = self.attr2
                except AttributeError:
                    x = None
        subdata[ti.label] = ti.min()

        for timer in ti.reset('try/except: self.attr1'):
            with timer:
                try:
                    x = self.attr1
                except AttributeError:
                    x = None
        subdata[ti.label] = ti.min()

        del x

    try:
        import pandas as pd
        df = pd.DataFrame(data) * 1e9
        try:
            from kwil.util.util_pandas import _to_string_monkey
            print(_to_string_monkey(df, key='minima'))
        except Exception:
            print(df)
    except ImportError:
        print('no pandas')
        print(ub.repr2(data, nl=2, precision=4))

    # print(ub.repr2(ti.measures))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_attr_access.py
    """
    benchmark_attribute_access()
