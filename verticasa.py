from sqlalchemy import types as sqltypes
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import reflection


class Vertica(PyODBCConnector, PGDialect):
    """ Vertica Dialect using a pyodbc connection and PGDialect """

    ischema_names = {
        'BINARY': sqltypes.BLOB,
        'VARBINARY': sqltypes.BLOB,
        'BYTEA': sqltypes.BLOB,
        'RAW': sqltypes.BLOB,

        'BOOLEAN': sqltypes.BOOLEAN,

        'CHAR': sqltypes.CHAR,
        'VARCHAR': sqltypes.VARCHAR,
        'VARCHAR2': sqltypes.VARCHAR,

        'DATE': sqltypes.DATE,
        'DATETIME': sqltypes.DATETIME,
        'SMALLDATETIME': sqltypes.DATETIME,
        'TIME': sqltypes.TIME,

        # Not supported yet
        # TIME WITH TIMEZONE
        # TIMESTAMP
        # TIMESTAMP WITH TIMEZONE
        # INTERVAL

        # All the same internal representation
        'FLOAT': sqltypes.FLOAT,
        'FLOAT8': sqltypes.FLOAT,
        'DOUBLE': sqltypes.FLOAT,
        'REAL': sqltypes.FLOAT,

        'INT': sqltypes.INTEGER,
        'INTEGER': sqltypes.INTEGER,
        'INT8': sqltypes.INTEGER,
        'BIGINT': sqltypes.INTEGER,
        'SMALLINT': sqltypes.INTEGER,
        'TINYINT': sqltypes.INTEGER,

        'NUMERIC': sqltypes.NUMERIC,
        'DECIMAL': sqltypes.NUMERIC,
        'NUMBER': sqltypes.NUMERIC,
        'MONEY': sqltypes.NUMERIC,
    }
    pyodbc_driver_name = 'Vertica'

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        s = ["SELECT table_name FROM v_catalog.tables"]
        if schema is not None:
            s.append("WHERE table_schema = '%s'" % (schema,))
        s.append("ORDER BY table_schema, table_name")

        rs = connection.execute(' '.join(s))
        return [row[0] for row in rs]

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        s = ["SELECT table_name FROM v_catalog.views"]
        if schema is not None:
            s.append("WHERE table_schema = '%s'" % (schema,))
        s.append("ORDER BY table_schema, table_name")

        rs = connection.execute(' '.join(s))
        return [row[0] for row in rs]

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        print 'in get columns', table_name
        s = ("SELECT * FROM v_catalog.columns "
             "WHERE table_name = '%s' ") % (table_name,)

        spk = ("SELECT column_name FROM v_catalog.primary_keys "
               "WHERE table_name = '%s' "
               "AND constraint_type = 'p'") % (table_name)

        if schema is not None:
            _pred = lambda p: ("%s AND table_schema = '%s'" % (p, schema))
            s = _pred(s)
            spk = _pred(spk)

        pk_columns = [x[0] for x in connection.execute(spk)]
        columns = []
        for row in connection.execute(s):
            name = row.column_name
            dtype = row.data_type.upper()
            if '(' in dtype:
                dtype = dtype.split('(')[0]
            coltype = self.ischema_names[dtype]
            primary_key = name in pk_columns
            default = row.column_default
            nullable = row.is_nullable

            columns.append({
                'name': name,
                'type': coltype,
                'nullable': nullable,
                'default': default,
                'primary_key': primary_key
            })
        return columns

    # constraints are enforced on selects, but returning nothing for these
    # methods allows table introspection to work

    def get_pk_constraint(self, bind, table_name, schema, **kw):
        return {'constrained_columns': [], 'name': 'undefined'}

    def get_foreign_keys(self, connection, table_name, schema, **kw):
        return []

    def get_indexes(self, connection, table_name, schema, **kw):
        return []
