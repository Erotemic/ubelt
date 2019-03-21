Version: 0.8.0
--------------
* The `sort` kwarg of `ub.repr2` can now accept a function, which will act as a key to the `sorted` function.
* Add `ub.dict_diff`
* Add some benchmarks
* Fix GH #53


Version: 0.7.1
--------------
* Fixed bug in `ub.dict_hist` when `ordered=True`. (half of the keys would be lost). Also effected `dict_take`. Thanks to [cite Chris Funk].


Version: 0.7.0
--------------
* `ub.cmd` now reports `cwd` on exception
* Reworked requirements to minimize dependencies. 
* The `xxhash` and `pygments` dependencies are now optional.
* The testing dependencies are now optional.
* Add `memoize_property`


Version: 0.6.3
--------------
* new tests
* add `util_stream`
* Fixed issue in `ub.download` with bad content header urls


Version: 0.6.2
--------------
* `ub.download` can now accept `fpath` as either a file path or a `io.BytesIO` object 
* `ub.FormatterExtensions.register` can now accept a type or tuple of types.
* `ub.platform_cache_dir` and `ub.platform_config_dir` now respect XDG environs on Linux systems.
* `ub.platform_resource_dir` is deprecated in favor of `ub.platform_config_dir`.


Version: 0.6.1
--------------
* `ub.repr2` now accepts negative values for `newlines`, which means use
  newlines until the current height is only `-newline`.
* `ub.repr2` now keeps track of nesting depth from the bottom
* Add custom extensions to `ub.repr2` and expose `ub.FormatterExtensions`
* Make result `ub.memoize_method` appear more like a bound method.
* Add `dict_isect` to `util_dict`.
* Fixed misspelling in docs 
* Fixed misspelled detach kwarg in `ub.cmd` (the old `detatch` argument is now deprecated and will be removed)


Version: 0.6.0
--------------
* Add class variable `FORCE_DISABLE` to `ub.Cacher`
* Add the `xxhash` algorithm as an option to `ub.hash_data`
* `ub.peek` - 4-letter syntactic sugar for `lambda x: next(iter(x))`


Version: 0.5.3
--------------
* Fixed GH#41
* Add `key` to `ub.find_duplicates`
* Renamed first argument of `ub.chunks` from sequence to items
* Improved type hints in google-style docstrings 
* `ub.cmd` verbose >= 3 now uses nicer Unicode characters if possible


Version: 0.5.2
--------------
* `ub.group_items` argument names have changed, and it can now take a callable as the second argument. The `sorted_` argument is now deprecated.
* Symlink now reports location of old target when the new target does not match
* Docstrings now uses `PathLike` as the type for arguments and attributes that should be considered paths (note strings are still accepted).
* `ub.download` will now keep a potentially corrupted file if the hash does not
  match.
* `ub.grabdata` will compute the hash of an existing file on disk if the .hash
  stamp is missing to try and avoid re-downloading the file.
* Improved efficiency of `ub.argmax`
* Add verbose flag to `u.bCacheStamp`


Version: 0.5.0
--------------
* Certain imports are not lazy to optimize startup time
* BREAKING CHANGE:
   * change `ub.cmd` `tee` parameter to `tee_backend`
   * change `ub.cmd` `verbout` parameter to `tee`
* `import_module_from_path` can now handle zip-imports where the zip-file is
  followed by a slash rather than a colon
* added `ub.expandpath` 


Version: 0.4.0
---------------
* Using ordered-set PyPI package for the `OrderedSet` implementation 
* Remove `ub.OrderedSet`.extend
* New functionality:
    * `ub.find_exe` - a python implementation of which 
    * `ub.find_path` - finds matching files in your PATH variables

* BREAKING CHANGES:
    Chaning default behavior of util_hash.
    Default of `ub.Cacher` maxlen changed to 40 for sha1 considerations
    Default of `ub.hash_data` `base` changed from `abc` to `hex`
    Default of `ub.hash_data` `types` changed from True to False.
    Moved argument position of hashlen to the end.

* ENH: `ub.download` now accepts `hash_prefix` and `hasher` args. 
* Add `ub.CacheStamp`
* ENH: `ub.hash_file` now accepts `types` args
* ENH: `ub.augpath` now accepts `multidot` args
* ENH: `ub.cmd` now accepts `cwd` and `env` args
* FIX: `ub.NoParam` is now Falsey

Version: 0.3.0
---------------
* Remove `ub.PY2` and `ub.PY3`. Use `six` instead.
* `ub.import_module_from_path` can now import modules within zip-files

Version: 0.2.1
---------------
* `ub.dzip` now accepts a backend dict class as a keyword argument
* `OrderedSet.intersection` can now handle a single argument
* `Timerit` `num` now defaults to 1 
* Add function `print` to Timerit

Version: 0.2.0
---------------
* Fix timezone issue with negative time-zones
* Move internal `__init__` auto-generation logic to new `mkinit` repo
* Network tests no longer run by default and require `--network`

