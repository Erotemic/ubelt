def bench_set_membership():
    """
    Q: Is there a speedup to using a set when the set is small?
    A: There seems to be a small benefit, but maybe with more variance?

    Results:
        Timed best=356.988 ns, mean=391.727 ± 31.0 ns for small-set-membership
        Timed best=375.992 ns, mean=413.521 ± 21.9 ns for small-str-membership
        Timed best=362.983 ns, mean=415.807 ± 63.7 ns for small-list-membership

    """
    import timerit
    import random
    ti = timerit.Timerit(300000, bestof=30, verbose=1)
    rng = random.Random(0)

    lhs_candidates = 'biufcmMOSUV'

    for i in range(100000):
        i += 1   # warmup, reduce variance?

    for timer in ti.reset('small-set-membership'):
        lhs = rng.choice(lhs_candidates)
        with timer:
            lhs in {'i', 'u', 'b'}

    for timer in ti.reset('small-str-membership'):
        lhs = rng.choice(lhs_candidates)
        with timer:
            lhs in 'iub'

    for timer in ti.reset('small-list-membership'):
        lhs = rng.choice(lhs_candidates)
        with timer:
            lhs in ['i', 'u', 'b']
