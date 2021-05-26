

from relationdb import MisoDB
import unittest
from unittest.mock import patch
from lark.exceptions import UnexpectedToken
import test
from shell import MisoDBShell
from exceptions import *
import os
from parser import QueryTransformer
from execution import *


duplicate_primary_create_query = """
                        CREATE TABLE people(
                        SECURITY_ID INT not null,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        PRIMARY KEY(SECURITY_ID),
                        PRIMARY KEY(first_name, middle_name, last_name));"""
non_existing_col_create_query = """
                        CREATE TABLE people(
                        SECURITY_ID INT not null,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        PRIMARY KEY(error_name, middle_name, last_name));""" 
non_existing_col_foreign_create_query = """
                        CREATE TABLE instructor(
                        ID INT not null,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        date_of_birth DATE,
                        PRIMARY KEY(ID),
                        FOREIGN KEY(error_name, middle_name, last_name) REFERENCES people(first_name, middle_name, last_name));"""
duplicate_column_create_query = """
                        CREATE TABLE people(
                        SECURITY_ID INT not null,
                        security_id INT,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        PRIMARY KEY(first_name, middle_name, last_name));""" 

char_length_erroneous_create_query = """
                        CREATE TABLE people(
                        SECURITY_ID INT not null,
                        first_name char(0),
                        middle_name char(10),
                        last_name char(10),
                        PRIMARY KEY(first_name, middle_name, last_name));""" 

test_query1 = """
                    CREATE TABLE people(
                    SECURITY_ID INT,
                    first_name char(10),
                    middle_name char(10),
                    last_name char(10),
                    PRIMARY KEY(SECURITY_ID));"""
test_query2 = """
                    CREATE TABLE instructor(
                    ID INT,
                    first_name char(10),
                    middle_name char(10),
                    last_name char(10),
                    date_of_birth DATE,
                    PRIMARY KEY(ID),
                    FOREIGN KEY(first_name, middle_name, last_name) REFERENCES people(first_name, middle_name, last_name));"""

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
erroneous_test_query6 = """
            DROP TABLE people;"""
test_query7 = """
            DESC people;"""

TEST = 'testBDB.db'

class ErrorTestCase(unittest.TestCase):
    def setUp(self):
        test.test_flg = True
        print(test.get_test_flg())
        self.transform = QueryTransformer().transform

        self.shell = MisoDBShell()
    def tearDown(self) -> None:
        return super().tearDown()
    

    @patch('builtins.input', side_effect = [duplicate_column_create_query, 'exit'])
    def test_duplicate_column_def_error(self, mock_input):
        self.assertRaises(DuplicateColumnDefError, self.shell.promptloop)

    @patch('builtins.input', side_effect = [non_existing_col_create_query, 'exit'])
    def test_non_existing_column_def_error_primary(self, mock_input):
        self.assertRaises(NonExistingColumnDefError, self.shell.promptloop)

    @patch('builtins.input', side_effect = [non_existing_col_foreign_create_query, 'exit'])
    def test_non_existing_column_def_error_foreign(self, mock_input):
        self.assertRaises(NonExistingColumnDefError, self.shell.promptloop)

    @patch('builtins.input', side_effect = [duplicate_primary_create_query, 'exit'])
    def test_duplicate_primary_key_def_error(self, mock_input):
        self.assertRaises(DuplicatePrimaryKeyDefError, self.shell.promptloop)

    @patch('builtins.input', side_effect = [char_length_erroneous_create_query, 'exit'])
    def test_char_length_error(self, mock_input):
        self.assertRaises(CharLengthError, self.shell.promptloop)
    
    def test_reference_non_primary_key_error(self):
        if os.path.exists('testBDB.db'):
            os.remove('testBDB.db')
        input = test_query1, test_query2

        for i, q in enumerate(input):
            param = self.transform(MisoDBShell().parser.parse(q))
            if i == 1:
                self.assertRaises(ReferenceNonPrimaryKeyError, execute, param)
            else:
                execute(param)

    def test_drop_referenced_table_error(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1, execution_test_query2, execution_test_query3, execution_test_query4, execution_test_query5, erroneous_test_query6

        for i, q in enumerate(input):
            param = self.transform(MisoDBShell().parser.parse(q))
            if i == 5:
                self.assertRaises(DropReferencedTableError, execute, param)
            else:
                execute(param)

    def test_drop_table_no_such_table_error(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = "drop table error_name;"
        param = self.transform(MisoDBShell().parser.parse(input))

        self.assertRaises(NoSuchTable, execute, param)