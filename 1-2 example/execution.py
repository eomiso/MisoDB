from core import SimpleBDB
from exceptions import *

FILENAME = 'myBDB.db'


def init_db():
    with SimpleBDB(FILENAME, flags=SimpleBDB.CREATE) as db:
        try:
            assert isinstance(db['.meta.tables'], set)
        except (KeyError, AssertionError):
            db['.meta.tables'] = set()


def execute(msg):
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


def check_fk(db, ad, fk):
    atts, ref_table, ref_atts = fk

    try:
        ref_ad = db[ref_table + '.ad']
        ref_pk = db[ref_table + '.pk']
    except KeyError as e:
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
    with SimpleBDB(FILENAME) as db:
        ad, pk, fk_list = schema
        for fk in fk_list:
            check_fk(db, ad, fk)

        tables = db['.meta.tables']
        if name in tables:
            raise TableExistenceError()
        tables.add(name)
        db['.meta.tables'] = tables

        db[name + '.ad'] = ad
        db[name + '.pk'] = pk
        db[name + '.fk'] = fk_list
        db[name + '.ref'] = 0

        for _, ref_table, _ in fk_list:
            key = ref_table + '.ref'
            db[key] = db[key] + 1


def drop_table(name):
    with SimpleBDB(FILENAME) as db:
        try:
            ref = db[name + '.ref']
        except KeyError as e:
            raise NoSuchTable() from e

        if ref > 0:
            raise DropReferencedTableError(name)

        for _, ref_table, _ in db[name + '.fk']:
            key = ref_table + '.ref'
            db[key] = db[key] - 1

        del db[name + '.ad']
        del db[name + '.pk']
        del db[name + '.fk']
        del db[name + '.ref']

        tables = db['.meta.tables']
        tables.remove(name)
        db['.meta.tables'] = tables


def desc_table(name):
    with SimpleBDB(FILENAME) as db:
        try:
            ad = db[name + '.ad']
            pk = db[name + '.pk']
            fk = db[name + '.fk']
            fk = {a for atts, _, _ in fk for a in atts}
        except KeyError as e:
            raise NoSuchTable() from e

        print_form = "{:22s}{:14}{:14}{:14}"

        print("-------------------------------------------------")
        print(f"table_name [{name}]")
        print(print_form.format("column_name", "type", "null", "key"))
        for a, d in ad.items():
            type = d[0] if d[0] != 'char' else f'char({d[1]})'
            null = 'Y' if d[2] else 'N'
            p, f = (a in pk), (a in fk)
            key = ("PRI/FOR" if f else "PRI") if p else ("FOR" if f else "")
            print(print_form.format(a, type, null, key))
        print("-------------------------------------------------")


def show_tables():
    with SimpleBDB(FILENAME) as db:
        print("----------------")
        for x in db['.meta.tables']:
            print(x)
        print("----------------")
