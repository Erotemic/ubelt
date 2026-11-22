def demo_named_product():
    import numpy as np
    import pandas as pd

    import ubelt as ub

    def some_function(thresh1, thresh2):
        x, y = thresh1, thresh2
        z = (x**2 + y**2 - 1) ** 3 - x**2 * y**3
        return np.log(z)

    s = 2.5
    basis = {
        'thresh1': np.linspace(-s, s, 128),
        'thresh2': np.linspace(-s, s, 128),
    }
    grid_iter = ub.named_product(basis)
    rows = []
    for params in grid_iter:
        key = ub.repr2(params, compact=1)
        row = {
            'key': key,
            **params,
        }
        score = some_function(**ub.compatible(params, some_function))
        row['score'] = score
        rows.append(row)

    data = pd.DataFrame(rows)
    print(data)

    # import seaborn as sns
    import kwplot

    sns = kwplot.autosns()
    sns.scatterplot(data=data, x='thresh1', y='thresh2', hue='score')
