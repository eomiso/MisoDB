from berkeleydb import db
import parser
from exceptions import *
import collections
import pickle

"""
Reserved Keys and methods.
You need serialize the objects to use berkeleydb.
"""

_schema_list_key = "__SCHEMA_LIST__" # a key for retrieving table_list

TN = 'Table_Name'
COL = 'Columns'
CN = 'Col_Name'
DT = 'Data_Type'
NONULL ='Not_NULL'
PRI = 'primary_key'
FOR = 'foreign_key'
REFTAB = 'RefTables'

def _encode_str(input):
    return bytes(input, 'utf-8')
def _decode_str(output):
    return str(output)
def _encode_pickle(input):
    return pickle.dumps(input)
def _decode_pickle(output):
    return pickle.loads(output)

class RelationDB(object):
    """
    A wrapper class for berkeleyDB. BerkelyDB doesn't support 
    Relational models. So we need a wrapper class to handle the 
    schemas.

    Attributes
    ----------
    self._db : berkeleydatabase instance
    self.schema_list : dict
        a dictionary of table schemas. It has a form of
        {'account' : table_def of account, 
         'student' : table_def of student,
            ...
        }
        
        ----
        the table_def should also be a dictionary probably a dictionary
        of key: column_name, pair: column_definition pairs
    
        I have formulated the definitions (table and column definition
         alike)
    """
    def __init__(self, filename):
        self._db = db.DB()
        self._db.open(filename, dbtype=db.DB_BTREE, flags=db.DB_CREATE)

        serial_obj = self._db.get(_encode_str(_schema_list_key))
        
        if serial_obj == None:
            self.schema_list = {}
        else:
            self.schema_list = _decode_pickle(serial_obj)

    def create_table(self, table_definition):
        """
        Parameter
        ---------
        table_definition
            dict from the Qeuery dict take a look at 'Param'.
            table_definition is the value of 'Param'.
            [{'Query': 'create_table', 'Param': {
                'Table_Name': 'student', 'Elem_List': [
                {'Col_Def': {'Col_Name': 'student_number', 'Data_Type': 'int'}}, 
                {'Col_Def': {'Col_Name': 'name', 'Data_Type': 'char(10)'}}, 
                {'Col_Def': {'Col_Name': 'acc_num', 'Data_Type': 'int'}}, 
                {'foreign_key': (['acc_num'], 'account', ['acc_number'])}
                ]}
            }]
        """
        #import pdb; pdb.set_trace()
        table_name = table_definition.get(TN)
        col_defs = [table_elem.get('Col_Def')                       \
                        for table_elem                              \
                            in table_definition.get('Elem_List')    \
                                # remove none type
                                if table_elem.get('Col_Def')]
        primary_key = [table_elem.get(PRI) \
                        for table_elem     \
                          in table_definition.get('Elem_List')  \
                            if table_elem.get(PRI)]
        foreign_key_defs = [table_elem.get(FOR)                     \
                             for table_elem                        \
                                in table_definition.get('Elem_List') \
                                  if table_elem.get(FOR)]
        #import pdb; pdb.set_trace()
        self._table_already_exists(table_name)
        self._has_duplicate_column_name(col_defs)
        self._has_multiple_primary_key_def(primary_key)
        self._primary_key_in_col_defs(col_defs, primary_key)
        self._foreign_key_in_col_defs(col_defs, foreign_key_defs)

        # create table schema
        # primary_key looks like this [[key1, key2...]]
        #import pdb; pdb.set_trace()
        self.schema_list[table_name] = self.Table(self.schema_list, table_name, col_defs, primary_key, foreign_key_defs)

        # save table schema
        self._db.put(_encode_str(_schema_list_key), _encode_pickle(self.schema_list))

        # add queue
        parser._queues.append(str(CreateTableSuccess(table_name)))

    def desc_table(self, table_name):
        #import pdb; pdb.set_trace()
        try:
            parser._queues.append(str(self.schema_list[table_name]))
        except KeyError:
            parser._queues.append(str(NoSuchTable()))
            raise NoSuchTable()

        parser._queues.append("desc_table called\n")

    def drop_table(self, table_name):
        for table in self.schema_list.values():
            if table_name in table[REFTAB]:
                parser._queues.append(str(DropReferencedTableError(table_name)))
                raise DropReferencedTableError(table_name)
        res = self.schema_list.pop(table_name)
        if res == None:
            parser._queues.append(str(NoSuchTable()))
            raise NoSuchTable()
        
        parser._queues.append(str(DropSuccess(table_name)))
        self._db.put(_encode_str(_schema_list_key), _encode_pickle(self.schema_list))

    def show_tables(self, param):
        ret  = "\n----------------\n"
        for table_name in self.schema_list.keys():
            ret += table_name + "\n"
        ret += "----------------\n"
        parser._queues.append(ret)
    
    def _table_already_exists(self, name):
        if self._schema_has_table(name):
            parser._queues.append(str(TableExistenceError()))
            raise TableExistenceError()

    def _schema_has_table(self, name):
        if name in self.schema_list.keys():
            return True
        else:
            return False
    
    def _has_duplicate_column_name(self, col_def_list):
        names = [col_def.get(CN) for col_def in col_def_list]
        if self._has_duplicate(names):
            parser._queues.append(str(DuplicateColumnDefError()))
            raise DuplicateColumnDefError()

    def _has_duplicate(self, input_list):
        if len(set(input_list)) != len(input_list):
            return True
        else:
            return False
    
    def _has_multiple_primary_key_def(self, primary_key_list):
        if len(primary_key_list) > 1:
            parser._queues.append(str(DuplicatePrimaryKeyDefError()))
            raise DuplicatePrimaryKeyDefError()

    def _primary_key_in_col_defs(self, col_def_list, primary_key_list):
        names = [col_def.get(CN) for col_def in col_def_list]
        # if there is no primary key definition
        if len(primary_key_list) == 0:
            return
        for key in primary_key_list[0]:
            if key not in names:
                parser._queues.append(str(NonExistingColumnDefError(key)))
                raise NonExistingColumnDefError(key)

    def _foreign_key_in_col_defs(self, col_def_list, foreign_key_list):
        if len(foreign_key_list) == 0:
            return

        names = [col_def.get(CN) for col_def in col_def_list]
        # this would be 2-depth list
        # foreign_key_def[0] is the list of 
        # foreign keys in the definition
        foreign_keys = [foreign_key_def[0] 
                        for foreign_key_def in foreign_key_list] 
        for col_names in foreign_keys:
            for column in col_names:
                if column not in names:
                    parser._queues.append(str(NonExistingColumnDefError(column)))
                    raise NonExistingColumnDefError(column) 
    def close(self):
        self._db.close()
        return

    class Table(collections.UserDict):
        def __init__(self, schema, name, columns, primary_keys, foreign_keys):
            """
            Parameter
            ---------
            name : string
            columns : list of tuples
                the tuples should conaint
                (
                    name : string,
                    data_type : string,
                    not_null : bool
                )
                there should also be prime:bool,
                and foreign_key, (table, ref_key) pair as an input for foreign
            primary_keys : list of strings
            foreign_keys : list of tuples
                the tuples should contain
                ( 
                    [list of foreign_keys],
                    ref_table name,
                    [list of ref_keys]
                )
            """
            super().__init__(self)
            self.setter(schema, name, columns, primary_keys, foreign_keys)
        
        def setter(self, schema, name, columns, primary_keys, foreign_keys):
            #import pdb; pdb.set_trace()
            self[TN] = name
            self[PRI] = primary_keys if len(primary_keys) == 0 else primary_keys.pop()
            
            
            #foreign keys [([foreign_keys], table, [ref_keys])]
            self[FOR] = dict()
            self[REFTAB] = set() # a set that contains all the reftables
            
            for foreign_key_def in foreign_keys:
                #(foreign_key1, foreign_key2) = (ref_table, (ref column1, ref column2))
                self[FOR][tuple(foreign_key_def[0])] = tuple([foreign_key_def[1], tuple(foreign_key_def[2])])
                self[REFTAB].add(foreign_key_def[1])
            
            self[COL] = {}
            for col_def in columns:
                col_name = col_def.get(CN)
                data_type = self.DataType(col_def.get(DT))
                if col_name in self[PRI]:
                    prime = True
                else:
                    prime = False
                
                if col_def.get(NONULL) or prime:
                    not_null = True
                else:
                    not_null = False

                foreign = None
                for k, (table, v) in zip(self[FOR].keys(), self[FOR].values()):
                    if len(k) != len(v):
                        parse._queues.append(str(ReferenceTypeError()))
                        raise ReferenceTypeError()
                    if col_name in k:
                        i = k.index(col_name)
                        foreign = table, v[i]
                self[COL][col_name] = self.Column(schema, col_name, data_type, not_null, prime, foreign)

        def __str__(self):
            ret = f""" 
                -------------------------------------------------\n
                table_name [{self[TN]}]\n
                {'column_name':15} {'type':10} {'null':10} {'key':10}\n"""

            for column in self[COL].values():   
                ret += str(column)

            ret += """-------------------------------------------------\n"""
            return ret
    
        class Column(collections.UserDict):
            def __init__(self, schema, name, data_type, not_null, prime, foreign):
                """
                Parameter
                ---------
                name : string
                    column name
                data_type : DataType ()
                    could be one of int, char(int), date
                not_null : bool
                    whether this column could be null
                prime : bool
                    wheter this column is primary or not
                foreign : none | (ref_table name: str, ref_key name: str)
                """
                super().__init__(self)
                self.setter(schema, name, data_type, not_null, prime, foreign)
            
            def setter(self, schema, name, data_type, not_null, prime, foreign):
                #TODO
                self[CN] = name
                self[DT] = data_type
                self[NONULL] = not_null
                self[PRI] = prime
                self._check_refrence_constraint(schema, foreign)
                self[FOR] = foreign

            def _check_refrence_constraint(self, schema, reference):
                """
                Parameter
                ---------
                reference : tuple
                    None | (table_name, ref column)
                """
                if not reference: #if foreign is None
                    return
                ref_table, ref_column = reference
                
                ref_table = schema.get(ref_table)
                if not ref_table:
                    parser._queues.append(
                        str(ReferenceTableExistenceError())
                    )
                    raise ReferenceTableExistenceError()

                ref_column = ref_table[COL].get(ref_column)
                if not ref_column:
                    parser._queues.append(str(ReferenceColumnExistenceError()))
                    raise ReferenceColumnExistenceError()
                if not (self[DT] == ref_column[DT]):
                    parser._queues.append(
                        str(ReferenceTypeError())
                    )
                    raise ReferenceTypeError()
                if not ref_column[PRI]:
                    parser._queues.append(
                        str(ReferenceNonPrimaryKeyError())
                    )
                    raise ReferenceNonPrimaryKeyError()
            
            def __str__(self):
                if self[PRI] and self[FOR]:
                    key = "PRI/FOR"
                elif self[PRI]:
                    key = "PRI"
                elif self[FOR]:
                    key = "FOR"
                else:
                    key = ""
                ret = f"""
                {self[CN]:15} {self[DT]:10} {'T' if not self[NONULL] else 'F':10} {key:10}
                """


                return ret

            
        class DataType(object):
            def __init__(self, type_str):
                self.setter(type_str)

            def setter(self, type_str):
                if type_str == 'int':
                    self.type = 'int'
                elif type_str == 'date':
                    self.type = 'date'
                else:
                    self.type = 'char'
                    self.len  = int(type_str.replace('char', '').replace('(', '').replace(')',''))
                    if self.len < 1:
                        parser._queues.append(str(CharLengthError()))
                        raise CharLengthError()

            def get_type(self):
                return self.type
            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    if self.type == 'char':
                        return self.type == other.type and self.len == other.len
                    else:
                        return self.type == other.type
            def __format__(self, format_spec):
                return self.__str__().__format__(format_spec)

            def __str__(self):
                if self.type == 'int':
                    return self.type
                elif self.type == 'date':
                    return self.type
                else:
                    return self.type + '(' + str(self.len) + ')'