"""
Ubelt Use Cases

Each use case starts with a modivation and follows with a solution. This makes
these cases perfect for presentations.
"""


def multiple_items_from_a_dictionary():
    """
    Spotlight:
        ubelt.take

    Modivation:
        Working with Lists of Dictionaries

    Requires:
        kwimage
    """
    ...

    """
    When working with data, a common pattern is to iterate through it, and
    gather information about the work to be done, so a you can make a final
    structured pass through the data.

    In python we might do this by initializing an empty list and appending
    **dictionary of information**, to the list. (or you might yield
    dictionaries of information from a generator instead, either way you have a
    flat list).

    Some people might use lists of tuples instead of Lists of dictionaries, but
    using dictionaries makes it easy to add new information later (and it works
    very will with pandas).
    """
    import kwimage

    import ubelt as ub
    kwimage_test_image_names = ['airport', 'amazon', 'astro', 'carl',
                                'lowcontrast']
    rows = []
    for test_image in kwimage_test_image_names:
        fpath = ub.Path(kwimage.grab_test_image_fpath(test_image))
        imdata = kwimage.imread(fpath)
        row = {
            'mean': imdata.mean(),
            'std': imdata.std(),
            'sum': imdata.sum(),
            'max': imdata.max(),
            'min': imdata.min(),
        }
        rows.append(row)

    """
    For each row, you might want to grab multiple specific items from it.

    But having a separate assignment on each row wastes a lot of vertical
    space.
    """

    for row in rows:
        mean = row['mean']
        std = row['std']
        sum = row['sum']
        min = row['min']
        max = row['max']

    """
    You might put them one line explicitly, but that wastes a lot of horizontal
    space
    """
    for row in rows:
        mean, std, sum, min, max = row['mean'], row['std'], row['sum'], row['min'], row['max']

    """
    What if we try to be clever? We can use a list comprehension
    """
    for row in rows:
        mean, std, sum, min, max = [row[k] for k in ['mean', 'std', 'sum', 'min', 'max']]

    """
    That's not too bad, but we can do better
    """
    for row in rows:
        mean, std, sum, min, max = ub.take(row, ['mean', 'std', 'sum', 'min', 'max'])

    """
    And now even better:
    """
    for row in map(ub.udict, rows):
        mean, std, sum, min, max = row.take(['mean', 'std', 'sum', 'min', 'max'])
