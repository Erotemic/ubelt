# Full-library audit and release backlog: Ubelt 1.5 through 2.0

## Status and baseline

This is a source-grounded planning audit, not an implementation patch. It
supplements `docs/planning/ubelt_2_0_and_llm_era.md`; use this document to refine
its priorities and populate implementation tasks. The earlier plan contains the
longer design discussions for hashing, Path, symlinks, bounded output, caching,
and agent evaluation. Where the audit identifies a more specific defect or a
new dependency between workstreams, this document takes precedence for triage.

Baseline: source archive for commit `4a23a1cd80d807d6f8f1ec521409efc4182a0487`,
version 1.5.0 (unreleased), plus the previously delivered
`ubelt-1.5-cache-and-agent-docs-overlay-v2.zip` and the existing 2.0 planning
overlay. Do not reimplement work already present in that baseline. Before
starting any task, check the actual checkout, since the source snapshot may
lag the maintainer's branch. Paths, symbol names and behavior below refer to
that baseline; line numbers are intentionally avoided so this plan survives
normal source edits.

Evidence labels:

* **R**: reproduced in a small executable probe on Linux / CPython 3.13.5.
* **S**: concrete source finding; verify with a regression before changing it.
* **C**: compatibility or design decision, not necessarily a bug.
* **E**: experiment or evaluation; do not implement speculative optimizations
  before collecting results.
* **P0**: prioritize silent wrong results, data integrity, or a release contract.
* **P1**: important correctness, compatibility, or practical improvement.
* **P2**: cleanup, ergonomics, documentation, or measured optimization.

### Conservative triage (maintainer direction)

Preserve existing behavior unless a change repairs a demonstrated violation of
an existing contract, or the maintainer explicitly approves a change. A
reproducible observation is not automatically a bug. Neither an undocumented
corner case nor a divergence from a standard-library class automatically
establishes incorrect behavior. The 2.0 release is an opportunity to consider
compatibility changes, not blanket authorization to make them.

The original A/B/D identifiers and evidence labels are retained for cross-
references. The new disposition on every A item is authoritative and narrower
than its original audit discussion:

* **FIX**: candidate for a small 1.5 regression fix, limited to the explicit
  scope below. Confirm current source, tests and contract before implementation.
  If existing tests or maintainer intent contradict the proposed correction,
  stop and reclassify rather than updating tests to make a preference pass.
* **REVIEW**: investigate and report; do not change behavior on the strength
  of the audit alone. If a separate narrow bug is verified, propose it for
  approval. P0 review means urgent evidence gathering, not a release mandate.
* **HOLD**: preserve behavior throughout 1.x; documentation and design only.
  Any new behavior needs a separately approved design, normally for 2.0.
* **MAINT**: non-behavioral documentation, accurate annotations, or ordinary
  release validation. Avoid speculative cleanup and broad refactors.

The detailed paragraphs below retain findings, potential remedies and test
ideas for future planning. Where a paragraph suggests an action outside the
stated disposition, treat it as a design option, not an implementation task.
B items are proposed major-version workstreams, not release commitments;
D items are independent evaluation/maintenance. Additive features still need
agreement on their API and scope. No task is automatically a release blocker.

**Explicit maintainer decision:** the memoize hashing/key ambiguity is known
and is a 2.0 fix. A27 is a historical evidence record only. Do not change
memoize keys, fallback hashing or equivalence in 1.x, even if the new hash
protocol becomes available as an opt-in.

### Validation performed

* Reviewed the package export structure, the executable portions of the 33
  top-level Python modules, relevant docstrings, selected tests, release notes,
  packaging and CI configuration, and earlier planning documents. The package
  contains about 24,100 physical Python lines, including extensive docstrings.
  This is a broad module-by-module pass, not a proof of every branch or an
  exhaustive line-by-line review of all examples and tests.
* `python -m pytest -o addopts='' -q tests --disable-warnings` could not collect
  because `xdoctest` is missing (tests/test_progiter.py and tests/test_time.py).
* With those two files and the download suite excluded: 256 passed, 5 skipped,
  1 failed (`test_package_submodules`, also because xdoctest is missing).
* A separate deterministic download subset: 35 passed, 24 deselected.
  Command: `python -m pytest -o addopts='' -q tests/test_download.py -k
  'content_length or verified_file_replacement or interrupted_read or write_error
  or stream_is_caller_owned or invalid_sizes or response_closes or
  relative_destination or explicit_no_param_progress or requestkw_headers or
  progress_reports_rate' --disable-warnings` (use a single shell line).
* The generated LLM documentation freshness check passed on the baseline.
* Targeted small probes reproduced the R findings below. They deliberately
  avoid external network access. No new production code or tests were applied.
* Windows, macOS, PyPy, Python 3.10/3.14/3.15, optional hasher backends,
  mypy/ty, full xdoctest coverage and real coding-agent evaluation remain
  unverified. Windows risk findings are source-derived, not observed failures.

## Release strategy

1. Land only small, contract-backed correctness patches with high signal-to-noise
   tests. Investigate possible data-loss issues promptly but do not change
   intentional compatibility behavior based on a source suspicion. Keep 1.5
   manageable; a later release is preferable to a rushed change.
2. Make the new 1.x documentation authoritative. Explicitly label legacy
   behavior and mark migration alternatives. Generate docs after API changes.
3. Build a 2.0 compatibility inventory before changing any defaults. Version
   persistent encodings, provide a bridge for expensive migrations, and avoid
   silently invalidating caches or changing data interpretation.
4. Consider bounded representations and subprocess capture as general-purpose
   additive improvements, not LLM runtime features. Settle APIs first; neither
   is required for 1.5. Evaluate before promoting any new defaults.
5. Maintain zero mandatory runtime dependencies unless the maintainer explicitly
   decides otherwise. Prefer standard library solutions when they meet the
   contract. Do not add a public atomic-I/O layer; recommend `safer` for that.

## A. Findings and conservative 1.x triage

### Collections: ordered sets, list utilities and dictionaries

#### A01 — Repair OrderedSet deletion invariants (P0, R)

**Disposition: FIX.** Repair the stale index map after deletion; retain existing index, exception, and return contracts.

`ubelt/orderedset.py`, `OrderedSet.__delitem__`, `discard`, `_update_items`.
Deleting a non-final element removes the item and its map entry, but leaves all
subsequent indices stale. `OrderedSet('abc')`, `del s[0]` leaves
`{'b': 1, 'c': 2}` instead of `{'b': 0, 'c': 1}`. A later discard can remove
another element or fail; lookup is already wrong.

Implement deletion using one consistent reindexing operation. Avoid unnecessary
full reindexing of a tail deletion if simple. Preserve negative indexing and
IndexError for invalid positions. Tests: front, middle, tail, negative index,
then add/discard/index; verify `s.map == {v: i for i, v in enumerate(s.items)}`
for every mutating operation and that `len(s.items) == len(s.map)`. Do not expose
a new public representation or change add/update return contracts here.

#### A02 — Make OrderedSet symmetric difference correct for one-shot iterables (P0, R)

**Disposition: FIX.** Repair one-shot Iterable consumption and duplicate-induced corruption; retain documented surviving order and return types.

`OrderedSet.symmetric_difference` consumes `other` twice;
`symmetric_difference_update` consumes it to build additions before computing
removals, and can preserve duplicate new elements. For example
`list(ub.oset([1, 2]).symmetric_difference(iter([2, 3])))` is `[1]` rather
than `[1, 3]`. In-place with `iter([2, 3, 3])` yields `[1, 2, 3, 3]` with an
inconsistent map. Repeated list elements can cause the same duplicate bug.

Consume each operand once, deduplicate while preserving first appearance, and
retain self's surviving order followed by other-only elements. Test list,
generator, OrderedSet, repeated items, empty operands, self-operand and in-place
versus out-of-place equivalence. Use a small reference implementation for the
invariant rather than duplicating the production algorithm in tests.

#### A03 — Correct OrderedSet set predicates and document sequence differences (P1, R/C)

**Disposition: FIX.** Remove the invalid length shortcut for supported sequences with duplicates; correct the inaccurate fancy-index annotation. Do not expand accepted operand protocols or change ordered equality/index semantics.

`issuperset([1, 1])` on `OrderedSet([1])` is false because of a length shortcut,
although membership semantics say true. `issubset` has a corresponding
length-based fast path, which is safe for ordinary sets but not all input
protocols. Generalize or clearly constrain accepted operands. Test duplicates,
sets, sequences, one-shot iterables if supported. Keep the historical ordered
comparison/equality behavior for now. Correct fancy-index return annotation:
`oset[[0, 0]]` returns a list (preserving repetitions), not OrderedSet. `index`
accepts `start`/`stop` but documentation explicitly marks these unsupported;
do not silently reinterpret that API in a bugfix. See B07.

#### A04 — Fix `varied_values` column consistency (P0, R)

**Disposition: FIX.** Enforce the documented KeyError when rows disagree on columns without a default; preserve column order and normalization as currently defined.

`ubelt/util_dict.py:varied_values` checks the number of columns rather than key
sets, and the comment that `NoParam` cannot occur is false. For
`[{'a': 1}, {'b': 2}]`, it returns both columns containing `NoParam` despite
no default being supplied. Empty leading rows also bypass the check. Track
first-row keys independently of whether the first row is empty; compare key
sets; when a default is specified collect the full union. Tests: equal lengths
with different keys, empty first/last row, default supplied including None,
empty dataset. Keep value normalization (lists to tuples) and threshold
semantics unchanged unless separately designed. Consider predictable column
order in B08, since set iteration is currently part of the output behavior.

#### A05 — Avoid input mutation in `named_product` (P1, R)

**Disposition: REVIEW.** Determine whether callers intentionally rely on mutation of the positional mapping. The union wording alone does not establish a no-mutation contract. Preserve current behavior until approved; document it if useful.

`named_product(basis, **overrides)` updates the caller's mapping in place when
iteration begins. The docstring describes a union, not mutation. If a nonmutating contract is approved, a possible implementation is a
fresh ordered mapping preserving override precedence and insertion
order; retain positional mapping support (useful for dynamically generated
keys, not just historical OrderedDict support). Test mutation before/after
consumption, overlapping keys, empty basis, and one-shot value iterables.

#### A06 — Argmin/argmax/argsort type and performance review (P1, R/C)

**Disposition: HOLD.** Preserve tie order and comparison rules, including the differences between iterables and sequences. Investigate optimization only with measured evidence and exact compatibility; any new ordering policy belongs in B06.

`util_list.argsort` without a key sorts `(value, index_or_key)` tuples: ties
compare mapping keys, so `ub.argsort({1: 0, 'a': 0})` raises TypeError. Reverse
sorting also reverses sequence-index ties. A key callable takes the stable
sorting branch. `argmax(iter([1, 1])) == 1`, whereas `argmax([1, 1]) == 0`;
`argmax`/`argmin` fall back to O(n log n) sorting for non-sequence iterables,
including mappings with key functions. Use single-pass extrema for cases with
unambiguous winners; changing tie behavior should be intentional (B06). A
safe 1.x path is to document tie differences, provide an explicit stable policy
if useful, and preserve existing results on supported legacy inputs. Tests
must cover non-comparable mapping keys, custom keys, first/last ties, empty
iterables, and single evaluation of each input. Do not change argsort ordering
as a side effect of optimizing it: util_hash uses argsort internally.

#### A07 — Define chunk size validation and empty input behavior (P1, R)

**Disposition: REVIEW.** Establish the intended behavior of zero sizes, empty input, and replicate/wrap before changing validation or output. Do not rewrite either chunks algorithm; the legacy transition belongs in B06.

