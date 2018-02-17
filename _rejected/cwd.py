def chdir(path):
    """
    Thin wrapper around `os.chdir` that tracks the current working directory
    using the `PWD` environment variable without resolving symbolic links.
    Used in conjunction with `ub.getcwd`.

    Args:
        path (str): new path. Can also be '-' to specify the previous
            directory.

    CommandLine:
        python -m ubelt.util_path chdir

    Example:
        >>> import ubelt as ub
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> ub.chdir(dpath)
        >>> cwd1 = ub.getcwd()
        >>> ub.chdir('..')
        >>> cwd2 = ub.getcwd()
        >>> ub.chdir('-')
        >>> cwd3 = ub.getcwd()
        >>> assert cwd1 == cwd3

    Example:
        >>> import ubelt as ub
        >>> import os
        >>> os.environ.pop('OLDPWD', None)
        >>> import pytest
        >>> with pytest.raises(KeyError):
        >>>     ub.chdir('-')
    """
    if path == '-':
        path = os.environ['OLDPWD']
    path_ = abspath(normpath(path))
    os.chdir(path_)
    if 'PWD' in os.environ:
        os.environ['OLDPWD'] = os.environ['PWD']
    os.environ['PWD'] = path_


def getcwd(physical=False):
    """
    Workaround to get the working directory without dereferencing symlinks.
    This will not work on all systems or if `os.chdir` was used. However,
    `ub.chdir` can be used instead.

    References:
        https://stackoverflow.com/questions/1542803/getcwd-dereference-symlinks

    Args:
        physical (bool): if True dereference all symlinks otherwise
            use PWD from environment even if it contains symlinks.

    Example:
        >>> import ubelt as ub
        >>> cwd = ub.getcwd()
        >>> dpath = ub.ensure_app_resource_dir('ubelt')
        >>> real_dpath = ub.ensuredir(join(dpath, 'real'))
        >>> link_dpath = join(dpath, 'link')
        >>> ub.symlink(real_dpath, link_dpath, overwrite=True)
        >>> ub.chdir(link_dpath)
        >>> print(ub.compressuser(ub.getcwd(physical=False)))
        ~/.config/ubelt/link
        >>> print(ub.getcwd(physical=True))
        ...config/ubelt/real
    """
    physical_cwd = os.getcwd()
    if physical:
        return physical_cwd
    real1 = normpath(realpath(physical_cwd))
    # test if we have the PWD environment variable
    logical_cwd = os.getenv('PWD', None)
    if logical_cwd is not None:
        # PWD is not updated if os.chdir was used.
        # Return a real path.
        real2 = normpath(realpath(logical_cwd))
        if real1 == real2:
            return logical_cwd
        else:
            warnings.warn('ub.getcwd may not be able to resolve symlinks')
    else:
        warnings.warn('The PWD environment variable does not exist')
    return physical_cwd
