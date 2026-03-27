# Ubelt Typing Triage Audit

Audit date: `2026-03-27`

## Baseline

- Current checker floor:
  - `python -m mypy ubelt --hide-error-context --no-error-summary` passes
  - `ty check ./ubelt` passes
- Scope of this document:
  - actionable typing suppressions and underspecified inline types in `ubelt/`
  - test typing debt in `tests/`
- Raw upper-bound scan counts from the initial sweep:
  - `ubelt/`: 96 ignore-style suppressions, 261 `Any` mentions
  - `tests/`: 90 ignore-style suppressions, 60 `Any` mentions
- Goal:
  - triage work needed to reach "robustly typed", not merely "currently checker-clean"

### Included As Actionable Debt

- `# type: ignore`, `pyright: ignore`, and `ty: ignore`
- annotation-level `Any`
- broad `Callable[..., Any]`, `dict[str, Any]`, `typing.cast(Any, ...)`, and similar underspecified inline types
- dynamic attribute tricks that remain checker-clean today but are still type-model debt

### Explicit Exclusions

- prose/docstring-only mentions of `Any`
- `dev/` code other than this plan file
- purely local duplicate suppressions when one nearby root cause explains them

### Reading Guide

- The scan counts above are upper bounds.
- The detailed inventory below is grouped by root cause, not by raw line count.
- A single finding may cover several adjacent suppressions if they all stem from the same type-model problem.

## Triage Categories

Every finding below uses one of these categories.

| Category | Grouped findings | Meaning |
| --- | ---: | --- |
| `Simple fix` | 13 | Mostly annotation tightening, better local aliases, or replacing `Any` with `object` / a narrower built-in type. |
| `Small refactor / type-model fix` | 25 | Needs a better local type model, helper alias, protocol, generic parameter, or branch split, but no meaningful behavior change. |
| `Requires runtime overhead` | 5 | Probably needs additional runtime narrowing or validation to express safely. |
| `Requires breaking backward compatibility` | 6 | Public API or inheritance contract is the real blocker. |
| `Test-only debt` | 19 | Test convenience typing, negative-test suppressions, or tests compensating for library typing debt. |

## Scan Summary By Module

Counts below are the initial scan counts, before grouping and before excluding prose/docstring-only `Any` mentions.

### Library Modules

| Module | Ignore lines | `Any` lines | Notes |
| --- | ---: | ---: | --- |
| `ubelt/util_cmd.py` | 23 | 2 | Largest suppressions hotspot; subprocess branch modeling is the main issue. |
| `ubelt/util_dict.py` | 17 | 34 | Mixed generic containers, set-style dict ops, and sorting helpers. |
| `ubelt/util_list.py` | 13 | 25 | Iterator/sentinel flows and mapping-vs-sequence unions. |
| `ubelt/util_path.py` | 10 | 8 | Several real API-contract blockers against `pathlib.Path`. |
| `ubelt/util_download.py` | 8 | 4 | `BinaryIO` vs filesystem path unions and kwargs passthrough. |
| `ubelt/util_indexable.py` | 5 | 33 | Highly dynamic nested container traversal and mutation. |
| `ubelt/util_memoize.py` | 4 | 16 | Descriptors and decorator type preservation. |
| `ubelt/util_stream.py` | 4 | 2 | Stream proxying plus one explicit LSP violation. |
| `ubelt/orderedset.py` | 4 | 2 | Fancy indexing and one clear override blocker. |
| `ubelt/util_hash.py` | 3 | 24 | Dynamic registry APIs and broad object-to-hash surfaces. |
| `ubelt/util_format.py` | 2 | 2 | Deprecated wrapper that exposes dynamic attributes. |
| `ubelt/util_futures.py` | 1 | 27 | Executor/future generics are underspecified. |
| `ubelt/util_func.py` | 1 | 13 | Type preservation missing for simple helpers. |
| `ubelt/util_mixins.py` | 1 | 0 | One local ignore due `hasattr` not narrowing. |
| `ubelt/util_cache.py` | 0 | 24 | Cache payload/result typing is broad but mostly fixable with generics. |
| `ubelt/util_repr.py` | 0 | 16 | Registry callbacks are intentionally dynamic but still underspecified. |
| `ubelt/util_import.py` | 0 | 6 | Static AST parsing returns broad `Any`. |
| `ubelt/util_zip.py` | 0 | 5 | Dynamic file-handle proxying. |
| `ubelt/progiter.py` | 0 | 5 | Loose helper kwargs and lock types. |
| `ubelt/_win32_jaraco.py` | 0 | 4 | Internal Windows-only ctypes surface. |
| `ubelt/_win32_links.py` | 0 | 3 | Internal Windows-only callback/handle surface. |
| `ubelt/util_colors.py` | 0 | 2 | Mostly `**kwargs` passthrough. |
| `ubelt/util_io.py` | 0 | 1 | `touch(**kwargs)` can be tighter. |
| `ubelt/util_download_manager.py` | 0 | 1 | Deprecated but still public. |

