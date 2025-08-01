# Changelog

We are currently working on porting this changelog to the specifications in
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project (loosely) adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version 1.3.8 - Unreleased

### Added
* Added: `ub.Path.relative_to` now backports the `walk_up` feature from Python 3.12 
* Add `keys` and `values` method to `IndexableWalker`

### Changed
* `ub.Path.walk` now supports the same signature as the new version in Python 3.12
* Support `FORCE_COLOR`

### Fixed
* Version checking issue in util-import
* Rare exception in Path.copy on windows with older pythons


## Version 1.3.7 - Released 2024-12-06

### Added
* Added `requestkw` to `ub.download`. 

### Fixed:
* Minor test issues.
* `ub.IndexableWalker.diff` for empty inputs
* Bug in `memoize_method` which could produce incorrect results if methods from different instances are assigned to variables.
* Rare error in `test_copy_directory_cases` test due to list sorting.

### Changed
* Added module name printout to `schedule_deprecation`
* `ub.hash_data` now supports `datatime.datetime`, `datetime.date`, `decimal.Decimal` objects. 


## Version 1.3.6 - Released 2024-06-08

### Added:
* Add `ub.IndexableWalker.diff` 

### Fixed:
* Added workarounds for copy / symlinks via `ub.Path` and `ub.symlink` on pypy.
* `ub.import_module_from_path` now correctly accepts `PathLike` objects.
* `ub.modname_to_modpath` fixed in cases where editable installs use type
  annotations in their MAPPING definition.

### Added
* Support for UNIX special permission (suid/sgid/svtx) codes in `Path.chmod`.

### Changed
* Moved windows dependencies from requires to optional. Windows users that make
  use of these will need to update their ubelt install or explicitly depend on
  them as well. 

## Version 1.3.5 - Released 2024-03-20

### Added:
* New wrapper around `pathlib.Path.chmod` in `ubelt.Path.chmod`. Can now
  specify string codes like "u+x" or "+rw". Old stat logic works as it
  previously did.


### Changed:
* Allow the argument to `ubelt.cmd` to be a `PathLike` object, which we will
  expect to be an executable.

### Fixed
* `ub.modname_to_modpath` now handles cases where editable packages have modules where the name is different than the package.
* Fixed deprecated usage of `ast.Num`


## Version 1.3.4 - 2023-10-27

### Added
* Add backend option to `highlight_code` which can be "pygments" or "rich". 
* Support for Python 3.12

### Changed
* Improve speed of inplace dictionary set operations.

### Fixed
* Align in the case of `nobraces=1` for `ubelt.urepr`.


## Version 1.3.3 - 2023-07-10

### Fixed

* Bug where the first call to `ub.hash_data` would error if it was given a
  ndarray with object type.
* Actually exposed `ChDir`.

### Changed 
* Docs and typing improvements

### Notes

* Skipped a release version due to a bad github tag.


## Version 1.3.0 - 2023-06-14

### Changed
* Removed experimental warning from `Path.copy` and `Path.move`; they are now well enough tested.
* The `util_format` submodule has been renamed to `util_repr`. The
  `util_format` is now a deprecated alias for `util_repr`.
* Stub out merge methods for SetDict.
* Renamed `FormatterExtensions` to `ReprExtensions`, with the former now being a deprecated alias.
* `ubelt.cmd` now returns an object that ducktypes `subprocess.CompletedProcess`.
* `ubelt.cmd` now contains a `capture` argument which will disable capturing of output.
* `ubelt.cmd` ...detaching now only prints if verbosity is > 1

### Fixed:
* Exposed `ChDir`.
* Removed usage of deprecated `pipes` module
* `ubelt.cmd` return dictionaries are now more consistent

### Deprecated
* The `recreate` argument to `ensuredir`


## Version 1.2.4 - 2023-02-28

### Added
* Added `ChDir` to `util_path`.
* Add transient option to `JobPool` so references to futures are released after they are yielded to the user.
* Added "base32" as an option for `hash_data`. Note that it is unpadded, hence non-RFC compliant.
* Added `pattern` as a convenience option to `ubelt.Path.ls`.