`util_list.chunks` has multiple legacy and newer paths. `list(ub.chunks(iter([1,
2]), chunksize=0))` returns `[]`; specifying `nchunks=2`, `bordermode='replicate'`,
`legacy=False` for an empty list raises UnboundLocalError. Validate positive
integer `chunksize`/`nchunks`, nonnegative total and supported bordermodes before
iteration. Define no-data behavior (probably no chunks) consistently with
`len()` where length is known. Inspect inaccurate `total`, more chunks than
items, inconsistent sizing options, wrap and replicate for short inputs.
Require a small matrix of actual edge cases; avoid a rewrite of the existing
successful cycle fix in 1.5. The legacy flag's default/removal belongs in B06.

#### A08 — Small iterable and string edge cases (P2, R/C)

**Disposition: REVIEW.** Do not add empty-input identities, new index semantics, or broaden iterable handling by default. An annotation correction supported by the current implementation and docs may proceed separately.

* `boolmask([])` raises ValueError from `max()`, while explicit `maxval=0`
  succeeds. Return `[]` for inferred empty extent if agreed; document negative
  indices (currently Python list indexing, e.g. `[-1], 3` marks the last item)
  and out-of-range behavior. Do not change negative-index semantics silently.
* `hzcat([])` raises ValueError from `max()`; returning `''` is the natural
  identity, unless a deliberate exception is desired.
* `take` accepts a default only for mappings according to docs, but the
  sequence overload allows it. Fix the type contract; support sequence
  defaults only as an explicit additive feature if useful. Separate default
  type variables can accurately express `list(take(mapping, keys, None))`.
* `iter_window` uses tee and cycle; validate sizes and step, document wrap on
  finite inputs versus memory behavior on infinite streams. Inspect `size=0`
  and step zero; avoid consuming an unbounded stream solely to wrap it.
* `iterable` catches any Exception from iter(); consider whether operational
  failures should propagate rather than be treated as not iterable (C).

#### A09 — Preserve dictionary set-operation invariants (P1, S/C)

**Disposition: HOLD.** Preserve ordering, collision precedence, and reserved merge behavior; compare against documented guarantees only. Any new mapping ordering policy belongs in B08.

`SetDict` / `UDict` / `AutoDict`, `util_dict.py`. In-place xor builds additions
from a set (`__ixor__`), so the order of added keys may differ from out-of-place
symmetric difference and depend on hash seed. Establish documented order and
collision precedence before changing it; add reference tests for operator vs
named-method semantics, reflected operators, one-shot key iterables, subclass
preservation, same-object operations and empty operands. `merge=` is accepted
by several methods but raises NotImplementedError: explicitly document as
reserved, or deprecate/remove if there is no need. Avoid introducing a merge
policy merely because the parameter exists. Check existing ordering and typing
contracts first (B08).

#### A10 — Make nested equality return a valid result for different paths (P0, R)

**Disposition: FIX.** Return a valid false comparison for unequal paths and support currently accepted hashable, non-orderable dictionary keys. Preserve existing leaf semantics, comparison tolerances, successful output ordering where defined, and return_info compatibility. No shared-kernel refactor required.

`util_indexable.IndexableWalker.allclose` sorts flattened `(path, value)` pairs
and asserts that paired paths match. `{'a': 1}` vs `{'b': 1}` raises AssertionError;
comparing `{1: 1, 'a': 2}` with itself raises TypeError during sorting. These
are ordinary valid nested mappings. Compare path sets/mappings rather than
requiring arbitrary keys to be orderable. Return false and meaningful failure
info for differing paths; preserve the existing `return_info` result schema as
far as possible. Do not use repr-sorting as an equality algorithm. Do not require a shared flattening or comparison kernel for this fix.
The use of walker1.indexable_cls when flattening walker2 is a separate
contract question; verify custom-class intent before changing it.
Tests: same size/different keys, mixed key types, reordered equal dicts, nested
empty containers, scalar-vs-container, tolerance and NaN, custom class policies.

#### A11 — Clarify nested container structure, comparison and traversal (P1, R/C)

**Disposition: HOLD.** Preserve leaf-path equivalence, empty-container and custom-class policies. Document limitations; strict structural matching, cycles, and array semantics require a separate design in B09.

Leaf-path equality collapses container types: `[1]` and `{0: 1}` compare equal;
`IndexableWalker([]).diff({})['similarity'] == 1.0`. This may be intentional for
some callers; introduce explicit structural comparison or a 2.0 policy instead
of silently making equality strict. Detect cyclic inputs with active-path
tracking or document and reject them; repeated references in an acyclic graph
are not cycles. Avoid requiring a new graph library. A plain `value1 == value2`
can yield a NumPy boolean array and fail truth testing; define whether array
leaves are supported, or require `list_cls=(..., np.ndarray)` explicitly. Review
NumPy floating type discovery and mixed Python/NumPy scalars. Make diff results
predictable in presentation without sorting mixed keys (B09). Distinguish
unmatched paths from value differences and approximations.

### Command execution, capture, progress, concurrency

#### A12 — Preserve standalone PathLike executables in cmd (P0, R)

**Disposition: FIX.** For shell=False, system=False, preserve an explicitly supplied PathLike as one executable argument. Keep string parsing, shell/system behavior, and display conventions unchanged except as needed for this fix.

`util_cmd._resolve_command`: a PathLike is converted to text, then POSIX shlex
splits it. A real executable at `/tmp/.../a b` fails with FileNotFoundError.
A PathLike denotes one executable, not shell source. In shell=False mode,
return a one-element argv list; use correct platform-specific display quoting.
Test with a temporary executable with spaces on POSIX and the analogous Windows
fixture; add a unit test for argument normalization on all platforms. Clarify
shell=True PathLike semantics separately. Do not reinterpret ordinary string
commands. Tests should use sys.executable or a controlled local executable.

#### A13 — Audit shell argument quoting, timeout cleanup and exception parity (P0, S/C)

**Disposition: REVIEW.** Investigate concrete hangs, leaks or incorrect execution on supported modes. Fix a demonstrated cleanup or quoting defect only in a separate reviewed patch. Do not redesign timeouts, exception schemas or shell contracts here.

`util_cmd._resolve_command` uses POSIX `shlex.quote` for sequence display and
shell/system commands even on Windows; Windows quoting is a separate contract.
Prefer argv/no shell by default. Windows cmd.exe expansion, metacharacters,
percent and exclamation handling cannot be solved by claiming POSIX quoting is
portable. Test normal spaces, empty args, Unicode, quotes and backslashes on
real target platforms. Explicitly reject or document shell sequence modes that
cannot be reliably specified rather than silently pass a different command.

Review timeout/exception paths in `_tee_output`, `_proc_iteroutput_thread`,
`_proc_iteroutput_select` and `cmd`: one monotonic deadline across read and wait,
reap child on failure, ensure worker threads terminate, preserve partial stdout
and stderr. Test a child producing no newline, separate stdout/stderr floods,
closed streams, decoding failures, sleeping descendants that retain pipe handles,
and interruption. Do not promise full process-tree cleanup by default; design
an opt-in policy under B05. Test both backends with hard outer test deadlines to
prevent the test suite hanging. `check=True` exceptions currently use display
text whereas `CmdOutput.check_returncode()` uses args; harmonize or document
this observable difference. Validate incompatible modes before spawning.

#### A14 — Fix repeated CaptureStream use and document limits (P1, R)

**Disposition: FIX.** Reset per-session capture state so reusing a capture returns all text for the new session. Preserve accumulation and existing stream semantics; do not add reentrancy or FD capture guarantees.

`util_stream.CaptureStream.start` creates a new StringIO without resetting
`_pos`. A second `with cap: print('second')` after `'first'` results in `'\n'`
in `cap.text` instead of `'second\n'`. Reset per-session cursor on new stream;
decide whether `parts` accumulates across sessions (existing behavior suggests
it does) and document `text` as the last segment. Test repeated contexts,
manual start/stop/close, nested distinct captures, exceptions, disabled capture,
stdout and stderr. Review re-entrant use of the *same* instance; if unsupported
raise an intelligible error rather than restore incorrectly. Note that this is
Python stream capture, not file-descriptor-level or thread-local capture;
`.buffer` and `.fileno()` are not guaranteed to capture binary/C/subprocess
writes. Do not expand the library into an FD interception framework.

#### A15 — Make ProgIter argument normalization and lifecycle robust (P1, R/S)

**Disposition: REVIEW.** Check intended tqdm alias behavior and documented parameter contracts; miniters=None may be a narrow fix if supported. Do not normalize all aliases, reject new inputs, or redesign lifecycle without approval.

`progiter.ProgIter(miniters=None)` overwrites `freq` with None and fails during
iteration; tqdm-compatible None should mean default if supported. Normalize
aliases without unexpected precedence; document accepted no-op options
(`position`, `leave`, `dynamic_ncols`, locks) honestly. Validate invalid
frequency/initial/total/time thresholds. Test early termination, exceptions,
restart, manual step, iterable with misleading length, empty and unknown total,
non-TTY/custom streams and `miniters=None`. Avoid importing optional display
libraries. Do not change synchronous low-overhead progress into a background
thread system. Consider a shared public measurement snapshot (B10) so download
reporting need not rely on private progress fields.

#### A16 — Harden executor and JobPool contracts without changing serial timing (P1, R/S)

**Disposition: REVIEW.** Preserve lazy serial execution and the deliberate Future compatibility compromise. Confirm zero-worker fallback and private helper reachability before proposing changes; B11 owns contract redesign.

`Executor('typo', max_workers=0)` silently selects serial; validate recognized
mode before zero-worker fallback, preserving zero as documented serial behavior
for valid modes. `SerialFuture` intentionally advertises FINISHED internally
so stdlib `as_completed` works even before evaluation, while `.done()` returns
False. Observed repr reports finished/None before the callable executes. This
is a fundamental compromise, not a one-line fix: see B11. In 1.x, clarify
serial laziness, cancellation, timeouts, callbacks and external `wait()`.
Check `_clear_completed` (filters `running()`, which also drops pending work)
if it is reachable; do not change private dead code without checking callers.
Test concurrency lifecycle: submit, exception, shutdown, join, transient results,
and use of Future with `wait`/`as_completed`. Keep the existing 1.5 once-only
serial evaluation fix. Do not make eagerly executed serial futures by accident.

### Filesystem, archives, platform, import

#### A17 — Make functional ensuredir enforce its own postcondition (P0, R)

**Disposition: FIX.** An existing regular file cannot satisfy the documented directory postcondition. Raise a clear exception without deleting it for ordinary recreate=False calls; retain recreate semantics, permissions, return types and verbose messages.

`util_path.ensuredir` tests `exists` and returns even when the target is a file.
`ub.Path(path).ensuredir()` correctly raises FileExistsError. Prefer the stdlib
`os.makedirs(..., exist_ok=True)` semantics (including symlink to directory)
or explicit isdir/error behavior. Preserve return spelling/type and `verbose`
contract. Test existing file, dangling link, existing directory, symlink to
folder, recreate mode, tuple path and relative paths. Avoid check-then-create
logic that introduces a new race. Do not delete files to fix this behavior.

#### A18 — Handle special files in delete and review symlink boundaries (P1, R/S)

**Disposition: REVIEW.** Special-file handling has no clear existing contract. Do not broaden deletion behavior for FIFO, socket, device or reparse-point paths without explicit approval; investigate any demonstrated unsafe behavior separately.

