from . import *

import sys

sys.path.insert(0,'../')

__all__ = ['set_test_flg', 'get_test_flg', 'test_shell', 'test_flg']

test_flg =False

def set_test_flg():
    test_flg = True
    return test_flg

def get_test_flg():
    return test_flg