### Test Files

| Test file | Ignore lines | `Any` lines | Notes |
| --- | ---: | ---: | --- |
| `tests/test_hash.py` | 29 | 3 | Many negative / numpy-specific cases and internal helper usage. |
| `tests/test_progiter.py` | 12 | 9 | Fake stream handling and internal state mutation. |
| `tests/test_import.py` | 9 | 1 | Legacy path/context usage linked to library typing gaps. |
| `tests/test_path.py` | 8 | 2 | Mostly linked to `ubelt.Path.copy` / `move`. |
| `tests/test_pathlib.py` | 8 | 0 | Legacy bool-int / command-call patterns. |
| `tests/test_download.py` | 6 | 1 | Linked to `BinaryIO` / `hasher=None` typing. |
| `tests/test_dict.py` | 4 | 0 | Intentional invalid-input tests. |
| `tests/test_cache_stamp.py` | 4 | 0 | Directly linked to `hasher=None` typing. |
| `tests/test_orderedset.py` | 3 | 7 | Invalid-input coverage plus `Any`-typed helpers. |
| `tests/test_cmd.py` | 3 | 3 | Legacy call patterns and monkeypatch helpers. |
| `tests/test_stream.py` | 2 | 0 | Compatibility-property assertions. |

## Known Structural Blockers

These are the clearest places where typing debt is downstream of public API shape, not missing annotation work.

| Location | Symbol / behavior | Current directive / type | Why this is a blocker | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/orderedset.py:225` | `OrderedSet.add()` | `# type: ignore[override]` and `-> int` | `MutableSet.add()` returns `None`; ubelt returns the insertion index. | `Requires breaking backward compatibility` | Yes | No | Decide whether `add()` keeps index-returning behavior, and if so document it as intentionally non-LSP; otherwise stage a deprecation toward `None`. |
| `ubelt/util_path.py:1071` | `Path.mkdir()` | `# type: ignore` and chainable return | `pathlib.Path.mkdir()` returns `None`; ubelt returns `Path` for chaining. | `Requires breaking backward compatibility` | Yes | No | Treat chainability as a compatibility decision; if typing purity wins, deprecate chaining or move it to a new method. |
| `ubelt/util_path.py:1323` | `Path.touch()` | `# type: ignore` and chainable return | Same shape as `mkdir()`: convenience return value conflicts with the stdlib contract. | `Requires breaking backward compatibility` | Yes | No | Handle with the same decision as `mkdir()`. |
| `ubelt/util_path.py:1653` | `Path.copy()` | `# type: ignore` | `pathlib.Path.copy()` now exists and its contract differs from ubelt's preexisting API. | `Requires breaking backward compatibility` | Yes | No | Decide whether to preserve ubelt semantics under the same name or rename/re-home the richer API. |
| `ubelt/util_path.py:1826` | `Path.move()` | `# type: ignore` | Same issue as `copy()`: stdlib name collision plus incompatible signature/behavior. | `Requires breaking backward compatibility` | Yes | No | Same resolution path as `copy()`. |
| `ubelt/util_stream.py:128` | `TeeStringIO.encoding` | `-> typing.Any` plus ignore on return | Current behavior intentionally violates the base-class expectation in `io.StringIO`. | `Requires breaking backward compatibility` | Yes | No | Either preserve the legacy behavior and fence it off with explicit local casts, or change semantics in a compatibility release. |

## Library Inventory

### `ubelt/util_cmd.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_cmd.py:423-437,926-938` | `make_proc()` plus select backend stdio access | Multiple `# type: ignore` around `Popen` kwargs, `proc.stdout`, and `proc.stderr` | The real issue is that the code models both "PIPE" and "not PIPE" states with the same dict and process type. | `Small refactor / type-model fix` | No | No | Split process construction into typed helper branches or use a local `TypedDict`-like model for `Popen` kwargs and a `PIPE`-only helper for tee/select paths. |
| `ubelt/util_cmd.py:444,859-867,921-923` | `os.system()` returncode path and timeout timers | One `# type: ignore` plus two `pyright: ignore` pairs | These are local control-flow issues, not dynamic API problems. | `Simple fix` | No | No | Hoist typed timer variables and make `_normalize_system_returncode()` accept the `os.system()` return type directly. |
| `ubelt/util_cmd.py:498-499,1008-1049` | timeout error population and logged output fallback | `typing.cast(Any, ...)` and several `# type: ignore` | The tee path is mixing "definitely text" and "maybe bytes" concepts in one container. | `Small refactor / type-model fix` | No | No | Normalize tee buffers to one concrete type per path, then remove the `Any` casts and append/join ignores. |
| `ubelt/util_cmd.py:130-158` | `CmdOutput` mapping-backed process result type | dict subclass with partially implicit keys | The public result object is only lightly typed today; robust typing wants a more explicit shape than "dict with some conventional keys". | `Small refactor / type-model fix` | Yes | No | Introduce a dedicated typed result schema for known keys while preserving dict compatibility. |

