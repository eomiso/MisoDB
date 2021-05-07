from lark import Lark, Transformer
import sys

_queues = [] # queues to be printed to the prompt

class Parser:
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="standard")

class MyTransformer(Transformer):
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
        _queues.append(str(tree) + '\n')
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
            if tree[-2].value +" "+ tree[-1].value == "not null":
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

    def insert_query(self, tree):
        _queues.append(
                self.fmtstr.format(query_type=
                            self.query_types['insert_query']))

    def drop_table_query(self, tree):
        _queues.append(
                self.fmtstr.format(query_type=
                            self.query_types['drop_table_query']))
        return {'Query': 'drop_table', 'Param': tree[2]}

    def descending_query(self, tree):
        _queues.append(
                self.fmtstr.format(query_type=
                            self.query_types['descending_query']))
        return {'Query': 'desc_table', 'Param': tree[1]}

    def show_tables_query(self, tree):
        _queues.append(
                self.fmtstr.format(query_type=
                            self.query_types['show_tables_query']))
        return {'Query': 'show_tables'}

    def delete_query(self, tree):
        _queues.append(
                self.fmtstr.format(query_type=
                            self.query_types['delete_query']))

