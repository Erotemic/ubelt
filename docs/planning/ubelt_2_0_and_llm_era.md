# Ubelt after 1.5: compatibility, correctness, and the LLM era

Status: proposed roadmap (2026-11-25). This is a planning document, not a
specification of new public APIs. The explicit intent to address structured
hash encoding ambiguities in 2.0 is already part of the 1.5 documentation
work. Other breaking changes require an explicit decision before implementation.

## Motivation

Ubelt has traditionally made common Python tasks more convenient. The cost of
producing boilerplate is declining as coding assistants become more capable,
but the cost of maintaining code, understanding its contracts, and dealing
with edge cases has not disappeared. An assistant can easily generate a small
replacement for a utility without realizing which cases the existing utility
handles. Ubelt can remain useful by making well-tested primitives easy to
find, understand, and reuse.

This is not a proposal to turn ubelt into an AI framework. The same properties
that help agents also help humans: clear contracts, useful examples, bounded
resource consumption, predictable errors, compatibility with the standard
library, and few dependencies. Prefer improvements to abstractions ubelt
already owns, rather than adding wrappers around every useful capability.

The historical usage analysis in
`docs/source/manual/function_usefulness.rst` is a starting point for deciding
where to invest. It reflects usage in the maintainer's code, not ecosystem-wide
adoption. High usage is useful evidence, but a rarely used primitive that
prevents a costly correctness error may warrant more work than a popular
trivial helper.

## Scope and release policy

The 1.5 cache and documentation changes are the assumed baseline for this
plan: `Cacher.tryload(default=...)`, correct handling of cached `None`, the
explicit pickle backend fix, `CacheStamp(log=...)`, documentation of the
legacy hash ambiguity, the task-oriented cookbook, and generated and packaged
agent-oriented API references. The current 1.5 symlink transition is also
assumed. Do not reimplement these features as part of this roadmap.

| Workstream | Priority | Earliest appropriate release |
| --- | --- | --- |
| Specify and implement structured hash v2 | P0 | Opt-in 1.x; default in 2.0 |
| Resolve `Path` / `pathlib` contract conflicts | P0 | Migration preparation in 1.x; decisions in 2.0 |
| Complete the symlink semantics transition | P0 | 2.0, per the 1.5 deprecation |
| Bounded `urepr` | P1 | Additive 1.x after design |
| Bounded capture and robust execution in `cmd` | P1 | Additive 1.x after design; incompatible changes in 2.0 |
| Cache keys, validation, and resumability | P1 | Additive 1.x; incompatible defaults/layouts in 2.0 |
| Agent usability evaluation and documentation maintenance | P1 | Independent of releases |
| Output-control conventions and logging | P2 | Incremental; no wholesale migration |
| Legacy API cleanup | P2 | 2.0 only where justified |

P0 denotes a compatibility or correctness problem worth resolving for 2.0;
P1 denotes a valuable candidate, not a release blocker; P2 denotes work to do
when there is a demonstrated need. A 1.6 compatibility bridge is an option,
not a requirement. There is no reason to hold 1.5 for large new features.
Do not infer that all of the workstreams must ship before 2.0.

## 1. Versioned structured hashing (P0)

Relevant code: `ubelt/util_hash.py`, especially `HashableExtensions`,
`_convert_to_hashable`, `_update_hasher`, and `hash_data`; callers in
`ubelt/util_cache.py`; existing hash tests and `dev/bench/bench_hash*.py`.

### Problem

The current encoding uses `_SEP`, `_ITER_PREFIX`, and `_ITER_SUFFIX` as
unescaped delimiters. `_update_hasher` also contains a known missing separator
on the recursive path. Distinct structures can encode to identical bytes
before the hash function is applied. These are encoding collisions, not
failures of SHA-512 or other hash algorithms.

Concrete legacy regression examples:

