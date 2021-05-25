import lark
from exceptions import *
from execution import init_db, execute


class CommonTransformer(lark.Transformer):
    def column_name_list(self, items):
        return items[1:-1]

    def data_type(self, items):
        type_name = items[0].type.replace('TYPE_', '')
        if type_name == 'CHAR':
            if (type_size := int(items[2].value)) < 1:
                raise CharLengthError()
            return [type_name.lower(), type_size]
        return [type_name.lower(), 0]

    def table_name(self, items):
        return items[0].value.lower()

    def column_name(self, items):
        return items[0].value.lower()


class TableTransformer(CommonTransformer):
    def create_table_query(self, items):
        return ('create', items[2], items[3])

    def drop_table_query(self, items):
        return ('drop', items[2])

    def desc_query(self, items):
        return ('desc', items[1])

    def show_tables_query(self, items):
        return ('show',)

    def table_element_list(self, items):
        attributes = {}     # {'att': ['type_name', 'type_size', nullable]}
        pk = []             # ['att']
        fk = []             # [(['att'], 'table', ['att'])]

        for type, *context in items[1:-1]:
            if type == 'column':
                a, d = context
                if a in attributes:
                    raise DuplicateColumnDefError()
                attributes[a] = d

            elif type == 'constraint':
                type, *context = context
                for a in context[0]:
                    if a not in attributes:
                        raise NonExistingColumnDefError(a)
                if type == 'PK':
                    if pk:
                        raise DuplicatePrimaryKeyDefError()
                    for a in (pk := context[0]):
                        attributes[a][2] = False  # pk → not null
                elif type == 'FK':
                    fk.append(tuple(context))

        return attributes, pk, fk

    def table_element(self, items):
        return items[0]

    def column_definition(self, items):
        items[1].append(len(items) <= 2)
        return ('column', items[0], items[1])

    def table_constraint_definition(self, items):
        return ('constraint', *items[0])

    def primary_key_constraint(self, items):
        return ('PK', items[2])

    def referential_constraint(self, items):
        return ('FK', items[2], items[4], items[5])

class RecordTransformer(CommonTransformer):

class Transformer(TableTransformer):
    def command(self, items):
        if not isinstance(items[0], list):
            exit()
        return items[0]

    def query_list(self, items):
        return items

    def query(self, items):
        return items[0]


def input_queries(prompt):
    s = input(prompt)
    if not s.strip():
        return []
    while not s.rstrip().endswith(';'):
        s += '\n' + input()
    return [x + ';' for x in s.split(';')[:-1]]


if __name__ == "__main__":
    prompt = "DB_example> "

    with open('grammar.lark') as file:
        parser = lark.Lark(file.read(), start="command", lexer='standard')
    transformer = Transformer()

    init_db()

    while True:
        for query in input_queries(prompt):
            try:
                tree = parser.parse(query)
                msg = transformer.transform(tree)[0]
                execute(msg)
            except lark.exceptions.UnexpectedInput:
                print(prompt + "SYNTAX ERROR")
            except lark.exceptions.VisitError as e:
                print(prompt + str(e.__context__))
            except SimpleDatabaseError as e:
                print(prompt + str(e))
