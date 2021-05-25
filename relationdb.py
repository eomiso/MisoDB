
from berkeleydb import db

__all__ = ['MisoDB']

class MisoDB:
    """
    Relational database
    """
    CREATE = db.DB_CREATE

    def __init__(self, filename, dbtype=db.DB_HASH, **kwargs):
        self.db = db.DB()
        self.filename = filename
        self.dbtype = dbtype
        self.kwargs = kwargs

    def __enter__(self):
        self.db.open(self.filename, dbtype=self.dbtype, **self.kwargs)
        return self
    
    def __exit__(self,type, value, trace_back):
        self.db.close()

    def __iter__(self):
        cursor = self.db.cursor()
        x = cursor.next()
        while x:
            yield x
            x = cursor.next()
    
    def __getitem__(self, key):
        val = self.db.get(key.encode())
        if val is None:
            raise KeyError(key)
        return eval(val.decode())

    def __setitem__(self, key, val):
        self.db.put(key.encode(), repr(val).encode())
    
    def __delitem__(self, key):
        self.db.delete(key.encode())