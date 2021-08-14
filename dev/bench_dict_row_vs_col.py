
def bench_dict_row_vs_col():
    """
    Check how long it takes to access atributes when we store them as either
    List[Dict] or Dict[List]. In other words the strategies to store data are
    either

    Row Major:

        [
            {'col_1': <item_0_0>, 'col_2': <item_1_0>, 'col_3': <item_2_0>},
            {'col_1': <item_0_1>, 'col_2': <item_1_1>, 'col_3': <item_2_1>},
            {'col_1': <item_0_2>, 'col_2': <item_1_2>, 'col_3': <item_2_2>},
            ...
        ]

    Column Major:

        {
            'col_1': [<item_0_0>, <item_1_0>, <item_2_0>, ...],
            'col_2': [<item_0_1>, <item_1_1>, <item_2_1>, ...],
            'col_3': [<item_0_2>, <item_1_2>, <item_2_2>, ...],
        }

    Conclusion:
        Using a Dictionary of Lists (i.e. column based data) is between 2x and
        4x faster in these tests.
    """

    import random
    rng = random.Random()

    ncols = int(3)
    nrows = int(1e5)

    def random_item(rng):
        item = rng.randbytes(rng.randint(1, 10))
        return item

    col_names = ['col_{:03d}'.format(c) for c in range(ncols)]

    row_major = [
        {col: random_item(rng) for col in col_names}
        for rx in range(nrows)
    ]

    column_major = {
        col: [row[col] for row in row_major]
        for col in col_names
    }

    import timerit
    import random
    ti = timerit.Timerit(100, bestof=10, verbose=1)

    col = col_names[rng.randint(0, len(col_names) - 1)]

    for timer in ti.reset('iterate-one-column (RM-C)'):
        with timer:
            result1 = [row[col] for row in row_major]

    for timer in ti.reset('iterate-one-column (CM-F)'):
        with timer:
            result2 = [item for item in column_major[col]]
    assert result1 == result2

    for timer in ti.reset('iterate-all-columns (RM-C)'):
        with timer:
            result1 = [[row[col] for col in col_names] for row in row_major]

    for timer in ti.reset('iterate-all-columns (CM-F)'):
        with timer:
            result2 = [list(items) for items in zip(*[column_major[c] for c in col_names])]
    assert result1 == result2

    for timer in ti.reset('column-to-row-based'):
        with timer:
            row_major2 = [
                dict(zip(col_names, items))
                for items in zip(*[column_major[c] for c in col_names])
            ]
    assert row_major2 == row_major

    for timer in ti.reset('row-to-column-based'):
        with timer:
            col_major2 = {
                col: [row[col] for row in row_major]
                for col in col_names
            }
    assert col_major2 == column_major

    # No real difference for single item access
    ti = timerit.Timerit(100000, bestof=10, verbose=1)
    row = rng.randint(0, nrows - 1)
    for timer in ti.reset('access-one-item (RM-C)'):
        with timer:
            result1 = row_major[row][col]

    for timer in ti.reset('access-one-item (CM-F)'):
        with timer:
            result2 = column_major[col][row]
    assert result1 == result2

    for timer in ti.reset('access-one-item (precache col) (CM-F)'):
        column = column_major[col]
        with timer:
            result2 = column[row]

    for timer in ti.reset('access-one-item (precache row) (CM-F)'):
        rowitems = row_major[row]
        with timer:
            result2 = rowitems[col]
