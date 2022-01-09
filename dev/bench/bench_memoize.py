

def bench_memoize():
    import ubelt as ub
    @ub.memoize
    def memoized_func():
        return object()

    def raw_func():
        return object()

    class Foo(object):
        @ub.memoize_property
        def a_memoized_property(self):
            return object()

        @ub.memoize_method
        def a_memoized_method(self):
            return object()

        @property
        def a_raw_property(self):
            return object()

        def a_raw_method(self):
            return object()

    self = Foo()
    ti = ub.Timerit(1000, bestof=100, verbose=1, unit='ns')

    ti.reset('memoized method').call(lambda: self.a_memoized_method())
    ti.reset('raw method').call(lambda: self.a_raw_method())

    ti.reset('memoized func').call(lambda: memoized_func())
    ti.reset('raw func').call(lambda: raw_func())

    ti.reset('memoized property').call(lambda: self.a_memoized_property)
    ti.reset('raw property').call(lambda: self.a_raw_property)

if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/bench_memoize.py
    """
    bench_memoize()