```python
import ubelt as ub

assert ub.hash_data(['a_,_b']) == ub.hash_data(['a', 'b'])
assert (ub.hash_data(['a_,_TXTb'], types=True)
        == ub.hash_data(['a', 'b'], types=True))
```

Preserve the historical results of the old protocol, including its defects.
Fixing just the missing separator is insufficient, and would itself break
existing identifiers.

### Design and implementation

1. Specify what it means for two supported values to have the same canonical
   encoding. `types=False` intentionally ignores some type distinctions, so
   the desired property is injectivity modulo the documented equivalence
   relation, not injectivity on every Python object. Decide what distinctions
   are retained even when types are omitted (e.g., scalar vs. container and
   sequence vs. mapping).
2. Specify an unambiguous framed encoding, with structural tags and lengths
   or an equivalent self-delimiting scheme. Include a protocol version/domain
   marker. Specify the treatment of empty values, byte strings, nested
   containers, and sequences of variable-length elements. Prefer streaming
   hashing where feasible instead of materializing a large serialized object.
3. Specify mapping and set ordering independently of Python's randomized hash
   seed and incidental iteration order. Decide separately how ordered mappings
   should behave. Cover mixed-type keys and stable ordering of encoded values.
4. Specify numeric equivalence (including signed zero, non-finite floats,
   NaNs, large integers, and optional NumPy scalars), Unicode, paths, UUIDs,
   dataclasses, arrays (shape, dtype, byte order, logical traversal), and
   existing registered types. Do not promise cross-platform stability for
   objects without a suitable canonical interpretation.
5. Decide how extensions encode values in v2. Existing extension hooks return
   pairs of byte strings; merely framing arbitrary extension output cannot
   guarantee uniqueness within that extension. Document the extension author's
   responsibilities and provide a separate v2 registration or adaptation
   mechanism as needed. Never silently reinterpret an incompatible extension.
6. Clarify `convert=True`, lazy iterables, shared references, and cycles. A
   JSON fast path must either implement the same documented encoding or be an
   explicitly distinct mode. Reject unsupported cases clearly rather than
   claiming general serialization support.
7. Keep the hash algorithm and output alphabet independently configurable.
   The version selector concerns structured encoding, not the choice of
   cryptographic hasher or the formatting of its digest. Do not change
   `hash_file` as a side effect.

An illustrative public interface (name and signature not finalized):

```python
ub.hash_data(data, version=1)  # historical behavior
ub.hash_data(data, version=2)  # new framed encoding
```

Introduce v2 as opt-in in a compatible release if possible. Keep v1 as the
1.x default and switch the default in 2.0. Retain an explicit v1 option for
reproducing old results, including persistent identifiers and experiment
records. Audit internal consumers and avoid silent fallback from a new cache
key to an old, potentially ambiguous key. Document version pinning and
migration examples. Recomputing a cache may be fine; changing an externally
stored identifier without a migration is not.

### Acceptance criteria

- Document the encoding with enough precision for another implementation to
  reproduce golden vectors. Test legacy vectors separately from v2 vectors.
- Assert distinct encoded byte streams for the collision examples and relevant
  adversarial nested structures; tests should inspect the encoding as well as
  digests. Test intentional equivalences separately.
- Cover ordering, optional types, unsupported inputs, extensions, and relevant
  interpreter/platform differences. Use targeted property tests if helpful.
- Compare throughput and peak memory to v1 for small and large inputs, nested
  data, and NumPy arrays. Keep expensive paths opt-in where appropriate.
- Do not claim collision-free hashes or security guarantees. Users still need
  an appropriate cryptographic algorithm, trustworthy canonicalization, and
  a domain-specific security review for security-sensitive applications.

## 2. Reassess `ub.Path` (P0)

Relevant code: `ubelt/util_path.py`, `tests/test_path.py` (and other path
consumers), the `Path` docstrings, and the cookbook.

