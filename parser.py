from lark import Lark, Transformer
from exceptions import *


class Parser:
    def __init__(self, file_name):
        self.file_name = file_name

    def get_parser(self):
        with open(self.file_name) as fd:
            return Lark(fd.read(), start="command", lexer="standard")


class CommonTransformer(Transformer):
    def column_name_list(self, items):
        return [col_tuple[1] for col_tuple in items[1:-1]]

    def table_name(self,items):
        return ('tab_name', items[0].value.lower())

    def column_name(self,items):
        return ('col_name', items[0].value.lower())

    def data_type(self, items):
        type_name = items[0].type.replace('TYPE_', '')
        if type_name == 'CHAR':
            type_size = int(items[2].value) 
            if type_size < 1:
                raise CharLengthError()
            return type_name.lower(), type_size
        return type_name.lower(), -1
        

class TableTransformer(CommonTransformer):
    def create_table_query(self, items):
        return ('create', items[2][1], items[3])
    
    def drop_table_query(self, items):
        return ('drop', items[2][1])
    
    def desc_query(self, items):
        return ('desc', items[1][1])
    
    def show_tables_query(self, items):
        return ('show', 0)
    
        
    def table_element_list(self, items):
        attributes = {}  # {'att': ['type_name', 'type_size', nullity]} 
        pk = []         # ['att']
        fk = []         # [(['att'], 'table', ['att'])]

        for type, *context in items[1:-1]:
            if type == 'col_def':
                at,(t, size_t), nullity = context 
                if at in attributes:
                    raise DuplicateColumnDefError()
                attributes[at] = [t, size_t, nullity]

            elif type == 'constraints':
                type, *context = context[0]
                for at in context[0]:
                    if at not in attributes:
                        raise NonExistingColumnDefError(at)
                if type == 'PK':
                    if pk:
                        raise DuplicatePrimaryKeyDefError()
                    pk = context[0]
                    for at in pk:
                        attributes[at][2] = False # pk -> not null
                elif type == 'FK':
                    fk.append(tuple(context))

        return attributes, pk, fk

    def table_element(self, items):
        return items[0]
    def column_definition(self, items):
        if len(items) <= 2:
            nullable = True
        else: 
            nullable = False
        #items[0] ('col_name', '<name>')
        return ('col_def', items[0][1], items[1], nullable)
    def table_constraint_definition(self, items):
        return ('constraints',items[0])
    
    def primary_key_constraint(self, items):
        return('PK', items[2])

    def referential_constraint(self, items):
        #items[4] ('tab_name', '<name>')
        return ('FK', items[2], items[4][1], items[5] )


class RecordTransformer(CommonTransformer):
    pass
class QueryTransformer(TableTransformer, RecordTransformer):
    def command(self, items):
        if not isinstance(items[0], tuple):
            exit("Program terminated")
        return items[0]
    def query_list(self, items):
        return items[0]
    def query(self, items):
        return items[0]

fmtstr = "'{query_type}' requested\n" # the string formnat to be printed
query_types = {
        "create_table_query": "CREATE TABLE", 
        "select_query": "SELECT", 
        "insert_query": "INSERT",
        "drop_table_query": "DROP TABLE",
        "descending_query": "DESC",
        "show_tables_query": "SHOW TABLES",
        "delete_query": "DELETE"
    }
def __init__(self):
    pass

def add_syntax_error(self):
    """Add syntax error to the queues(output)"""
    _queues.append("Syntax error\n")

def error_handler(self, t):
    """transform then add syntax error to the end of queues"""
    self.transform(t)
    self.add_syntax_error()

def command(self, tree):
    # remove list wrapper
    return tree[0]

def query_list(self, tree):
    return tree

def query(self, tree):
    return tree[0]
# methods for each corresponding queries
def create_table_query(self, tree):
    return {'Query': 'create_table', 'Param': {'Table_Name': tree[2], 'Elem_List': tree[3]}}


def table_element_list(self, tree):
    return tree[1:-1]

def table_element(self, tree):
    #print(type(tree[0]))
    if 'Col_Name' in tree[0].keys():
        # means that this is column_defintion
        return {'Col_Def' : tree[0]}
    else:
        return tree[0]

