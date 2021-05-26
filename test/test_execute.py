import unittest
from unittest import result
from lark import Tree, Token
from parser import QueryTransformer

import test


from execution import *
from shell import MisoDBShell

from lark.exceptions import VisitError
from exceptions import CharLengthError

import pathlib as pl
import os

create_query = """ 
               CREATE TABLE teaches(
               id INT not null,
               course_id INT,
               sec_id INT,
               semester CHAR(8),
               year CHAR(4),
               PRIMARY KEY(id),
               FOREIGN KEY(course_id) REFERENCES section(sec_id),
               FOREIGN KEY(course_id) REFERENCES section(course_id));"""

execution_test_query1 = """
            CREATE TABLE people(
            SECURITY_ID INT,
            first_name char(10),
            middle_name char(10),
            last_name char(10),
            PRIMARY KEY(SECURITY_ID));"""
execution_test_query2 = """
            CREATE TABLE instructor(
            ID INT,
            first_name char(10),
            middle_name char(10),
            last_name char(10),
            date_of_birth DATE,
            PRIMARY KEY(ID),
            PRIMARY KEY(first_name, middle_name, last_name)
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
            dept_name,
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

class ExecutionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists('testBDB.db'):
            os.remove('testBDB.db')
        else:
            print("'testBDB.db' does not exist")
        self.transform = QueryTransformer().transform
        test.test_flg = True
        print(test.get_test_flg())
        return super().setUp()
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_execute(self):
        input = execution_test_query1
        result = self.transform(MisoDBShell().parser.parse(input))
        print(result)
        execute(result)

    def test_init_db(self):
        init_db()
        file = 'testBDB.db'
        self.assertTrue(pl.Path(file).resolve().is_file())