The standard library has acquired some of the functionality that originally
motivated `ub.Path`. In particular, the current implementation delegates
`walk` and `relative_to(walk_up=...)` to `pathlib` on supported Python
versions, with backports for older interpreters. The current `copy` and
`move` docstrings explicitly acknowledge conflicts with newer `pathlib`
methods. `mkdir`, `touch`, and `chmod` return `self` for chaining instead of
preserving the inherited return-value contract.

We should not deprecate `ub.Path` merely because `pathlib` improved. There is
still value in its path augmentation, application-directory construction,
expanded paths, idempotent directory creation and deletion, and conveniences
that work across supported Python versions. But it should become a smaller,
more carefully defined extension of `pathlib` rather than an alternative
filesystem API.

### Preserve fluent workflows while improving substitutability

Recommended direction: inherited standard-library method names should
satisfy the applicable `pathlib.Path` contracts; ubelt-specific operations may
return paths for chaining. Returning `self` instead of `None` often works in
practice, and is convenient, but clients observing the return value or using
static type checking can distinguish the subclass. `copy` and `move` are
more consequential because differences may change which filesystem objects
are modified or overwritten.

| API | Direction |
| --- | --- |
| `ensuredir`, `delete`, `augment`, `appdir`, `expand` | Retain useful ubelt-specific behavior and fluent returns |
| `walk`, `relative_to` | Keep compatible backports while needed; delegate when available |
| `mkdir`, `touch`, `chmod` | Audit inherited contracts; preserve fluent alternatives where justified |
| `copy`, `move` | Resolve collisions without silently changing existing overwrite, destination, symlink, or metadata behavior |
| `ls`, `shrinkuser`, string-like methods/operators | Assess their distinct value and existing usage individually |

For example, the desired ergonomic pattern remains valid:

```python
dpath = (ub.Path.cwd() / 'results').ensuredir()
fpath = dpath / 'output.txt'
fpath.touch()
```

The second operation is less convenient than the current fluent `touch`.
Consider a narrowly scoped fluent alternative if usage data supports it; its
name and exact contract are open questions. A create-if-missing operation is
not necessarily equivalent to `touch`, which may update timestamps. The same
consideration applies to symbolic permission strings in `chmod`. Do not add a
second name for every mutating method by default.

### Migration work

- Build a method/signature/behavior matrix against `pathlib` on all supported
  Python versions (currently the 1.5 minimum is Python 3.10). Include return
  types, exception behavior, keyword names, symlink handling, overwrite
  semantics, and inherited methods that were added after `ub.Path`.
- Find chained calls and calls relying on existing `copy`/`move` semantics
  within ubelt, its examples, and a representative sample of downstream code.
- Decide whether to move the existing copy/move implementations to explicitly
  named ubelt-specific methods or functions, or provide another migration
  mechanism. Do not choose a new spelling before identifying the semantic
  difference it needs to communicate. If providing standard-library-compatible
  methods on older Python versions, make their behavior consistent across
  versions rather than changing it based on the installed interpreter.
- Add replacement APIs and migration documentation in 1.x as appropriate.
  Warnings about return-contract changes may need to be coarse-grained or
  documented, because a method cannot reliably detect whether its result is
  being chained. Avoid warning on every ordinary standard-library-style use
  without considering noise.
- In 2.0, resolve the known conflicts or document specific retained exceptions
  to the substitutability goal. Do not change behavior before migration paths
  are available and tested. Keep inexpensive compatibility conveniences where
  they do not conflict with the standard library.

Tests should include actual source/destination state, existing and missing
paths, symlinks, permissions and metadata where supported, and explicit
no-overwrite cases. Check static typing with the project's existing tools.
Prefer standard `pathlib.Path` in examples that do not need an extension.

## 3. Complete the symlink transition (P0)

Relevant code: `ubelt/util_links.py`, `_win32_links.py`, symlink tests, and the
1.5 changelog.