### `ubelt/util_dict.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_dict.py:232-235` | `group_items()` pair iterator | `# type: ignore[assignment]` on `zip(key, items)` | The callable-vs-iterable key union is not reflected cleanly in local iterator typing. | `Simple fix` | Yes | No | Use separate local variables for callable and iterable branches with a single concrete iterator type. |
| `ubelt/util_dict.py:312-405` | `dict_hist()` and `find_duplicates()` staging containers | Several `# type: ignore[assignment]` | The code moves among `Counter`, `defaultdict`, and `dict` without a stable local mapping type. | `Simple fix` | Yes | No | Normalize these locals to a single `MutableMapping[...]` model and stop reassigning them across unrelated concrete types. |
| `ubelt/util_dict.py:759-836` | `sorted_values()` and `sorted_keys()` | `typing.cast(Any, lambda ...)` plus `# type: ignore` | `Any` is compensating for poorly typed sort-key lambdas. | `Small refactor / type-model fix` | Yes | No | Use named helper functions with concrete tuple parameter types instead of `Any`-casts inside `sorted()`. |
| `ubelt/util_dict.py:899-902,1145,1725` | `invert_dict()`, `varied_values()`, and `SetDict.union()` staging | `# type: ignore[arg-type]`, `attr-defined`, `assignment` | These are classic "container mutation shape" issues that should be modelable without `Any`. | `Small refactor / type-model fix` | Yes | No | Introduce concrete local aliases for `defaultdict[VT, set[KT]]`, iterable-of-items constructors, and list-to-tuple normalization. |
| `ubelt/util_dict.py:1406-1861` | set-style dict operators and helpers | Repeated `Mapping[Any, Any]`, `Iterable[Any]`, and `other: typing.Any` | The public API is broader than necessary and leaks `Any` through nearly every set-like operator. | `Small refactor / type-model fix` | Yes | No | Replace public `Any` surfaces with `object`, `Mapping[KT, VT]`, `Iterable[tuple[KT, VT]]`, or a small shared alias that preserves `Self`. |

### `ubelt/util_list.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_list.py:294-369` | chunk iterator and sentinel handling | Multiple `# type: ignore[...]` in `_new_iterator()`, `noborder()`, and `replicate()` | Sentinel filtering is defeating the checker because the iterator/value type is not modeled clearly. | `Small refactor / type-model fix` | Yes | No | Introduce a private helper for chunk post-processing so each branch returns `list[VT]` without inline ignores. |
| `ubelt/util_list.py:396,490,499` | `iterable()` and `take()` | `# type: ignore` on `iter(obj)`, indexed sequence access, and `Mapping.get()` | These functions mix sequence and mapping behavior in a way that is easy at runtime but awkward statically. | `Requires runtime overhead` | Yes | Small | If we want to eliminate the ignores completely, add runtime branch narrowing (`isinstance(..., Sequence)` / `Mapping`) before indexing. |
| `ubelt/util_list.py:906-920,926-995` | `argsort()`, `argmax()`, and `argmin()` key functions | `# type: ignore[misc]`, `typing.Any` tuple/key helpers | The key-function plumbing is too loose for a strongly typed comparator path. | `Simple fix` | Yes | No | Use typed helper functions for `(value, key)` tuples and return narrower local types after mapping-vs-sequence branching. |