`util_io.delete` tests isfile/isdir/islink; a POSIX FIFO is silently left in
place. For deletion of a non-directory leaf, use an appropriate lstat/unlink
policy, distinguishing missing from permission errors, preserving links without
following them. Define special-file behavior explicitly (FIFO/socket/device;
never delete device fixtures outside a temp directory). Test with a temporary
FIFO and local symlink, directory, regular file, missing path and Windows
junction fixtures. `os.path.exists()` can suppress errors; avoid reporting
successful deletion when inaccessible paths remain. Remove unreachable old
Python <3.8 rmtree path only after supported platform tests pass.

#### A19 — Fix Windows physical-path overwrite risk and reparse-point handling (P0, S)

**Disposition: REVIEW.** Urgent native Windows investigation, not an authorized behavior change. Verify real overwrite behavior and fallback provenance; if an unintended destructive path is confirmed, propose a narrowly reviewed safety patch before broader compatibility changes.

`_win32_links._symlink`: if the destination is a regular file not hardlinked to
the source and native symlinks are unavailable, the code may enter the
overwrite branch and delete it. The non-Windows path refuses physical files.
Hard links have no privileged original/link identity; a regular file must not
be treated as expendable because it might be a hard link. Reproduce in a real
Windows test with capability disabled/controlled, existing ordinary file and
`overwrite=True`. Preserve contents on refusal. If compatibility requires
replacing a recognized legacy hardlink, define an explicit policy; do not
guess provenance from a filename. Review dangling junction detection, reparse
handle ownership/closure in `_win32_links` and `_win32_jaraco`, source target
kind for dangling directory symlinks, cross-drive relative requests and fallback
diagnostics. Windows implementation is unverified in this audit; avoid
sweeping ctypes refactors. Use actual CI tests with symlink privilege and
fallback coverage, not Linux-only mocks as the sole evidence.

#### A20 — Correct platform directory selection and document migration (P0, S/R simulation)

**Disposition: HOLD.** Keep current default data/config/cache locations in 1.x even if selection appears accidental. Document observations and migration options; B12 owns any path relocation or XDG policy change.

`util_platform.platform_{data,config,cache}_dir` test POSIX before DARWIN;
macOS is POSIX, so intended `~/Library/...` branches are unreachable. Probe
with both flags true returns Linux-style `.cache`. Empty XDG_CACHE_HOME
returns `'.'`; also inspect relative/invalid XDG values. Honor the intended
OS-specific selection (decide whether explicit XDG variables override macOS)
and document fallback. **Changing default cache/config directories moves user
data**: do not silently relocate/delete existing files; consider retaining
legacy lookup or a migration switch in 1.x and defaulting native paths in 2.0.
The source issue is clear; actual release placement depends on migration. Test
all three directory kinds, unset/empty/relative environment, real macOS/Windows
CI and Windows missing env. Evaluate platformdirs as a recommended specialist,
not mandatory dependency. See B12.

#### A21 — Unify archive path parsing and resource lifetime (P1, R)

**Disposition: FIX.** Fix the documented colon spelling for zopen without changing actual on-disk path precedence. Treat case handling as a separate compatibility check; independently verify extraction/open safety before a security patch. No parser rewrite or expanded archive format support required.

`util_zip.split_archive` recognizes colon and case-insensitive archive suffixes
within a path, but `_open` only detects a lowercase suffix followed by slash;
`zopen('x.zip:member.txt')` fails. Bare `split_archive('a.ZIP')` returns
`(None, None)`. A shared parser may be a future simplification; a localized correction of
the documented colon spelling is sufficient in 1.5. Preserve the priority of
real on-disk paths. Clarify nested archives (not automatic nested
archive extraction), Windows drive colon, literal files and extension case.
The seekable branch extracts a member then builds `join(temp, internal)`;
ZipFile.extract sanitizes paths, so these names need not match and a parent or
absolute member could lead to opening a path outside the temp directory. In a
probe with `../outside.txt`, it failed to open the intended member. No actual
escape read was attempted. Prefer streaming/spooling the exact member or use
and validate the returned extraction path, not an unchecked join. Test normal,
parent/absolute-like member names, missing member, cleanup on failure and
archive close. Do not add general archive extraction APIs.

#### A22 — Make importing by path fail clearly on a name collision (P0, R/C)

**Disposition: HOLD.** Do not change import-by-path name-resolution behavior, raise new default errors, emit new default warnings, or evict modules in 1.x. Document the limitation. A confirmed rollback loss of an existing sys.modules entry may be separately reviewed as a bug.

`util_import._custom_import_modpath` modifies sys.path then imports by name;
`sys.modules` and path precedence still win. Two distinct `auditmod.py` files
with x=1 and x=2, imported by path, returned the first module twice. In 1.x
prefer documenting the limitation and detecting a resolved path mismatch with
a warning or explicit strict opt-in; choose whether to raise by default with
maintainer input. Do not evict an existing module or mutate package namespaces
silently. For zip import, `_load_zip_module` assigns sys.modules then on failure
pops the name even if a previous entry existed; preserve old entry on failure,
and avoid retrying arbitrary module-execution exceptions as if they were path
spelling failures. Test two same-name modules, packages with relative imports,
zip modules, failure rollback, same file repeated and namespace identity.
Define future exact-path semantics in B13.

#### A23 — Fix PythonPathContext restoration (P1, R)

**Disposition: FIX.** Fix cleanup for ordinary list.insert-compatible indices that the context manager accepts; preserve normal sys.path behavior and avoid removing third-party entries. Leave concurrent mutation and duplicate policy redesign for review.

`util_import.PythonPathContext.__exit__` detects index beyond len(sys.path)
but still indexes it before recovery. With `index=10**6`, Python insert appends
successfully and exit raises IndexError; the injected path remains. Clamp
actual insertion index like list.insert, handle negative positions and
shortened sys.path safely, and define duplicate path handling. Tests with
mutable sys.path restored in finally, duplicate path and nested contexts;
avoid overwriting legitimate third-party modifications. This is module-level
(not top-level) functionality and also used by import_module_from_path.

#### A24 — Scope and modernize non-importing module discovery (P1, R/S/C)

**Disposition: REVIEW.** Document supported discovery cases and verify existing promises. Namespace, pyc, zip and editable-install expansion is not automatically a bug fix; do not execute finder code or replace the non-importing abstraction.

`modname_to_modpath` intentionally manually searches paths and statically reads
editable-install mapping files, rather than executing imports. Namespace package
child `ns.child` without `ns/__init__.py` was not found in a temp fixture.
Compare documented support to namespace packages, `.pyc`-only modules, builtins,
zip paths, editable mappings, pathlike search roots and duplicate namespaces.
Keep no-import guarantees; `importlib.util.find_spec` for a dotted name can
import the parent, so it is not an interchangeable replacement. Use machinery
suffix constants where compatible; improve narrow error handling for malformed
unrelated editable finder files. Add targeted support where straightforward;
full namespace/import system semantics may be B13 or outside scope. Explicitly
document omissions so `is_modname_importable` is not treated as an execution
or availability guarantee. Do not run arbitrary finder code during discovery.

#### A25 — Path backport and compatibility maintenance (P1, S)

**Disposition: MAINT.** Correct the wrong method name in the existing error text and verify current backports on supported interpreters. Do not change copy/move semantics or add backports absent a concrete need.

`util_path.Path.walk` already delegates to pathlib on >=3.12. Its unknown
keyword error incorrectly names `.relative_to()`; fix. Validate old alias
conflicts and warn only if a migration is planned. Audit `relative_to(walk_up)`
backport against native behavior, including other anchors, drives and parents;
keep support on 3.10/3.11. Test copy/move on dangling symlinks, directory links,
existing destination and same file using current semantics. Document where
`pathlib` has caught up. `ChDir` is process-global and should not be used for
concurrent operations; prefer `cwd=` in cmd. Reserve method renaming/contract
changes for B02. Avoid adding new backports just to maintain historical breadth.

### Hashing, memoization, caching and downloads

#### A26 — Document hash protocol dependencies and validate non-terminating inputs (P0, R/S)

**Disposition: FIX.** Reject a nonpositive blocksize that yields a false file digest, and prevent nontermination for bases of length one (with clear handling for empty bases). Preserve every valid v1 encoding and hash. Other parameter/alphabet restrictions, including duplicate or multicharacter symbols, need separate approval.

`util_hash.hash_file(blocksize=0)` returns the empty digest for a nonempty file.
Validate a positive integer blocksize and stride, nonnegative maxbytes or None.
Treat maxbytes=0 as intentionally hashing no bytes; document sampled stride
hashes as not whole-file integrity checks. `_rectify_base` accepts arbitrary
list/tuple; `_convert_hexstr_base` repeatedly divides by length. A one-symbol
base cannot make progress on positive integers, and empty alphabets fail with
an incidental exception. Reject non-terminating one-symbol bases and empty bases. Duplicate symbols
and multi-character alphabets are separate compatibility questions; preserve
their behavior in 1.x. Do not
execute a non-terminating probe; this is a source finding. Test invalid inputs
without changing any valid v1 golden hashes. Clarify custom hasher factory
contract and distinguish digest algorithm from serialization version.

#### A27 — Known memoization key ambiguity (P0, R/C; deferred to 2.0)

**Disposition: HOLD.** Maintainer decision: all memoize hash/key ambiguity
fixes are deferred to 2.0 (B01/B14). Preserve `_hashable`, key equivalence,
fallback encoding, cache layout and default behavior throughout 1.x. No
independent tagged-key or opt-in memoize fix in 1.x.

`util_memoize._hashable` uses the original object if hashable and an untagged
`hash_data` string otherwise. `ub.memoize(len)(['a_,_b'])` and a subsequent
call with `['a', 'b']` on the same memoized function return 1 for both. This
is a known consequence of the legacy structured hashing protocol, not a new
1.5 regression. Native equality (e.g. `True == 1`) may also conflate inputs
when a function distinguishes type; that equivalence policy is not necessarily
wrong. Preserve the observations for B14 design and regression testing in 2.0;
do not add an independently maintained encoder or change `.cache` keys in 1.x.
The reproduction appendix is informational and must not become a failing 1.5
regression test expecting the 2.0 behavior.

#### A28 — Make CacheStamp verify all expected prefixes (P0, R)

**Disposition: FIX.** Reject mismatched explicit prefix-list cardinality so supplied expectations are not silently ignored. For a scalar prefix with multiple products, or a proposed partial verification policy, obtain a decision before changing behavior. Preserve certificate layout, reasons and valid calls.

`_check_certificate_hashes` uses zip without checking lengths. With two
products and a single correct expected hash, renew and expired both succeed;
with one product and two prefixes (including a bad second prefix), validation
also succeeds. The existing docs describe matching the expected hash(es) of each product.
An explicit prefix list should not silently ignore excess expectations;
require exact cardinality unless a supported partial-list convention is
identified. The scalar prefix case is a distinct policy decision; do not
change it as part of this patch without approval.
Validate at renew and when reading existing certs, including missing hash,
wrong types, hasher=None, zero products and corrupted certificate structure.
Do not convert absent integrity metadata into success. Preserve false/reason
return convention in 1.x; use specific reason for invalid cert or raise clear
configuration error. Existing test files `test_cache_stamp.py` and
`test_download.py` are the primary regression targets.

#### A29 — Validate certificate identity, expiry and metadata schema (P1, S/C)

**Disposition: HOLD.** Preserve certificate identity, expiration semantics, metadata layout and existing validation policy. Source findings are design inputs for B04, not proof of a bug. A malformed-certificate failure may be separately reviewed if it violates the current contract.

`CacheStamp.expired` checks existing certificate expiry and products' metadata
but does not explicitly compare certificate product path list or hasher name.
`_product_info(product=...)` computes stats via `_product_file_stats()` without
passing its normalized products. Audit product changes, optional hash mode,
identical file contents, missing products and changed expiry settings; decide
whether stamp represents identity of paths or identity of their contents.
Current expiration semantics intentionally compute an absolute expiration at
renewal; preserve this unless an explicit new policy is introduced. Validate
malformed JSON/cert types, catch only expected read/decode errors, avoid hiding
permission errors and programmer failures. Prefer a small versioned certificate
schema in B04; old certificates should be intentionally expired or supported,
not misinterpreted. Test with fake time / fixed tz rather than sleeping.

