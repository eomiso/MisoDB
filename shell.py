COMMAND = 'Query'
PARAM = 'Param'

from exceptions import SimpleDatabaseError
import sys
from parser import Parser, QueryTransformer
import lark
import test
from execution import init_db, execute

__all__ = ['MisoDBShell']

class MisoDBShell():
    prompt = "DB_2014-15554>"
    intro = "Your input should end with ';' to activate the interpreter"

    def __init__(self, msg=intro):
        if not test.get_test_flg():
            print(msg)
        self.parser = Parser("grammar.lark").get_parser()
        init_db()

    def promptloop(self, prompt=prompt):
        while True:
            for query in self.input_queries(prompt):
                try:
                    tree = self.parser.parse(query)
                    #print(tree.pretty())
                    #print(tree)
                    param = QueryTransformer().transform(tree)
                    execute(param)
                except lark.exceptions.UnexpectedInput:
                    print(prompt + 'SYNTAX ERROR')
                    if test.test_flg: raise
                except lark.exceptions.VisitError as cm:
                    print(prompt + str(cm.__context__))
                    if test.test_flg: raise cm.__context__
                except SimpleDatabaseError as e:
                    print(prompt + str(e))
                    if test.get_test_flg(): raise 
            
                    

    def input_queries(self, prompt):
        s = input(prompt)
        if s == 'quit()':
            self.terminate()
        if not s:
            return []
        while not s.rstrip().endswith(';'):
            s += '\n' + input()
        return [x.lstrip() + ';' for x in s.split(';')[:-1]]