### `ubelt/util_path.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_path.py:375` | legacy tuple-input handling in `ensuredir()` | `join(*dpath)  # type: ignore` | This is a local path coercion issue, not a public design blocker. | `Simple fix` | Yes | No | Normalize tuple-like path inputs through `os.fspath()` / explicit sequence handling before calling `join()`. |
| `ubelt/util_path.py:1071,1323` | chainable `mkdir()` / `touch()` | `# type: ignore` on override signatures | These directly conflict with `pathlib.Path` contracts. | `Requires breaking backward compatibility` | Yes | No | Decide whether chainability stays; if yes, keep the type escape hatch and record it as intentional. |
| `ubelt/util_path.py:1218,1344,1402,1612-1626` | `chmod()`, `relative_to()`, `walk()`, `_request_copy_function()` | `-> typing.Any`, `**kwargs: typing.Any`, `Callable[..., Any]` | Most of these can be modeled with tighter return and callback types. | `Simple fix` | Yes | No | Tighten `chmod()` to return `Path`, narrow `**kwargs` to `object`, and use a concrete alias for the shutil copy-callable shape. |
| `ubelt/util_path.py:1653,1826` | `copy()` / `move()` | `# type: ignore` | Stdlib added these names later with incompatible contracts, so typing debt is downstream of API shape. | `Requires breaking backward compatibility` | Yes | No | Resolve the name-collision strategy before attempting precise typing. |
| `ubelt/util_path.py:2050,2148-2156,2218-2256` | chmod parser staging, Windows stat monkeypatch, path backports | `# type: ignore[assignment]`, attribute injection, `self: Any`, `other: Any` | These are internal compatibility shims that are broader than they need to be. | `Small refactor / type-model fix` | No | No | Use local aliases for parsed chmod actions and concrete `Path`-like inputs for the backports instead of `Any`. |

### `ubelt/util_download.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_download.py:204,224` | timeout default and `fpath` path-vs-IO split | private socket default plus `# type: ignore` on filesystem ops | Static typing is exposing that the function accepts both path-like and file-like destinations but narrows only with `hasattr`. | `Requires runtime overhead` | Yes | Small | Add explicit runtime narrowing for IO objects vs filesystem paths and isolate the default-timeout sentinel in a typed helper. |
| `ubelt/util_download.py:234-310` | `requestkw` / `progkw` mutation and passthrough | `Mapping[str, Any]` plus ignores on mutation, `Request`, `urlopen`, and `Progress(**...)` | Read-only mapping types and kwargs passthrough are mismatched with the actual mutating implementation. | `Small refactor / type-model fix` | Yes | No | Copy into mutable local dicts with concrete value types before mutation and passing through to constructors. |
| `ubelt/util_download.py:388,589` | `grabdata()` passthrough kwargs and coupled return type | `**download_kw: Any` plus ignore near passthrough call | The wrapper inherits the looseness of `download()` instead of preserving its public result coupling. | `Small refactor / type-model fix` | Yes | No | Mirror the narrowed `download()` types here and keep the wrapper result surface aligned. |

### `ubelt/util_indexable.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_indexable.py:29-274` | cache fallback, walker protocol, `_lazy_numpy()`, and traversal API | import ignore, many `Any`-typed generator inputs/outputs | The public walker is intentionally dynamic, but the current type surface is much broader than it needs to be. | `Small refactor / type-model fix` | Yes | No | Introduce explicit path/value aliases and a small container protocol instead of raw `Any` in the generator signatures. |
| `ubelt/util_indexable.py:308-383` | nested mutation and deletion | `# type: ignore[assignment]`, `index`, and `union-attr` | Eliminating these cleanly likely requires explicit runtime narrowing between mapping and sequence branches. | `Requires runtime overhead` | Yes | Small | Add concrete `isinstance`-based branches before mutation and deletion so each operation sees one container kind at a time. |
| `ubelt/util_indexable.py:426-857` | `values()`, `_walk()`, diff/info helpers | `Iterator[Any]`, `dict[str, Any]`, `tuple[Any, dict[str, Any]]` | These internal summary/result structures can be tighter even if the traversed payload stays open-ended. | `Small refactor / type-model fix` | Yes | No | Replace payload `Any` with `object` where possible and define named result aliases for info dicts and diff tuples. |

### `ubelt/orderedset.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/orderedset.py:158-160` | fancy indexing in `__getitem__()` | two bare `# type: ignore` comments | The index parameter is richer than the local branch typing, but this is still modelable. | `Small refactor / type-model fix` | Yes | No | Split the branch types more explicitly and avoid relying on `hasattr('__index__')` for everything. |
| `ubelt/orderedset.py:205,424` | pickle restore path and equality input | `# type: ignore[arg-type]` and `other: typing.Any` | Both are looser than needed. | `Simple fix` | Yes | No | Narrow `__setstate__()` to the actual accepted restore shape and change `other` to `object`. |
| `ubelt/orderedset.py:225` | `add()` return type | override ignore and `-> int` | This is the strongest `OrderedSet` typing blocker and is a public API decision, not an annotation omission. | `Requires breaking backward compatibility` | Yes | No | Keep tracked under the structural blocker list until the return contract is settled. |

