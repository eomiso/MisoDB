class RelationalDBException(Exception):
    def __init__(self, messages):
        super().__init__(messages)

class CreateTableSuccess(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: '{table_name}' table is created\n")

class DuplicateColumnDefError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: column definition is duplicated\n")

class DuplicatePrimaryKeyDefError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: primary key definition is duplicated\n")

class ReferenceTypeError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references wrong type\n")

class ReferenceNonPrimaryKeyError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references non primary key column\n")

class ReferenceColumnExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references non existing column\n")

class ReferenceTableExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}:  Create table has failed: foreign key references non existing table\n")

class NonExistingColumnDefError(RelationalDBException):
    def __init__(self, col_name):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: '{col_name}' does not exists in column definition\n")

class TableExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: table with the same name already exists\n")

class DropSuccess(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: '{table_name}' table is dropped\n")

class DropReferencedTableError(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: Drop table has failed: '{table_name}' is referenced by other table\n") 

class NoSuchTable(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: No such table\n")

class CharLengthError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Char length should be over 0\n")