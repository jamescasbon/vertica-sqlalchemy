vertica-sqlalchemy
==================

Vertica dialect for sqlalchemy

This module implements a Vertica dialect for SQLAlchemy.  You can use it: 

    >>> import sqlalchemy as sa
    >>> sa.create_engine(sa.engine.url.URL(
        drivername='vertica+pyodbc',
        username='myusername',
        password='mypassword',
        host='hostname',
        database='dbname',
    ))


This work is mainly a package of code
[posted](https://groups.google.com/d/msg/sqlalchemy/ttJzN-t9R74/9W1d9KfHK_0J)
to the SQLAlchemy mailing list.

I have tested this for table introspection, selects and joins.  However, I do
not have access to a Vertica database to test against.  If you do, let me know.

The primary, foreign and index constraints return nothing.  This is because I'm
told these are 'enforced on select'.  Maybe a Vertica expert can tell me the
correct way to handle this.

Installation
------------

With pip 

    pip install vertica-sqlalchemy

From git: 

    git clone https://github.com/jamescasbon/vertica-sqlalchemy
    cd vertica-sqlalchemy
    python setup.py install