### `ubelt/util_memoize.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_memoize.py:65-105` | `_hashable()` and `_make_signature_key()` | pervasive `typing.Any` | These internals operate on arbitrary inputs, but `object` and a narrower key alias would still be more meaningful than `Any`. | `Small refactor / type-model fix` | No | No | Replace raw `Any` with `object` or a dedicated cache-key alias where mutation of the value is not intended. |
| `ubelt/util_memoize.py:121-165,299,346,356` | `memoize()` and `memoize_property()` | `Callable[..., Any]`, `typing.Any` returns | The decorators do not preserve callable signatures or result types. | `Small refactor / type-model fix` | Yes | No | Add type-preserving generic wrappers for function and property cases. |
| `ubelt/util_memoize.py:251-295` | `memoize_method` descriptor machinery | `# type: ignore` on wrapper metadata and `setattr()` | Descriptor state and bound-method caching are being modeled as `Any` instead of a narrow descriptor type. | `Small refactor / type-model fix` | Yes | No | Introduce a dedicated descriptor helper type and typed cache storage for bound memoizers. |

### `ubelt/util_stream.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_stream.py:62-64,243` | `buffer` attribute and `_make_proxy()` | `# type: ignore` on dynamic stream proxy state | These are dynamic but not inherently untypable. | `Small refactor / type-model fix` | No | No | Introduce a small text-stream proxy protocol with optional `buffer` and use that consistently. |
| `ubelt/util_stream.py:128-160` | `encoding` property | `-> typing.Any`, setter `value: typing.Any`, return ignore | This is a real base-class contract conflict, not just a local annotation miss. | `Requires breaking backward compatibility` | Yes | No | Keep tracked as a structural blocker unless the runtime behavior changes. |
| `ubelt/util_stream.py:42-55` | `redirect` surface | `io.IOBase | None` but behavior expects richer text-stream attributes | The implementation uses `write`, `flush`, `fileno`, and sometimes `encoding` / `buffer`, which is more specific than `IOBase`. | `Small refactor / type-model fix` | Yes | No | Define a local protocol for the redirected stream rather than relying on a too-broad base class. |

### `ubelt/util_cache.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_cache.py:191-204` | logger callback type | `Callable[[str], Any]` | A logger sink should not need `Any` for its return type. | `Simple fix` | Yes | No | Narrow to `Callable[[str], object]` or `Callable[[str], None]`. |
| `ubelt/util_cache.py:486-710` | cached payload methods | `load() -> Any`, `save(data: Any)`, `_backend_* -> Any` | The cache payload can be generic without erasing all type information. | `Small refactor / type-model fix` | Yes | No | Parameterize cache payload/result type where possible and use `object` for metadata-only flows. |
| `ubelt/util_cache.py:729-1400` | `ensure()` / metadata / deprecated compatibility params | `*args: Any`, `**kwargs: Any`, `dict[str, Any]`, `product: Any` | Generic payload work and deprecated metadata compatibility are mixed into one loose surface. | `Small refactor / type-model fix` | Yes | No | Keep `ensure()` type-preserving, but isolate deprecated metadata helpers and narrow the non-payload dicts. |

### `ubelt/util_futures.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_futures.py:81-99,230-252,448-470,574-693` | executor, job-pool, and map/join surfaces | many `Any`-typed callables, iterables, results | The concurrency wrappers should preserve submitted function result types more explicitly. | `Small refactor / type-model fix` | Yes | No | Thread a single result type parameter through `Executor`, `SerialFuture`, and `JobPool`. |
| `ubelt/util_futures.py:139-174` | `SerialFuture` private stdlib hooks | `_invoke_callbacks()  # type: ignore` and `_Future__get_result() -> Any` | This depends on private stdlib internals and is therefore brittle both semantically and typably. | `Requires runtime overhead` | No | Small | Either keep the private override and local casts, or add wrapper logic that avoids depending on private internals. |

### `ubelt/util_hash.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_hash.py:404,566` | hasher lookup and extension registration | `str | Any`, `Callable[..., Any]` | These are public extension points and should expose a clearer protocol than raw `Any`. | `Small refactor / type-model fix` | Yes | No | Replace `Any` with the existing hasher protocol types and keep public helpers aligned with them. |
| `ubelt/util_hash.py:558,1697-1698` | dynamic function attributes on dispatch / `hash_data` | `# type: ignore` on attached attributes | The pattern is intentional but hidden from the type system. | `Small refactor / type-model fix` | Yes | No | Wrap the function-plus-registry state in a dedicated object or annotate the augmented callable explicitly. |
| `ubelt/util_hash.py:778-1457` | converter callbacks and public `data` arguments | many `data: Any` annotations and one `cast(Any, data)` | Many of these should be `object` or the concrete registered type instead of `Any`. | `Small refactor / type-model fix` | Yes | No | Narrow public payload entry points to `object`, and narrow converter callbacks to the concrete registered types they actually handle. |