#### A30 — Clarify download integrity and partial failure behavior (P0, R/C)

**Disposition: REVIEW.** Keep tested hash-mismatch behavior and filesize-as-hint semantics. Investigate short transfers with realistic responses and document guarantees; strict validation, destination replacement policy and output changes need approval. Do not introduce general atomic I/O.

`util_download.download` now preserves an existing destination on interruption
and bad hash, which is useful. But if the destination does not exist, a hash
mismatch deliberately installs the failed payload before raising (confirmed;
there are tests of this behavior). Do not silently change it in 1.5 if callers
rely on it for diagnosing wrong expected hashes. Document explicitly, add a
safe opt-in if needed, and change default in B03. A fake response whose
`Content-Length` is 10 but returns one byte replaced an existing file with that
byte. Check whether a trustworthy response length is available and verify it
before committing where applicable; `filesize=` is currently a progress hint,
not necessarily a validation promise, so separate strict transfer validation
from hints. Real urllib HTTP responses may themselves detect some incomplete
reads, but the fake response demonstrates the library does not check.
Test missing length, misleading size, compressed/encoded body assumptions,
nonseekable streams, read/write exceptions, hash mismatch for existing and new
files, and cleanup. Caller-owned streams cannot generally roll back; document.
Remove redundant printing of digest on error if approved; exception has both.
No general atomic I/O API; use the existing internal temporary replacement
where appropriate, without claiming crash durability or concurrent semantics.

#### A31 — Improve download URL-derived filenames and cache identity (P1, S/C)

**Disposition: HOLD.** Preserve URL-derived filename and destination-based reuse behavior in 1.x. Existing same-path/different-URL reuse is deliberate tested behavior, not a defect. B03 owns any new identity/default naming policy.

Both `download` and `grabdata` use basename(url) rather than a parsed URL path.
Query strings/fragments, percent escapes, empty/trailing-slash paths and
Windows-invalid characters merit explicit behavior. Preserve explicit
`fname`/`fpath` caller paths; avoid untrusted URL metadata choosing arbitrary
paths. Add tests for same basename different URL and distinct query values;
existing `test_grabdata_same_fpath_different_url` explicitly expects reuse when
no hash prefix is provided. Do not change that default casually. Offer explicit
cache identity policy in B03, and never store raw auth headers or tokens in
metadata by default. Review mismatched `appname`/dpath/fpath validation between
functions. Keep download/grabdata focused on simple requests, not HTTP caches,
retry frameworks, authentication managers or resumable HTTP protocols.

#### A32 — Harden Cacher filenames and metadata semantics (P1, S/C)

**Disposition: HOLD.** Preserve cache filename construction, key layout, depends snapshot semantics, metadata and serialization defaults. Document trusted inputs and known limitations; design new policies in B04. No silent cache relocation or key rewriting.

`Cacher._condense_cfgstr` leaves short strings untouched, including separators;
`get_fpath` joins then normalizes. Treat name and configuration identity
separately, document trusted input today; a future safe key layout must not
allow arbitrary cfg strings to introduce directories or escape the cache root.
Add explicit safe opt-in and legacy lookup only when proven unambiguous; B04.
Audit `_rectify_cfgstr` memoizing depends into cfgstr when depends later changes;
document snapshot or mutation policy. `save` writes data and metadata separately;
metadata append failure can leave a valid data file and a raised exception.
Separate metadata optionality and data validity; don't promise transactionality.
Preserve 1.5 `tryload(default=...)`, explicit pickle backend and cached None
fixes; audit `tryload` error classification and JSON/pickle trust. Prefer
internal file integrity safeguards over public atomic primitives.

### Time, formatting, output, miscellaneous

#### A33 — Accept timezone objects and review timestamp round-trip boundaries (P1, R/C)

**Disposition: REVIEW.** ZoneInfo and broader tzinfo support are possible additive features, not an established bug. Preserve timestamp formatting, local timezone and existing parser contract; verify against current supported inputs first.

`util_time._timezone_coerce` accepts only `datetime.timezone` instances,
not the broader `datetime.tzinfo` (e.g. `zoneinfo.ZoneInfo('UTC')` produces
TypeError in timeparse). If public type contract intentionally limits this,
broaden as an additive feature with matching annotations. Define behavior for
aware/naive datetime, fold, DST gaps, local vs named time zone, fractional
offsets and precision. Keep existing 1.5 offset/DST fixes. Test on fixed UTC,
fixed offset and ZoneInfo; guard optional tz database availability. Evaluate
`datetime.fromisoformat` as first-pass parser with 3.10 vs later compatibility
and retain ubelt's filename-safe timestamp format/legacy parser. Do not change
compact time strings or default local timezone in 1.x without migration.

#### A34 — Fix NO_COLOR / FORCE_COLOR handling consistently (P1, R)

**Disposition: FIX.** Correct FORCE_COLOR reading the wrong environment variable and restore documented NO_COLOR-only behavior. Preserve existing explicit overrides/import-time state; a broader precedence policy (especially both flags present) needs review rather than a wholesale change.

`util_colors.py` sets `FORCE_COLOR = bool(os.environ.get('NO_COLOR'))` instead
of FORCE_COLOR. With only NO_COLOR=1, color_text still emits ANSI; with only
FORCE_COLOR=1, the FORCE_COLOR constant is false. `highlight_code` checks only
NO_COLOR, while `color_text` has a different precedence rule. For the 1.5 typo fix preserve the current explicit overrides and import-time
state model. Investigate rather than change precedence when both flags are
present; test the agreed env cases in subprocesses without mutating process-
global color state. Rich backend does not accept the arbitrary
kwargs that highlight_code forwards to it; document backend-specific options
or support a small common subset. Ensure forced ANSI and trailing newline
behavior is predictable on captured streams. Do not add a Rich dependency.

#### A35 — Repair representation edge cases without changing default format broadly (P1, R/S/C)

**Disposition: REVIEW.** Correct a demonstrably documented option spelling mismatch only after checking compatibility with the existing alias. Preserve formatting conventions, empty-set representation, custom extensions and unknown-kwarg handling until B15 or explicit approval.

`urepr(set()) == '{}'`, which represents an empty dict if evaluated as Python;
formatting APIs may not guarantee eval round-trip, but this is misleading in
inspection. Consider emitting `set()` in ordinary repr-like mode, preserving
explicit `nobraces`/compact output and documenting difference. Fix the NumPy
formatter reading only `supress_small` even though the type dictionary accepts
`suppress_small`; support both with explicit precedence. Review NumPy scalar
and dtype display, non-Python-reconstructible custom repr, sorting mixed keys,
ANSI handling vs visual width, and empty/frozenset/one-tuple special cases.
Do not turn urepr into a serializer. `urepr(..., not_a_real_option=True)` ignores
unknown kwarg; strict validation must account for custom extensions before
adopting any default. Bounded representation and cycles belong in B15.

#### A36 — Make compatible() explicit about signature filtering (P2, R/C)

**Disposition: HOLD.** Preserve compatible(start=...) interpretation, original-object passthrough, and callable/signature restrictions. Document examples; new binding/filter semantics need separate approval.

`util_func.compatible` skips positional-only parameters before applying `start`;
for `(a, /, b, c)`, `start=1` selects only c. Is start count of *consumed
positional arguments* or count of eligible keyword names? Current behavior
needs clear examples, rather than a guessed correction. Also review use of
`**kwargs` passthrough returning the original config object (not a copy),
explicit keyword strings vs iterables, callable instances / builtins with no
inspectable signature and bound methods. Keep it a filter, not a validator for
full call binding. `inject_method` now handles bound methods; callable objects
without descriptor protocol should either be supported deliberately or rejected
with informative TypeError. No new signature framework.

#### A37 — Keep minimal CLI helpers minimal (P2, C)

**Disposition: MAINT.** Keep the minimal CLI, string helpers, NoParam, and NiceRepr contracts unchanged; documentation/accurate typing only. Do not expand parser or change exception policy.

`util_arg.argval` / `argflag` deliberately scan argv, support aliases and
`--key=value`, and do not implement full argparse semantics. Document duplicate
flags (first match), missing value, `--` separator, next token beginning with
hyphen, explicit argv vs sys.argv and sentinel. Do not silently reinterpret
negative numbers as flags. Prefer argparse for full CLIs. Fix clear typing
limitations if useful (e.g. list aliases), not a new parser. `util_str`
codeblock/paragraph/indent are valuable vocabulary despite easy reimplementation;
keep existing whitespace semantics. `NiceRepr` fallback behavior is useful;
warn stacklevel and exception policy can be tested without promising executable
repr. `NoParam` is a public singleton with pickle/copy identity guarantees;
retain those and use identity checks, not falsiness. Review reload/type identity
only if there is a concrete consumer need.

### Release engineering and documentation

#### A38 — Remove accidental dependence on optional packaging (P0, S/C)

**Disposition: REVIEW.** Verify minimal-install failure and determine whether packaging is intentionally optional for this feature. Propose narrow documentation or a fix after approval; do not add dependencies or invent PEP 440 parsing.

Minimal runtime requirements are empty, but `schedule_deprecation` imports
`packaging.version` unconditionally, even for a simple always-warn call.
Thus calling a deprecated function or using the deprecation helper may fail in
a genuinely minimal venv. `packaging` is an optional extra; do not assume
setuptools or pip is present at runtime. Verify in a fresh venv with only the
wheel installed. Decide explicit optional dependency message, lightweight
path for non-versioned schedules, or policy for version comparison that does
not reimplement PEP 440 incorrectly. Full version semantics should stay with
packaging rather than a homegrown parser. Audit other optional imports
(`dateutil`, `numpy`, `pygments`, `colorama`, Windows extras) for clean failure
and documentation. Keep optional behavior explicit and test core functions in
minimal environment. This is not a recommendation to add mandatory packaging.

#### A39 — Improve typed API and runtime-introspection fidelity (P1, S)

**Disposition: MAINT.** Correct verified annotation mismatches without changing runtime behavior, import overhead, or supported inputs. Do not promise runtime get_type_hints or redesign APIs for typing alone.

Inventory public functions and methods against actual supported inputs and
return values; focus on mismatches, not annotation volume. Concrete examples:
`OrderedSet.__getitem__(Sequence[int])` says OrderedSet but returns list;
`take` sequence overload accepts default despite mapping-only semantics;
`CmdOutput` exposes untyped dict keys; serial vs detached process results are
mode dependent; `Path` overrides incompatible with typeshed; `NoParam` default
sentinel may be mistaken for ordinary user values. Validate mypy and ty on
minimum supported Python and newest supported typeshed, including downstream
`tests/typecheck_consumer.py`. TYPE_CHECKING-only imports can make
`typing.get_type_hints` fail at runtime; decide whether that is supported (do
not promise it by default), document limitations for agent introspection, and
keep import overhead measured. Do not import optional libraries just to satisfy
runtime hints. Distinguish annotations from actual runtime contracts.

#### A40 — Make packaging/CI and generated docs reproducible (P1, S)

**Disposition: MAINT.** Run existing release checks and maintain documentation/package consistency. No new CI machinery, dependency policy or compatibility-floor changes without approval.