### Changed
* Updated vendored ProgIter to match progiter 1.3.0
* The download progress bar now gives more relevant information and updates less frequently.
* `IndexableWalker.allclose` can now take unwrapped objects.

### Fixed
* `ubelt.cmd` now respects `cwd` when `system=True`.


## Version 1.2.3 - Released 2022-12-03  

### Added 
* Support for FreeBSD in `util_platform`
* `ub.Path.copy` and `ub.Path.move`
* Tentative Python 3.11 support
* `ub.urepr` which is `ub.repr2` with new defaults.
* `ub.IndexableWalker.allclose` method to replace `indexable_allclose`

### Changed
* `ub.schedule_deprecation` can now accept the strings "soon" or "now" for "when" arguments.
* `ub.schedule_deprecation` can now accept `stacklevel` as as an argument.
* `ub.Path.apppdir` can now be called without arguments.
* Deprecate `TempDir`
* `ub.Timer` can now accept `ns` as a keyword to enable nanosecond resolution.
* `ProgIter.format_message` return value has changed.
* `ub.Path.mkdir` now returns itself
* Speedup `dict_hist` in the basic case by 2x

### Fixed
* Issue in `indexable_allclose` where tolerances were not respected.
* Issue in `modname_to_modpath` with exclude and editable installs.
* Incompatibility with pathlib in `PythonPathContext`
* Fixed issue in progiter with line clears
* Issue in `import_module_from_modname` with editable installs where it would try to match modules that had the requested module as a prefix.
* The `timeout` argument is now respected in the thread / process case of `JobPool` 


### Deprecated
* `ub.indexable_allclose`. Use `ub.IndexableWalker.allclose` instead.


## Version 1.2.2 - Released 2022-09-05 

### Added

* Add `ubelt.util_dict.UDict.take`.
* Added `__add__`, `__radd__`, `startswith`, and `endswith` methods to `ubelt.Path` to make
  it a better drop-in replacement for string based paths.

### Changed
* Reverse dunder methods of `ubelt.SetDict` now promote the type.
* Add `cls` keyword argument to `ubelt.SetDict` methods.
* Deprecate: `ensure_app_cache_dir`, `ensure_app_config_dir`, `ensure_app_data_dir`,
  `get_app_cache_dir`, `get_app_config_dir`, `get_app_data_dir`, `readfrom`, `writeto`, `ensure_unicode`.
* Initial work on new Path methods for move and copy.
* CacheStamp.renew now does nothing and returns None if the stamp is disabled.
* AutoDict, SetDict, and UDict are now always ordered. In Python 3.6 it inherits from OrderedDict. Otherwise it uses regular dict, which will be ordered in 3.7+
* AutoDict now inherits from UDict.
* PathLike objects can now be used in args to ub.cmd when the command is an iterable.


### Deprecated
* deprecate AutoOrderedDict, which is now indistinguishable from AutoDict


### Fixed
* Tentative fixes for new `__editable__` based install path with `ub.modname_to_modpath`

## Version 1.2.1 - Released 2022-08-06

### Fixed
* Implemented inplace and reverse versions of dictionary set operations
* Added copy to setdict

## Version 1.2.0 - Released 2022-08-02

### Added
* Added keywords argument to `ub.compatible`.
* Added `warncls` argument to `ub.schedule_deprecation`.
* Experimental SetDict, UDict and aliases sdict, udict.

### Fixed
* Race condition on win32 in `ubelt.symlink`
* Issue with `ubelt.memoize_method` where the method name and docstring were
  not wrapped correctly.
* The `timeout` argument now works correctly with `ub.cmd` when `tee=True`.
* Added `appname` to `ubelt.download` which was supposed to exist as indicated
  by the docs, but didn't.
* The resources used by `ubelt.cmd` are now properly closed.

### Changed
* `ub.compatible` no longer errors on positional only functions, instead it
  returns the keyword-compatible arguments.
* An issue in `ubelt.symlink` with unintuitive behavior when an empty string
  was given as the link path. This now raises an error.
* The main implementations of `ubelt.sorted_vals` and `ubelt.map_vals` were
  renamed to `ubelt.sorted_values` and `ubelt.map_values`, but the old names
  are still available as aliases.
