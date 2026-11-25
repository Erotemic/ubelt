# Ubelt cookbook

Examples use `import ubelt as ub`. The full API documentation is at
<https://ubelt.readthedocs.io/en/latest/>. Check the installed version with
`ub.__version__` before using recently added arguments. These examples target
ubelt 1.5.

## Find the utility for a task

| Task | API |
| --- | --- |
| Execute a subprocess, capture stdout/stderr, and optionally stream live output | `ub.cmd` |
| Create output directories or manipulate filenames with fluent helpers | `ub.Path.ensuredir`, `ub.Path.augment` |
| Create a symbolic link with an explicit target representation | `ub.symlink` |
| Download a file and verify a known digest prefix | `ub.download`, `ub.grabdata` |
| Hash a file or generate a key for nested Python data | `ub.hash_file`, `ub.hash_data` |
| Cache a Python result on disk or skip completed work | `ub.Cacher`, `ub.CacheStamp` |
| Pretty-print a nested data structure | `ub.urepr` |
| Compare nested configurations or walk all their paths | `ub.IndexableWalker`, `ub.indexable_allclose` |
| Group records by a key, count occurrences, find duplicates | `ub.group_items`, `ub.dict_hist`, `ub.find_duplicates` |
| Select or reorder by indices/keys; flatten one level | `ub.take`, `ub.compress`, `ub.flatten` |
| Batch an iterable or make sliding windows | `ub.chunks`, `ub.iter_window` |
| Generate parameter-grid combinations | `ub.named_product` |
| Transform mappings or perform set operations on keys | `ub.udict`, `ub.map_values`, `ub.map_keys` |
| Run jobs serially, in threads, or processes with a uniform API | `ub.Executor`, `ub.JobPool` |
| Report progress or elapsed time | `ub.ProgIter`, `ub.Timer` |
| Build multiline strings without indentation artifacts | `ub.codeblock`, `ub.paragraph`, `ub.hzcat` |
| Find executables or locate Python modules | `ub.find_exe`, `ub.modname_to_modpath` |
| Get application cache/data/config directories | `ub.Path.appdir` |

## Run a subprocess and get both live and captured output

```python
import sys
import ubelt as ub

result = ub.cmd([sys.executable, '-c', 'print("hello")'],
                tee=True, check=True, timeout=30)
assert result.returncode == 0
assert result.stdout.strip() == 'hello'
```

Prefer argument lists instead of `shell=True` when passing variable inputs.
`check=True` raises on nonzero exit status; it is not the default. `tee=True`
streams and captures output. Captured output can be large; use `capture=False`
when no captured result is needed. Detached execution has different result
semantics; see the `cmd` docstring.

## Create directories and manipulate paths

```python
from tempfile import TemporaryDirectory
import ubelt as ub

with TemporaryDirectory() as tmp:
    dpath = (ub.Path(tmp) / 'results').ensuredir()
    fpath = dpath / 'summary.txt'
    fpath.write_text('done')
    assert fpath.augment(stemsuffix='_old').name == 'summary_old.txt'
```

