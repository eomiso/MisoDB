class RelationalDBException(Exception):
    def __init__(self, messages):
        super().__init__(messages)

class CreateTableSuccess(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: '{table_name}' table is created")

class DuplicateColumnDefError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: column definition is duplicated")

class DuplicatePrimaryKeyDefError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: primary key definition is duplicated")

class ReferenceTypeError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references wrong type")

class ReferenceNonPrimaryKeyError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references non primary key column")

class ReferenceColumnExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key references non existing column")

class ReferenceTableExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}:  Create table has failed: foreign key references non existing table")

class NonExistingColumnDefError(RelationalDBException):
    def __init__(self, col_name):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: '{col_name}' does not exists in column definition")

class TableExistenceError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: table with the same name already exists")

class DropSuccess(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: '{table_name}' table is dropped")

class DropReferencedTableError(RelationalDBException):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: Drop table has failed: '{table_name}' is referenced by other table") 

class NoSuchTable(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: No such table")

class CharLengthError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Char length should be over 0")