Run supported Python/OS matrix, full xdoctest/pytest/coverage (repository policy
is 100% coverage; do not relax it silently), minimal wheel and full extras.
CI is generated by xcookie; coordinate generated file edits with generator
configuration, don't introduce recurring drift. Check docs/examples on
supported versions; optional requirements still contain dead Python <3.10
markers and source has obsolete version branches. Remove only demonstrably
unreachable code, keep platform-specific tests. The previous generator
`dev/maintain/generate_llm_docs.py --check` passes here but uses inspect.signature
on a live interpreter; default repr, aliases and signatures can change across
versions. Choose one canonical docs generation interpreter, check root/package
copies and stale warning sections, validate wheel/sdist and hosted docs links.
Audit README, changelog, Sphinx doc version, `__all__`, `py.typed`, metadata and
README feature ranking. Do not change `python -m ubelt` doctest behavior just
for an agent CLI. See D01 for evaluating discoverability before new infrastructure.

## B. Major-version contracts and additive bridge work

These workstreams are larger than individual bug fixes. Each should have a
short design note with motivating use cases, semantics, compatibility impact,
and examples before implementation. Where possible, offer the new behavior
under an opt-in 1.x spelling, then change the default in 2.0. Do not interpret
2.0 as a requirement to remove all historical aliases or to finish every P2
item.

### B01 — Specify and implement structured hashing v2 (P0)

This remains the strongest justification for a 2.0 semantic release. In
addition to the delimiter ambiguities in the earlier plan, observed v1
`types=True` equivalences include bytes/str, list/tuple, and bool/int. Some
were deliberate, others are consequences of an encoding that lacks exact type
information. Do not assert that all such equalities are necessarily bugs.
Instead define the equivalence relation the protocol is intended to respect.

Design dimensions:

* Distinguish hash algorithm, encoded data version, and output alphabet. A
  version is not merely a new digest algorithm. Preserve v1 bit-for-bit for
  reproducing historical IDs (including its existing quirks and extension
  encodings).
* A self-delimiting grammar with explicit record tags and lengths, or an
  equivalent unambiguous construction. Do not rely on ad hoc reserved
  separators. Separate the encoding of a sequence from the encoding of its
  elements. Extensions must have framed payloads, not arbitrary unframed
  concatenation. Do not call the encoder a general serialization framework
  if it deliberately supports only one-way stable encodings.
* Define typed and untyped equality, including whether bool/int, bytes/str,
  list/tuple, float/int, set/frozenset, decimal representations, negative
  zero, NaNs, infinities and platform path types should collapse. If typed
  mode is intended to distinguish these, test it. Untyped mode must still
  have unambiguous structural boundaries. Document unsupported values and
  never claim an injective representation across arbitrary Python objects.
* Specify deterministic ordering for unordered containers by encoded keys
  (or another proved total order), not `str(key)` or comparability of arbitrary
  Python objects. For example, test keys 1 and '1', mixed scalar types, custom
  extensions and sets across multiple PYTHONHASHSEED values. Decide how to
  treat keys that canonicalize to identical encoded bytes; do not silently
  lose entries. OrderedDict order remains meaningful where specified.
* For NumPy, specify dtype (including structured dtype fields), shape, logical
  order vs memory layout, endianness and scalar semantics. v1 uses native
  `tobytes()` plus metadata; do not change its behavior as a side effect of
  improving v2. Reject object arrays unless a deliberate safe value encoding
  is implemented. Benchmark noncontiguous arrays and avoid materializing
  large copies unnecessarily. Decide whether a lossless representation of
  long double or extended precision is supported rather than casting it to
  ordinary float implicitly.
* Dataclasses: fields, class identity, inheritance, module/qualified name
  and treatment of recursive graphs need an explicit policy. Do not equate
  a dataclass instance with an ordinary dict by accident. Decide whether
  cyclic data is rejected (recommended starting point); distinguish cycles
  from repeated references. Document recursion/size limits.
* Existing extension callbacks should remain supported in v1. Provide a v2
  extension contract that distinguishes type/domain and encoded payload,
  handles registration priority, and does not mutate global registrations
  during hashing in surprising ways. Verify optional package import behavior.
* `hash_file` hashes file bytes, and normally should not change with the
  structured-data version. A file digest and structured bytes digest may
  happen to coincide by design; consumers wanting domain separation can
  explicitly namespace their use. Keep output alphabets independently
  documented; do not confuse a custom base with RFC encodings.

Proposed API shape (not fixed): `hash_data(..., version=1|2)` or named
encoding modes. Explicit opt-in in a 1.x release if feasible; v2 default in
2.0; retain a documented v1 route for existing users. Do not silently try an
old encoding to satisfy a new cache lookup: it can yield a false hit. Audit
all internal callers, especially Cacher and memoize (B04, B14), and preserve
legacy configuration keys if explicitly requested. Do not migrate memoize to
v2 or otherwise change its key construction in any 1.x release; B14 is a
2.0-only migration. Decide whether v2 needs
an externally inspectable byte stream for golden vectors and extension tests;
no requirement for a new public serializer.

Acceptance: a documented grammar and reference vectors, structured cases
showing v1 ambiguities and v2 differences under the chosen equivalence,
cross-process/reordered unordered containers, cross-platform tests on
supported scalar types, extension tests, negative tests for unsupported
values and cycles, benchmark representative nested objects and arrays,
backward-compatibility fixtures from actual v1 releases, and a migration
recipe. Do not treat a finite set of collision tests as proof of an
unambiguous encoding; justify framing structurally.

### B02 — Reduce ub.Path's deviation from pathlib without giving up fluent use (P0)

The standard library has absorbed some of Path's original value (walk,
relative_to(walk_up), and copy/move). The remaining benefits include
`augment`, `ensuredir`, `delete`, `expand`, `appdir`, `ls`, symbolic chmod and
convenient interoperability with string paths. Retain those with demonstrated
use cases, not all historical overrides by default.

The central trade-off: `p.mkdir().touch()`-style chaining is desirable but
`pathlib.Path.mkdir()` and `.touch()` return None. Returning self is a real
substitution/type contract difference even when it is usually ignored.
`Path.copy`/`move` have a more substantial collision: names now exist in
pathlib with different arguments, overwrite and symlink behavior. These
changes merit explicit migration, not a version-dependent API that silently
means something different on a different Python version.

* Inventory every override on 3.10, 3.12, 3.13 and >=3.14. Compare method
  signatures, return values, side effects, exceptions, symlink behavior and
  subclass return type. Include `mkdir`, `touch`, `chmod`, `relative_to`,
  `walk`, `copy`, `move`, string operators, and the class's construction
  mechanism. Build a typed consumer test and a behavioral compatibility table.
* Establish the goal: a substitutable pathlib subclass versus an explicitly
  non-substitutable fluent wrapper. Prefer the former if practical, with
  ubelt-owned methods returning self. Do not force this decision solely to
  satisfy a typechecker; quantify the migration cost in maintainer projects.
* Preserve `p.ensuredir()` (already a good fluent API). Consider a specifically
  named chainable file creation helper, e.g. `p.ensurefile()` or a different
  spelling chosen by the maintainer. It must have clear behavior for existing
  files/parents; do not implement file truncation by accident. Avoid a parallel
  alias for every mutating method or a magical `Path.chain` proxy unless an
  actual use case demonstrates value.
* For copy and move, consider retaining Ubelt's distinct safe-no-overwrite and
  file/dir-symlink-control semantics under clearly named extension methods or
  standalone utilities. Publish a side-by-side matrix with pathlib's
  operations; consider using pathlib internals on supported versions only if
  contracts match. Decide whether the old names become deprecated or get
  standard-compatible behavior in 2.0. Preserve separate file/dir symlink
  policies if users need them. Never make existing safe-copy code silently
  overwrite data during a migration; a loud incompatibility is preferable.
* Retain backports while supporting 3.10/3.11; delete them after raising the
  minimum version only when the native implementation meets the contract.
  Reassess if the support window changes, not because a new Python exists.
* Prefer standard pathlib in docs when sufficient; retain the compact
  `ub.Path` idioms where they provide real value. Retain low-cost functional
  helpers for users of string/pathlike objects where justified.

Acceptance: explicit old-to-new mapping, deprecation/migration tests,
representative fluent examples, cross-version tests, comparison against
pathlib itself, and no data-loss regressions in copy/move. The maintainer
should approve naming and any break in chaining before implementation.

### B03 — Download cache identity and integrity defaults (P0)

Separate "ensure the named local artifact exists" from "ensure this URL's
content is cached". Existing `grabdata` behavior and tests support the former:
when no hash is given, a different URL with the same destination can reuse the
previous data. Some workflows deliberately choose an explicit destination as
identity. Others expect URL identity. The difference needs an explicit policy.

Potential modes: legacy path identity, request identity (URL and only
explicitly selected request attributes), or content identity (expected
digest). Avoid using an auth token in a filename or certificate. Treat URL
normalization conservatively: query order or encoding can be meaningful.
Do not infer a universal HTTP cache key; recommend specialized HTTP cache
libraries for cache-control, ETag/revalidation, Vary, resumable transfer and
credential-aware caching. For new behavior, verify size/hash when requested
before publishing a path; default to leaving an absent target absent on
hash failure, with opt-in retention of failed content at an explicitly
separate debugging path if needed. Preserve caller-owned stream behavior
with a clear caveat. Integrate stamp identity and schema with B04. Provide
1.x opt-in and migration notes. Acceptance: local/mock transfers with same
basename, different URL/query, explicit filename, correct/wrong hashes,
existing/new destinations, no secret disclosure, and documented legacy lookup.

### B04 — Version cache identity and certificate layout (P0)

Introduce a cache format that is inspectable and supports reliable reuse
without becoming a workflow engine. Preserve ability to open v1 caches when
explicitly requested. A v2 key should use a fixed safe filename encoding
with names and dependencies independently scoped, avoiding path separators,
Windows reserved names, trailing dots/spaces and accidental normalization.
Hash arbitrary dependency objects with a versioned protocol (B01); choose
whether short text remains human readable as a label, not a substitute for
identity. Distinguish user-provided root and trusted filenames from untrusted
config data. Legacy lookups must be explicit and never undermine correctness.

Certificate schema: version, hash algorithm and structured-key version where
applicable, expected product paths or identity, sizes/mtime policy, hashes,
absolute expiry and optional metadata. Distinguish invalid certificate from
cache miss and invalid product; return a structured result through an additive
method while preserving `expired()`'s false/reason return in 1.x. Design
serialization backend policy (`pickle` trusted-only, JSON explicit), opt-out
or structured metadata, and clearer exceptions for corrupted/unreadable
cache. Do not change pickle's default merely for fashion; evaluate actual
consumer data and provide migration. Review dependency changes and artifact
hash cost, especially large outputs. Improve internal data-write integrity
with small appropriate mechanisms and clear failure semantics; general
atomic reads/writes, file locking, multi-file transactions, power-loss
resilience and distributed cache coordination are not owned by Ubelt. Use
specialized libraries when needed; recommend safer for atomic I/O.

Acceptance: cache hit/miss, None, key layout, safe filenames, existing legacy
cache explicit read, cert version mismatch, schema corruption, failed write,
metadata failure, multi-product prefix mismatch, expected expiry and
config/product changes. Benchmark overhead for simple hits and large files.

### B05 — Normalize cmd's result and execution contracts (P0/P1)

The current API combines synchronous capture, tee, inherit/discard, detach,
shell and system. Don't introduce a second subprocess framework: retain the
small convenience surface and strengthen semantics. Design a mode table
first, specifying argument parsing, stdout/stderr destinations, capture,
return/exception shapes, lifetime and cleanup. A useful direction is a typed
completed result plus a distinct detached handle, while preserving dictionary
access compatibility (`info['out']`, `info['err']`, `info['ret']`) where
possible. Evaluate `CmdOutput` as a mapping with typed properties rather than
an entirely new incompatible return type. Separate display text from argv
and exception command metadata.

