import re
from sqlalchemy import types as sqltypes
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import reflection


class VerticaDialect(PyODBCConnector, PGDialect):
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
        'TIME': sqltypes.TIME(timezone=True),
        'TIMESTAMP': sqltypes.TIMESTAMP,
        'TIMESTAMP WITH TIMEZONE': sqltypes.TIMESTAMP(timezone=True),

        # Not supported yet
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
    name = 'vertica'
    pyodbc_driver_name = 'Vertica'

    def has_schema(self, connection, schema):
        query = ("SELECT EXISTS (SELECT schema_name FROM v_catalog.schemata "
                 "WHERE schema_name='%s')") % (schema)
        rs = connection.execute(query)
        return bool(rs.scalar())

    def has_table(self, connection, table_name, schema=None):
        if schema is None:
            schema = self._get_default_schema_name(connection)
        query = ("SELECT EXISTS ("
                 "SELECT table_name FROM v_catalog.all_tables "
                 "WHERE schema_name='%s' AND "
                 "table_name='%s'"
                 ")") % (schema, table_name)
        rs = connection.execute(query)
        return bool(rs.scalar())

    def has_sequence(self, connection, sequence_name, schema=None):
        if schema is None:
            schema = self._get_default_schema_name(connection)
        query = ("SELECT EXISTS ("
                 "SELECT sequence_name FROM v_catalog.sequences "
                 "WHERE sequence_schema='%s' AND "
                 "sequence_name='%s'"
                 ")") % (schema, sequence_name)
        rs = connection.execute(query)
        return bool(rs.scalar())

    def has_type(self, connection, type_name, schema=None):
        query = ("SELECT EXISTS ("
                 "SELECT type_name FROM v_catalog.types "
                 "WHERE type_name='%s'"
                 ")") % (type_name)
        rs = connection.execute(query)
        return bool(rs.scalar())

    def _get_server_version_info(self, connection):
        v = connection.scalar("select version()")
        m = re.match(
            '.*Vertica Analytic Database '
            'v(\d+)\.(\d+)\.(\d)+.*',
            v)
        if not m:
            raise AssertionError(
                "Could not determine version from string '%s'" % v)
        return tuple([int(x) for x in m.group(1, 2, 3) if x is not None])

    def _get_default_schema_name(self, connection):
        return connection.scalar("select current_schema()")

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        query = "SELECT schema_name FROM v_catalog.schemata"
        rs = connection.execute(query)
        return [row[0] for row in rs if not row[0].startswith('v_')]

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

    # Disable index creation since that's not a thing in Vertica.
    def visit_create_index(self, create):
        return None