* Positional arguments in `Path.augment` have been modified. 
* In `Path.augment`, deprecate overloaded `suffix` and introduce `stemsuffix`
  as an alternative.
* Added cls to a lot of util_dict funcs


## Version 1.1.2 - Released 2022-06-30

### Added
* Added new module `util_deprecate` with the function `schedule_deprecation`,
  which is generally useful for library maintenance.

### Fixed
* Fixed issue where ubelt Cacher triggered its own warnings
* Fixed deprecated usage of LooseVersion

### Changed
* Tentative deprecation or backwards incompatible change in ub.Path.augment with suffix or prefix keywords


## Version 1.1.1 - Released 2022-06-09

### Changed
* Removed warning from `ubelt.Cacher` when depends is not specified.
* `ub.timestamp` / `ub.timeparse` now respects a `default_timezone` argument and handles `datetime.date` objects.
* Type stubs are now included in the distribution

### Fixed
* Issue #113, where a `ub.find_exe` test failed on Gentoo. Fixed by #114
* Issue where older versions of CacheStamp would be interpreted as 1.1 stamps.

## Version 1.1.0 - Released 2022-06-03

### Added
* New method: `ub.timeparse` can parse the result of `ub.timestamp` into a
  `datetime` object. Can optionally use `dateutil.parser.parse` under the hood.
* `ub.Path.ls` a convenience function that aliases `list(path.iterdir())`.
* `ub.Path.walk` to wrap `os.walk`. 

### Changed
* Register `pathlib.Path` with `ub.repr2`
* Can now register global `ub.repr2` extensions via `ub.repr2.register`
* Can now register global `ub.hash_data` extensions via `ub.hash_data.register`
* Removed deprecated arguments from `ubelt.cmd`.
* `ub.CacheStamp` will now check the mtime and size to quickly check if the products
  have changed and force expiration.
* `ub.CacheStamp` now takes an `expires` keyword arg, which will keep the cache valid 
  only for the specified amount of time.
* `ub.CacheStamp` now takes an `hash_prefix` keyword arg, which will check that it
  matches the hash of the product.
* `ub.cmd` now has a `system` argument for modularity with `os.system`.
* `ub.cmd` now accepts a `timeout` argument (tee support is pending).
* `ub.JobPool` now contains a protected `_prog` variable allowing the user
  finer-grained progress controls.
* `ub.JobPool` now contains a convenience method `join` that executes all jobs
  and returns a list of results.
* `ub.timestamp` can now accept a `datetime` object as an argument, and will return 
   the timestamp for that object.
* The `ubelt.util_download.grabdata` function now uses `CacheStamp` instead of
  implementing its own stamp solution.
* The `ubelt.util_hash.HashableExtensions` implementation was updated to use
  `functools.singledispatch` instead of the custom solution. This seems faster
  and should not have any API impact.

### Deprecated
* `product` and `cfgstr` arguments to `CacheStamp.expired`
* `product` and `cfgstr` arguments to `CacheStamp.renew`
* Passing `hasher` as an instance to functions like `grabdata` or `CacheStamp`
  can cause unexpected hashes as they may be used more than once.

### Fixed
* `ub.hash_data` now recognizes subclasses of registered types.
* `ub.timestamp()` has been outputting incorrect (negated) UTC offsets. This is now fixed.
* `ub.timestamp()` now works correctly when the year has less than 4 digits.


## Version 1.0.1 - Released 2022-02-20

### Fixed

* Bug where six was used but not listed as a dependency. Six is now removed as a dependency.
* Fixed out of date docs in some places.


## Version 1.0.0 - Released 2022-02-15

### Added

* :func:`ubelt.Path.appdir` which functions like the `get_app_*_dir` methods in `util_platform`.
* Add `tail` argument to :func:`ubelt.Path.augment` and  :func:`ubelt.util_path.augpath`
* Add json `backend` option to Cacher.

### Changed
* `IndexableWalker` behavior has been changed, each time `iter` is called it
  resets its global state. 
