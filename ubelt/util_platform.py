# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from os.path import normpath, expanduser, join, exists
import os
import sys

PY2 = sys.version_info.major == 2
PY3 = sys.version_info.major == 3

WIN32  = sys.platform.startswith('win32')
LINUX  = sys.platform.startswith('linux')
DARWIN = sys.platform.startswith('darwin')


def platform_resource_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for persistent configuration files.
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Roaming'
    elif LINUX:  # nocover
        dpath_ = '~/.config'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Application Support'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def platform_cache_dir():
    """
    Returns a directory which should be writable for any application
    This should be used for temporary deletable data.
    """
    if WIN32:  # nocover
        dpath_ = '~/AppData/Local'
    elif LINUX:  # nocover
        dpath_ = '~/.cache'
    elif DARWIN:  # nocover
        dpath_  = '~/Library/Caches'
    else:  # nocover
        raise NotImplementedError('Unknown Platform  %r' % (sys.platform,))
    dpath = normpath(expanduser(dpath_))
    return dpath


def get_app_resource_dir(appname, *args):
    r"""
    Returns a writable directory for an application
    This should be used for persistent configuration files.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory
    """
    dpath = join(platform_resource_dir(), appname, *args)
    return dpath


def ensure_app_resource_dir(appname, *args):
    """
    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_resource_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def get_app_cache_dir(appname, *args):
    r"""
    Returns a writable directory for an application.
    This should be used for temporary deletable data.

    Args:
        appname (str): the name of the application
        *args: any other subdirectories may be specified

    Returns:
        str: dpath: writable cache directory
    """
    dpath = join(platform_cache_dir(), appname, *args)
    return dpath


def ensure_app_cache_dir(appname, *args):
    """
    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_cache_dir('ubelt')
        >>> assert exists(dpath)
    """
    dpath = get_app_cache_dir(appname, *args)
    ensuredir(dpath)
    return dpath


def ensuredir(dpath, mode=0o1777, verbose=None):
    r"""
    Ensures that directory will exist. creates new dir with sticky bits by
    default

    Args:
        dpath (str): dir to ensure. Can also be a tuple to send to join
        mode (int): octal mode of directory (default 0o1777)
        verbose (int): verbosity (default 0)

    Returns:
        str: path - the ensured directory

    Example:
        >>> from ubelt.util_platform import *  # NOQA
        >>> import ubelt as ub
        >>> cache_dpath = ub.ensure_app_cache_dir('ubelt')
        >>> dpath = join(cache_dpath, 'ensuredir')
        >>> if exists(dpath):
        >>>     os.rmdir(dpath)
        >>> assert not exists(dpath)
        >>> ub.ensuredir(dpath)
        >>> assert exists(dpath)
        >>> os.rmdir(dpath)
    """
    if verbose is None:  # nocover
        verbose = 0
    if isinstance(dpath, (list, tuple)):  # nocover
        dpath = join(*dpath)
    if not exists(dpath):
        if verbose:  # nocover
            print('[ubelt] mkdir(%r)' % dpath)
        try:
            os.makedirs(normpath(dpath), mode=mode)
        except OSError as ex:  # nocover
            print('Error in ensuredir')
            raise
    return dpath


def _run_process(proc):
    while True:
        # returns None while subprocess is running
        retcode = proc.poll()
        line = proc.stdout.readline()
        yield line
        if retcode is not None:
            # The program has a return code, so its done executing.
            # Grab any remaining data in stdout
            for line in proc.stdout.readlines():
                yield line
            raise StopIteration('process finished')


def cmd(command, shell=False, detatch=False, verbose=False, verbout=None):
    r"""
    Trying to clean up cmd

    Args:
        command (str): string command
        shell (bool): if True, process is run in shell
        detatch (bool): if True, process is run in background
        verbose (int): verbosity mode
        verbout (bool): if True, `command` writes to stdout in realtime.
            defaults to True iff verbose > 0

    Returns:
        dict: info - information about command status

    CommandLine:
        python -m ubelt.util_platform cmd
        python -m ubelt.util_platform cmd:0

    Example:
        >>> import ubelt as ub
        >>> info = ub.cmd('echo hello world')
        >>> assert info['out'].strip() == 'hello world'
        >>> #info = ub.cmd(['echo' 'hello world'])
        >>> #assert info['out'].strip() == 'hello world'
        >>> print('info = {!r}'.format(info))

    # Example1:
    #     >>> import ubelt as ub
    #     >>> varydict = {
    #     >>>    'shell': [True, False],
    #     >>>    'detatch': [False],
    #     >>>    'sudo': [True, False] if ub.get_argflag('--test-sudo') else [False],
    #     >>>    'args': ['echo hello world', ('echo', 'hello world')],
    #     >>> }
    #     >>> for count, kw in enumerate(ub.all_dict_combinations(varydict), start=1):
    #     >>>     print('+ --- TEST CMD %d ---' % (count,))
    #     >>>     print('testing cmd with params ' + ub.dict_str(kw))
    #     >>>     args = kw.pop('args')
    #     >>>     restup = ub.cmd(args, pad_stdout=False, **kw)
    #     >>>     tupfields = ('out', 'err', 'ret')
    #     >>>     output = str(list(zip(tupfields, restup)), nobraces=True)
    #     >>>     print('L ___ TEST CMD %d ___\n' % (count,))

    # Example2:
    #     >>> # ping is not as universal of a command as I thought
    #     >>> from ubelt.util_cplat import *  # NOQA
    #     >>> import ubelt as ub
    #     >>> varydict = {
    #     >>>    'shell': [True, False],
    #     >>>    'detatch': [True],
    #     >>>    'args': ['ping localhost', ('ping', 'localhost')],
    #     >>> }
    #     >>> proc_list = []
    #     >>> for count, kw in enumerate(ub.all_dict_combinations(varydict), start=1):
    #     >>>     print('+ --- TEST CMD %d ---' % (count,))
    #     >>>     print('testing cmd with params ' + ub.dict_str(kw))
    #     >>>     args = kw.pop('args')
    #     >>>     restup = ub.cmd(args, pad_stdout=False, **kw)
    #     >>>     out, err, proc = restup
    #     >>>     proc_list.append(proc)
    #     >>>     print(proc)
    #     >>>     print(proc)
    #     >>>     print(proc.poll())
    #     >>>     print('L ___ TEST CMD %d ___\n' % (count,))
    """
    import shlex
    if isinstance(command, (list, tuple)):
        raise ValueError('command tuple not supported yet')
    args = shlex.split(command, posix=not WIN32)
    if verbose is True:
        verbose = 2
    if verbout is None:
        verbout = verbose >= 1
    if verbose >= 2:
        print('+=== START CMD ===')
        print('Command:')
        print(command)
        if verbout:
            print('----')
            print('Stdout:')
    import subprocess
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=shell,
                            universal_newlines=True)
    if detatch:
        info = {'proc': proc}
    else:
        write_fn = sys.stdout.write
        flush_fn = sys.stdout.flush
        logged_out = []
        for line in _run_process(proc):
            #line_ = line if six.PY2 else line.decode('utf-8')
            line_ = line if PY2 else line
            if len(line_) > 0:
                if verbout:
                    write_fn(line_)
                    flush_fn()
                logged_out.append(line)
        try:
            out = ''.join(logged_out)
        except UnicodeDecodeError:
            # from utool import util_str  # NOQA
            # logged_out = util_str.ensure_unicode_strlist(logged_out)
            # out = ''.join(logged_out)
            out = '\n'.join(_.decode('utf-8') for _ in logged_out)
            # raise
        (out_, err) = proc.communicate()
        ret = proc.wait()
        info = {
            'out': out,
            'err': err,
            'ret': ret,
        }
    if verbose >= 2:
        print('L___ END CMD ___')
    return info


def startfile(fpath, detatch=True, quote=False, verbose=False, quiet=True):
    """
    Uses default program defined by the system to open a file.

    References:
        http://stackoverflow.com/questions/2692873/quote-posix-shell-special-characters-in-python-output

    """
    import pipes
    if verbose:
        print('[ubelt] startfile(%r)' % fpath)
    fpath = normpath(fpath)
    # print('[cplat] fpath=%s' % fpath)
    if not exists(fpath):
        raise Exception('Cannot start nonexistant file: %r' % fpath)
    #if quote:
    #    fpath = '"%s"' % (fpath,)
    if not WIN32:
        fpath = pipes.quote(fpath)
    if LINUX:
        outtup = cmd(('xdg-open', fpath), detatch=detatch, verbose=verbose, quiet=quiet)
    elif DARWIN:
        outtup = cmd(('open', fpath), detatch=detatch, verbose=verbose, quiet=quiet)
    elif WIN32:
        os.startfile(fpath)
    else:
        raise RuntimeError('Unknown Platform')
    if outtup is not None:
        out, err, ret = outtup
        if not ret:
            raise Exception(out + ' -- ' + err)


if __name__ == '__main__':
    r"""
    CommandLine:
        python -m ubelt.util_platform
        python -m ubelt.util_platform all
    """
    import ubelt as ub  # NOQA
    ub.doctest_package()
