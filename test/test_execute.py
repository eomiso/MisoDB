import unittest
from unittest import result
from lark import Tree, Token
from parser import QueryTransformer

import test

from shell import MisoDBShell
from execution import *

from lark.exceptions import VisitError
from exceptions import CharLengthError

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

class ExecutionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.transform = QueryTransformer().transform
        test.test_flg = True 
        return super().setUp()
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_execute(self,):
        input = create_query
        result = self.transform(MisoDBShell().parser.parse(input))
        execute(result)