* Remove support for Python 2.7 and Python 3.5
* Removed deprecated functions scheduled for removal.
* :func:`ubelt.util_dict.dict_diff` now preserves original dictionary order in Python 3.7+.
* `ub.hash_data` can now hash slice objects.
* INTENTION OF BREAKING CHANGE NOTIFICATION: `ubelt.util_format.repr2` may no longer sort
  dictionaries by default. Looking into a backwards compatible way to work around this.


## Version 0.11.1 - Released 2022-02-15

### Added
* More `ubelt.Path` extensions for `delete` 
* Add `timeout` parameter to `ubelt.download`

### Changed
* Modified default `ubelt.Path` behavior for `touch` to return a self-reference for chaining

## Version 0.11.0 - Released 2022-01-03

### Added
* Added `ubelt.Path`, as an extension and quicker-to-type version of pathlib.Path with extra functionality.
* Added `progkw` as argument to `JobPool.as_completed` to control progress reporting
* Added `progkw` as argument to `ub.download` / `ub.grabdat` to control progress reporting
* Added `util_zip` with the `zopen` function. Access a file inside a zipfile with a standard `open` like interface. 


### Fixed
* `ubelt.hash_data` now handles non-numeric float values.
* `ubelt.chunks` now works correctly when nchunks is specified.

### Changed

* Changed default of `_hashable_sequence` `types` arg from True to False to be
  consistent, but kept existing types=True behavior in hashable extensions. Changes
  should be backwards compatible, but in the future we may introduce a breaking
  change to make hash behavior more consistent.


## Version 0.10.2 - Released 2021-12-07

### Added
* Added pyi type annotation files. (Used a custom script to export docstring type annotations)
* Added `default` keyword argument to signature of `ub.peek`

### Fixed
* Added `map` function to the executor classes.
* `ub.Executor` now correctly returns itself from `__enter__`
* Docstrings now have better type annotations
* ProgIter had a bug in `time_thresh`, where it was never used (modified adjustment rules).
* Fixed performance regression in ProgIter

### Changed
* New CI GPG Keys: Erotemic-CI: 70858F4D01314BF21427676F3D568E6559A34380 for
  reference the old signing key was 98007794ED130347559354B1109AC852D297D757.
* Verbose test from symlink previously showed "real -> link" which makes no
  sense because a link should be the object that "is pointing". Thus it now
  shows "link -> real"
* `ub.download` should now generate less stdout text
* New in-repo "dev" benchmarks

## Version 0.10.1 - Released 2021-08-23

### Changed
* Documentation fixes

## Version 0.10.0 - Released 2021-08-22

### Added
* new hashing 36-character base with alias (alphanum / abc123 / 36)
* Added "compact" argument to `ub.repr2`
* added candidate utilities: `named_product`,  `varied_values` to `util_dict`
* added candidate utilities: `compatible` to  `util_func`
* Added `util_indexable` and `IndexableWalker` (ported from kwcoco)
* Added `util_futures` with `ub.JobPool` and `ub.Executor` (ported from kwcoco)
* Added `util_download_manager` with simple implementation of `ub.DownloadManager`
* Added candidate functions to `ubelt` proper

### Fixed
* `ubelt.download` now errors earlier if the parent directory does not exist
* PyTest no longer throws warnings
* Fixed issue with `download` and ByteIO objects in 3.8
* Bug in Python 3.8+ on win32 that did not account for the change on
  `os.readlink` behavior


### Changed 

* Modified corner cases in `ub.repr2` to move towards behavior that is easier
  to reason about.

* Remove support for Python 3.4


## Version 0.9.5 - Released 2021-02-05


### Added 

* `blake3` is now an optional hasher

### Changed 

* `ubelt.hash_data` can now hash dictionaries and sets by default.

* increased test speed

* Internal change in how external hashers are maintained. 


### Fixes 

* On windows colorama init is no longer called if it was ever initialized
  before. This fixes rare infinite recursion bugs when using pytest.
 

## Version 0.9.4 - Released 2021-01-15


### Added

* Added `maxbytes` parameter to `hash_file` to allow for only hashing a prefix.

### Fixed

* Docs seem to be building correctly now


### Changed

* Made import time 13x faster (was 109680, is now 8120) by using lazy
  external type registration in `util_hash` and removing other eager imports.

