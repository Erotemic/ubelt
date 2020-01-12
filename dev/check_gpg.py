

def main():
    """
    Checks that the latest wheels on pypi agree with the gpg key
    """
    import requests

    package_name = 'ubelt'
    url = "https://pypi.python.org/pypi/{}/json".format(package_name)
    package = requests.get(url).json()
    max_ver = max(package["releases"].keys())
    # ... check compatibility
    latest_wheel_info_list = package['releases'][max_ver]

    for wheel_info in latest_wheel_info_list:
        import ubelt as ub
        whl_fpath = ub.grabdata(
            wheel_info['url'],
            hash_prefix=wheel_info['digests']['sha256'],
            hasher='sha256'
        )

        if not wheel_info['has_sig']:
            raise ValueError('info says no sig')

        sig_fpath = ub.download(
            wheel_info['url'] + '.asc',
        )

        info = ub.cmd('gpg --verify {} {}'.format(sig_fpath, whl_fpath),
                      verbose=3)
        assert info['ret'] == 0

if __name__ == '__main__':
    pass