Additive 1.x candidates:

* Bounded capture for each stream with explicit beginning/tail policy, byte
  vs character budget, truncation flag/count, retained data in exception,
  and independent live tee. The bound must apply to the accumulation path
  (and intermediate queues), not just truncate after communicate has retained
  the full output. Maintain incremental decoder correctness on split Unicode
  sequences and support controlled line/chunk policy. Do not conflate stream
  budget with display/report budget. No tokenizer dependency.
* Explicit stdout/stderr stream destinations and command reporting callable;
  separate stream writes from diagnostic/logging records. Preserve existing
  `verbose` and tee behavior absent new options. Consider bytes/encoding/errors
  support in a small opt-in API; locale decoding is currently implicit.
* Process cleanup and cancellation policy: default child-only semantics,
  optional process group/tree behavior where support is real, not just a
  Linux-only claim. Expose timeout/partial results, avoid background thread
  leaks and deadlocks with inherited pipes, test SIGINT/interrupt semantics.
  Do not promise safe shell-string interpolation. Use argv for untrusted args.

2.0 decisions: deprecate `system=True` (already documented as soft-deprecated
underlying os.system), clarify detached capture and ignored parameters, and
reject conflicting options rather than silently choosing one. Retain
`check=False` unless the maintainer deliberately diverges from subprocess.run;
prefer check=True in examples where failure is fatal. Detached capture must
not promise autonomous draining if the caller owns the Popen pipe; document
`communicate()` requirement and provide safe explicit modes. Evaluate whether
`cmd` can share standard subprocess result behavior without adding large
surface-area wrappers. Test all supported platform/tee modes, big outputs
with bounded RSS, partial lines, simultaneous streams, errors, timeouts,
process descendants, and binary/Unicode behavior. Make bounded capture and
output control usable without requiring global logging configuration.

### B06 — Establish consistent iterator and extrema contracts (P1)

Decide stable tie behavior for argsort, argmax, argmin, including reverse order.
Recommend stable ordering for ties and first winner for extrema (consistent
with sorted/max/min key-based behavior). This breaks some historical outputs;
provide explicit legacy behavior if downstream usage warrants. Preserve
mapping insertion order for ties, don't compare arbitrary keys. O(n) extrema
with bounded memory for one-pass iterables; evaluate large sequences. Audit
hash protocol v1 call sites before changing utility internals (B01). Ensure
`chunks` has one intelligible semantics for chunk size vs count, empty input,
length hints, `legacy`, and border policy; evaluate simplifying the old and
new paths. Define which behavior remains valid when total is only a hint.
Do not change iterator consumption or re-iterability as an undocumented side
effect. Optional general sequence default for take, boolmask negative-index
policy, and wrapped windows should be driven by actual use. See A06-A08.

### B07 — Clarify OrderedSet's deliberate deviations from set and sequence (P1)

The class inherits MutableSet and Sequence. It returns index from add and
update, supports fancy indexing that can repeat items, and has order-aware
equality for sequences but set-like equality for other iterables. These are
historical features, not all defects. Decide whether to retain this hybrid
with explicit contracts or tighten substitutions. Avoid breaking add()'s
index return if that is the primary value for consumers. Consider whether
index(start, stop) should follow Sequence.index, raise for unsupported
arguments, or use a distinct lookup method; missing item currently raises
KeyError despite docstring saying IndexError, standard list.index raises
ValueError. Do not change exception type without checking callers. Consider
new clearly named sequence/set equality helpers only when needed. Preserve
internal ordered uniqueness and map invariants regardless. Align `oset`
with OrderedSet; do not maintain two separate implementations. Decide whether
upstream ordered-set interchangeability is intended, given this is a vendored
variant. Fix invariant bugs in 1.x first (A01-A03).

### B08 — Establish mapping order and collision semantics (P1)

`UDict` and `SetDict` provide genuine value beyond native `dict | dict`,
especially differences, intersections, grouping and transformations. Keep
those. For operations overlapping dict, compare rightmost-wins union and
in-place behavior; make result class and order guarantees explicit. Design
collision policy for `map_keys`, `invert_dict(unique_vals=True)`, `dzip`, and
key transforms: should non-injective mapping silently take last, raise, or
allow explicit merge? Existing behavior is often useful; expose strict mode
if requested rather than change every default. Decide whether `merge=` is
worth implementing with a small consistent signature or removing as a
reserved unimplemented option. Document `AutoDict` read mutation and conversion
semantics, avoid serializing/inspecting it in ways that create keys. Evaluate
sorted_values/sorted_keys and set operations on mixed types under documented
ordering, not arbitrary implicit repr comparisons. Preserve insertion order
when meaningful; do not arbitrarily order unique sets just for deterministic
strings. A focused property suite should compare reflected/in-place operators
and ordinary dict/set references. Use native `dict` for basic union in new
examples; `udict` remains useful for the larger vocabulary.

### B09 — Structural comparison and traversal semantics (P1)

Refactor the nested-data comparison work from A10-A11 around a common
policy/kernel. Decide strict container type matching versus leaf equivalence,
root empty structures, named comparison tolerances, NumPy scalar/array handling,
NaNs and infinities, repeated references, cycles and custom indexable types.
The API can remain small: `allclose` for predicate and `diff` for structured
inspection. Provide useful missing/extra paths and mismatched node kinds,
ordered difference records or explicitly unordered sets, and bounds on
inspection output via urepr rather than an entirely new diff renderer.
Avoid a structural similarity score that silently equates arbitrary types;
state what its denominator counts. The legacy Generator inheritance is
awkward: `__iter__` creates a fresh generator but `next(walker)` and `send`
operate on mutable internal state; `throw` is nonstandard and the pruning
`send(False)` convention includes an intermediate yield. Treat traversal and
iterator protocol as distinct concepts. Consider separate iterator instances
per walk, with optional explicit pruning, preserving common usage and the
current generator bridge until migrated. Do not introduce general JSON Patch,
graph traversal framework, or NumPy dependency just to handle nested mappings.

### B10 — Separate progress measurement from presentation (P2)

ProgIter's low-overhead synchronous design is worth preserving. Evaluate
whether a small public measurement snapshot (count, total, elapsed, rate,
ETA) can replace download's accesses to private fields. Make it possible to
consume progress programmatically without scraping carriage-return output.
Offer optional reporting callback only if a concrete caller needs it; design
frequency and exception semantics so it is not called on every fast iteration
unnecessarily. Keep default output behavior and tqdm compatibility subset;
document that it is not a full concurrent/nested progress-bar library.
Compare overhead against current ProgIter and a bare loop, measure unknown
length and byte-oriented progress. If this would duplicate standalone
ProgIter's maintenance, coordinate ownership rather than creating two
separate semantics. Do not add a dependency on tqdm or Rich to core.

### B11 — Reconcile lazy serial execution with Future semantics (P1)

The serial mode allows debugging without thread/process overhead and lets
callers use a common submit/as_completed API. Current fake FINISHED state
is a workaround that contradicts the semantic meaning of stdlib Future
before computation. Decide whether the future contract is important enough
to change evaluation timing (eager serial execution) or whether a distinct
lazy job/result handle and a library-owned completion iterator are preferable.
Preserve lazy mode as explicit opt-in if valuable. Standard wait/as_completed
must not claim a result is ready that is not actually available unless the
object is explicitly documented as a special adapter. Consider eager vs lazy
exception timing, cancellation, timeout, callback order, shutdown and memory
retention; compatibility tests should characterize current behavior before
any redesign. For Executor/JobPool, consider forwarding `wait` and
`cancel_futures` shutdown parameters and modern executor map parameters
only where they can be implemented honestly across supported versions.
Process/interpreter executors are stdlib-owned; don't create a scheduler.
Validate 3.14 interpreter backend, start-method changes and process lifecycle
on actual CI. Add bounded outstanding job patterns if benchmarks justify;
keep complex resource scheduling out of scope.

### B12 — Platform directories and filesystem links as explicit contracts (P1)

Follow A19-A20 with a migration decision for native directories and XDG
fallback. Decide whether platformdirs is a more appropriate recommendation
for advanced site/user/runtime directory policy. Keep existing simple helpers
if they are useful and correct. No surprise relocation of cached or persisted
user data. Publish old/new path examples and opt-in migration guidance.
Complete existing `ub.symlink(relative=...)` transition: preserve explicit
relative vs absolute intent, make omitted choice on relative input fail or
follow the agreed warning schedule, ensure existing equivalent targets are
idempotent only when representation matches. Distinguish lexical path
normalization from filesystem resolution: `a/link/../file` may not mean the
same thing when link is a symlink. Test relative path traversal, missing
parents, dangling links, cross-drive links, Windows junction/hardlink fallback
and explicit directory type where target does not exist. Define when a true
relative symlink cannot be represented; do not silently claim a hardlink or
junction is equivalent. Overwriting a physical path must require explicit,
well-documented behavior, not an inferred link provenance. Avoid expanding
into general safe filesystem transaction APIs.

### B13 — Define what importing and finding a module means (P1)

Provide a precise distinction between static filesystem discovery, ordinary
import by qualified name, and exact-path loading. Existing `import_module_from_path`
intentionally manipulates sys.path then imports by name; it cannot guarantee
exact path with duplicate names and existing modules. An exact-path mode may
need `spec_from_file_location`, explicit qualified module name and well-defined
package/relative import handling. Loading arbitrary modules has execution
side effects; never advertise this as sandboxing. Prefer conflict detection
and refusal over silent module replacement. Preserve ability to load proper
packages and extension modules with their expected names. Decide what static
lookup promises for builtins, namespace packages with multiple roots, zip and
editable installs; return a spec-like object only if needed, not a reimplementation
of the import system. Use stdlib machinery where semantics fit, and document
limitations rather than chasing every packaging backend. Make separate
`is_modname_importable` semantics clear (discoverable vs successfully executable).

### B14 — Memoization semantics and compatibility (P1)

**Target: 2.0 only for memoize key changes.** The maintainer explicitly
identified this as a known issue to address in 2.0. Even if B01 provides an
opt-in encoder during 1.x, do not connect it to memoize or introduce an
alternative keying scheme in 1.x. Design the solution together with B01 and
preserve the existing equivalences unless intentionally revised. Test the
known delimiter collision, a direct digest-string argument versus an unhashable
value, kwargs order, typed equivalence, mutable arguments, exceptions, and
cache invalidation against the agreed 2.0 contract.

Coordinate with B01 and A27. `functools.cache`, `lru_cache`, and
`cached_property` now cover much of historical use. Ubelt's support for
unhashable inputs and per-instance method caching still distinguishes it.
Document the choice between typed equivalence, positional/keyword canonical
binding and exact call signature; use fast native keys when the agreed
semantics permit. A typed and tagged fallback should prevent legacy framing
ambiguities, but must not claim to support arbitrary mutable objects without
stable semantics. Evaluate extension use, method inheritance with same method
names and instance storage conflicts, pickling cached instances, slotted
classes, thread races and invalidation (`.cache`, clearing properties/methods).
Do not promise at-most-once concurrent calls unless synchronization is
explicitly provided. Do not automatically replace with stdlib cache if it loses
unhashable input support or existing `.cache` behavior. Retain current simple
API or narrow recommended use; introduce bounded cache behavior only if there
is a demonstrated need not already met by functools. Recommend functools when
inputs are hashable and its contract is sufficient.

### B15 — Bounded urepr, deterministic display and cycles (P1)