* Removed import dependency on six. There is still a runtime dependency, but we
  are moving away from six. This is a first step to deprecating Python2 support

* Changed default of "blocksize" in `hash_file` to `2 ** 20` based on benchmarks.

* Removing Travis-CI, will soon migrate to Circle-CI


## Version 0.9.3 - Released 2020-10-24

### Added
* Added `meta` and `depends` to `CacheStamp` to agree with `Cacher`
* `ProgIter.step` can now accept the `force` keyword argument to force display
* `ProgIter.step` returns True if the display was written

### Fixed
* Bug in `dict_isect` where order was not taken into account
* Bug in `ProgIter` display frequency adjustment 

### Changed
* Tweaked display frequency adjustment in `ProgIter`
* `ProgIter` no longer displays wall time by default. Set `show_wall=True` to
  regain this functionality. When true this now shows the date and time.

## [Version 0.9.2] - 2020-08-26

### Added
* `ub.repr2` now accept type name strings at register time (which makes it
  easier to lazy-load heavy libraries)
* `ub.repr2` now handles pandas.DataFrame objects by default
* `ub.repr2` now accepts the `align` keyword arg, which will align dictionary kv separators.
* functions in `ub.util_color` now respects a global `NO_COLOR` flag which
  prevents ANSI coloration. 

### Changed
* `ProgIter.step` now respects update freq, and will not update the estimates
  if too few iterations have passed. This prevents `ub.download` from
  generating extremely large amounts of standard out. 
* `ub.Cacher` now reports the file size of the cache file.
* `ub.Cacher` now defaults to the latest pickle protocol (-1), which may cause
  compatibility issues.

### Fixed
* `ProgIter` now correctly checks if it needs to displays a message on every iteration.
* Fixed uninitialized `_cursor_at_newline ` variable in `ProgIter`.


## [Version 0.9.1] - 2020-03-30

### Changed
* `ub.repr2` now encodes inf and nan as `float('inf')` and `float('nan')` to
  allow output to be evaluated.
* `ub.grab_data` now uses the hasher name in the cached hash stamp file.


## [Version 0.9.0] - 2020-02-22

### Fixed
* Fixed issue in setup.py that broke the previous release.

## [Version 0.8.9] - 2020-02-20

NOTE: THIS RELEASE WAS BROKEN DUE TO AN ISSUE WITH THE SETUP SCRIPT

### Added
* `dpath` and `fname` keywords to the `ub.download` function.
* `modname_to_modpath` can now find modules referenced by egg-link files.
* `ub.sorted_keys` and `ub.sorted_vals` for sorting dictionaries


### Fixed
* `ub.download` now accepts `sha256` and `md5` hashes.

### Changed
* The argument names in `ub.group_items`, `groupids` was changed to `key`.
* The argument names in `ub.dict_hist`. `item_list` was changed to `items`, 
  `weight_list` was changed to `weights`.
* The argument names in `ub.flatten`. `nested_list` was changed to `nested`


## [Version 0.8.8] - 2020-01-12

### Added
* Added `check` kwarg to `ub.cmd`, which when True will raise a
  `CalledProcessError` if the exit-code is non-zero.
* Added support for pypy.

### Changed
* Moved `timerit` to its own module.

## [Version 0.8.7] - 2019-12-06

### Fixed
* Fixed corner case where `util_hash` raised an import error when python was
  not compiled with OpenSSL.

## [Version 0.8.6] - 2019-12-05

### Fixed
* Removed the `NoParam.__call__` method. This method should not have been
  defined, and by existing it caused issues when using `NoParam` as a
  column-key in pandas.


## [Version 0.8.5] - 2019-11-26

### Added
* Timerit now has 3 new properties `measures`, `rankings`, and `consistency`.
  These keep track of and analyze differences in timings between labeled
  timerit runs.
* `ub.take` now accepts `default=NoParam` keyword argument. 


### Changed
* Substantially improved documentation.
* The following functions are now officially deprecated:  `dict_take`


## [Version 0.8.4] - 2019-11-20

