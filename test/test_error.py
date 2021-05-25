

import unittest
from unittest.mock import patch
from lark.exceptions import UnexpectedToken
import test
from shell import MisoDBShell
from exceptions import *

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


class ErrorTestCase(unittest.TestCase):
    def setUp(self):
        test.test_flg = True
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