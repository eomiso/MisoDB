from exceptions import *
from test import test_flg
from relationdb import MisoDB

if test_flg:
    FILENAME = 'testBDB.db'
else:
    FILENAME = 'myBDB.db'

def init_db():
    with MisoDB(FILENAME, flags=MisoDB.CREATE) as db:
        try:
            assert isinstance(db['.meta.tables'], set)
        except (KeyError, AssertionError):
            # initializae the berkeleydatabase
            db['.meta.tabels'] = set()