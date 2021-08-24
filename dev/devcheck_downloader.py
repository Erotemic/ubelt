"""
Alternative to ub.DownloadManager
"""


def check_fsspec():
    import ubelt as ub
    from os.path import join
    dpath = ub.ensure_app_cache_dir('ubelt/simple_server')
    info = ub.cmd(['python', '-m', 'http.server', '--directory', dpath], detatch=True)

    fnames = ['file_{}.txt'.format(i) for i in range(100)]
    for fname in fnames:
        ub.writeto(join(dpath, fname), ub.hash_data(fname))
    # info = ub.cmd('python -m http.server --directory "{}"'.format(dpath), verbose=3)

    # proc = info['proc']
    # TODO: ub.cmd return with some object that can tee the output on demand?
    # _proc_iteroutput = ub.util_cmd._proc_iteroutput_thread(proc)
    # line = next(_proc_iteroutput)

    urls = ['http://localhost:8000/{}'.format(fname) for fname in fnames]

    import fsspec
    file = fsspec.open(urls[0]).open().read()

    with ub.Timer(label='fsspec.cat', verbose=1):
        fs = fsspec.filesystem("http")
        out = fs.cat(urls)  # fetches data concurrently

    with ub.Timer(label='ub.DownloadManager', verbose=1):
        dpath = ub.ensure_app_cache_dir('ubelt/simple_download_root')
        dman = ub.DownloadManager(dpath)
        for url in urls:
            dman.submit(url)

        results = []
        for future in dman.as_completed(prog=True):
            fpath = future.result()
            results.append(fpath)
            # print('fpath = {!r}'.format(fpath))

    proc.terminate()