### Changed
* The following functions are now officially deprecated: `startfile`, `truepath`, `compressuser`, `editfile`, `platform_resource_dir`, `get_app_resource_dir`, and `ensure_app_resource_dir`, `dict_take`
* Improve docs
* `Timerit` and `ProgIter` are back, remove dependency on the external modules.


## [Version 0.8.3] - 2019-11-06

### Changed
* `PythonPathContext` now works in more corner cases, although some rarer
  corner cases will now break. This trade-off should be a net positive. 


## [Version 0.8.2] - 2019-07-11

### Added
* Added `dpath` as an argument to `ub.augpath`

### Fixed
* Custom extensions for `ub.hash_data` are fixed. Previously they were not passed down more than a single level.
* The `convert` option for `ub.hash_data` was previously not hooked up.
* Correctly expose `dict_diff`
* Fixed issue in `ub.augpath` where `multidot` did not preserve the original extension

### Changed
* `ub.Cacher` no longer ensures that the `dpath` exists on construction. This check is delayed until `save` is called.
* `ub.CacheStamp` now accepts the `enabled` keyword. 
* `modpath_to_modname` now properly handles compiled modules with ABI tags.


## [Version 0.8.0] - 2019-05-12

### Added
* Add `ub.dict_diff`, which removes keys from a dictionary similar to `set` difference.
* Add `ub.paragraph`, which helps with writing log messages
* Add some benchmarks
* Add lots more documentation.


### Changed
* `ub.identity` now accepts `*args` and `**kwargs` and defaults the first argument to `None`, but still only returns the first argument.
* The `sort` kwarg of `ub.repr2` can now accept a callable, which will act as a key to the `sorted` function
* `ub.hash_data` now accepts the `extensions` kwarg, which allows the user to define how particular types are hashed. 

### Fixed
* Fix GH #53
* the `index` argument in `import_module_from_path` is now correctly used.


## [Version 0.7.1] - 2019-03-19

### Fixed

* Fixed bug in `ub.dict_hist` when `ordered=True`. (half of the keys would be lost). Also effected `dict_take`.
* `platform_data_dir` now correctly raises an exception when the operating system is unknown. 


## [Version 0.7.0] - 2019-03-12

### Added
* Add `memoize_property`

### Changed
* `ub.cmd` now reports `cwd` on exception
* Reworked requirements to minimize dependencies. 
* The `xxhash` and `pygments` dependencies are now optional.
* The testing dependencies are now optional.


## [Version 0.6.3] - ???

### Added
* new tests
* add `util_stream`

### Fixed
* Fixed issue in `ub.download` with bad content header urls


## [Version 0.6.2] - 2019-02-14

### Added
* `ub.platform_cache_dir` and `ub.platform_config_dir` now respect XDG environs on Linux systems.

### Changed
* `ub.download` can now accept `fpath` as either a file path or a `io.BytesIO` object 
* `ub.FormatterExtensions.register` can now accept a type or tuple of types.

### Deprecated
* `ub.platform_resource_dir` is deprecated in favor of `ub.platform_config_dir`.


## [Version 0.6.1] - 2019-01-08

### Changed
* `ub.repr2` now accepts negative values for `newlines`, which means use newlines until the current height is only `-newline`.
* `ub.repr2` now keeps track of nesting depth from the bottom
* Make result `ub.memoize_method` appear more like a bound method.


### Added
* Add custom extensions to `ub.repr2` and expose `ub.FormatterExtensions`
* Add `dict_isect` to `util_dict`.


### Fixed
* Fixed misspelling in docs 
* Fixed misspelled detach kwarg in `ub.cmd` (the old `detatch` argument is now deprecated and will be removed)


## [Version 0.6.0] - 2018-11-10

### Added
* Add class variable `FORCE_DISABLE` to `ub.Cacher`
* Add the `xxhash` algorithm as an option to `ub.hash_data`
* Add `ub.peek` - 4-letter syntactic sugar for `lambda x: next(iter(x))`


## [Version 0.5.3] - 2018-10-24

### Added 
* Add `key` to `ub.find_duplicates`

### Changed
* Renamed first argument of `ub.chunks` from sequence to items
* Improved type hints in google-style docstrings 
* `ub.cmd` verbose >= 3 now uses nicer Unicode characters if possible

