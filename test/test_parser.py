import unittest
from unittest import result
from lark import Tree, Token
from parser import QueryTransformer

from lark.exceptions import VisitError
from exceptions import CharLengthError

class TransformerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.transform = QueryTransformer().transform
        select_query = """
                       select customer_name, borrower.loan_number, amount
                       from borrower as B, loan
                       where borrower.loan_number = loan.loan_number
                       and branch_name = 'Perryridge';
                    """
        create_query = """
                       create table account(acc_number int not null, 
                       branch_name char(10), primary key(acc_number));
                    """ 
        delete_query = """
                       delete from account
                       where branch_name = 'Perryridge';
                    """
        insert_query = """
                       INSERT INTO account VALUES(123, 'Hello');
                    """
        show_query   = """
                    """
        drop_query   = """
                    """
        desc_query   = """
                     """
        #join_query =

        self.very_long_tree = Tree('table_element_list', [Token('LP', '(')
                                  , Tree('table_element', [Tree('column_definition', [Tree('column_name', [Token('IDENTIFIER', 'ID')]), Tree('data_type', [Token('TYPE_INT', 'INT'), Token('NOT', 'not'), Token('NULL', 'null')])])])
                                  , Tree('table_element', [Tree('column_definition', [Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('data_type', [Token('TYPE_CHAR', 'char'), Token('LP', '('), Token('INT', '10'), Token('RP', ')')])])])
                                  , Tree('table_element', [Tree('column_definition', [Tree('column_name', [Token('IDENTIFIER', 'middle_name')]), Tree('data_type', [Token('TYPE_CHAR', 'char'), Token('LP', '('), Token('INT', '10'), Token('RP', ')')])])])
                                  , Tree('table_element', [Tree('column_definition', [Tree('column_name', [Token('IDENTIFIER', 'last_name')]), Tree('data_type', [Token('TYPE_CHAR', 'char'), Token('LP', '('), Token('INT', '10'), Token('RP', ')')])])])
                                  , Tree('table_element', [Tree('column_definition', [Tree('column_name', [Token('IDENTIFIER', 'date_of_birth')]), Tree('data_type', [Token('TYPE_DATE', 'DATE')])])])
                                  , Tree('table_element', [Tree('table_constraint_definition', [Tree('primary_key_constraint', [Token('PRIMARY', 'PRIMARY'), Token('KEY', 'KEY'), Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'ID')]), Token('RP', ')')])])])])
                                  , Tree('table_element', [Tree('table_constraint_definition', [Tree('referential_constraint', [Token('FOREIGN', 'FOREIGN'), Token('KEY', 'KEY'), Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')]), Tree('column_name', [Token('IDENTIFIER', 'last_name')]), Token('RP', ')')]), Token('REFERENCES', 'REFERENCES'), Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')]), Tree('column_name', [Token('IDENTIFIER', 'last_name')]), Token('RP', ')')])])])]), Token('RP', ')')])
        self.maxDiff = None

        return super().setUp()
    def tearDown(self) -> None:
        return super().tearDown()

    """
    (1) column_name test
    """
    def test_trans_table_name(self):
        input = Tree('table_name', [Token('IDENTIFIER', 'account')])
        result = self.transform(input)
        expected = ('tab_name', 'account')

        self.assertTupleEqual(result, expected)

    def test_trans_column_name(self):
        input = Tree('column_name', [Token('IDENTIFIER', 'acc_num')])
        result = self.transform(input)
        expected = ('col_name', 'acc_num')

        self.assertTupleEqual(result, expected)

    def test_trans_column_name_list(self):
        input = Tree('column_name_list',[Token('LP', '(')
                                       , Tree('column_name', [Token('IDENTIFIER', 'col1')])
                                       , Tree('column_name', [Token('IDENTIFIER', 'col2')])
                                       , Tree('column_name', [Token('IDENTIFIER', 'col3')])
                                       , Token('RP', ')')])

        result = self.transform(input)
        expected = ['col1', 'col2', 'col3']

        self.assertListEqual(result, expected)
    
    def test_trans_zero_lengh_char_type(self):
        input = Tree('data_type', [Token('TYPE_CHAR', 'char')
                                 , Token('LP', '(')
                                 , Token('INT', '0')
                                 , Token('RP', ')')])
        
        self.assertRaises((CharLengthError, VisitError), self.transform, input)

    def test_trans_table_element(self):
        input = Tree('table_element', [Tree('column_definition'
                    , [Tree('column_name', [Token('IDENTIFIER', 'ID')]), Tree('data_type', [Token('TYPE_INT', 'INT')])])])
        result = self.transform(input)
        expected = ('col_def', 'id', ('int', -1), True)
        self.assertTupleEqual(result, expected)

    def test_trans_table_element_list(self):
        input = Tree('table_element_list', [Token('LP', '(')
                    , Tree('table_element', [Tree('column_definition'
                        , [Tree('column_name', [Token('IDENTIFIER', 'acc_number')]), Tree('data_type', [Token('TYPE_INT', 'int')]), Token('NOT', 'not'), Token('NULL', 'null')])])
                    , Tree('table_element', [Tree('column_definition'
                        , [Tree('column_name', [Token('IDENTIFIER', 'branch_name')]), Tree('data_type', [Token('TYPE_CHAR', 'char'), Token('LP', '('), Token('INT', '10'), Token('RP', ')')])])])
                    , Tree('table_element', [Tree('table_constraint_definition'
                        , [Tree('primary_key_constraint', [Token('PRIMARY', 'primary'), Token('KEY', 'key')
                        , Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'acc_number')]), Token('RP', ')')])])])])
                    , Token('RP', ')')])
        result = self.transform(input)
        expected = ( {'acc_number': ['int', -1, False], 'branch_name' : ['char', 10, True]}
                   , ['acc_number']
                   , [] )   
        #expected = ( ('col_def', 'acc_number', ('int', -1), False)
        #           , ('col_def', 'branch_name', ('char', 10), True)
        #           , ('PK', ['acc_number'])
        #           )
        self.assertTupleEqual(result, expected)

    def test_trans_table_element_list_long(self):
        input = self.very_long_tree
        result = self.transform(input)
        expected = ( {'id': ['int', -1, False]
                   , 'first_name': ['char', 10, True]
                   , 'middle_name': ['char', 10, True]
                   , 'last_name': ['char', 10, True]
                   , 'date_of_birth': ['date', -1, True]}
                   , ['id']
                   , [(['first_name', 'middle_name', 'last_name'], 'people', ['first_name', 'middle_name', 'last_name'])]
                   )
        self.assertTupleEqual(result, expected)
    
    def test_trans_column_definition_char_type(self):
        input = Tree('column_definition'
                     , [Tree('column_name', [Token('IDENTIFIER', 'branch_name')])
                      , Tree('data_type'
                           , [Token('TYPE_CHAR', 'char')
                                , Token('LP', '('), Token('INT', '10'), Token('RP', ')')])
                        ])
        result = self.transform(input)
        # column_def, table_name, type, nullity
        expected = ('col_def', 'branch_name', ('char', 10), True)
        self.assertTupleEqual(result, expected)

    def test_trans_column_definition_int_type(self):
        input = Tree('column_definition'
                     , [Tree('column_name', [Token('IDENTIFIER', 'acc_number')])
                      , Tree('data_type', [Token('TYPE_INT', 'int')]), 
                             Token('NOT', 'not'), Token('NULL', 'null')
                        ])
        result = self.transform(input) 
        expected = ('col_def', 'acc_number', ('int', -1), False)
        self.assertTupleEqual(result, expected)
    
    def test_trans_primary_constraint(self):
        input = Tree('primary_key_constraint'
                    , [Token('PRIMARY', 'PRIMARY')
                     , Token('KEY', 'KEY')
                     , Tree('column_name_list', [Token('LP', '(')
                     , Tree('column_name', [Token('IDENTIFIER', 'ID')])
                     , Token('RP', ')')])])
        result = self.transform(input)
        expected = ('PK', ['id'])
        self.assertTupleEqual(result, expected)

    def test_trans_referential_constraint(self):
        input = Tree('referential_constraint'
                    , [ Token('FOREIGN', 'FOREIGN')
                      , Token('KEY', 'KEY')
                      , Tree('column_name_list'
                        , [ Token('LP', '(')
                          , Tree('column_name', [Token('IDENTIFIER', 'first_name')])
                          , Tree('column_name', [Token('IDENTIFIER', 'middle_name')])
                          , Tree('column_name', [Token('IDENTIFIER', 'last_name')])
                          , Token('RP', ')')])
                      , Token('REFERENCES', 'REFERENCES')
                      , Tree('table_name', [Token('IDENTIFIER', 'people')])
                      , Tree('column_name_list'
                        , [Token('LP', '(')
                          , Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')]), Tree('column_name', [Token('IDENTIFIER', 'last_name')])
                          , Token('RP', ')')])
                      ])
        result = self.transform(input)
        expected = ('FK', ['first_name', 'middle_name', 'last_name'], 'people', ['first_name', 'middle_name', 'last_name'])
        self.assertTupleEqual(result, expected)