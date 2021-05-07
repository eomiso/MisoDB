import sys
import parser
from parser import Parser, MyTransformer
import lark
import re
from tabledb import RelationDB
from utils import get_index
from exceptions import *


PROMPT="DB_2014-15554> "
INTRO="Your input should end with ';' to activate the interpreter."

COMMAND = 'Query'
PARAM = 'Param'

class PromptShell:
    """ A shell for a prompt.
        Referenced python standard library cmd.py.
        https://github.com/python/cpython/blob/3.9/Lib/cmd.py
    """
    sql_parser = Parser().sql_parser # class Lark from parser.py
    transformer = MyTransformer() # class inheriting Transformer from parser.py
    db = RelationDB('myDB.db')

    def __init__(self):
        """ Instantiate a interpreter framework""" 
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.prompt = PROMPT # line 8. 'DB_2014-15554> '
        self.input_queue = []
        self.query = ""

    def add_input_queue(self, input: str) -> None:
        """ Add to input_queue unless the input_queue is empty.
            If input_queue is empty then, pressing enter should print
            prompt again. While input_queue not empty, then prompt 
            shouldn't print and continue receiving input from self.stdin.
        """
        if input != '' :
            self.input_queue.append(input)

    def read_line(self):
        """ Read a line from sys.stdin. Should get read of '\n' and '\t'.
            then the 
        """
        line = self.stdin.readline().replace('\n', '').replace('\t', '')
        self.add_input_queue(line) # add to input_queue unless empty

    def flush_query(self):
        """ Flush the input_queue after joining them as a query
        """
        self.input_queue=[]
        self.query = ""

    def check_endof_line(self, opnd):
        # A method for checking if the end of the input string is ';'
        return self.input_queue[-1][-1] == opnd

    def error_handler(self, token):
        """ A method for handling UnexpectedToken exception.
            token : the token should be lark.Token type.

        """
        # pos_in_stream from lark.Token.pos_in_stream
        self.query = self.query[:token.pos_in_stream]

        # get the index of the last ';' before the eroneous query
        pos = get_index(self.query, ';', reverse=True, count=1)

        if pos == -1:
            # error in the first query
            self.transformer.add_syntax_error()
            return
        # get the correct queries before the eroneous one.
        self.query = self.query[:pos+1] 
        t = self.sql_parser.parse(self.query)
        self.transformer.error_handler(t)
        
    def promptloop(self, intro=INTRO):
        """ Repeatedly issue a prompt, accept input, parse using 
            a parser. Print out appropriate string to the prompt.
            The approprate strings are handled in MyTransformer
            from parser.py
        """
        if intro is not None:
            self.intro = intro
        if self.intro is not None:
            self.stdout.write(str(self.intro)+'\n')
        stop = None

        while not stop:
            self.stdout.write(self.prompt)
            self.stdout.flush()
            
            # get input from prompt
            self.read_line()
            while (len(self.input_queue)!=0):
                # continue reading line without printing prompt
                # until there is ";" at the end of input
                if self.check_endof_line(";"):
                    self.stdout.write(self.prompt)
                    # parse the queries stacked so far
                    self.query = " ".join(self.input_queue)
                    try:
                        t = self.sql_parser.parse(self.query)
                        t = self.transformer.transform(t) 
                    except lark.exceptions.UnexpectedToken as error:
                        self.error_handler(error.token)    
                    
                    # TODO make the methods to compute the database

                    for query in t:
                        try:
                            getattr(self.db, query[COMMAND])(query[PARAM]) # t[QUERY] could_be create_table, desc_table ...
                        except RelationalDBException:
                            pass
                    # queues: prompt messages to be printed in order

                    while (parser._queues):
                        # print the responses to queries
                        self.stdout.write(parser._queues.pop(0))
                        self.stdout.flush
                        if (parser._queues):
                            self.stdout.write(self.prompt)

                    self.stdout.flush()
                    self.flush_query()
                    # foto the prompt printing
                    break

                self.read_line()    
                



            
            