def column_definition(self, tree):
    ret = {'Col_Name': tree[0],
            'Data_Type': tree[1]}
    if len(tree) == 4 : # means that it has not null option
        if tree[-2].value +" "+ tree[-1] == "not null":
            # just in case for other options to come
            ret['Not_Null'] = True
    return ret

def table_constraint_definition(self, tree):
    if tree[0][0] == 'primary_key':
        # from return ('primary_key', tree[2]) 
        return {'primary_key': tree[0][1]}
    if tree[0][0] == 'foreign_key':
        # from ('foreign_key', tree[2], tree[4], tree[5]) 
        return {'foreign_key': (tree[0][1], tree[0][2], tree[0][3])}

def primary_key_constraint(self,tree):
    return ['primary_key', tree[2]]

def referential_constraint(self, tree):
    return ['foreign_key', tree[2], tree[4], tree[5]]

def column_name_list(self, tree):
    #print(tree)
    return tree[1:-1]

def data_type(self, tree):
    ret = ""
    for token in tree:
        ret += token.value
    return ret

def table_name(self, tree):
    return tree[0].value.lower()

def column_name(self, tree):
    return tree[0].value.lower()

def select_query(self, tree):
    _queues.append(
            self.fmtstr.format(query_type=
                        self.query_types['select_query']))
def NULL(self, item):
    return item.value.lower()
def comparable_value(self, tree):
    if tree[0].type == 'INT':
        return int(tree[0].value)
    elif tree[0].type == 'STR':
        return tree[0].value.strip('\'')
    else:
        return "WRONG"
def value(self, tree):
    return tree[0]
def value_list(self, tree):
    return tree[2:-1]
def insert_columns_and_sources(self, tree):
    if len(tree) == 2:
        # [Token('INSERT', 'INSERT'), Token('INTO', 'INTO'), 'account', [['account_name'], [123, 'sillim', None]]]
        return tree
    else:
        # [Token('INSERT', 'INSERT'), Token('INTO', 'INTO'), 'account', [None, [123, 'name', None]]]
        return [None] + tree
        
def insert_query(self, tree):
    # {'Query': 'insert_query', 'Param': {'Table_Name': 'account', 'Columns': [None, [123, 'name', None]], 'Val_List': [None, [123, 'name', None]]}}
    return {'Query': 'insert_query', 'Param': {'Table_Name': tree[2], 'Columns':tree[3][0] ,'Val_List': tree[3][1]}}

def drop_table_query(self, tree):
    return {'Query': 'drop_table', 'Param': tree[2]}

def descending_query(self, tree):
    return {'Query': 'desc_table', 'Param': tree[1]}

def show_tables_query(self, tree):
    return {'Query': 'show_tables', 'Param': None}
def OR(self, item):
    return item.value.lower()
def AND(self, item):
    return item.value.lower()
def NOT(self, item):
    return item.value.lower()

def COMP_OP(self, item):
    if item.value == '=':
        return '=='
    else:
        return item.value
def parenthesized_boolean_expr(self, items):
    return tuple(items[1])
def boolean_expr(self, items):
    if len(items) == 1:
        return items[0]
    return tuple(items)
def boolean_term(self, items):
    if len(items) == 1:
        return items[0]
    return tuple(items)
def boolean_factor(self, items):
    if len(items) == 1:
        return items[0]
    return (items[0], items[1])
def boolean_test(self, item):
    return item[0]
def predicate(self, item):
    return item[0]
def comparison_predicate(self, tree):
    return (tree[0],tree[1],tree[2])
def comp_operand(self, item):
    if len(item)==1:
        return item[0]
    else:
        return item[0]+'.'+item[1]
def null_predicate(self, items):
    if len(items) == 3:
        return (items[0]+'.'+items[1],items[2])
    return tuple(items)
def null_operation(self, items):
    num = len(items)
    res = items[0].lower()
    for i in range(num-1):
        res += (' '+items[i+1])
    return res
def from_clause(self, tree):
    return tree[1]
def where_clause(self, tree):
    print(tree[1])
    return tree[1]
def table_reference_list(self, items):
    return items
def referred_table(self, items):
    if len(items) == 1:
        return items[0]
    else:
        return (items[0],'as', items[2])
def delete_query(self, tree):
    print(tree)
    return {'Query': 'delete_query', 'Param': {'From': tree[1], 'Where': tree[2]} }
    _queues.append(
            self.fmtstr.format(query_type=
                        self.query_types['delete_query']))