This is a high-value additive candidate independent of the 2.0 major release.
`urepr` is primarily a configurable human-readable representation, not a
serialization format; a bounded form would also be useful for agents inspecting
large values. Explicitly distinguish per-container item limit, recursion-depth
limit and global output budget. Candidate options `max_items`, `max_depth`,
`max_chars` are only proposed spellings. Define whether a limit counts shown
items, bytes or Unicode code points; make truncation evident. Do not perform a
complete formatting pass then slice the resulting string when the object is
huge. A global budget must constrain traversal and expensive formatting as
far as practical, including NumPy/pandas summaries. An arbitrary user-defined
repr/custom extension can itself do expensive work; document this limit to any
resource guarantee. Cycle detection should track active identities rather
than globally suppress shared references. Choose deterministic omission
markers, preserve important delimiters and truncation metadata if possible,
and state that bounded output need not be evaluable as Python.

Extension dispatch uses ordered type and typename registration; define precedence
for overlapping base/subclass registrations, custom extensions and built-ins.
Support a budget-aware extension protocol only if existing kwargs are
insufficient; avoid breaking existing callbacks. Decide whether invalid kwargs
should warn or raise for built-in paths while allowing extensions to consume
custom kwargs. Redaction by explicit keys or predicate may be useful, but do
not claim automatic secret detection. Keep compact and multiline formatting,
legacy repr2 behavior, and default output stable absent opt-in. Test cycles,
shared references, huge leaves, large arrays, deep nesting, mixed keys,
custom repr/extensions, non-ASCII output, and interactions of budget and
format options. Benchmark import time and execution overhead on small inputs.

### B16 — Standardize output control without replacing print wholesale (P2)

Diagnostics, explicitly requested textual output, and continuous streams are
different. Introduce stdlib module loggers only where diagnostic event records
are useful independent of caller verbosity. Never configure the root logger
or set application policies. Keep `verbose=` as an explicit request and
support callable/stream overrides where natural (Cacher and CacheStamp
already do this). Avoid duplicate logging plus printing, secret exposure in
command/URL/config logs, and error logging immediately before propagating an
exception with identical information. ProgIter, Timer, capture and subprocess
tee are stream-oriented. Do not force logging configuration to get requested
output. Consider silent operation and structured results first. Do not
introduce a public logging framework or multiple new levels. See earlier
planning document for details; settle this only after the output-heavy
workstreams B05/B10/B15 establish their contracts.

### B17 — Explicitly resolve scheduled deprecations before 2.0 (P0)

Many existing `schedule_deprecation` calls already plan errors at 2.0 and
removal at 2.1. Simply bumping `__version__` can turn commonly used calls,
including examples in other modules, into RuntimeErrors. Inventory these
before bumping; choose action for each and test a hypothetical 2.0 version.
The source includes:

| API | Existing direction | Proposed decision process |
| --- | --- | --- |
| `repr2`, `FormatterExtensions` | urepr migration; legacy sorting behavior | retain cheap alias if semantics are acceptable; preserve old formatting explicitly or retire with migration |
| `readfrom`, `writeto` | built-in/pathlib I/O | remove or retain thin alias based on usage; do not rebuild atomic I/O |
| `ensure_unicode` | unnecessary in Python 3 | retire or retain tiny compatibility helper, no new behavior |
| `get_app_*_dir`, `ensure_app_*_dir` | Path.appdir | coordinate with Path reassessment, directory identity migration; avoid forcing Path unnecessarily |
| `ensuredir(recreate=True)` | delete().ensuredir() | retire destructive flag with clear migration; do not drop standalone ensuredir |
| `DownloadManager` | already deprecated, vendor code | retire; use JobPool/Executor plus download or grabdata; fix own references before version bump |
| `indexable_allclose` | IndexableWalker.allclose | inexpensive wrapper; decide if permanent alias is useful, no explicit removal schedule in source |
| `symlink` implicit relative target | explicit choice in 2.0 | complete documented migration (B12) |
| `cmd(system=True)` | possible future removal | decide after mode-table audit |
| Path legacy aliases/overrides | unresolved | handle under B02 with migration and compatibility tests |

Distinguish deprecated spelling from problematic behavior. Remove costly or
misleading semantics rather than maximizing deleted API count. LLMs may keep
producing old names indefinitely; recommend canonical APIs in docs, and retain
low-cost aliases when they do not hurt correctness. Existing API deprecation
calls need suitable `packaging` support in minimal installs (A38). Consider
an explicit deprecation inventory generated from calls to schedule_deprecation
or maintained alongside release planning, not a complex runtime registry.
Update all in-tree examples to use supported recommended names or demonstrate
legacy behavior deliberately. Ensure package exports, docs, tests and public
annotations agree. A compatibility test may simulate version 2.0 in a separate
process; do not change published version just to test this. Preserve
pickle-loaded references to old public classes where reasonable, or document
incompatibility clearly.

## D. Evaluation and maintenance tasks independent of releases

### D01 — Measure discoverability and correct reuse (P1, E)

The previous overlay provides `llms.txt`, `llms-full.txt`, cookbook, and wheel
resources. Do not assume these automatically influence coding agents. Start
with a small controlled benchmark of perhaps 12-20 tasks, expand only if
informative. Representative tasks: run and stream a subprocess, handle paths
with spaces, group inputs, compute a configuration key, cache None, validate
multiple artifacts, iterate chunks, compute stable extrema, represent a large
nested structure, and resolve a symlink. Include a task where pathlib or
functools is the correct answer without ubelt. Design tests against intended
contracts, not current bugs. If evaluating a known broken path, report that
failure separately so docs aren't credited with making a broken utility
correct.

Compare baseline stdlib only, ubelt installed with no instructions, one-line
recommendation, and compact task-oriented docs. Use same model/settings and
seed/repetitions where possible; separate model capability from retrieval.
Record actual use of ubelt, correct function/argument choices, pass rate on
hidden tests, generated code size, latency, token use and tool calls. Include
small local models and stronger coding models where available. Agents must
not have access to hidden test answers. Evaluate dependency overhead and
reuse when already installed versus installing a new dependency. Report
uncertainty and actual failure examples, not an unsupported claim about all
LLMs. Feed concrete misuse into cookbook and API docs; avoid optimizing for
one model's idiosyncrasies. No paid service or runtime model dependencies
required; benchmark harness can live under dev.

### D02 — Measure import cost and hot-path performance (P1, E)

Ubelt's value includes lightweight setup. Benchmark cold `import ubelt` in
fresh processes, baseline vs post-change, minimal install and optional
NumPy/other extras. Record module counts, median timings and spread, and
first-call lazy setup of hash_data and urepr separately. Examine lazy
registration costs before optimizing; do not add complex lazy public exports
solely for microbenchmarks. Representative throughput tests: `chunks`,
`argsort`/extrema, set and dict ops, `hash_data`, `hash_file`, urepr small and
large, ProgIter disabled and enabled, cache hits and subprocess tee.
Benchmark data sizes and realistic distributions; distinguish CPU/memory
limits. Prefer improvements with correctness evidence and measurable impact,
not generic Python style refactoring. Keep benchmarks outside unit-test
critical paths.

### D03 — Audit existing consumer usage and migration cost (P1, E)

Historical usage counts in docs/source/manual/function_usefulness.rst are
useful but not population-wide adoption statistics. Re-run the usage survey
on an explicitly chosen set of current public or maintainer-owned repositories
with permission; keep private code local. Inventory method calls and aliases
(especially `Path.mkdir/touch/copy/move`, repr2, ensure_app_*_dir,
indexable_allclose, chunks, argsort ties, memoize, Cacher and grabdata).
Look for return-value chaining, catch clauses, filename parsing, caches
persisting IDs, expected output, and optional dependency assumptions. Static
AST analysis cannot resolve every alias/dynamic call; supplement with targeted
runtime tests or migration diffs. Classify high-cost breaking changes and
prioritize 1.x bridge APIs. This informs removal decisions and 2.0 scope.

### D04 — Add contract-oriented regression checks, not test-count inflation (P1)

Use existing test files. A small invariant/reference test is often better
than many identical examples. Useful properties: OrderedSet list/map
bijection after mutation; dictionary operator/named-method parity; iterator
consumption exactly once; nested equality symmetric and reflexive for supported
values under chosen NaN policy; hash framing and unordered-container invariance;
cache miss vs cached None; validated artifact identity; cmd argv round-trip,
bounded output memory and timeout cleanup; links never destroy physical targets
under a safe policy. Test platform-specific paths on actual operating systems.
Use deterministic pseudo-random small cases (seeded stdlib) if adequate, not
mandatory Hypothesis. Add property dependency only with justification and
maintainer approval. Separate unit tests from benchmark/integration tests;
use local/mock downloads and isolated temp paths, never rely on public network
availability for correctness. Keep branch coverage according to repository
policy and report untested paths honestly. Avoid low-value coverage-only tests.

### D05 — Maintain a version-aware recommended API and migration table (P1)

The public flat namespace is a strength. Generate stable documentation with
problem-to-function mapping, canonical spellings, deprecation status, versions
and critical caveats. Keep docs source in signatures/docstrings as far as
possible. The compact generated reference currently extracts first paragraph
and signature; assess whether critical conditions are discoverable (e.g.
legacy hashing, Path collision, capture behavior, cache trust) without making
full reference enormous. The curated cookbook can provide such caveats.
Consider machine-readable `api.json` or a CLI only after D01 shows value
beyond introspection. Expose package resources with standard importlib.resources
and version-appropriate links. `python -m ubelt` currently runs doctests;
do not replace it casually. Build/release freshness checks should catch
changes in root and wheel docs. Correct stale Python version statements and
legacy internal examples. Recommend specialized libraries (safer, platformdirs,
full subprocess/HTTP tools) when Ubelt deliberately doesn't solve a problem;
verify scope and avoid new runtime dependencies. Explicit non-goals can help
agents avoid reinventing features.

## Module coverage ledger

Every top-level Python module is represented here. This ledger separates
review coverage from a decision to modify it: some modules warrant only
maintenance, and that is a valid outcome. Public flat exports from `__init__`
are covered by their defining modules. The ledger also identifies interfaces
that require more focused verification before implementation.

| Module | Main scope | Task references / disposition |
| --- | --- | --- |
| `__init__.py` | flat exports, aliases, version, type/export hygiene | A39-A40, B17, D05; regenerate mkinit only after changes |
| `__main__.py` | xdoctest entry point | A40, D05; keep existing behavior |
| `_win32_jaraco.py` | vendored ctypes/reparse internals | A19, B12; targeted Windows validation |
| `_win32_links.py` | symlink privilege, junction/hardlink fallback | A19, B12; high-priority safety review |
| `orderedset.py` | ordered mutable set and sequence | A01-A03, B07; invariant fixes before redesign |
| `progiter.py` | adaptive progress and tqdm subset | A15, B10; preserve fast synchronous design |
| `util_arg.py` | tiny argv helpers | A37; minimal parser, document boundaries |
| `util_cache.py` | Cacher, CacheStamp | A28-A29, A32, B01/B04; correctness and migration |
| `util_cmd.py` | subprocess modes, tee, output result | A12-A13, B05; high priority |
| `util_colors.py` | color and syntax highlighting | A34; fix env policy, retain optional backends |
| `util_const.py` | NoParam sentinel | A37, A39; retain singleton compatibility |
| `util_deprecate.py` | versioned deprecation lifecycle | A38, B17; avoid optional dependency surprises |
| `util_dict.py` | dictionary functions and UDict | A04-A05, A09, B08; preserve useful vocabulary |
| `util_download.py` | download and cached artifacts | A30-A31, B03/B04; identity and integrity |
| `util_download_manager.py` | deprecated multi-download helper | B17; no new feature work |
| `util_format.py` | repr2 / compatibility extensions | B15/B17; alias/format policy |
| `util_func.py` | identity, compatible, inject_method | A36-A39; document and type rather than expand |
| `util_futures.py` | serial futures, executor, job pool | A16, B11; explicit laziness contract |
| `util_hash.py` | file and structured hashing, extensions | A26, B01; v1 stability, v2 grammar |
| `util_import.py` | module discovery and import by path | A22-A24, B13; precise non-importing guarantees |
| `util_indexable.py` | nested traversal, equality and diff | A10-A11, B09; correct comparison first |
| `util_io.py` | legacy I/O, touch, delete | A18, B17; no general atomic I/O |
| `util_links.py` | portable symlink abstraction | A19/A25, B12; explicit relative intent |
| `util_list.py` | iterables, chunks, extrema | A06-A08, B06; ordering/consumption contracts |
| `util_memoize.py` | unhashable and method/property caching | A27, B14; coordinate with hash v2 |
| `util_mixins.py` | NiceRepr | A37/A39; keep small |
| `util_path.py` | fluent path, path compatibility, ChDir | A17/A25, B02/B12/B17; reassess stdlib overlap |
| `util_platform.py` | platform directories, executable/path lookup | A20, B12/B17; compare shutil.which for simple executable lookup |
| `util_repr.py` | configurable representations, extensions | A35, B15; bounded inspection |
| `util_str.py` | formatting and text convenience | A08/A37, B17; preserve common idioms |
| `util_stream.py` | Python stream capture and tee | A14, B16; lifecycle and scope |
| `util_time.py` | timestamps, time parsing, Timer | A33, B16; preserve compact filename-friendly form |
| `util_zip.py` | archive path parsing and read wrapper | A21; no general extraction framework |

