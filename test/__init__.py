from . import *

import sys

sys.path.insert(0,'../')

test_flg =False

def set_test_flg():
    test_flg = True

def get_test_flg():
    return test_flg

__all__ = ['set_test_flg', 'get_test_flg', 'test_shell']