### Fixed
* Fixed GH#41


## [Version 0.5.2] - 2018-09-04

### Added
* Add verbose flag to `ub.CacheStamp`

### Changed
* `ub.group_items` argument names have changed, and it can now take a callable as the second argument. The `sorted_` argument is now deprecated.
* Symlink now reports location of old target when the new target does not match
* Docstrings now uses `PathLike` as the type for arguments and attributes that should be considered paths (note strings are still accepted).
* `ub.download` will now keep a potentially corrupted file if the hash does not match.
* `ub.grabdata` will compute the hash of an existing file on disk if the .hash stamp is missing to try and avoid re-downloading the file.
* Improved efficiency of `ub.argmax`


## [Version 0.5.0] - 2018-07-23

### Added
* added `ub.expandpath` 

### Changed
* Certain imports are now lazy to optimize startup time
* change `ub.cmd` `tee` parameter to `tee_backend` (BREAKING CHANGE)
* change `ub.cmd` `verbout` parameter to `tee` (BREAKING CHANGE)
* `import_module_from_path` can now handle zip-imports where the zip-file is followed by a slash rather than a colon

### Removed
* `tee` parameter from `ub.cmd` to `tee_backend` 
* `verbout` from `ub.cmd`


## [Version 0.4.0] - 2018-07-12

### Added
* `ub.find_exe` - a python implementation of which 
* `ub.find_path` - finds matching files in your PATH variables
* `ub.CacheStamp`

### Modified
* Replace in-house implementation of `OrderedSet` with the ordered-set PyPI package.
* `ub.download` now accepts `hash_prefix` and `hasher` args. 
* `ub.hash_file` now accepts `types` args
* `ub.augpath` now accepts `multidot` args
* `ub.cmd` now accepts `cwd` and `env` args
* Changing default behavior of `util_hash`. (BREAKING CHANGE)
    - Default of `ub.Cacher` `maxlen` changed to 40 for sha1 considerations 
    - Default of `ub.hash_data` `base` changed from `abc` to `hex` 
    - Default of `ub.hash_data` `types` changed from True to False.
    - Moved argument position of `hashlen` to the end. 

### Removed
* Remove `ub.OrderedSet`.extend

### Fixed
* `ub.NoParam` is now Falsey


## [Version 0.3.0] - 2019-07-12

### Changed
* `ub.import_module_from_path` can now import modules within zip-files

### Removed
* `ub.PY2` and `ub.PY3`. Use `six` instead.


## [Version 0.2.1] - 2018-05-27

### Modified
* `ub.dzip` now accepts a backend dict class as a keyword argument
* `OrderedSet.intersection` can now handle a single argument
* `Timerit` `num` now defaults to 1 
* Add function `print` to Timerit


## [Version 0.2.0] - 2018-05-05

* Fix timezone issue with negative time-zones
* Move internal `__init__` auto-generation logic to new `mkinit` repo
* Network tests no longer run by default and require `--network`


## [Version 0.1.1] - 2018-04-20

* Add `ub.argmin` and `ub.argmax`
* `ub.Cacher` can now be used as a decorator.
* Rename `util_decor.py` to `util_memoize.py`
* Add `key` argument to `ub.unique` and `ub.unique_flags`
* Add `ub.argunique`
* `import_module_from_path` now prefers the path module when there are name conflicts
* Fix `ub.repr2` precision with numpy scalars 
* Add `ub.dzip`


## [Version 0.1.0] - 2018-04-02

### Added
* Add `inject_method` to `util_func.py`.
* Add `allsame`

### Modified
* simplified dynamic imports
* `memoize_method` now handles kwargs
* Can now update `ProgIter` description on the fly
* Add methods to `OrderedSet` to complete the set API (e.g. `intersection`, `difference`, etc...)
* Can now index into an `OrderedSet` using a slice
* Add `appname` keyword argument to `grabdata`
* Add `extend` to ordered set API
* Increase `tqdm` compatibility with `ProgIter`

### Fixed
* Fixed issue with `OrderedSet.union` where it ignored `self`
* Fixed issue with `OrderedSet.union` where `__eq__` and `isdisjoint` were wrong
* Fix issue with `ub.repr2` dictionaries with newlines in keys
* Fix issue with relative paths and symlink