Use standard `pathlib.Path` when it provides the operations you need. Choose
`ub.Path` for conveniences such as `ensuredir()`, `augment()`, `expand()`,
`delete()`, and `appdir()`, or for backports on older supported Python
versions. On Python 3.12+, standard `Path.walk()` is available. Note that
`ub.Path.mkdir()`, `touch()`, and `chmod()` return the path for chaining,
whereas the corresponding standard methods return `None`. The `ub.Path`
copy and move contracts also differ from their newer pathlib counterparts;
consult the relevant docstrings rather than assuming interchangeability.
For symlinks, choose `relative=True` or `relative=False` explicitly. For general-purpose
atomic file I/O, consider a specialized package such as
[safer](https://pypi.org/project/safer/). Ubelt does not promise atomicity or
concurrent-writer safety for its cache operations.

## Hash data or file contents

```python
import ubelt as ub

config = {'epochs': 10, 'model': 'example'}
key = ub.hash_data(config, types=True)
assert key == ub.hash_data(config, types=True)
```

Use `ub.hash_file(path, hasher='sha256')` for the digest of a file's bytes.
`hash_data` is convenient for ordinary trusted cache keys, but the legacy
structured encoding is ambiguous even with `types=True`. It is not suitable
for security-sensitive identifiers or where distinct structured values must
have distinct encodings. See its docstring for examples. Hash compatibility
also depends on serialization and hashing settings; do not assume a future
major version will have identical defaults.

## Cache a Python result (including None)

```python
from tempfile import TemporaryDirectory
import ubelt as ub

with TemporaryDirectory() as tmp:
    cacher = ub.Cacher('result', depends=['v1'], dpath=tmp,
                       backend='json', ext='.json', verbose=0)
    missing = object()
    result = cacher.tryload(default=missing)
    if result is missing:
        result = None
        cacher.save(result)
    assert cacher.tryload(default=missing) is None
    assert cacher.ensure(lambda: 'not recomputed') is None
```

Make `depends` include the relevant inputs and computation version. Short
string dependencies and `fname` are used directly in filenames: use safe
strings or explicitly hash the input. The default pickle backend must only
load trusted data. Select JSON for JSON-compatible values when appropriate.
`tryload(on_error='clear', default=missing)` can clear certain corrupt caches;
it does not make pickle loading safe. Use `verbose=0` to suppress reporting or
`log=some_callable` to redirect it.

## Skip a computation that produces files

```python
from tempfile import TemporaryDirectory
import ubelt as ub

with TemporaryDirectory() as tmp:
    product = ub.Path(tmp) / 'result.txt'
    messages = []
    stamp = ub.CacheStamp('build', dpath=tmp, depends=['v1'],
                          product=product, log=messages.append)
    if stamp.expired():
        product.write_text('result')
        stamp.renew()
    assert stamp.expired() is False
```

`expired()` returns `False` for a valid stamp or a truthy reason string for
an expired stamp. Renew only after all expected products have been produced.
The caller is responsible for specifying dependencies and coordinating workers.

## Inspect and compare nested data

```python
import ubelt as ub

before = {'model': {'depth': 4}, 'scores': [1, 2]}
after = {'model': {'depth': 5}, 'scores': [1, 2]}
print(ub.urepr(after, nl=1, sort=True))
info = ub.IndexableWalker(before).diff(after)
assert info['num_differences'] == 1
```

`urepr` is a representation, not a serialization format. `IndexableWalker`
walks nested dictionaries, lists and tuples; consult `diff` for tolerance
semantics when comparing numeric values.

## Group, select, and batch records

```python
import ubelt as ub

records = [{'kind': 'a', 'value': 1}, {'kind': 'b', 'value': 2},
           {'kind': 'a', 'value': 3}]
groups = ub.group_items(records, key=lambda row: row['kind'])
assert [r['value'] for r in groups['a']] == [1, 3]
assert list(ub.take(records, [2, 0])) == [records[2], records[0]]
assert list(ub.chunks(range(5), chunksize=2)) == [[0, 1], [2, 3], [4]]
assert len(list(ub.named_product(depth=[2, 4], width=[16, 32]))) == 4
```

## Submit jobs with progress reporting

```python
import ubelt as ub

with ub.JobPool(mode='thread', max_workers=2) as pool:
    for n in range(5):
        pool.submit(pow, n, 2)
    values = [job.result() for job in pool.as_completed(desc='collect')]
assert sorted(values) == [0, 1, 4, 9, 16]
```

Use `mode='serial'` for debugging and deterministic serial execution. For
process-based jobs, ensure functions and arguments are pickleable and follow
the standard-library multiprocessing entry-point requirements. The order of
`as_completed()` results is not guaranteed.

## Read this reference from an installed wheel

```python
from importlib.resources import files

reference = files('ubelt').joinpath('_docs', 'llms-full.txt').read_text(encoding='utf-8')
assert 'ub.cmd' in reference
```

`llms.txt`, `llms-full.txt`, and `cookbook.md` are also available under the
package's `_docs` resource directory. Regenerate these files in a source
checkout with `python dev/maintain/generate_llm_docs.py`.
