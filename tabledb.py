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
_record_list_key = ".__DATA__"

TN = 'Table_Name'
COL = 'Columns'
CN = 'Col_Name'
DT = 'Data_Type'
NONULL ='Not_NULL'
PRI = 'primary_key'
FOR = 'foreign_key'
REFTAB = 'RefTables'
REC = 'Data'
COL_LIST = 'Column_List'


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
        self.schema_list[table_name] = self.Table(self.schema_list, \
                        table_name, col_defs, primary_key, foreign_key_defs)

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
    
    def insert_query(self, param):
        # INSERT INTO account VALUES(123, 'Hello', NULL)
        # {'Query': 'insert_query', 'Param': {'Table_Name': 'account', 'Columns': None, 'Val_List': [123, 'Hello', 'NULL']}}
        table_name = param[TN]
        if table_name not in self.schema_list.keys():
            parser._queues.append(str(NoSuchTable))
            raise NoSuchTable()

        serial_reclist_obj = self._db.get(_encode_str(param[TN]+_record_list_key))

        if serial_reclist_obj == None:
            records = Records(table_name,  
                    self.schema_list[table_name][PRI], 
                    self.schema_list[table_name][FOR], 
                    self.schema_list[table_name][COL],
                    self.schema_list[table_name].get_column_names())
        else:
            records = _decode_pickle(serial_reclist_obj)

        records.add_record(param['Columns'],param['Val_List'])
        parser._queues.append("The row is inserted\n")
        self._db.put(_encode_str(table_name+_record_list_key), _encode_pickle(records))

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
            # to get the columns of a table you can do
            # <table>[COL].get_keys()
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
                        parser._queues.append(str(ReferenceTypeError()))
                        raise ReferenceTypeError()
                    if col_name in k:
                        i = k.index(col_name)
                        foreign = table, v[i]
                self[COL][col_name] = self.Column(schema, col_name, data_type, not_null, prime, foreign)
        
        def get_column_names(self):
            return list(self[COL].keys())

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
                self._check_reference_constraint(schema, foreign)
                self[FOR] = foreign

            def _check_reference_constraint(self, schema, reference):
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

class Records(collections.UserDict): 
    """
    This class can be accessed by "<table_name>.__data__."
    Attributes
    ---------
    Records[TN] : string
        table name of the record
    Records[DATA] : list: dict
        [
            {col1 : val1, col2 : val2, col3 : val3 ...},
            {col1 : val1, col2 : val2, col3 : val3 ...},
        ]
    Records[PRI] : list: column_names
        from table[PRI]
    Records[FOR] : dict
        {tuple(foreign_key_def[0]) : (foreign_key_def[1], tuple(foreign_key_def[2]) }
        {(foreign_key1, foreign_key2) : (ref_table, (ref column1, ref column2))}
    Records[REFTAB] : list
        [ref_table1, ref_table2]
    """
    def __init__(self, table_name, pk_list, fk_list, col_dict, colname_list):
        super().__init__(self)
        self[TN] = table_name
        self[REC] = []
        self[PRI] = pk_list
        self[FOR] = fk_list
        self[COL] = col_dict
        self[COL_LIST] = colname_list

    def get_records_with_column(self, args:list) -> list :
        """
        args : [col1, col2, col3]
        returns
        -------
            {col1:[items], col2:[items], col3:[items]}
        """
        ret = {} # initialize
        for column in args:
            ret[column] = []

        for rec in self[REC]:
            for column in args:
                ret[column].append(rec[column])
        return ret



    def add_record(self, columns:list, vals:list) -> bool:
        rec = {}
        # initialize the input record to None
        for column in self[COL_LIST]:
            rec[column] = None
        
        # check for the number of vals
        if columns == None: 
            if len(vals) != len(self[COL_LIST]):
                parser._queues.append(str(InsertTypeMismatchError()))
                raise InsertTypeMismatchError()
            else:
                for i, (k, _) in enumerate(rec.items()):
                    rec[k] = (vals[i] if vals[i] != 'NULL' else None)
        
        # check for type error, primary constraint, foreign key constraints
        for k, v in rec.items():
            # Column existence check
            if k not in self[COL_LIST]:
                parser._queues.append(str(InsertColumnExistenceError(k)))
                raise InsertColumnExistenceError(k)

            # Nullity check
            if v ==None:
                if self[COL][k][NONULL]:
                    parser._queues.append(str(InsertColumnNonNullableError(k)))
                    raise InsertColumnNonNullableError(k)

            # type error check
            if self[COL][k][DT].type == 'int':
                if type(v) == int:
                    pass
                else:
                    parser._queues.append(str(InsertTypeMismatchError()))
                    raise InsertTypeMismatchError()
            elif self[COL][k][DT].type == 'char':
                if type(v) == str:
                    if len(v) > self[COL][k][DT].len:
                        parser._queues.append(str(InsertTypeMismatchError()))
                        raise InsertTypeMismatchError()
                    else:
                        pass
                else:
                    parser._queues.append(str(InsertTypeMismatchError()))
                    raise InsertTypeMismatchError()
            else: #date
                pass

            # primary constraint check
            if k in self[PRI]:
                primary_recs = self.get_records_with_column(self[PRI])
                # if already in
                if v in primary_recs[k]:
                    parser._queues.append(str(InsertDuplicatePrimaryKeyError()))
                    raise InsertDuplicatePrimaryKeyError()

            # foreign constraint check
            # if self[COL][k][FOR] not none
            if self[COL][k][FOR]:
                # self[COL][k][FOR][0] : table name of the ref_table
                # self[COL][k][FOR][1] : column name of the ref column
                ref_table_name = self[COL][k][FOR][0]
                ref_col_name = self[COL][k][FOR][1]
                serial_obj =  \
                    self._db.get(_encode_str(ref_table_name + _record_list_key))
                if serial_obj == None:
                    parser._queues.append(str(InsertReferentialIntegrityError()))
                    raise InsertReferentialIntegrityError()
                else:
                    ref_records = _decode_pickle(serial_obj)
                    ref_recs = ref_records.get_records_with_column([ref_col_name])
                    if v not in ref_recs[ref_col_name]:
                        parser._queues.append(str(InsertReferentialIntegrityError()))
                        raise InsertReferentialIntegrityError()

        self[REC].append(rec)