### `ubelt/util_repr.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_repr.py:428-1113` | formatter registry, lookup, and formatter callbacks | `Callable[..., Any]`, `data: Any`, `**kwargs: Any` | The registry is intentionally dynamic, but it still has a recognizable contract: formatters take an object and return `str`. | `Small refactor / type-model fix` | Yes | No | Define a formatter protocol with `object` input and `str` output, then narrow registry storage and callback signatures toward it. |

### `ubelt/util_format.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_format.py:17,73-74` | deprecated `repr2()` wrapper and attached attributes | `**kwargs: Any` and two dynamic-attribute ignores | The wrapper is thin enough that it should either reuse the upstream formatter protocol or be deliberately fenced off as deprecated shims. | `Small refactor / type-model fix` | Yes | No | Keep deprecation behavior but reuse the tighter `util_repr` callable/registry types. |

### `ubelt/util_func.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_func.py:21-25` | `identity()` | `arg: Any | None`, `*args: Any`, `**kwargs: Any`, `-> Any` | This function is a textbook type-preservation candidate. | `Simple fix` | Yes | No | Preserve the first argument type instead of returning raw `Any`. |
| `ubelt/util_func.py:68-124` | `inject_method()` and `compatible()` | `self: Any`, `Callable[..., Any]`, `dict[str, Any]`, one `# type: ignore` | The APIs are broad, but not so broad that they need `Any` everywhere. | `Small refactor / type-model fix` | Yes | No | Use object-typed instance inputs, a typed bound-method helper, and mapping/object-oriented config types instead of raw `Any`. |

### `ubelt/progiter.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/progiter.py:111,251,264,298,431` | length inference, lock setter, and loose kwargs passthrough | several `typing.Any` params / `**kwargs` | Most of these can be tightened to `object` or a small stream/progress protocol without affecting behavior. | `Simple fix` | Yes | No | Replace obviously inert `Any` annotations with `object` and tighter helper protocols. |

### `ubelt/util_zip.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_zip.py:287-323,382` | zip handle proxying | `self._handle: Any`, `zfile() -> Any`, `__getattr__() -> Any` | The proxy is dynamic, but the underlying archive/file-handle surfaces are still much narrower than `Any`. | `Small refactor / type-model fix` | Yes | No | Define a small archive-handle protocol and separate the read-handle and wrapped-handle types. |

### `ubelt/util_download_manager.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_download_manager.py:68-161` | deprecated manager result surface | `_dl_func: Callable[..., object]` and `as_completed() -> Iterable[Any]` | Even though the class is deprecated, it is still public and should advertise a stable result type. | `Small refactor / type-model fix` | Yes | No | Thread the download result type through the internal pool and `as_completed()`. |

### `ubelt/util_colors.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_colors.py:56,122` | pygments kwargs passthrough | `**kwargs: typing.Any` | These kwargs are open-ended, but `object` is still a better signal than `Any`. | `Simple fix` | Yes | No | Replace passthrough `Any` with `object` or a tiny pygments-kwargs alias. |

### `ubelt/util_io.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_io.py:183-188` | `touch()` extra kwargs | `**kwargs: typing.Any` | The args are forwarded but not semantically "any value changes control flow". | `Simple fix` | Yes | No | Narrow to `object` or a dedicated `os.utime` kwargs alias. |

### `ubelt/util_import.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_import.py:1118-1224` | `_static_parse()` and `_parse_static_node_value()` | `-> typing.Any` and `cast(Any, node)` | This AST helper parses only a limited set of literal node shapes, so `Any` is broader than the runtime behavior. | `Simple fix` | No | No | Replace `Any` with a dedicated static-literal alias and keep unsupported nodes raising `TypeError`. |

### Windows-Only Internals

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/_win32_jaraco.py:218-222`, `ubelt/_win32_links.py:607-663` | ctypes callback / handle surfaces | several `typing.Any` params and returns | These are internal and platform-specific, but they still deserve narrower Windows handle / callback types than raw `Any`. | `Small refactor / type-model fix` | No | No | Introduce minimal Windows-only aliases or protocols without changing runtime behavior on non-Windows platforms. |

### `ubelt/util_mixins.py`

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ubelt/util_mixins.py:159` | `NiceRepr.__nice__()` default `__len__` path | `# type: ignore` on direct `self.__len__()` call | This is a local narrowing issue caused by `hasattr()` not implying `Sized`. | `Simple fix` | Yes | No | Use a local protocol / `typing.cast` to `Sized` in the narrowed branch instead of a blanket ignore. |

## Test Appendix