Version 1.5 added `relative=True` / `relative=False`, preserving legacy
behavior when requested. An ambiguous relative `real_path` with no explicit
mode currently warns. Equivalent target spellings are handled idempotently;
changing the requested representation of an existing link requires overwrite.

Follow through on the documented 2.0 commitment to require an explicit mode
for the ambiguous relative-target case. Confirm the intended status of
`relative='legacy'` (remove or keep as an explicit compatibility escape hatch)
and the default for already absolute targets before implementation. These are
separate from `Path` method compatibility.

Audit internal uses and examples. Preserve tests for link targets, broken
links, equivalent spellings, representation changes, destination collisions,
relative targets from different working directories, and Windows-specific
behavior. Do not remove a compatibility branch before the documented transition.

## 4. Bounded `urepr` (P1)

Relevant code: `ubelt/util_repr.py`, including `UReprKwargs`, `_urepr_impl`,
container formatting and `ReprExtensions`; `dev/bench/bench_urepr_vs_alternatives.py`.

A representation that is a few thousand characters is often much more useful
than one containing millions of characters. This applies to interactive
inspection, test failures, logs, and coding agents with finite context.
`urepr` should be able to produce a useful summary without first formatting an
entire large object.

Candidate opt-in controls (illustrative, not a final signature):

```python
ub.urepr(data, max_depth=4, max_items=20, max_chars=4000)
```

Design a shared traversal/budget state that accounts for indentation,
separators, omission markers and nested containers. Define depth from the root,
per-container versus global item limits, head/tail selection, sorting, and the
meaning of a character budget (Unicode code points rather than bytes or model
tokens unless otherwise documented). Decide whether the character limit is a
hard final-string guarantee and define behavior for budgets too small for an
omission marker. Distinguish a final output limit from limits on formatting work
and memory use.

Cycle detection should distinguish recursion through ancestors from shared
objects that are not cyclic. Truncation and cycle markers must be explicit;
bounded representations need not be evaluable Python, unlike the usual
`urepr` goal. Preserve ordinary unbounded output and existing formatting
options. Specify how the budget interacts with extensions, array summaries,
long scalar representations, and arbitrary user-defined `__repr__` methods.
Arbitrary custom formatters may do unbounded work: document that boundary.

Optional redaction by a user-supplied predicate is a separate candidate, not a
prerequisite or a guarantee that secrets will never appear. Avoid tokenizer
or model dependencies.

Start with built-in containers and explicit budget semantics. Acceptance:
unchanged existing doctests, bounded outputs on large and deep inputs, cyclic
structures, tiny budgets, deterministic omission policies, extension behavior,
and performance tests demonstrating that bounded mode need not traverse or
materialize all values when its policy permits early stopping.

## 5. Subprocess execution and bounded capture (P1)

Relevant code: `ubelt/util_cmd.py`, `CmdOutput`, `cmd`, `_tee_output`, and the
thread/select backends. Existing `cmd` tests cover a variety of execution modes.

`cmd` is useful because it combines subprocess execution, capture and live
output. It is worth making this abstraction robust rather than replacing it
with an agent-specific command runner. The current synchronous capture path
uses `communicate`; tee accumulates output in lists. Limiting only the final
string would not bound memory use. The current text and line-oriented
streaming path also needs to be considered for very long unterminated lines.

### Additive features

- Introduce an opt-in capture limit after deciding units (bytes vs. decoded
  characters), per-stream versus total budget, and head/tail retention policy.
  A possible interface is `max_capture_bytes=...`, not yet a commitment.
- Continue draining stdout and stderr even after the capture budget is reached,
  so a large volume of output does not cause a pipe deadlock. If tee is enabled,
  continue forwarding the full stream to its configured destination. Make
  truncation and omitted counts explicit in the returned result, not merely
  a magic string inserted into the process output.
- Separate diagnostic presentation (e.g., the printed command) from subprocess
  output destinations. Consider configurable stdout/stderr sinks for teeing.
  Preserve existing capture, tee, and verbosity defaults.