Additional repository areas: pyproject/requirements/lockfile and xcookie CI
(A38-A40), tests/typecheck_consumer.py and regression tests (A39, D04),
README/changelog/docs/Sphinx and new docs generator (A40, D05), dev/bench and
usage scripts (D01-D03). This pass did not exhaustively audit dev scripts,
notebooks, generated CI, every old changelog entry or dependency release.
Treat those as targeted release-engineering follow-ups rather than implicit
permission for unrelated refactors.

## Suggested implementation batches (revised conservative queue)

For a maintainer or coding agent, work in narrow independent patches. Do not
stage unrelated changes, create worktrees, or change release number early.
The table below lists candidate patches, not a directive to implement every
original A item. Each patch must honor the disposition above and avoid
unrelated fixes. Stop if the actual checkout has changed or existing intent
is inconsistent with the proposed behavior.

| Batch | Tasks | Scope eligible for 1.5 |
| --- | --- | --- |
| 1: collection invariants | A01, A02, A03, A04 | Repair corrupt indices, generator/duplicate set operations, duplicate-sensitive predicate, documented column consistency; do not change order or equality policies |
| 2: nested comparison | A10 | Unequal paths return false, supported mixed keys work; preserve leaf comparison and return_info contracts |
| 3: filesystem and command basics | A12, A17, A21, A23 | PathLike argv, existing-file directory postcondition, documented colon archive spelling, context restoration; keep broader archive safety review separate |
| 4: validation | A26, A28 | False file digest/invalid base nontermination and explicit prefix list length mismatch only; no valid hash, cert layout or scalar-prefix policy changes |
| 5: output | A14, A34 | Repeated capture and wrong environment variable; no reporting redesign |
| Maintenance | A25, A37, A39, A40 | Targeted docs, annotations and normal release checks; no runtime redesign |

The immediate queue consists of 13 **FIX** items; several have intentionally
narrower scopes than their original descriptions. These are candidates, not
all mandatory before 1.5. For each: reproduce on current code, identify the
existing contract, write the smallest regression, make the smallest fix,
check neighboring existing tests, and regenerate derived documentation when
necessary. A review that finds intentional behavior should close the issue as
preserved, not create a different test expectation.

### Investigation and approval queue (not automatic implementation)

| Category | Tasks | Direction |
| --- | --- | --- |
| Safety/integrity | A13, A19, A30 | Verify actual platform/transfer behavior, prioritize potential destructive failures; propose narrow patches only with evidence |
| Ambiguous existing contracts | A05, A07, A08, A15, A16, A18, A24, A33, A35, A38 | Check docs, tests, caller usage and maintainer intent before proposing any change |
| Existing 1.x behavior retained | A06, A09, A11, A20, A22, A27, A29, A31, A32, A36 | Document only; bring proposed contract changes to 2.0 design. A27 is expressly deferred by maintainer |

### 2.0 sequence (proposed, subject to approval)

| Workstream | Tasks | Direction |
| --- | --- | --- |
| Durable hash protocol | B01 -> B04, B14 | Specify encoding and migration; memoize key fix only in 2.0 |
| Path and links | B02, B12, B13 | Decide migration policy; platform tests before defaults change |
| Output-heavy utilities | B05, B15, B10, B16 | Consider additive bounded output separately; keep output semantics unless approved |
| Collection/concurrency contracts | B06-B09, B11 | Establish intended semantics and actual migration cost before deciding changes |
| Downloads/deprecations | B03, B17 | Respect tested legacy reuse, hash-mismatch behavior and inexpensive aliases; choose changes explicitly |
| Parallel evaluation | D01-D05 | Agent/consumer/performance evidence and quality gates, independent of release |

**Recommended 1.5 release gate:** verified and approved localized fixes,
explicit triage of any confirmed integrity/data-loss problems, ordinary
supported test matrix, minimal install, and docs build. Do not change memoize
keys, existing valid hashes, Path inheritance semantics, cache/download
identity, platform directories, ordering rules, or serialization defaults.
Do not add mandatory runtime dependencies or public atomic I/O. A source-only
platform risk merits investigation, not a speculative patch or automatic
release blocker. Features requiring design can wait.

**2.0 planning gate:** document the contract and compatibility impact of each
proposed change, check consumer usage, and get maintainer approval. Fix the
known memoize hash issue in coordination with the versioned structured hash
protocol. Path substitutability and the relative symlink transition are major
candidates. Other B items may remain unchanged if present behavior is desired;
there is no requirement to implement every audit suggestion in a major release.

## Reproduction appendix

Run against a clean checkout with the earlier overlay applied. These are
observational probes describing baseline failures, not a test suite asserting
that the bugs must remain. Convert to appropriately named regression tests only for approved fixes
when their target release and intended behavior have been established. Paths must be confined
to temp directories; none of these requires an external service.

```python
import ubelt as ub

# A01: internal index no longer describes sequence.
s = ub.oset('abc')
del s[0]
print(list(s), s.map, s.index('b'))  # ['b', 'c'], {'b': 1, 'c': 2}, 1

# A02: one-shot and repeated values.
print(list(ub.oset([1, 2]).symmetric_difference(iter([2, 3]))))  # [1]
s = ub.oset([1, 2])
s.symmetric_difference_update(iter([2, 3, 3]))
print(list(s), s.map)  # [1, 2, 3, 3], {1: 0, 2: 1, 3: 3}

# A04/A05: columns and mutation.
print(ub.varied_values([{'a': 1}, {'b': 2}]))  # NoParam in both sets
basis = {'a': [1]}
list(ub.named_product(basis, b=[2]))
print(basis)  # {'a': [1], 'b': [2]}

# A10: raises rather than returning a predicate result.
# Run these separately, each raises on the baseline.
ub.IndexableWalker({'a': 1}).allclose({'b': 1})  # AssertionError
ub.IndexableWalker({1: 1, 'a': 2}).allclose({1: 1, 'a': 2})  # TypeError
```

```python
import ubelt as ub

# A06/B06: ordering choices.
print(ub.argsort([1, 1], reverse=True))  # [1, 0]
print(ub.argmax([1, 1]), ub.argmax(iter([1, 1])))  # 0, 1
# ub.argsort({1: 0, 'a': 0}) raises TypeError

# A14: capture reuse.
cap = ub.CaptureStdout()
with cap:
    print('first')
with cap:
    print('second')
print(repr(cap.text))  # '\n', not 'second\n'

# A27/B01/B14: known 2.0 issue, not a 1.5 regression target.
f = ub.memoize(len)
print(f(['a_,_b']), f(['a', 'b']))  # 1, 1
print(ub.hash_data(['a_,_b']) == ub.hash_data(['a', 'b']))  # True
print(ub.hash_data('a', types=True) == ub.hash_data(b'a', types=True))  # True
print(ub.hash_data([1], types=True) == ub.hash_data((1,), types=True))  # True
print(ub.hash_data(True, types=True) == ub.hash_data(1, types=True))  # True
```

```python
import hashlib
import os
import pathlib
import tempfile
import zipfile
import ubelt as ub

with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    p = root / 'existing.txt'
    p.write_bytes(b'a')
    print(ub.ensuredir(str(p)))  # A17: returns existing regular file
    print(ub.hash_file(p, blocksize=0) == hashlib.sha512(b'').hexdigest())  # A26

    q = root / 'other.txt'
    q.write_bytes(b'b')
    stamp = ub.CacheStamp('demo', dpath=root, product=[p, q],
                          hash_prefix=[hashlib.sha512(b'a').hexdigest()],
                          hasher='sha512', verbose=0)
    cert = stamp.renew()
    print(len(cert['hash']), stamp.expired())  # A28: 2, False

    if os.name == 'posix':
        exe = root / 'program with space'
        exe.write_text('#!/bin/sh\nprintf ok')
        exe.chmod(0o755)
        try:
            ub.cmd(exe, check=True)  # A12: FileNotFoundError
        except FileNotFoundError as ex:
            print(ex)
        fifo = root / 'fifo'
        os.mkfifo(fifo)
        ub.delete(fifo)
        print(fifo.exists())  # A18: True

    archive = root / 'sample.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('member.txt', 'hello')
    print(ub.split_archive(str(archive) + ':member.txt'))
    try:
        ub.zopen(str(archive) + ':member.txt').read()  # A21: OSError
    except OSError as ex:
        print(ex)

    dst = root / 'download.txt'
    ub.grabdata(p.as_uri(), fpath=dst, verbose=0)
    ub.grabdata(q.as_uri(), fpath=dst, verbose=0)
    print(dst.read_bytes())  # B03: b'a' (documented legacy identity)
```

Other probes and source findings are recorded at the individual tasks. Before
fixing an approved item, write a small regression that demonstrates a breach
of the existing contract on the actual current branch. For source-only risks,
verify reachability and intended behavior, then obtain approval for any change.
Observations of deliberate or ambiguous legacy behavior are not 1.5 failure
expectations.

## Explicit non-goals and unresolved decisions

* Do not own atomic reads/writes as general abstractions; recommend safer.
  Internal data integrity improvements are allowed, with bounded guarantees.
* Do not turn ubelt into an LLM SDK, token accounting library, async agent
  framework, workflow engine, general cache service, full CLI framework,
  filesystem sandbox or HTTP client framework.
* Do not replace print wholesale with logging or add a new logging framework.
* Do not maximize the number of deprecations, aliases removed, annotations,
  or tests. Optimize for clarity, demonstrated correctness and reuse.
* Do not change established behavior in 1.5 solely because a corner case looks
  cleaner with different semantics. Document first; even explicit opt-ins need
  agreed contracts. Memoize key changes are expressly 2.0 only.
* Open maintainer decisions: hash v2 equality and extension contracts; fluent
  Path naming and standard substitutability; platform-directory migration;
  safe Windows fallback policy; structured cache layout and serialization;
  grabdata identity; extrema tie policy; lazy serial Future compatibility;
  scope of deprecations; and whether the agent benchmark justifies further
  docs/CLI work. These require design approval and sometimes real-world usage
  evidence, not independent unilateral implementation by a coding agent.

