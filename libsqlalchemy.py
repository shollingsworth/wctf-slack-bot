#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy.engine.url import URL as SQLURL
import os
import constants
import sqlalchemy as sa
from sqlalchemy import orm, inspect
from sqlalchemy.pool import StaticPool

CONTYPE_ROOT_NO_DB = 'mysql_root_no_db'
CONTYPE_ROOT = 'mysql_root'
CONTYPE_RDS = 'mysql_rds'
CONTYPE_SQLITE = 'sqlite'
CONTYPE_SQLITE_MEMORY = 'sqlite_memory'
SQLTIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class DbConfig(object):
    def __init__(
        self,
        connection_type,
        db_name,
        sqlite_db_file=None,
    ):
        self.sqlite_db_file = sqlite_db_file
        self.db_name = db_name
        self.connection_type = connection_type

        self.root_mysql_user = None
        self.root_mysql_pass = None
        self.mysql_user = None
        self.mysql_pass = None
        self.mysql_endpoint = None
        self.mysql_endpointport = None
        self.set_vars()

        self.connection_url = self.get_connection_url()
        self.engine = self.get_engine()
        self.session = orm.scoped_session(orm.sessionmaker(bind=self.engine))
        self.inspector = inspect(self.engine)

    def set_vars(self):
        empties = [
            i for i in dir(constants)
            if i.startswith('ENV_SQL') and
            not getattr(constants, i)
        ]
        if empties:
            raise Exception(" ".join([
                "Error, the following environment variables",
                "were not detected: {}".format(empties),
            ]))
        self.root_mysql_user = os.environ.get(constants.ENV_SQL_MASTER_USER)
        self.root_mysql_pass = os.environ.get(constants.ENV_SQL_MASTER_PASS)
        self.mysql_user = os.environ.get(constants.ENV_SQL_USER)
        self.mysql_pass = os.environ.get(constants.ENV_SQL_PASS)
        self.mysql_endpoint = os.environ.get(constants.ENV_SQL_ENDPOINT)
        self.mysql_endpointport = os.environ.get(constants.ENV_SQL_PORT)

    def set_connection_type(self, connection_type):
        self.connection_type = connection_type
        self.set_vars()
        self.connection_url = self.get_connection_url()
        self.engine = self.get_engine()
        self.session = orm.scoped_session(orm.sessionmaker(bind=self.engine))
        self.inspector = inspect(self.engine)

    def get_connection_url(self):
        types = {
            CONTYPE_ROOT_NO_DB: SQLURL(**{
                'drivername': 'mysql+mysqldb',
                'username': self.root_mysql_user,
                'password': self.root_mysql_pass,
                'host': self.mysql_endpoint,
                'port': self.mysql_endpointport,
            }),

            CONTYPE_ROOT: SQLURL(**{
                'drivername': 'mysql+mysqldb',
                'username': self.root_mysql_user,
                'password': self.root_mysql_pass,
                'host': self.mysql_endpoint,
                'port': self.mysql_endpointport,
                'database': self.db_name,
            }),

            CONTYPE_RDS: SQLURL(**{
                'drivername': 'mysql+mysqldb',
                'username': self.mysql_user,
                'password': self.mysql_pass,
                'host': self.mysql_endpoint,
                'port': self.mysql_endpointport,
                'database': self.db_name,
            }),

            CONTYPE_SQLITE: SQLURL(**{
                'drivername': 'sqlite',
                'database': self.sqlite_db_file,
            }),

            CONTYPE_SQLITE_MEMORY: SQLURL(**{
                'drivername': 'sqlite',
                'database': ':memory:',
            })
        }
        if self.connection_type not in types:
            raise Exception(" ".join([
                "Error, could not find connection type: {}".format(self.connection_type),
                "in values: {}".format(types.keys()),
            ]))
        return types[self.connection_type]

    def get_engine(self):
        if not self.connection_type:
            raise Exception("Error, invalid connection type: {}".format(
                self.connection_type
            ))
        if 'sqlite' in self.connection_type:
            # otherwise when I'm using blinker I'll get thred warnings
            # 2018-06-11 12:43:01,213 INFO sqlalchemy.pool.NullPool Invalidate
            # connection <sqlite3.Connection object at 0x7fa3fdfa0200> (reason:
            # ProgrammingError:SQLite objects created in a thread can only
            # be used in that same thread.The object was created in thread id
            # 140342330623744 and this is thread id 140342490633984)
            engine = sa.create_engine(
                self.connection_url,
                connect_args={
                    'check_same_thread': False,
                },
                poolclass=StaticPool,
            )
        else:
            engine = sa.create_engine(
                self.connection_url,
                connect_args={'connect_timeout': 10},
            )
        return engine


def __commit_rollback(db):
    try:
        return db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(e)


def __get_primary_keys(db, Data):
    return [key.name for key in inspect(Data).primary_key]


def __get_primary_key(db, Data):
    keys = __get_primary_keys(db, Data)
    assert len(keys) == 1, "{} Error, more than one primary key found on {}".format(
        __name__,
        Data.__dict__
    )
    return keys[0]


def __get_dict(DataResults):
    return {k : v for k, v in DataResults.__dict__.items() if not k.startswith('_')}


def insert_bulk(db, DataObj, value_set):
    insert_values = [DataObj(**val) for val in value_set]
    db.session.bulk_save_objects(insert_values)
    return __commit_rollback(db)


def get_filtered(db, Data, filter_key, filter_value):
    res = db.session.query(Data).filter(
        getattr(Data, filter_key) == filter_value
    )
    __commit_rollback(db)
    return [__get_dict(i) for i in res]


def get_by_id(db, Data, id, null_ok=False):
    pkey = __get_primary_key(db, Data)
    pkey_col = getattr(Data, pkey)
    res = db.session.query(Data).filter(
        pkey_col == id,
    )
    res = [
        __get_dict(i)
        for i in res
    ]
    if len(res) == 0 and null_ok:
        return {}
    elif len(res) == 1:
        return res[0]
    elif len(res) == 0:
        raise Exception("{} Error, no results found for id: {}".format(
            __name__,
            id,
        ))
    else:
        raise Exception(" ".join([
            "{} Error, id: {} has {} results!".format(
                __name__,
                id,
                len(res),
            ),
            "Do you not have a primary key set on the table...",
            "actually I take that back. You shouldn't be here :disapproval:",
            "I'm going to report this",
        ]))
    __commit_rollback(db)


def get_all(db, Data):
    res = [
        __get_dict(i)
        for i in db.session.query(Data).all()
    ]
    __commit_rollback(db)
    return res


def delete(db, Data, id):
    pkey = __get_primary_key(db, Data)
    pkey_col = getattr(Data, pkey)
    res = db.session.query(Data).filter(
        pkey_col == id,
    )
    res.delete()
    return __commit_rollback(db)


def add_update_one(db, Data, value, id=None):
    pkey = __get_primary_key(db, Data)
    data = value
    if id:
        pkey_col = getattr(Data, pkey)
        res = db.session.query(Data).filter(
            pkey_col == id,
        )
        res.update(values = data)
    else:
        db.session.add(Data(**data))
    return __commit_rollback(db)