Tests are grouped by library surface under test. If a test suppression exists only because of a library typing gap, the owning library finding is called out explicitly.

### `cmd` / subprocess-related tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_cmd.py:86` | `ub.Path(ub.find_exe('ls'))` | `# type: ignore` | Linked to path-like / optional executable-path typing. | `Test-only debt` | Linked to `util_path` / platform path helpers | No | Tighten `find_exe()` result typing or cast locally in the test once the library type is settled. |
| `tests/test_cmd.py:200,218` | monkeypatching `os.waitstatus_to_exitcode` | `# type: ignore` | Intentional monkeypatch of a stdlib function slot is not worth typing precisely in the test. | `Test-only debt` | No | No | Leave as explicit test-only escape hatch. |
| `tests/test_cmd.py:458,524` | `common_kwargs: Any` helper typing | annotation-level `Any` | Pure test convenience typing. | `Test-only debt` | No | No | Replace with `dict[str, object]` or a small helper alias. |

### `dict` tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_dict.py:60-62` | intentional invalid-input coverage for `dzip()` | `# type: ignore` | These are negative tests, not library typing debt. | `Test-only debt` | No | No | Keep grouped under "intentional invalid-input tests". |
| `tests/test_dict.py:86-87` | `map_values()` result coercion | `# type: ignore[arg-type,return-value]` | Linked to `util_dict` generic value transformation typing. | `Test-only debt` | Linked to `util_dict` | No | Revisit after tightening `map_values()` / `map_keys()` generics. |

### `download` / cache tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_cache_stamp.py:15,46,72,88`, `tests/test_download.py:181,187` | `hasher=None` call sites | several `# type: ignore` comments | These are direct symptoms of the current download/cache hasher surface being narrower in types than in runtime behavior. | `Test-only debt` | Linked to `util_download` / cache API | No | Decide whether `None` is a supported public hasher sentinel and type it consistently. |
| `tests/test_download.py:60,446` | `BinaryIO` destination handling | `# type: ignore` on file object use | Directly linked to `download()` path-vs-IO typing. | `Test-only debt` | Linked to `util_download` | No | Remove after `download()` narrows destination kinds with a better public type model. |
| `tests/test_download.py:488,539` | singleton / third-party import looseness | assignment ignore and `import-untyped` | Pure test scaffolding. | `Test-only debt` | No | No | Keep as test-local debt unless requests typing becomes required. |

### `hash` tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_hash.py:38,54,639` | internal helper / external helper typing | several `# type: ignore` comments | Mixture of external helper typing gaps and direct use of internals. | `Test-only debt` | Partial | No | Keep grouped until `Timerit` and internal tracer usage are revisited. |
| `tests/test_hash.py:116-149,253-348,762` | numpy/object edge cases and intentionally weird payloads | many `# type: ignore` comments | Mostly negative or edge-case tests for a function that intentionally accepts very broad inputs. | `Test-only debt` | Linked to `util_hash` | No | Leave grouped; revisit only after deciding whether public `hash_data(data)` should be typed as `object` or remain broader. |
| `tests/test_hash.py:97,131,220` | helper annotations with `typing.Any` | annotation-level `Any` | Test helpers can be narrowed independently of the library. | `Test-only debt` | No | No | Replace with `object` in helpers that only inspect or forward values. |

### `import` / path / platform tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_import.py:20,42,150-152,451,454` | temp-path and tuple-path helpers | several `# type: ignore` comments | Linked to legacy `Path` / `ensuredir()` typing. | `Test-only debt` | Linked to `util_path` | No | Remove after path coercion and `ensuredir()` typing are tightened. |
| `tests/test_import.py:170,459` | `PythonPathContext(dpath)` | `# type: ignore` | Linked to import-context path typing. | `Test-only debt` | Linked to `util_import` / path helpers | No | Revisit once the public path/context surface is narrowed. |
| `tests/test_import.py:79`, `tests/test_platform.py:39` | helper kwargs and executable-path assertion typing | `typing.Any` and one ignore | Minor test-local looseness. | `Test-only debt` | No | No | Narrow to `object` / explicit optional handling. |
| `tests/test_path.py:86`, `tests/test_pathlib.py:140-226,591-592` | intentionally loose legacy call patterns | invalid-arg ignore and command-call ignores | These preserve runtime compatibility for legacy calling styles. | `Test-only debt` | Mixed | No | Keep documented as compatibility tests unless the library explicitly rejects the legacy forms. |
| `tests/test_path.py:177-187,327-349` | `Path.copy()` / `move()` call sites | many `# type: ignore` comments | Direct fallout from the `util_path` copy/move typing blocker. | `Test-only debt` | Linked to `util_path` structural blocker | No | Remove only after the public `copy()` / `move()` contract decision is made. |

