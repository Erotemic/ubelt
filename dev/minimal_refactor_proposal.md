Draft: Proposal to Refactor Ubelt to as an Un-Standard Library
==============================================================

This may will have to be resolved the existing but dormant unstdlib project.

I've found ubelt to be one of the most important pieces of software I've
developed over the past decade. The fact that it contains everything
in a single place is great for me, but for new people it can 

1. prove daunting 
2. provide too many things they don't need


It would be nice if things were separated out into separate pip installable
modules. This has been done to some degree with progiter and timerit.


But this also has a negative impact on ubelt itself, because now it has a
choice either vendor in those libraries, or depend on them. Originally we added
them as dependencies, but eventually settled on vendoring to reduce our
apparent dependency footprint and because of issues with cross-domain
documentation (which should be solved via intersphinx).


However, this first problem is mitigated if all of the packages are available
as standalone modules, because then the user can just depend on what they
actually use, but it becomes difficult to interoperate with normal ubelt (all
of these std functions are top-level by default) paradigms.


We seek the best of both worlds. Consider if ubelt was broken into subpackages:

What would the name of the stand alone packages be?

Some packages might get standalone love: progiter, thats about it. But misc
ones could be prefixed with ub or something.

Given this splitup, the ubelt package would point at each member and depend on
it.  It would expose it as normal.


Lets try and take a subset of ubelt and map them to packages.


progiter
    ubelt.ProgIter

ubhash
    - `ub.hash_data`
    - `ub.hash_file`

ubpathlib
    - ub.Path

ubcmd
    - ub.cmd

ubcache
    - Cacher, CacheStamp, memoize, 
    memoize_property - can this be folded into memoize?
    memoize_method

ubdownload
    - grabdata, download 

ubdict

ubfutures

    JobPool
    Executor

ubimport

    modname_to_modpath
    import_module_from_name
    import_module_from_path

ubiter ? ubseq ? ublist ?

ubbase?

ubdevelop ? ubdev ?  ubdesign ? ubmaintain ? ubwarn

schedule_deprecation


identity? 
flatten
chunks
group_items
take
compress
peek
allsame
iterable
unique
named_product
iter_window
find_duplicates
varied_values 
argmax
argmin
argsort
argunique
boolmask?
unique_flags?


dzip

oset


ubtext

    codeblock
    paragraph
    hzcat
    hzcat

CaptureStdout ?
CaptureStream ?

IndexableWalker
indexable_allclose

do NiceRepr, NoParam, 


ubtime:

    timestamp
    Timer
    timeparse


### Cut

argflag
argval
delete
repr2 ? This might be a good function, but it really needs a new name.

expandpath
ensuredir
map_vals
dict_isect
dict_diff

odict
ddict - This might still be useful

color_text


symlink - rename and put in Path?

find_exe - maybe? Or just add which to path?
highlight_code


compatible
inject_method
zopen
