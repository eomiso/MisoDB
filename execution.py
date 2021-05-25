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


def execute(msg:list):
    if msg[0] == 'create':
        create_table(msg[1], msg[2])
        print(f"'{msg[1]}' table is created")
    if msg[0] == 'drop':
        drop_table(msg[1])
        print(f"'{msg[1]}' table is dropped")
    if msg[0] == 'desc':
        desc_table(msg[1])
    if msg[0] == 'show':
        show_tables()
    if msg[0] == 'insert':
        # TODO
        insert_records()
    if msg[0] == 'delete':
        # TODO
        delete_records()
    if msg[0] == 'select':
        select_records()

def create_table():
    pass
def drop_table():
    pass
def desc_table():
    pass
def show_tables():
    pass
def insert_records():
    pass
def delete_records():
    pass
def select_records():
    pass