### `orderedset` tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_orderedset.py:85,172,179` | intentionally invalid indexing / update calls | `# type: ignore[...]` | These are negative tests and should stay grouped as such. | `Test-only debt` | No | No | Keep as intentional invalid-input coverage. |
| `tests/test_orderedset.py:22,183,188,259-273`, `tests/test_oset.py:37-39` | helper annotations using `Any` | several annotation-level `Any` sites | Test helpers are broader than necessary even after accounting for invalid-input coverage. | `Test-only debt` | No | No | Replace local helper `Any` with `object` and a few narrower iterable/result aliases. |

### `progiter`, `stream`, `list`, and `futures` tests

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_progiter.py:339-357,469-811` | fake streams, internal field mutation, and helper annotations | many ignores plus several `prog: Any` annotations | Mix of legitimate internal-state testing and avoidable helper looseness. | `Test-only debt` | Linked to `progiter` | No | Split internal-state tests from helper typing cleanup; use a small fake-stream protocol instead of `Any`. |
| `tests/test_stream.py:26-27`, `tests/test_list.py:20,25` | compatibility aliases and generator helper locals | ignores plus `gen: Any` | These are pure test ergonomics. | `Test-only debt` | No | No | Replace with concrete local helper types or explicit casts. |
| `tests/test_futures.py:70,119,168,189,220,295` | optional capture text, weak-future maps, kill-file helper | one ignore plus several `Any` / `cast(Any, ...)` | Mostly test-local convenience typing. | `Test-only debt` | No | No | Narrow helper maps and local sentinel values to concrete optional/object types. |

### `indexable`, `links`, `repr`, `editable_modules`, and misc helpers

| Location | Symbol / behavior | Current directive / type | Why dubious | Category | Public API impact | Runtime/import cost | Proposed next step |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/test_indexable.py:8-244` | mapping helper functions and fixture locals | pervasive annotation-level `Any` | Mostly test-local scaffolding around a highly dynamic library surface. | `Test-only debt` | Partial | No | Introduce simple local aliases for nested-test data and callable transforms. |
| `tests/test_links.py:516-522`, `tests/test_repr.py:89` | helper wrappers / nested-data builders | annotation-level `Any` | Test helpers are broader than the behavior actually exercised. | `Test-only debt` | No | No | Replace with `object`-based helpers and concrete nested-data aliases. |
| `tests/test_editable_modules.py:40,366-375`, `tests/test_cache.py:86` | repo-path helpers and return-value convenience typing | annotation-level `Any` | Pure helper debt, not library debt. | `Test-only debt` | No | No | Tighten local helper signatures independently of production typing work. |

## Suggested Implementation Order

1. Start with `Simple fix` items in `util_func`, `util_mixins`, `util_import`, `util_colors`, `util_io`, `progiter`, and the local-cleanup portions of `util_dict` / `util_cmd`.
2. Move to `Small refactor / type-model fix` hotspots with high suppressions payoff: `util_cmd`, `util_dict`, `util_list`, `util_download`, `util_indexable`, `util_memoize`.
3. Tackle generic preservation work in `util_cache`, `util_futures`, `util_hash`, and `util_repr`.
4. Leave structural blockers (`OrderedSet.add`, `Path` chainable overrides, `Path.copy` / `move`, `TeeStringIO.encoding`) for an explicit compatibility decision.
5. Clean the tests after each library surface tightens so test-only debt does not hide real regressions.

## Assumptions And Defaults

- This audit prefers low-runtime-cost fixes first, in line with `dev/agents/TYPING_RULES.md`.
- When a location could be typed either by adding runtime validation or by slightly broadening a static type, this audit defaults to the broader low-overhead static type and records the runtime-checking option only when it seems necessary.
- `object` is preferred over `Any` whenever the code is not meant to perform unchecked arbitrary operations on the value.
- Dynamic function-attribute patterns and monkeypatch-style APIs are inventoried even when current checkers accept them.
- `ubelt/util_links.py` and `ubelt/util_arg.py` were not given dedicated rows because their scan hits were prose/docstring-only `Any` mentions, which are excluded by rule.
- No runtime code changes are part of this document; checker commands are recorded only to anchor the baseline.

## Verification Checklist

- [x] Recorded the baseline date and checker status.
- [x] Captured the requested upper-bound scan counts.
- [x] Included both `ubelt/` and `tests/`.
- [x] Added a summary table with counts by category.
- [x] Added summary tables with counts by module/test file.
- [x] Added a dedicated structural-blocker section with the requested seeds.
- [x] Grouped test debt separately and linked it back to owning library issues where applicable.
