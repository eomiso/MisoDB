from berkeleydb import db
import parser
from exceptions import *
import collections

"""
Reserved Keys and methods.
You need serialize the objects to use berkeleydb.
"""

_schema_list_key = "__SCHEMA_LIST__" # a key for retrieving table_list

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
        table_definition : dict
            dict from: take a look at 'Param'
            [{'Query': 'create_table', 'Param': {
                'Table_Name': 'student', 'Elem_List': [
                {'Col_Def': {'Col_Name': 'student_number', 'Data_Type': 'int'}}, 
                {'Col_Def': {'Col_Name': 'name', 'Data_Type': 'char(10)'}}, 
                {'Col_Def': {'Col_Name': 'acc_num', 'Data_Type': 'int'}}, 
                {'foreign_key': (['acc_num'], 'account', ['acc_number'])}
                ]}
            }]
        """
        parser._queues.append("create_table called\n")

    def desc_table(self, table_name):
        parser._queues.append("desc_table called\n")
    def drop_table(self, table_name):
        parser._queues.append("drop_table called\n")
    def show_tables(self):
        parser._queues.append('show_tables called\n')

    TN = 'Table_Name'
    COL = 'Columns'
    CN = 'Col_Name'
    DT = 'Data_Type'
    NONULL ='Not_NULL'
    PRI = 'primary_key'
    FOR = 'foreign_key'




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
        