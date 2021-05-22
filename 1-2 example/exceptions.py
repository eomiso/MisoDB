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
    def __init__(self, column):
        super().__init__(f"'{column}' does not exists in column definition")


class TableExistenceError(CreateTableError):
    def __init__(self):
        super().__init__("table with the same name already exists")


class DropReferencedTableError(DropTableError):
    def __init__(self, table):
        super().__init__(f"'{table}' is referenced by other table")


class NoSuchTable(SimpleDatabaseError):
    def __str__(self):
        return "No such table"


class CharLengthError(SimpleDatabaseError):
    def __str__(self):
        return "Char length should be over 0"
