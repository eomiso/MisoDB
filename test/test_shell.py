from exceptions import SimpleDatabaseError
import unittest
from unittest.mock import patch
from lark.exceptions import UnexpectedToken
import test
from shell import MisoDBShell
from execution import init_db

import os

db = 'testBDB.db'

class ShellTestCase(unittest.TestCase):
    def setUp(self) -> None:
        test.test_flg = True
        self.shell = MisoDBShell()
        return super().setUp()
    def tearDown(self) -> None:
        return super().tearDown() 
    """
    (1) Check the input splition single line
    """
    @patch('builtins.input', return_value='desc table hello; sdifj; ijw;')
    def test_input_queries_single_line(self, mock_input):
        # [RELEASE] expected_prompt = "MisoDB>"
        result = self.shell.input_queries("Testing")
        expected = ['desc table hello;', 'sdifj;', 'ijw;']

        self.assertListEqual(result, expected)


    """
    (2) Check the input splition multiple line
    """
    @patch('builtins.input', side_effect=['desc table', 'hello; sdi', 'fj; ijw;'])
    def test_input_queries_multi_line(self, mock_input):
        # [RELEASE] expected_prompt = "MisoDB>"
        result = self.shell.input_queries("Testing")
        expected = ['desc table\nhello;', 'sdi\nfj;', 'ijw;']

        self.assertListEqual(result, expected)

    """
    (2) Check if the syntaxerror is raised with erroneous input
    """
    @patch('builtins.input', side_effect=['desc table hello; sdifj; ijw;','exit' ])
    def test_syntax_error_erroneous_input(self, mock_input):
        #with self.assertRaises(UnexpectedToken) as cm:
        #    self.shell.promptloop()
        self.assertRaises(UnexpectedToken, self.shell.promptloop)

    """
    (3) Check if the correct input passes without error
    """
    @patch('builtins.input', 
            side_effect=['desc ', 'hello;', 'select *', 'from account;', 'exit'])
    def test_syntax_error_correct_input(self, mock_input):
        if os.path.exists(db):
            os.remove(db)
        init_db()
        try:
            self.assertRaises(SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass
    
    @patch('builtins.input', 
            side_effect=['create table account(acc_number int not null,  \
                           branch_name char(10), primary key(acc_number));', 'exit'])
    def test_syntax_error_correct_input_create_query(self, mock_input):
        if os.path.exists(db):
            os.remove(db)
        init_db()
        try:
            self.assertRaises(StopIteration or SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass

    @patch('builtins.input', 
            side_effect=["""
                        CREATE TABLE teaches(
                        id INT not null,
                        course_id INT,
                        sec_id INT,
                        semester CHAR(8),
                        year CHAR(4),
                        PRIMARY KEY(id),
                        FOREIGN KEY(course_id) REFERENCES section(sec_id),
                        FOREIGN KEY(course_id) REFERENCES section(course_id));"""
                        , """
                        CREATE TABLE instructor(
                        ID INT not null,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        date_of_birth DATE,
                        PRIMARY KEY(ID),
                        FOREIGN KEY(first_name, middle_name, last_name) REFERENCES people(first_name, middle_name, last_name));"""
                        , """
                        CREATE TABLE people(
                        SECURITY_ID INT not null,
                        first_name char(10),
                        middle_name char(10),
                        last_name char(10),
                        PRIMARY KEY(first_name, middle_name, last_name));"""
                        , 'exit'])
    def test_syntax_error_correct_input_create_query_with_foreign_primary(self, mock_input):
        try:
            self.assertRaises(SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass


    @patch('builtins.input', 
            side_effect=["""
                       select customer_name, borrower.loan_number, amount
                       from borrower as B, loan
                       where borrower.loan_number = loan.loan_number
                       and branch_name = 'Perryridge';
                    """, 'exit'])
    def test_syntax_error_correct_input_select_query(self, mock_input):
        if os.path.exists(db):
            os.remove(db)
        init_db()
        try:
            self.assertRaises(SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass

    @patch('builtins.input', 
            side_effect=["""
                       delete from account
                       where branch_name = 'Perryridge';
                    """, 'exit'])
    def test_syntax_error_correct_input_delete_query(self, mock_input):
        try:
            self.assertRaises(SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass

    @patch('builtins.input', 
            side_effect=["""
                       delete from account
                       where branch_name = 'Perryridge';
                    """, 'exit'])
    def test_syntax_error_correct_input_select_query(self, mock_input):
        try:
            self.assertRaises(SystemExit, self.shell.promptloop)
        except SimpleDatabaseError:
            pass

if __name__ == "__main__":
    unittest.main()