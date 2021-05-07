from berkeleydb import db
import parser
from exceptions import *
import collections

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

        self._table_already_exists(table_name)
        self._has_duplicate_column_name(col_defs)
        self._has_multiple_primary_key_def(primary_key)
        self._primary_key_in_col_defs(col_defs, primary_key)
        self._foreign_key_in_col_defs(col_defs, foreign_key_defs)

        parser._queues.append("create_table called\n")

    def desc_table(self, table_name):
        parser._queues.append("desc_table called\n")
    def drop_table(self, table_name):
        parser._queues.append("drop_table called\n")
    def show_tables(self):
        parser._queues.append('show_tables called\n')
    
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
        for key in primary_key_list.pop():
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

    def _check_reference_type(self, foreign_key):
        pass






    class Table(collections.UserDict):
        def __init__(self, name, columns, primary_keys, prime_keys, foreign_keys):
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
            self.setter(name, columns, primary_keys, prime_keys, foreign_keys)
        
        def setter(self, name, columns, primary_keys, foreign_keys):
            self[TN] = name
            self[PRI] = primary_keys
            #foreign keys [([foreign_keys], table, [ref_keys])]
            self[FOR] = {}
            #TODO
            pass
    
    class Column(collections.UserDict):
        def __init__(self, name, data_type, not_null, prime, foreign):
            """
            Parameter
            ---------
            name : string
                column name
            data_type : string
                could be one of int, char(int), date
            not_null : bool
                whether this column could be null
            prime : bool
                wheter this column is primary or not
            foreign : none | (ref_table name: str, ref_key name: str)
            """
            super().__init__(self)
            self.setter(name, data_type, not_null, prime, foreign)
        
        def setter(self, name, data_type, not_null, prime, foreign):
            #TODO
            pass
        