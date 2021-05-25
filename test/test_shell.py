from io import StringIO
import unittest
from unittest.mock import patch
from lark.exceptions import UnexpectedToken
import test
from shell import MisoDBShell

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
    @patch('builtins.input', return_value='desc table hello; sdifj; ijw;')
    def test_syntax_error_erroneous_input(self, mock_input):
        #with self.assertRaises(UnexpectedToken) as cm:
        #    self.shell.promptloop()
        self.assertRaises(UnexpectedToken, self.shell.promptloop)

    """
    (3) Check if the correct input passes without error
    """
    @patch('builtins.input', 
            side_effect=['desc ', 'hello;', 'select *', 'from account;', 'quit()'])
    def test_syntax_error_correct_input(self, mock_input):
        try:
            self.shell.promptloop()
        except SystemExit:
            pass


if __name__ == "__main__":
    unittest.main()