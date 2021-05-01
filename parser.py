from lark import Lark, Transformer

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
        self.queues = [] # queues to be printed to the prompt

    def get_queues(self):
        return self.queues

    def add_syntax_error(self):
        """Add syntax error to the queues(output)"""
        self.queues += ["Syntax error\n"]

    def error_handler(self, t):
        """transform then add syntax error to the end of queues"""
        self.transform(t)
        self.add_syntax_error()

    # methods for each corresponding queries
    def clean_up_queues(self):
        self.queues = []
    
    def create_table_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['create_table_query'])]

    def select_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['select_query'])]

    def insert_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['insert_query'])]

    def drop_table_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['drop_table_query'])]

    def descending_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['descending_query'])]

    def show_tables_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['show_tables_query'])]

    def delete_query(self, tree):
        self.queues +=  [
                self.fmtstr.format(query_type=
                            self.query_types['delete_query'])]


t = Parser().sql_parser.parse('show tables;')
a = MyTransformer()
