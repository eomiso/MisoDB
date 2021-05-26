import unittest
from unittest import result
from unittest.mock import patch
from lark import Tree, Token
from parser import QueryTransformer

import test


from execution import *
from shell import MisoDBShell

from lark.exceptions import VisitError
from exceptions import CharLengthError

import pathlib as pl
import os
import io

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
test_query6 = """
            DROP TABLE advisor;"""
test_query7 = """
            DESC people;"""

TEST = 'testBDB.db'

class ExecutionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.transform = QueryTransformer().transform
        test.test_flg = True
        self.maxDiff = None
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_init_db(self):
        if os.path.exists('testBDB.db'):
            os.remove('testBDB.db')
        init_db()
        file = 'testBDB.db'
        self.assertTrue(pl.Path(file).resolve().is_file())

    def test_execute(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1
        param = self.transform(MisoDBShell().parser.parse(input))
        execute(param)
    
    def test_create_table_check_meta_datas(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1
        param = self.transform(MisoDBShell().parser.parse(input))
        execute(param)

        expected_tables = {'people'}
        expected_attrs = {'people.security_id', 'people.first_name', 'people.middle_name', 'people.last_name'}
        with MisoDB(TEST) as db:
            self.assertSetEqual(db['.meta.tables'], expected_tables)
            self.assertSetEqual(db['.meta.attrs'], expected_attrs)

    def test_create_table_check_primary_keys(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1
        param = self.transform(MisoDBShell().parser.parse(input))
        execute(param)
        name = 'people'
        with MisoDB(TEST) as db:
            self.assertListEqual(db['people.pk'], ['first_name', 'middle_name', 'last_name'])

    def test_create_table_check_attr_dict(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1
        param = self.transform(MisoDBShell().parser.parse(input))
        execute(param)
        name = 'people'

        expected = {
            'security_id':['int', -1, True],
            'first_name':['char', 10, False],
            'middle_name':['char', 10, False],
            'last_name':['char', 10, False]
        }

        with MisoDB(TEST) as db:
            self.assertDictEqual(db['people.ad'], expected)

    def test_create_table_check_foreign_keys(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1, execution_test_query2, execution_test_query3, execution_test_query4, execution_test_query5

        for q in input:
            param = self.transform(MisoDBShell().parser.parse(q))
            execute(param)

        with MisoDB(TEST) as db:
            res1 = []
            res2 = [(['first_name', 'middle_name', 'last_name'], 'people', ['first_name', 'middle_name', 'last_name'])]
            res3 = []
            res4 = [(['dept_name'], 'department', ['dept_name'])]
            res5 = [(['i_id'], 'instructor', ['id']), (['s_id'], 'student', ['id'])]
            self.assertListEqual(db['people.fk'], res1)
            self.assertListEqual(db['instructor.fk'], res2)
            self.assertListEqual(db['department.fk'], res3)
            self.assertListEqual(db['student.fk'], res4)
            self.assertListEqual(db['advisor.fk'], res5)
    
    def test_create_table_check_foreign_keys_consistency(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1, execution_test_query2, execution_test_query3, execution_test_query4, execution_test_query5

        for q in input:
            param = self.transform(MisoDBShell().parser.parse(q))
            execute(param)

        with MisoDB(TEST) as db:
            res1 = 1
            res2 = [('first_name', 'instructor', 'first_name'), ('middle_name', 'instructor', 'middle_name'), ('last_name', 'instructor', 'last_name')]
            self.assertEqual(db['people.rf.cnt'], res1)
            self.assertListEqual(db['people.rf'], res2)

    def test_drop_table(self):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1, execution_test_query2, execution_test_query3, execution_test_query4, execution_test_query5, test_query6

        for i, q in enumerate(input):
            param = self.transform(MisoDBShell().parser.parse(q))
            execute(param)

        with MisoDB(TEST) as db:
            self.assertRaises(KeyError, lambda: db['advisor.ad'])
            self.assertTrue('advisor' not in db['.meta.tables'])
            self.assertTrue('advisor.i_id' not in db['.meta.attrs'] and 'advisor.s_id' not in db['.meta.attrs'])
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_desc_table(self, mock_stdout):
        if os.path.exists(TEST):
            os.remove(TEST)
        input = execution_test_query1, execution_test_query2, execution_test_query3, execution_test_query4, execution_test_query5, test_query6, "desc people;"

        expected_output = "'people' table is created\n"
        expected_output += "'instructor' table is created\n"
        expected_output += "'department' table is created\n"
        expected_output += "'student' table is created\n"
        expected_output += "'advisor' table is created\n"
        expected_output += "'advisor' table is dropped\n"
        expected_output += "-------------------------------------------------\n"
        expected_output += "table_name [people]\n"
        expected_output += "column_name           type          null          key           \n"
        expected_output += "security_id           int           Y                           \n"
        expected_output += "first_name            char10        N             PRI           \n"
        expected_output += "middle_name           char10        N             PRI           \n"
        expected_output += "last_name             char10        N             PRI           \n"
        expected_output += "-------------------------------------------------\n"

        for i, q in enumerate(input):
            param = self.transform(MisoDBShell().parser.parse(q))
            execute(param)
        
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_tables(self,mock_stdout):
        if os.path.exists(TEST):
            os.remove(TEST)
        inputs = execution_test_query1, execution_test_query2, "show tables;"

        for i, q in enumerate(inputs):
            param = self.transform(MisoDBShell().parser.parse(q))
            execute(param)

        expected_output = "'people' table is created\n"
        expected_output += "'instructor' table is created\n"
        expected_output += "----------------\n"
        expected_output += "instructor\n"
        expected_output += "people\n"
        expected_output += "----------------\n"
        
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_select_records_check_from_join(self):
        pass
    def test_select_records_check_where(self):
        pass

    def test_select_records_all_attrs(self):
        pass
    def test_select_records_particular_attrs(self):
        pass
