def demo():
    import dis

    def func1(x):
        return x + 1

    def func2(x):
        if True:
            return x + 1
        else:
            return x + 2

    import io
    file = io.StringIO()
    print('--- DIS1 ---')
    dis.dis(func1, file=file)
    file.seek(0)
    dis1 = file.read()
    print('--- DIS2 ---')
    file = io.StringIO()
    dis.dis(func2, file=file)
    file.seek(0)
    dis2 = file.read()
    print('dis1 =\n{}'.format(dis1))
    print('dis2 =\n{}'.format(dis2))
    print('dis1 == dis2 = {}'.format(dis1 == dis2))
    print('repr(dis1) ~= repr(dis2) = {}'.format(repr(dis1)[10:] == repr(dis2)[10:]))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/ubelt/dev/demodis.py
    """
    demo()