Version: 0.1.1
---------------
* Add `ub.argmin` and `ub.argmax`
* `ub.Cacher` can now be used as a decorator.
* Rename `util_decor.py` to `util_memoize.py`
* Add `key` argument to `ub.unique` and `ub.unique_flags`
* Add `ub.argunique`
* `import_module_from_path` now prefers the path module when there are name conflicts
* Fix `ub.repr2` precision with numpy scalars 
* Add `ub.dzip`


Version: 0.1.0
---------------
* simplified dynamic imports
* `memoize_method` now handles kwargs
* Add `inject_method` to `util_func.py`.
* Can now update `ProgIter` description on the fly
* Add methods to `OrderedSet` to complete the set API
    (e.g. `intersection`, `difference`, etc...)
* Can now index into an `OrderedSet` using a slice
* Fixed issue with `OrderedSet.union` where it ignored `self`
* Fixed issue with `OrderedSet.union` where `__eq__` and `isdisjoint` were wrong
* Add `appname` keyword argument to `grabdata`
* Add `allsame`
* Add `extend` to ordered set API
* Fix issue with `ub.repr2` dictionaries with newlines in keys
* Fix issue with relative paths and symlink
* Increase `tqdm` compatibility with `ProgIter`

Version: 0.0.44
---------------
* Add `ub.iter_window`

Version: 0.0.43
---------------
* Remove `util_stress`, it was out of scope. 
* Spelling: changed the `Timer.ellapsed` attribute to `Timer.elapsed`.
* Verbosity of `Timer` and `Timerit` now depends on if a label was
  specified. 
* `Timer.tic` now returns a reference to the `Timer` instance.


Version: 0.0.42
---------------
FIX: bug in `hash_data` where negative integers did not work.
ENH: `hash_data` can now accept `OrderedDict` input
ENH: `dict_union` now returns `OrderedDict` if the first argument is one

Version: 0.0.41
---------------
ADD: `OrderedSet` / `oset`
ENH: Add base to `augpath`
ENH: Add `symlink` function that works on UNIX and Windows*.
(*if use has symlink permissions, it works just like UNIX without caveats.
  Otherwise `ub.symlink` falls back to using junctions and hard links, 
  which should still work mostly the same, except `os.path.islink` and
  `os.readlink` will not work among other minor issues).
ENH: `ub.delete` now treats nested junctions as symlinks, unlike `shutil.rmtree`.


Bersion: 0.0.40
---------------
ENH: Add `numpy` support to `ub.repr2`

Version: 0.0.39
---------------
ENH: Changed `ub.Timerit`.call API to return a reference to the Timerit object
instead of of the average seconds. Note this change is backwards incompatible.


Version: 0.0.38
---------------
ADD: `ub.hash_data` and `ub.hash_file` for easy hashing of arbitrary structured
    data and file.

ADD: `ub.dict_union` combines multiple dictionaries and returns the result.

ENH: `ub.Timerit` reports better measures of expected time.

ENH: new argument `total` to `ub.chunks` lets you specify how long an iterable is if
`len` is not available (for generators)

Version: 0.0.37
---------------
ADD: Add `ub.TempDir`

ADD: Add `ub.import_module_from_path`

ADD: Add `ub.import_module_from_name`

ENH: can now choose `ub.cmd` tee backend (select or thread) on POSIX. 

FIX: fixed unused argument `chunksize` in `util_download`

ENH: `ProgIter` now supports a more `tqdm`-like API

FIX: `ub.cmd` tests now work on windows

FIX: terminal colors now work on windows

ENH: Add standard deviation to `timerit`

ENH: Minor enhancements to `ub.Cacher`

DEPRECATE: Remove most of the `static_analysis` module. Use code in xdoctest for now. Note: some of this functionality may return as general utilities in the future, but the existing constructs were only needed for doctests, which are now done via xdoctest.

Version: 0.0.34
---------------

FEATURE: Add `ub.truepath`

FEATURE: Add `ub.iterable`

FEATURE: Add `util_func.py` with `ub.identity`

FEATURE: Add `util_download.py` with `ub.download` and `ub.grabdata`

ENH: `__init__` imports are now statically generated, this fixes
   the random third party attributes (e.g. `expanduser`, `Thread`) that were
    exposed in the __init__ file.

ENH: `ProgIter` now uses scientific notation when it is small

ENH: `ub.AutoOrderedDict` now inherits from `ub.AutoDict`

ENH: tests are now running using `pytest` and `xdoctest`

ENH: `ub.cmd` now uses thread based logging 

FIX: Fixed many failing tests on windows

FIX: Small bug and documentation fixes.

ISSUE: `ub.cmd` does not work correctly on windows

ISSUE: some Unicode formatting does not work correctly on windows


Version: 0.0.33
---------------
FEATURE: Add `ub.repr2` and `ub.hzcat`
FEATURE: Add `ub.color_text`


Version: 0.0.31
---------------
FEATURE: Add `ub.argflag` and `ub.argval`


Version: 0.0.28
---------------
FEATURE: Add `ub.AutoDict` and `ub.AutoOrderedDict`.