- Clarify timeout and cleanup guarantees. Audit the overall deadline across
  execution and draining, partial output carried by exceptions, child exit
  codes, worker/thread cleanup, and sink errors. Process-tree cancellation is
  a separate, optional design problem with platform-specific limitations;
  do not promise portable cleanup of arbitrary descendant processes.

Implement bounded capture first for a well-defined supported set of modes;
reject unsupported combinations before creating a subprocess. Default
unbounded behavior must remain compatible. Measure peak memory, not just final
result size, including queue buffers, partial lines, and Unicode decoding.

### Possible 2.0 modernization

Audit the mode matrix (`capture`, `tee`, `verbose`, `detach`, `system`,
`shell`, `check`, `timeout`) and the `CmdOutput` contract. A typed completed
result and a separately typed process handle could provide a clearer API;
consider overloads and mode-specific types before changing the public result
representation. Preserve `info['out']`, `info['err']`, and `info['ret']` where
practical, along with the completed-process-like properties. Consider retiring
`system=True` if its compatibility cost warrants it; preserve explicit shell
execution for legitimate uses. There is no current plan to change the
`check=False` default.

Acceptance: child scripts producing simultaneous stdout/stderr, large output,
long lines, non-ASCII data, nonzero exits, timeouts, sink failures and detached
execution as applicable. Cover both tee backends where supported. Use a
portable Python child process for tests where possible. Verify that capture
limits do not hide the exit code, that timeout/called-process errors expose
useful partial output, and that child/worker cleanup does not regress.

## 6. Caching and lightweight resumability (P1)

Relevant code: `ubelt/util_cache.py`, `Cacher`, `CacheStamp`, and cache tests.
The 1.5 sentinel and reporting improvements are the starting point.

### Cache key and layout policy

`Cacher._rectify_cfgstr` uses string dependencies directly, and
`_condense_cfgstr` hashes only longer strings. A short dependency such as
`'model/name'` therefore contributes a path separator to the cache filename.
Review key construction across separators, reserved names, absolute or drive
paths, `..`, Unicode and filename length, including user-supplied `fname` and
`ext`. Define which arguments are names and which are paths; make the safe
naming policy explicit. Lexical validation alone is not a defense against
symlink races or untrusted cache directories.

Prefer a deterministic versioned layout with an explicit migration story.
The current readable names may have legitimate value; consider a readable
prefix plus a digest rather than silently switching all paths to opaque keys.
Coordinate this work with hash v2. Distinguish cache storage layout versions
from structured hash encoding versions. Avoid fallback to ambiguous or unsafe
legacy paths. Do not silently delete or migrate a user's old cache.

### Metadata, serialization, and validation

- Evaluate optional structured metadata and disabling the existing `.meta`
  sidecar. Specify schema, compatibility, sensitive configuration handling and
  what happens when metadata writes fail. A new format need not be mandatory.
- Document that pickle loading is only suitable for trusted cache contents.
  Preserve explicit pickle support; evaluate an explicit backend policy or
  optional custom serialization hooks before changing defaults. JSON is not a
  drop-in replacement for arbitrary Python objects.
- Consider an additive, typed validation result for `CacheStamp`, e.g. a new
  method reporting status, reason, and affected products. Preserve the current
  `expired()` contract (false when valid, truthy reason string when expired)
  and existing reason strings. Reuse validation logic rather than running
  product checks twice. Keep optional details lazy where they require extra
  filesystem access.
- Examine failure behavior when writing cache-owned artifacts. In particular,
  document or prevent replacement of a previously valid cache by a failed
  serialization. This is an internal cache correctness concern, not a new
  public atomic I/O abstraction. Decide whether existing mechanisms or an
  established specialized library are appropriate before writing new code.
  Do not introduce a dependency without a separate decision, or claim
  multi-writer transactional consistency or power-loss durability.

