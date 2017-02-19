# -*- coding: utf-8 -*-
"""
Functions for stress testing
"""
from __future__ import print_function, division, absolute_import, unicode_literals


def find_nth_prime(n, start_guess=2, start_num_primes=0):
    """
    Args:
        n (int): the n-th prime (n=2000 takes about a second)
        start_guess (int): starting number to guess at (default=2)
        start_num_primes (int): number of primes before the guess


    CommandLine:
        python -m utool.util_alg find_nth_prime --show

    Example:
        >>> # DISABLE_DOCTEST
        >>> from ubelt.util_stress import *  # NOQA
        >>> import utool as ut
        >>> n_list = []
        >>> time_list = []
        >>> for n in range(1, 2000 + 2, 500):
        >>>     with ut.Timer(verbose=0) as t:
        >>>         find_nth_prime(n)
        >>>     time_list += [t.ellapsed]
        >>>     n_list += [n]
        >>> ut.quit_if_noshow()
        >>> import plottool as pt
        >>> pt.multi_plot(n_list, [time_list], xlabel='prime', ylabel='time')
        >>> ut.show_if_requested()
    """
    guess = start_guess
    num_primes_found = start_num_primes
    while True:
        if guess >= 2 and not any(guess % j == 0 for j in range(2, guess)):
            num_primes_found += 1
        if num_primes_found == n:
            nth_prime = guess
            break
        guess += 1
    return nth_prime
