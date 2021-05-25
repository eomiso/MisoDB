class SimpleDatabaseError(Exception):
    pass

class CreateTableError(SimpleDatabaseError):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return f"Create table has failed: {self.msg}"

class DropTableError(SimpleDatabaseError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f"Drop table has failed: {self.msg}"

class InsertError(SimpleDatabaseError):
    pass
class DeleteError(SimpleDatabaseError):
    pass
class SelectError(SimpleDatabaseError):
    pass
class WhereError(SimpleDatabaseError):
    pass
class NoSuchTable(SimpleDatabaseError):
    def __str__(self):
        return "No such Table"


class SelectTableExistenceError(SelectError):
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return f"Selection has failed: '{self.msg}' does not exist"


class SelectColumnResolveError(SelectError):
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return f"Selection has failed: failed to resolve '{self.msg}'"

class DuplicateColumnDefError(CreateTableError):
    def __init__(self):
        super().__init__("column definition is duplicated")

class DuplicatePrimaryKeyDefError(CreateTableError):
    def __init__(self):
        super().__init__("primary key definition is duplicated")

class ReferenceTypeError(CreateTableError):
    def __init__(self):
        super().__init__("foreign key references wrong type")

class ReferenceNonPrimaryKeyError(CreateTableError):
    def __init__(self):
        super().__init__("foreign key references non primary key column")

class ReferenceColumnExistenceError(CreateTableError):
    def __init__(self):
        super().__init__("foreign key references non existing column")

class ReferenceTableExistenceError(CreateTableError):
    def __init__(self):
        super().__init__("foreign key references non existing table")

class NonExistingColumnDefError(CreateTableError):
    def __init__(self, col_name):
        super().__init__(f"'{col_name}' does not exists in column definition")

class TableExistenceError(SimpleDatabaseError):
    def __init__(self):
        super().__init__("table with the same name already exists")

class DropSuccess(SimpleDatabaseError):
    def __init__(self, table_name):
        super().__init__(f"{self.__class__.__name__}: '{table_name}' table is dropped\n")

class DropReferencedTableError(DropTableError):
    def __init__(self, table_name):
        super().__init__(f"'{table_name}' is referenced by other table") 

class NoSuchTable(SimpleDatabaseError):
    def __str__(self):
        return "No such table"

class CharLengthError(SimpleDatabaseError):
    def __str__(self):
        return "Char length should be over 0"

class ReferenceSameTableError(SimpleDatabaseError):
    def __init__(self):
        super().__init__(f"{self.__class__.__name__}: Referencing the table that is containing the foreign key\n")

class InsertionError(SimpleDatabaseError):
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

class DeletionError(CreateTableError):
    pass

class DeleteResult(DeletionError):
    def __init__(self, count):
        super().__init__(f"{count} row(s) are deleted\n")
class DeleteReferentialIntegrityPassed(DeletionError):
    def __init__(self, count):
        super().__init__(f"{count} row(s) are not deleted due to referential integrity\n")

class WhereError(CreateTableError):
    pass

class WhereIncomparableError(WhereError):
    def __init__(self):
        super().__init__("Where clause try to compare incomparable values\n")

class WhereTableNotSpecified(WhereError):
    def __init__(self):
        super().__init__("Where clause try to reference tables which are not specified\n")

class WhereColumnNotExist(WhereError):
    def __init__(self):
        super().__init__("Where clause try to reference non existing column\n")