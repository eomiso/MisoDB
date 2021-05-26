import unittest
from unittest import result
from unittest.case import expectedFailure
from unittest.signals import registerResult
from lark import Tree, Token
from parser import QueryTransformer

from shell import MisoDBShell
import test

from lark.exceptions import VisitError
from exceptions import CharLengthError

test_query0 = """
            CREATE TABLE account(
                acc_number int,
                branch_name char(15),
                balance int NOT NULL,
                PRIMARY KEY(acc_number)
            );"""
test_query1 = """
            INSERT INTO account(acc_number, branch_name, balance) 
            VALUES(12345678, 'sillim', 3000);"""
test_query2 = """
            INSERT INTO account(acc_number, branch_name, balance) 
            VALUES(987655, 'jamsil', 3500);"""

test_query3 = """
            SELECT * FROM account;"""
test_query4 = """
            SELECT * FROM account Where balance > 3000;"""

execution_test_query1 = """
            CREATE TABLE people(
            SECURITY_ID INT,
            first_name char(10),
            middle_name char(10),
            last_name char(10),
            PRIMARY KEY(first_name, middle_name, last_name));"""
execution_test_query2 = """
            CREATE TABLE instructor(
            ID INT,
            first_name char(10),
            middle_name char(10),
            last_name char(10),
            date_of_birth DATE,
            PRIMARY KEY(ID),
            FOREIGN KEY(first_name, middle_name, last_name) REFERENCES people(first_name, middle_name, last_name));"""
execution_test_query3 = """
            CREATE TABLE department(
            dept_name char(15),
            building char(15),
            budget int,
            PRIMARY KEY(dept_name));"""
execution_test_query4 = """
            CREATE TABLE student(
            ID int not null,
            name char(10),
            dept_name char(15),
            tot_cred int,
            PRIMARY KEY(ID),
            FOREIGN KEY(dept_name) REFERENCES department(dept_name));"""
execution_test_query5 = """
            CREATE TABLE advisor(
            s_id int not null,
            i_id int,
            PRIMARY KEY(s_id),
            FOREIGN KEY(i_id) REFERENCES instructor(ID),
            FOREIGN KEY(s_id) REFERENCES student(ID)); """
execution_test_query6 = """
            INSERT INTO instructor VALUES(12345, 'david', 'von', 'park', '1981-09-10');"""
execution_test_query7 = """
            INSERT INTO instructor VALUES(22345, 'James', 'junior', 'Hofer', '1971-09-10');"""
execution_test_query8 = """
            INSERT INTO instructor VALUES(42345, 'Nash', 'spark', 'Lee', '1995-09-10');"""
execution_test_query9 = """
            INSERT INTO student VALUES(42345, 'LEE', 'CS', 150);"""
execution_test_query10 = """
            INSERT INTO student VALUES(42345, 'Cook', 'EEC', 49);"""

test_query6 = """
            select first_name, middle_name
            from people
            where first_name is not null
            and last_name = 'Eom';"""
test_qeury7 = """
            select A.id, B.id
            from instructor as A, students as B
            where A.id = B.id and where instructor.date_of_birth is not null;"""
test_query8 = """
            delete from instructor
            where date_of_birth > '1980-11-08';"""

class TransformerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        test.test_flg = True # wrapper function doesn't seem to work
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

    def test_trans_drop_table_query(self):
        input = 'drop table account;'
        result = self.transform(MisoDBShell().parser.parse(input))
        expected = ('drop', 'account')
        self.assertTupleEqual(result, expected)
    
    def test_trans_desc_table_query(self):
        input = 'desc account;'
        result = self.transform(MisoDBShell().parser.parse(input))
        expected = ('desc', 'account')
        self.assertTupleEqual(result, expected)
        
    def test_trans_show_tables_query(self):
        input = 'show tables;'
        result = self.transform(MisoDBShell().parser.parse(input))
        expected = ('show', 0)
        self.assertTupleEqual(result, expected)
        
    def test_trans_null_operation_is_not_null(self):
        input = Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])
        result = self.transform(input)
        expected = False
        self.assertEqual(result, expected)

    def test_trans_null_operation_is_null(self):
        input = Tree('null_operation', [Token('IS', 'is'),  Token('NULL', 'null')])
        result = self.transform(input)
        expected = True
        self.assertEqual(result, expected)

    def test_trans_null_predicate(self):
        input = Tree('null_predicate', [Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])])
        result = self.transform(input)
        expected = [('attr', 'first_name'), False]

        self.assertListEqual(result, expected)
    
    def test_trans_null_predicate_with_table_name(self):
        input = Tree('null_predicate', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'first_name')]), Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])])
        result = self.transform(input)
        expected = [('attr', 'people', 'first_name'), False]

        self.assertListEqual(result, expected)
    
    def test_trans_comparable_value_str(self):
        input = Tree('comparable_value', [Token('STR', "'EP'")])
        result = self.transform(input)
        expected = ('str', 'EP')
       
        self.assertTupleEqual(result,expected)

    def test_trans_comparable_value_int(self):
        input = Tree('comparable_value', [Token('INT', "5")])
        result = self.transform(input)
        expected = ('int', 5)
       
        self.assertTupleEqual(result,expected)

    def test_trans_comparable_value_date(self):
        input = Tree('comparable_value', [Token('DATE', "1995-07-09")])
        result = self.transform(input)
        expected = ('date', '1995-07-09')
       
        self.assertTupleEqual(result,expected)
    
    def test_trans_comp_operand_comparable_val(self):
        input = Tree('comp_operand', [Tree('comparable_value', [Token('INT', "4")])])
        result = self.transform(input)
        expected = ('int',4)

        self.assertTupleEqual(result,expected)
    
    def test_trans_comp_operand_attr_with_table(self):
        input = Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'first_name')])])
        result = self.transform(input)
        expected = ('attr', 'people', 'first_name')

        self.assertTupleEqual(result,expected)

    def test_trans_comp_operand_attr_without_table(self):
        input = Tree('comp_operand', [Tree('column_name', [Token('IDENTIFIER', 'las_name')])])
        result = self.transform(input)
        expected = ('attr', 'las_name')

        self.assertTupleEqual(result,expected)
    
    def test_trans_comp_predicate(self):
        input = Tree('comparison_predicate', [Tree('comp_operand', [Tree('column_name', [Token('IDENTIFIER', 'id')])]), Token('COMP_OP', '>'), Tree('comp_operand', [Tree('comparable_value', [Token('INT', "4")])])])
        result = self.transform(input)
        expected = ['>', ('attr', 'id'), ('int', 4)]

        self.assertTupleEqual(result,expected)
    
    def test_trans_comp_predicate_str(self):
        input = Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'first_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'DAVID'")])])])
        result = self.transform(input)
        expected = ['=', ('attr', 'people', 'first_name'), ('str', 'david')]

        self.assertTupleEqual(result,expected)
    
    def test_trans_predicate(self):
        input = Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'first_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'David'")])])])])
        result = self.transform(input)
        expected = ['=', ('attr', 'people', 'first_name'), ('str', 'david')]

        self.assertTupleEqual(result, expected)
    
    def test_trans_predicate(self):
        input = Tree('predicate', [Tree('null_predicate', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'id')]), Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])])])
        result = self.transform(input)
        expected = [('attr', 'people', 'id'), False]

        self.assertTupleEqual(result, expected)

    def test_trans_boolean_test_predicate(self):
        input = Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'FON'")])])])])])
        result = self.transform(input)
        expected = ['=', ('attr', 'people', 'middle_name'), ('str', 'fon')]

        self.assertTupleEqual(result, expected)

    def test_trans_boolean_factor(self):
        # select * from people 
        # where people.first_name = 'David' and 
        # people.id is not null and (people.middle_name = 'VON' or people.middle_name = 'FON');
        input = Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'FON'")])])])])])])
        result = self.transform(input)
        expected = ('pos', ['=', ('attr', 'people', 'middle_name'), ('str', 'von')])

        self.assertTupleEqual(result, expected)

    def test_trans_boolean_factor_with_parenthesis(self):
        # select * from people 
        # where people.first_name = 'David' and
        # people.id is not null and 
        # not (people.middle_name = 'VON');
        input = Tree('boolean_factor', [Token('NOT', 'not'), Tree('boolean_test', [Tree('parenthesized_boolean_expr', [Token('LP', '('), Tree('boolean_expr', [Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'VON'")])])])])])])])]), Token('RP', ')')])])])
        result = self.transform(input)
        expected = ('neg', ['=', ('attr', 'people', 'middle_name'), ('str', 'von')])

        self.assertTupleEqual(result, expected)

    def test_trans_boolean_term(self):
        # select * from people where 
        # people.id is not null and people.middle_name = 'VON' and people.last_name = 'Lee';
        # triple and
        input = Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('null_predicate', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'id')]), Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])])])])])
                                     , Token('AND', 'and')
                                     , Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'VON'")])])])])])])
                                     , Token('AND', 'and')
                                     , Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'last_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'Lee'")])])])])])])])
        result = self.transform(input)
        expected = [
                    [('pos', [('attr', 'people', 'id'), False])
                        , ('pos', ['=', ('attr', 'people', 'middle_name'), ('str', 'von')]), 'and']
                    , ('pos', ['=', ('attr', 'people', 'last_name'), ('str', 'lee')])
                    , 'and']

        self.assertListEqual(result, expected)

    def test_trans_boolean_expr_with_parenthesis_behind(self):
        # select * from people where 
        # people.id is not null and (people.middle_name = 'VON' and people.last_name = 'Lee');
        # with parenthesis behind
        input = Tree('boolean_expr', [Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('null_predicate', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'id')]), Tree('null_operation', [Token('IS', 'is'), Token('NOT', 'not'), Token('NULL', 'null')])])])])])
                                                           , Token('AND', 'and')
                                                           , Tree('boolean_factor', [Tree('boolean_test', [Tree('parenthesized_boolean_expr'
                                                                                                                    , [Token('LP', '(')
                                                                                                                     , Tree('boolean_expr', [Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'VON'")])])])])])])
                                                                                                                                                                  , Token('AND', 'and')
                                                                                                                                                                  , Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'last_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'Lee'")])])])])])])])])
                                                                                                                     , Token('RP', ')')])])])])])
        result = self.transform(input)
        expected = [
                        ('pos', [('attr', 'people', 'id'), False])
                        , ('pos', [ ('pos', ['=', ('attr', 'people', 'middle_name'), ('str', 'von')])
                                  , ('pos', ['=', ('attr', 'people', 'last_name'), ('str', 'fon')])
                                  , 'and'])
                        , 'and']
        self.assertListEqual(result, expected)

    def test_trans_parenthesized_boolean_expr(self):
        # select * from people 
        # where people.first_name = 'David' and 
        # people.id is not null and (people.middle_name = 'VON' or people.middle_name = 'FON');
        input = Tree('parenthesized_boolean_expr', [Token('LP', '('), Tree('boolean_expr', [Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'VON'")])])])])])])]), Token('OR', 'or'), Tree('boolean_term', [Tree('boolean_factor', [Tree('boolean_test', [Tree('predicate', [Tree('comparison_predicate', [Tree('comp_operand', [Tree('table_name', [Token('IDENTIFIER', 'people')]), Tree('column_name', [Token('IDENTIFIER', 'middle_name')])]), Token('COMP_OP', '='), Tree('comp_operand', [Tree('comparable_value', [Token('STR', "'FON'")])])])])])])])]), Token('RP', ')')])
        result = self.transform(input)
        expected = ('pos', [ ('pos', ['=', ('attr', 'people', 'middle_name'), ('str', 'von')])
                                  , ('pos', ['=', ('attr', 'people', 'last_name'), ('str', 'fon')])
                                  , 'and'])
        self.assertTupleEqual(result, expected)

# --------------------------------
    def test_trans_value_int(self):
        input = Tree('value', [Tree('comparable_value', [Token('INT', '1234')])])
        result = self.transform(input)
        expected = ('int', 1234)

        self.assertTupleEqual(result, expected)

    def test_trans_value_null(self):
        input = Tree('value', [Token('NULL', 'null')])
        result = self.transform(input)
        expected = ('null', None)

        self.assertTupleEqual(result, expected)

    def test_trans_value_list(self):
        input = Tree('value_list', [Token('VALUES', 'values'), Token('LP', '('), Tree('value', [Tree('comparable_value', [Token('INT', '1234')])]), Tree('value', [Tree('comparable_value', [Token('STR', "'sillim'")])]), Tree('value', [Token('NULL', 'null')]), Token('RP', ')')])
        result = self.transform(input)
        expected = [('int', 1234), ('str', 'sillim'), ('null', None)]

        self.assertListEqual(result, expected)

    def test_trans_insert_columns_and_sources(self):
        input = Tree('insert_columns_and_sources', [Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'acc_number')]), Tree('column_name', [Token('IDENTIFIER', 'branch_name')]), Tree('column_name', [Token('IDENTIFIER', 'balance')]), Token('RP', ')')]), Tree('value_list', [Token('VALUES', 'values'), Token('LP', '('), Tree('value', [Tree('comparable_value', [Token('INT', '1234')])]), Tree('value', [Tree('comparable_value', [Token('STR', "'sillim'")])]), Tree('value', [Token('NULL', 'null')]), Token('RP', ')')])])
        result = self.transform(input)
        expected = (['acc_number', 'branch_name', 'balance'], [('int', 1234), ('str', 'sillim'), ('null', None)])

        self.assertTupleEqual(result, expected)

    def test_trans_insert_columns_and_sources_empty_columns(self):
        input = Tree('insert_columns_and_sources', [Tree('value_list', [Token('VALUES', 'values'), Token('LP', '('), Tree('value', [Tree('comparable_value', [Token('INT', '1234')])]), Tree('value', [Tree('comparable_value', [Token('STR', "'sillim'")])]), Tree('value', [Token('NULL', 'null')]), Token('RP', ')')])])
        result = self.transform(input)
        expected = ([], [('int', 1234), ('str', 'sillim'), ('null', None)])

        self.assertTupleEqual(result, expected)

    def test_input_query(self):
        input = Tree('command', [Tree('query_list', [Tree('query', [Tree('insert_query', [Token('INSERT', 'Insert'), Token('INTO', 'into'), Tree('table_name', [Token('IDENTIFIER', 'account')]), Tree('insert_columns_and_sources', [Tree('column_name_list', [Token('LP', '('), Tree('column_name', [Token('IDENTIFIER', 'acc_number')]), Tree('column_name', [Token('IDENTIFIER', 'branch_name')]), Tree('column_name', [Token('IDENTIFIER', 'balance')]), Token('RP', ')')]), Tree('value_list', [Token('VALUES', 'values'), Token('LP', '('), Tree('value', [Tree('comparable_value', [Token('INT', '1234')])]), Tree('value', [Tree('comparable_value', [Token('STR', "'sillim'")])]), Tree('value', [Token('NULL', 'NULL')]), Token('RP', ')')])])])])])])

        result = self.transform(input)
        expected = ('insert', 'account', ['account', 'branch_name', 'balance'], [('int',1234), ('str', 'sillim'), ('null', None)])

        self.assertTupleEqual(result, expected)
    
    def test_input_query(self):
        input = Tree('command', [Tree('query_list', [Tree('query', [Tree('insert_query', [Token('INSERT', 'Insert'), Token('INTO', 'into'), Tree('table_name', [Token('IDENTIFIER', 'account')]), Tree('insert_columns_and_sources', [Tree('value_list', [Token('VALUES', 'values'), Token('LP', '('), Tree('value', [Tree('comparable_value', [Token('INT', '1234')])]), Tree('value', [Tree('comparable_value', [Token('STR', '"sillim"')])]), Tree('value', [Token('NULL', 'null')]), Token('RP', ')')])])])])])])

        result = self.transform(input)
        expected = ('insert', 'account', [], [('int',1234), ('str', 'sillim'), ('null', None)])

        self.assertTupleEqual(result, expected)
