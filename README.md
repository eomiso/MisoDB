---
author : Uiseop Eom
student number : 2014-15554

project name : database 1-2
---

## Index
1. [Data Structure of Schema](#schema)
2. [RelationDB class](#relationdb)
3. [Table & Column Class](#table_column)
4. [Transformer Class](#parser)
5. [Misc: Errors, ... etc](#etc)

## 1. <a name="schema">Data Structure of Schema</a>
Basically the data structure of a set of table schema's is maintained as a dictionary.
It looks like below, where `Table()` is a dictionary like custom class used for saving table
meta informations such as names, primary keys, foreign key definitions, and column definitions.
The column definitions are saved in another dictionary like class `Column()`.

```
{
    'table1_name' : Table(),
    'table2_name' : Table(),
    ...
}
```

You can access a table's schema by using it's name as a key. i.e. `self.schema_list['student']`.
(`self.schema_list` is the attribute of RelationDB that calls and saves the schema dictionary from `myDB.db`)
If you want to change the name of the dictionary go to PromptShell and change the `filename` parameter to `RelationDB()`

To call the schema dictionary from the database, you have to use a gobal key `_schema_list_key` in `tabledb.py`.
It is serialized by the global method `_encode_str()`, then used as a key to retriev data from the database. The retreived
data should also be decrypted, which is done by `_decode_pickle()`

## 2. <a name="relationdb">RelationDB class</a>
`RelationDB` is where every implementation of the queries are. Ones initialized, it calls for
the schema dictionary and saves it in `self.schema_list`.

It has inner classes `Table()` which is a dictionary like class used as a data structure for a table schema.
Details on the `Table()` and `Column()` classes are in section 3.

The Errors checked inside `RelationDB()` class are as below.
```
NoSuchTable()
DropReferencedTableError(#tablename)
TableExistenceError()
DuplicateColumnDefError()
DuplicatePrimaryKeyDefError()
NonExistingColumnDefError(#columnname)
```
Other Errors that concerns Reference key constraints are dealt with in `Column()` class.

## 3. <a name="table_column">Table & Column Class</a>
The `Table` inner class of `RelationDB` that receives schema dictionary, table name, column definitions, primary key(s), foreign key definitions, and
builds a wrapper class that has all the meta data of the table, including a dictionary containing all the column informations.

The attributes are as such.
```
self[TN] : str
    name of table
self[PRI] : list
    a list of primary key. A list with single entry if the 
    primary key is not a composite key.
self[FOR] : dict
    a dictionary of foreign key definitions. The dictionary
    looks like this.
    {
        (foreign_key1, foreign_key2) : (ref table_name, (ref_key1, ref_key2))
        (foreign_key3) : (ref table_name, (ref_key3))
    }
self[REFTAB] : set
    a set of table_names that this table refers to. this set is used to check if any
    table is being referenced by another table. The schema dictionary would have to be
    iterated to check this.
self[COL] : dict
    a dictionary of columns in a table. The dictionary looks like this.
    {
        'col_name1' : Column()
        'col_name2' : Column()
    }
```

`Column` class is a inner class of `Table` that saves all the meta data of columns including
its name, data_type, nullity, primary, foreign characters.
This class also inherits from `collections.UserDict()` so it can be handled like a normal dictionary as well.

The attributes to this class are as such below.
```
self[CN] : str
self[DT] : DataType
self[NONULL] : bool
self[PRI] : bool
self[FOR] : Nonetype or dict
    None | (ref table name, ref column)


(foreign key1, foreign key2) -> (ref key1, ref key2)
Each keys are expected to reference to reference key in order. Thereby
foreign key1 -> ref key1
foreign key2 -> ref key2

if the number of composite keys doensn't match it would throw ReferenceTypeError.

```
`DataType` is a custom class for efficient data type handling. It makes use of magic methods for
`==`(equal) operation and printing.

The Errors dealt inside `Column` class are as such:
```
ReferenceTableExistenceError()
ReferenceColumnExistenceError()
ReferenceTypeError()
ReferenceNonPrimaryKeyError()
```

## 4. <a name="parser">Transformer Class</a>
There has been change in the Transformer class to make sure that it parses the query into a
structure that is apprehencible to this specific application. Thereby I have decided to parse the
query into a dictionary.

For example a query
```
input query:
create table student(student_number int, name char(10), acc_num int, foreign key(acc_num) references account(acc_number));

after transformation:
[{'Query': 'create_table', 'Param': {
    'Table_Name': 'student', 'Elem_List': [
    {'Col_Def': {'Col_Name': 'student_number', 'Data_Type': 'int'}}, 
    {'Col_Def': {'Col_Name': 'name', 'Data_Type': 'char(10)'}}, 
    {'Col_Def': {'Col_Name': 'acc_num', 'Data_Type': 'int'}}, 
    {'foreign_key': (['acc_num'], 'account', ['acc_number'])}
    ]}
}]
```

The value of 'Query' and 'Param' are used as a method and parameter for calling the respective
method from `RelationDB`.
Look into `shell.py` `Powershell().promptloop()` to see how the transformed queries are passed into RelationDB.

## 5. <a name="etc">Misc: Errors, ... etc</a>
The Errors are raised whenever the application runs into one. However the messaging is done via a global queue in `parser.py`
whenever a Error is raised, it's message is stacked into `parser._queues` for later printing. The exceptions are
received inside `shell.py` but there no more control done after the Exception is raised. The application simply
continues to receive input.

If the KeyboardInterrupt is received however it closes the database and terminates the process.
However the `Ctrl-C`( SIGINT ) is not safe when asynchroneously raised. So SIGINT should only be
passed to the process after you see the prompt message `DB_2014_15554`.