Keep this subsystem a primitive for trusted, local computation caching and
artifact validation, not a workflow engine, database, or distributed lock
manager. Acceptance includes legacy cache reproduction, safe filename
construction, clear miss/failure behavior, explicit trust boundaries,
serialization failures, and product validation reasons with and without
optional detail.

## 7. Output control and diagnostics (P2)

Do not replace every `print` with `logging`. Distinguish three kinds of
output: diagnostic events, explicitly requested reports, and stream-oriented
output. `verbose` controls the amount of requested output; logging levels
express diagnostic severity and are filtered by application configuration.
They are not interchangeable.

`Cacher` and (with the 1.5 changes) `CacheStamp` already expose a `log`
callable. `cmd` has internal reporting and tee streams. Progress display,
stream capture, and timer output have different requirements again.

Consider extending the callable convention where there are concrete use
cases, and module-level standard logging for diagnostic events that need
application-wide control. Preserve the meaning of `verbose=0` and positive
verbosity; if independent diagnostic logging can still emit messages when
verbose is zero, document that explicitly. Choose a single emission path for
an event to avoid duplicate messages when a user enables both reporting and
logging. Never configure the root logger from ubelt. Do not log exceptions
immediately before raising them by default. Avoid eager expensive formatting
and unnecessary import overhead. Review command arguments, paths, URLs and
cache metadata for accidental disclosure of secrets.

Keep progress output, subprocess stdout/stderr, and stream capture stream-based.
No custom logging framework or global configuration switch is currently
planned. Use targeted compatibility tests and benchmark import/runtime overhead
if introducing logging. Defer broad changes until a concrete downstream
problem justifies them.

## 8. Discoverability and evaluation (P1)

The 1.5 documentation work establishes `llms.txt`, `llms-full.txt`,
`cookbook.md`, their installed counterparts, and
`dev/maintain/generate_llm_docs.py`. Keep the public docstrings and signatures
as the primary source, with the cookbook providing curated task-to-API
mappings. Avoid duplicating large amounts of prose across hand-maintained
references. Add the generator freshness check to an appropriate existing
release or CI check if it is not already run there.

Improve task coverage in response to observed discovery failures. Include
alternatives and tradeoffs (e.g. use `pathlib` or `subprocess.run` where they
suffice; use `safer` for specialized safe file I/O). Do not change the existing
`python -m ubelt` doctest entry point into a documentation CLI. Consider an
additional inspection interface or `api.json` only if an actual consumer needs
it; offline introspection and packaged text may already suffice.

### Agent usability benchmark

Start with a small, reproducible development benchmark (around ten tasks), not
an elaborate platform. Grow it only if it produces actionable findings. A
possible home is `dev/bench/agent_usability/`. Include tasks such as:

| Task family | Candidate utility | Hidden cases |
| --- | --- | --- |
| Run and inspect a command | `cmd` | Nonzero status, simultaneous streams, timeout |
| Hash nested configuration | `hash_data` | Ordering and the documented protocol constraints |
| Cache a computation | `Cacher` | Cached `None`, disabled/missing cache |
| Validate generated products | `CacheStamp` | Changed or absent outputs |
| Display nested values | `urepr` | Nested structures and formatting requirements |
| Build paths or manipulate files | `Path` / `pathlib` | No-overwrite behavior, relative paths |
| Group or transform data | `group_items`, `udict` | Duplicate keys, missing or empty values |
| Compare nested configurations | `IndexableWalker` | Mixed nesting and different values |

Write tasks in terms of desired behavior rather than ubelt function names.
The standard-library solution should be valid. Hidden tests should measure
correctness and avoid requiring ubelt use or inadvertently rewarding a
legacy defect. Include tasks where ubelt is not the best choice.

