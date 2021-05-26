from exceptions import *
import test
from relationdb import MisoDB

if test.test_flg:
    FILENAME = 'testBDB.db'
else:
    FILENAME = 'myBDB.db'

def init_db():
    with MisoDB(FILENAME, flags=MisoDB.CREATE) as db:
        try:
            assert isinstance(db['.meta.tables'], set)
            assert isinstance(db['.meta.attrs'], set)
        except (KeyError, AssertionError):
            # initializae the berkeleydatabase
            db['.meta.tables'] = set()
            db['.meta.attrs'] = set()


def execute(msg:tuple):
    if msg[0] == 'create':
        create_table(msg[1], msg[2])
        print(f"'{msg[1]}' table is created")
    elif msg[0] == 'drop':
        drop_table(msg[1])
        print(f"'{msg[1]}' table is dropped")
    elif msg[0] == 'desc':
        desc_table(msg[1])
    elif msg[0] == 'show':
        show_tables()
    elif msg[0] == 'insert':
        # TODO
        insert_records()
    elif msg[0] == 'delete':
        # TODO
        delete_records()
    elif msg[0] == 'select':
        select_records()
    else:
        if test.test_flg:
            raise NotImplementedError("Execute")

def check_fk(db:MisoDB, ad:dict, fk:tuple):
    atts, ref_table, ref_atts = fk

    try:
        ref_ad = db[ref_table + '.ad'] # dict
        ref_pk = db[ref_table + '.pk'] # list
    except KeyError as e: # e->cause
        raise ReferenceTableExistenceError() from e
    
    for a in ref_atts:
        if a not in ref_ad:
            raise ReferenceColumnExistenceError()

    if set(ref_atts) != set(ref_pk):
        raise ReferenceNonPrimaryKeyError()
    
    if len(atts) != len(ref_atts):
        raise ReferenceTypeError()
    for a1, a2 in zip(atts, ref_atts):
        d1 = ad[a1]
        d2 = ref_ad[a2]
        if d1[0] != d2[0] or d1[1] != d2[1]:
            raise ReferenceTypeError()


def create_table(name, schema):
    with MisoDB(FILENAME) as db:
        # ad -> attribute dictionary
        ad, pk, fk_list = schema 
        for fk in fk_list:
            check_fk(db, ad, fk)
        
        tables = db['.meta.tables'] # set
        if name in tables:
            raise TableExistenceError
        tables.add(name)
        db['.meta.tables'] = tables
        db[name + '.ad'] = ad
        db[name + '.pk'] = pk
        db[name + '.fk'] = fk_list
        db[name + '.rf'] = [] # (ref_from, ref_table_name, ref_to)
        db[name + '.rf.cnt'] = 0

        for attr in list(ad):
            db['.meta.attr'] = name+'.'+attr
        
        for rf, ref_table, rt in fk_list:
            key = ref_table + '.rf.cnt'
            db[key] = db[key] + 1

            key = ref_table + '.rf'
            for rf_name_rt in zip(rf, name, rt):
                referenced = db[key]
                referenced.append(rf_name_rt)
                db[key] = referenced

def drop_table(name):
    with MisoDB(FILENAME) as db:
        try:
            rf_cnt = db[name + '.rf.cnt']
        except KeyError as e:
            raise NoSuchTable() from e
        
        if rf_cnt > 0:
            raise DropReferencedTableError(name)
        
        for rf, ref_table, rt in db[name+'.fk']:
            key = ref_table + '.rf.cnt'
            db[key] = db[key] - 1

            key = ref_table + '.rf'
            for rf_name_rt in zip(rf, name, rt):
                referenced = db[key]
                referenced.remove(rf_name_rt)
                db[key] = referenced
        
        attrs = db['.meta.attrs']
        ad = db[name + '.ad']
        for a in ad:
            attrs.remove(name+'.'+a)
        db['.meta.attrs'] = attrs

        tables = db['.meta.tables']
        tables.remove(name)
        db['.meta.tables'] = tables
        
        del db[name + '.ad']
        del db[name + '.pk']
        del db[name + '.fk']
        del db[name + '.rf']
        del db[name + '.rf.cnt']
        # should delete the records as well


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
