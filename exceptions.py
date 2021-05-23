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

class ForeignKeyandReferenceKeyNumMatchError(RelationalDBException):
    def __init__(self, foreign, reference):
        super().__init__(f"{self.__class__.__name__}: Create table has failed: foreign key '{foreign}' and reference key '{reference}' doesn't match in number\n")

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

class ReferenceSameTableError(RelationalDBException):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Referencing the table that is containing the foreign key\n")

class InsertionError(RelationalDBException):
    pass

class InsertTypeMismatchError(InsertionError):
    def __init__(self):
        super().__init__("Insertion has failed: Types not matched\n")

class InsertColumnNonNullableError(InsertionError):
    def __init__(self, col_name):
        super().__init__(f"Insertion has failed: '{col_name}' is not nullable\n")

class InsertColumnExistenceError(InsertionError):
    def __init__(self, col_name):
        super().__init__(f"Insertion has failed: '{col_name}' does not exist\n")

class InsertDuplicatePrimaryKeyError(InsertionError):
    def __init__(self):
        super().__init__(f"Insertion has failed: Primary Key duplication\n")

class InsertReferentialIntegrityError(InsertionError):
    def __init__(self):
        super().__init__(f"Insertion has failed: Referential integrity violation\n")