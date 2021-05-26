from exceptions import *
import test
from relationdb import MisoDB
from itertools import zip_longest
import time # for unique keys

FILENAME = 'myBDB.db'

def init_db():
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
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
        print("The row is inserted")
    elif msg[0] == 'delete':
        # TODO
        cnt = delete_records()
        print(f"{cnt} rows are deleted")
    elif msg[0] == 'select':
        select_records()
        print("select")
    else:
        if test.get_test_flg():
            raise NotImplementedError("problem occured in 'execute()'")

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
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
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
        db['.meta.'+name+'.keys'] = []

        attrs = db['.meta.attrs']
        for attr in list(ad):
            attrs.add(name+'.'+attr)
        db['.meta.attrs'] = attrs
        
        for rf, ref_table, rt in fk_list:
            key = ref_table + '.rf.cnt'
            db[key] = db[key] + 1

            key = ref_table + '.rf'
            rf_pairs = zip_longest(rf, [name], rt, fillvalue=name)
            for rf_name_rt in rf_pairs:
                referenced = db[key]
                referenced.append(rf_name_rt)
                db[key] = referenced

def drop_table(name):
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
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
            rf_pairs = zip_longest(rf, [name], rt, fillvalue=name)
            for rf_name_rt in rf_pairs:
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
        del db['.meta.'+name+'.keys'] 
        # TODO
        # should delete the records as well

def desc_table(name):
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
    with MisoDB(FILENAME) as db:
        try:
            ad = db[name + '.ad']
            pk = db[name + '.pk']
            fk = db[name + '.fk']
            fk = {a for atts, _, _ in fk for a in atts}
        except KeyError as e:
            raise NoSuchTable() from e
        
        print_fmt = "{:22s}{:14}{:14}{:14}"

        print("-------------------------------------------------")
        print(f"table_name [{name}]")
        print(print_fmt.format("column_name", "type", "null", "key"))
        for at, d in ad.items():
            type = d[0] if d[0] != 'char' else f'char{d[1]}'
            null = 'Y' if d[2] else 'N'
            p, f = (at in pk), (at in fk)
            key = ("PRI/FOR" if f else "PRI") if p else ("FOR" if f else "")
            print(print_fmt.format(at, type, null, key))
        
        print("-------------------------------------------------")


def show_tables():
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
    with MisoDB(FILENAME) as db:
        print("----------------")
        for x in db['.meta.tables']:
            print(x)
        print("----------------")


def insert_records(name, attrs, vals):
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
    with MisoDB(FILENAME) as db:
        try:
            ad = db[name + '.ad']
            pk = db[name + '.pk']
            fk = db[name + '.fk']
            # refences to tables
            rt_tab = {tab for _ , tab, _ in fk}
        except KeyError as e:
            raise NoSuchTable() from e

        rec = {}
        # initialize with None
        for at in ad: # at-> attribute
            rec[ad] = None

        # make a record
        if not attrs:
            if len(ad) != len(vals):
                raise InsertTypeMismatchError
            for at, v in zip(ad, vals):
                if ad[at][0] == 'char' and ad[at][1] < len(v[1]):
                    l = ad[at][1] # l-> length
                    v[1] = v[1][0:l]
                rec[at] = v[1]

        else:
            if len(attrs) != len(vals):
                raise InsertTypeMismatchError()

            for at in attrs:
                if at not in list(ad):
                    raise InsertColumnExistenceError(at)

            for at, v in zip(attrs, vals):
                if ad[at][0] != v[0]:
                    raise InsertTypeMismatchError()

                if ad[at][0] == 'char' and ad[at][1] < len(v[1]):
                    l = ad[at][1] # l-> length
                    v[1] = v[1][0:l]
                rec[at] = v[1]
        
        for at in ad: # nullity check
            if ad[at][2] == False and rec[at] is None:
                raise InsertColumnNonNullableError(at)

    check_pk_rec(db, name, pk ,rec)
    check_fk_rec(db, name, rec)

    # if flawless then add the record to the DB
    key = str(time.time()).replace('.','')
    db[name+'.'+key+'.rec'] = rec 

    # TODO: change key for meta_keys
    meta_keys = db['.meta.'+name+'.keys'] 
    meta_keys.append(key)
    db['.meta.'+name+'.keys'] = meta_keys

    for at in rec:
        try:
            assert isinstance(db[name+'.'+at+'.ci'], list)
        except (KeyError, AssertionError):
            # initialize column item
            db[name+'.'+at+'.ci'] = []
        col = db[name+'.'+at+'.ci'] 
        col.append(rec[at])
        db[name+'.'+at+'.ci'] = col
            
def check_pk_rec(db:MisoDB, name:str, pk:list, rec:dict):
    for at in rec: 
        if at in pk:
            col_item = db[name+'.'+at+'.ci']
            if rec[at] in col_item:
                raise InsertDuplicatePrimaryKeyError()

def check_fk_rec(db:MisoDB, name:str, fk:list, rec:dict):
    fkeys = {a for atts, _, _ in fk for a in atts}
    fpairs = [ (a, n, f) for atts, n, fs in fk for a, f in zip(atts, fs)]

    for at in rec:
        if at in fkeys:
            rt, rk = [(n, f) for a, n ,f in fpairs if at == a][0]
            col_item = db[rt+'.'+rk+'.ci']
            if rec[at] not in col_item:
                raise InsertReferentialIntegrityError()
        

def delete_records():
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'

def select_records():
    if test.get_test_flg():
        FILENAME = 'testBDB.db'
    else:
        FILENAME = 'myBDB.db'
