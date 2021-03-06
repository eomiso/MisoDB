import unittest
from tabledb import Records

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

"""
    Class On Test: Records
    Method On Test: get_records_with_column
        # Argument(type): x(np.ndarray)
"""
class RecordsTestCase(unittest.TestCase):
    """
    (1) Check with single column
    """
    def setUp(self):
        self.record = Records("sample table", \
                              ['col1'],
                              [{('col3'):('ref_table', ('ref_col'))}],
                              {})

        self.record[REC] = \
                    [
                        {'col1': 123, 'col2': "David", 'col3': "Seoul"},
                        {'col1': 369, 'col2' : "YoungA", 'col3':"Washington"}
                    ]

    def test_get_records_with_column_single(self):
        self.assertDictEqual(self.record.get_records_with_column(['col1']), {'col1':[123, 369]})
    """
    (2) Check with multiple column
    """
    def test_get_records_with_column_double(self):
        self.assertDictEqual(self.record.get_records_with_column(    \
                ['col1', 'col2']), {'col1':[123, 369],    
                'col2':["David", "YoungA"]})
    def test_add_record(self):
        self.assertFalse(add_record({'col1': '1235'}))



def _where_condition(param:tuple):
    ret = ""
    for expr in param:
        if type(expr) != tuple:
            ret += _wrapper(expr) 
        else:
            ret += ( '(' + _where_condition(expr) +')')
    return ret

STRINGS = ['and', 'or', 'not', '==', '>=', '<=', '<', '>', '!=', 'is null', 'is not null']
def _wrapper(expr):
    if type(expr) == int:
        return str(expr)
    elif expr not in STRINGS:
        return '\'' + expr + '\''
    else:
        return ' '+ expr+' '
        
a = (('borrower.branch_name', 'is not null'), 'and', ('branch_name', '==', 'hello'), 'and', ('not', ('branch_num', '==', 123)))