Compare four conditions: A, no ubelt dependency; B, ubelt installed with no
extra guidance; C, installed with a short recommendation to consider ubelt;
D, installed with the compact reference and cookbook available. Make the
package and documentation discovery conditions explicit. B may already have
access to packaged documentation; D should measure a defined additional
exposure, not assume that the text is inaccessible in B. Control other
available tools, budgets, versions, and starting environment. Pin model,
prompt, harness, Python and ubelt versions, repeat trials where feasible, and
report variability rather than claiming a universal advantage from one run.

Record functional and edge-case correctness, correct reuse, API errors,
code size, token usage, elapsed time, and dependency choices. Store raw
results in a suitable development location rather than making proprietary
model calls a requirement for ordinary unit tests. Local models are useful
for repeated affordable experiments. Do not require a paid service or add a
runtime LLM dependency.

Success means useful evidence for decisions: whether documentation improves
correctness/discovery, which APIs invite misuse, and where ubelt offers no
measurable advantage. Improve the documentation or API based on failures
rather than optimizing solely for benchmark reuse rate.

## 9. Deprecations and compatibility (P2)

Separate the recommended API from the supported API. Generated code may keep
using old spellings from historical examples long after a deprecation period.
A simple alias of a correct implementation is often cheap to maintain;
a parallel implementation with different semantics is not. Do not remove
working aliases solely to shrink an export list or because an assistant can
reimplement them.

Inventory scheduled deprecations, their original motivations, cost and
conflicting semantics. Preserve or revisit inexpensive aliases when useful,
while still honoring safety and correctness transitions. Do not automatically
reverse a committed removal or reset a deprecation schedule. Update examples
to prefer the canonical API and add a migration guide mapping old calls to
new ones (including behavioral differences). Follow the existing
`schedule_deprecation` convention where appropriate.

## Explicit non-goals

- **General-purpose atomic reads/writes.** Specialized libraries such as
  `safer` already address this problem and define their own guarantees. Do not
  add `Path.atomic_open`, `atomic_write_text`, or a generic atomic I/O wrapper.
  Internal cache/download correctness is a separate, narrowly scoped concern.
- **An AI runtime, agent framework, or tokenizer.** Keep the runtime useful
  independently of models and preserve the minimal-dependency philosophy.
- **A wholesale logging migration.** Improve control and diagnostics only
  where there is a clear need.
- **A workflow orchestrator or transactional cache database.** Keep the cache
  primitives composable with external systems.
- **Replacing `pathlib` or reproducing every new standard-library convenience.**
  Preserve distinct ubelt functionality, and retire or delegate backports
  when the supported Python versions allow it.
- **Indiscriminate API expansion or removal.** Avoid speculative features and
  unnecessary breakage merely because 2.0 allows it.

## Suggested execution order

1. Finish 1.5, including the existing cache/docs changes and symlink transition.
   Keep its release scope small.
2. Start two focused design efforts: a versioned structured-hash specification
   and a `Path`/`pathlib` compatibility inventory with migration options.
   Confirm the 2.0 symlink policy in the same compatibility review.
3. Establish a minimal agent benchmark and document its baseline results.
   Improve the cookbook from actual failure cases.
4. Prototype bounded `urepr` and `cmd` capture as independent opt-in features.
   Settle semantics and measure resource use before exposing public knobs.
5. Design cache key/version migration in conjunction with hash v2; handle
   metadata, validation and internal write correctness in separate changes.
6. Provide compatible opt-in APIs and migration guidance in a 1.x release if
   useful. For 2.0, switch only the defaults and contracts that have been
   specified, tested and communicated. Defer the rest rather than making the
   major release a catch-all rewrite.

For each implemented workstream, update the relevant Google-style docstrings,
executable examples, changelog and generated references. Keep Python 3.10+
support unless the project separately changes its minimum. Follow `AGENTS.md`:
update public exports and typing where relevant, avoid unnecessary runtime
overhead, use xdoctest and the existing test runner, and maintain coverage.
Prefer focused semantic regression tests and measured performance checks to
large collections of redundant tests. For behavior involving files, subprocesses,
or platform-specific features, use the existing cross-platform test matrix.