## [Version 0.0.44] - 2018-03-12

### Added
* `ub.iter_window`


## [Version 0.0.43] - 2018-03-09

### Modified
* Spelling: changed the `Timer.ellapsed` attribute to `Timer.elapsed`.
* Verbosity of `Timer` and `Timerit` now depends on if a label was specified. 
* `Timer.tic` now returns a reference to the `Timer` instance.

### Removed
* Remove `util_stress`, it was out of scope. 


## [Version 0.0.42] - 2018-02-26

## Modified
* `hash_data` can now accept `OrderedDict` input
* `dict_union` now returns `OrderedDict` if the first argument is one

### Fixed
* bug in `hash_data` where negative integers did not work.


## [Version 0.0.41] - ???

### Added
* `OrderedSet` / `oset`
* Add `symlink` function that works on UNIX and Windows*.  (*if use has symlink permissions, it works just like UNIX without caveats.  Otherwise `ub.symlink` falls back to using junctions and hard links, which should still work mostly the same, except `os.path.islink` and `os.readlink` will not work among other minor issues).

### Modified
* Add base to `augpath`
* `ub.delete` now treats nested junctions as symlinks, unlike `shutil.rmtree`.


## [Version 0.0.40] - 2018-02-04

### Modified
* Add `numpy` support to `ub.repr2`


## [Version 0.0.39] - 2018-01-18

### Modified
* Changed `ub.Timerit`.call API to return a reference to the Timerit object instead of of the average seconds. Note this change is backwards incompatible.


## [Version 0.0.38] - ???

### Added

* `ub.hash_data` and `ub.hash_file` for easy hashing of arbitrary structured data and file.
* `ub.dict_union` combines multiple dictionaries and returns the result.

### Modified

* `ub.Timerit` reports better measures of expected time.
* New argument `total` to `ub.chunks` lets you specify how long an iterable is if `len` is not available (for generators)


## [Version 0.0.37] - ???

### Added

* Add `ub.TempDir`
* Add `ub.import_module_from_path`
* Add `ub.import_module_from_name`

### Modified

* can now choose `ub.cmd` tee backend (select or thread) on POSIX. 
* `ProgIter` now supports a more `tqdm`-like API
* Add standard deviation to `timerit`
* Minor enhancements to `ub.Cacher`

### Fixed

* fixed unused argument `chunksize` in `util_download`
* `ub.cmd` tests now work on windows
* terminal colors now work on windows

### Deprecated
* Remove most of the `static_analysis` module. Use code in xdoctest for now. Note: some of this functionality may return as general utilities in the future, but the existing constructs were only needed for doctests, which are now done via xdoctest.


## [Version 0.0.34] - 2017-11-11

### Added

- `ub.truepath`
- `ub.iterable`
- `util_func.py` with `ub.identity`
- `util_download.py` with `ub.download` and `ub.grabdata`


### Changed

- The`__init__` imports are now statically generated, this fixes the random third party attributes (e.g. `expanduser`, `Thread`) that were exposed in the `__init__` file.
- `ProgIter` now uses scientific notation when it is small
- `ub.AutoOrderedDict` now inherits from `ub.AutoDict`
- tests are now running using `pytest` and `xdoctest`
- `ub.cmd` now uses thread based logging 

### Fixed

- Fixed many failing tests on windows
- Small bug and documentation fixes.

### Issues
- `ub.cmd` does not work correctly on windows
- some Unicode formatting does not work correctly on windows


## [Version 0.0.33] - 2017-09-13

### Added
- `ub.repr2` and `ub.hzcat`
- `ub.color_text`


## [Version 0.0.31] - 2017-09-04

### Added
- Add `ub.argflag` and `ub.argval`


## [Version 0.0.28] - 2017-07-05

### Added
- `ub.AutoDict` and `ub.AutoOrderedDict`.
- Many undocumented changed
- Starting a changelog

## [Version 0.0.1] - 2017-02-01

### Added
- First release of ubelt
- Changed from and before this time are undocumented
## Version 0.9.3 - Released 2020-10-24


