#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import string
import random
import sqlalchemy
import glob
import argparse
import json
import libsqlalchemy
import constants
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))

OPERATION_INIT = 'init'
DEFAULT_SQLUSER = os.environ.get('DEFAULT_SQLUSER', 'sql_user')
ORIG_PATH = os.getcwd()
CONN_NO_DB = 'mysql_root_no_db'


def json_norm(obj):
    try:
        json.load(obj)
        return obj
    except Exception:
        return str(obj)


class InitDB(object):
    def __init__(
        self,
        env_file,
        sql_user,
        sqlite_db_file=None,
    ):
        self.sqlite_db_file = sqlite_db_file
        self.env_file = os.path.join(*[CONFIG_PATH, env_file])
        self.env = self.get_load()
        self.sql_pass = self.__get_pass()
        self.sql_user = sql_user
        self.conn_type = CONN_NO_DB
        self.can_drop_db = True
        self.set_no_db_env()  # needs to run right before we initialize any DB connects
        self.raw_db = libsqlalchemy.DbConfig(self.conn_type, constants.DB_NAME)
        try:
            mod = self.__get_mod()
        except ValueError:
            LOG.exception("Value Error!")
            sys.exit(-1)
        except sqlalchemy.exc.OperationalError as e:  # Create DB from Scratch if it doesn't exist
            if 'Unknown database' in str(e.orig):
                LOG.info("DB Doesn't exist, creating one.")
                self.create_db()
                self.can_drop_db = False
                mod = self.__get_mod()
            else:
                LOG.error("SQL Operation Error!: {}".format(e.message))
                sys.exit(-1)
        except Exception:
            LOG.exception("Unknown Exception!")
            sys.exit(-1)
        self.db_name = mod.db.DB_NAME
        self.db = mod.db
        self.engine = mod.db.engine
        self.metadata = mod.db.Base.metadata
        self.metadata.bind = self.engine

        self.data_objects = {t.__tablename__: t for t in self.db.Base.__subclasses__()}

    def __get_mod(self):
        # previously used for different db's but we only have one
        import db_wctf
        return db_wctf

    def __get_pass(self):
        LENGTH = 40
        return ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits + string.lowercase
            ) for _ in range(LENGTH)
        )

    def create_all(self):
        LOG.info("Running Create ALL")
        LOG.info("Attmping {} init".format(self.db_name))
        LOG.info("running base.create_all")
        self.metadata.create_all()
        LOG.info("Running Grants for: {}".format(self.sql_user))
        conn = self.raw_db.engine.connect()
        conn.execute("COMMIT")
        grants = [
            'DELETE',
            'INSERT',
            'SELECT',
            'UPDATE',
        ]
        conn.execute(
            "GRANT USAGE on *.* TO %s@%s",
            self.db_name,
            '%',
        )
        conn.execute("FLUSH PRIVILEGES")
        conn.execute(
            "GRANT {} on {}.* TO %s@%s".format(
                ",".join(grants),
                self.db_name,
            ),
            self.sql_user,
            '%',
        )
        conn.execute("FLUSH PRIVILEGES")
        conn.close()

    def create_user(self):
        LOG.info("Running Create User")
        # need a raw connection because we're working on a DB outside of of the imported mod
        conn = self.raw_db.engine.connect()
        conn.execute("COMMIT")
        conn.execute(
            "CREATE USER %s@%s IDENTIFIED BY %s",
            self.sql_user,
            '%',
            self.sql_pass,
        )
        conn.close()

    def create_db(self):
        if not self.can_drop_db:
            LOG.info("Looks like the DB is fresh, no need to create")
            return
        LOG.info("Running Create DB")
        conn = self.raw_db.engine.connect()
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE {}".format(self.raw_db.db_name))
        conn.close()

    def kill_in_use(self):
        conn = self.raw_db.engine.connect()
        res = [
            dict(zip(row.keys(), row.values()))
            for row in conn.execute("show processlist")
        ]
        in_use = [
            (i.get('Id'), i.get('Command'), i.get('User'), i.get('Host')) for i in res
            if i.get('User') == self.sql_user and
            i.get('Time') >= 10
        ]
        for sql_id, cmd, user, host in in_use:
            LOG.info(" ".join([
                "Killing id: {}".format(sql_id),
                "cmd: {}".format(cmd),
                "user: {}".format(user),
                "host: {}".format(host),
            ]))
            q = "call mysql.rds_kill({})".format(sql_id)
            conn.execute(q)

    def drop_db(self):
        self.kill_in_use()
        if not self.can_drop_db:
            LOG.info("Looks like the DB is fresh, no need to drop")
            return
        LOG.info("Running Drop DB")
        conn = self.raw_db.engine.connect()
        conn.execute("COMMIT")
        conn.execute("DROP DATABASE {};".format(self.raw_db.db_name))
        conn.close()

    def write_new_user_pass(self):
        self.env[constants.FIELD_SQL_USER] = self.sql_user
        self.env[constants.FIELD_SQL_PASS] = self.sql_pass
        with open(self.env_file, 'wb') as fh:
            fh.write(
                json.dumps(self.env, indent=4, separators=(',', ' : '))
            )

    def set_no_db_env(self):
        os.environ[constants.ENV_CONNECTION_TYPE] = libsqlalchemy.CONTYPE_ROOT
        os.environ[constants.ENV_SQL_MASTER_USER] = self.env.get(constants.FIELD_SQL_MASTER_USER)
        os.environ[constants.ENV_SQL_MASTER_PASS] = self.env.get(constants.FIELD_SQL_MASTER_PASS)
        os.environ[constants.ENV_SQL_ENDPOINT] = self.env.get(constants.FIELD_SQL_ENDPOINT)
        os.environ[constants.ENV_SQL_PORT] = self.env.get(constants.FIELD_SQL_PORT)

    def get_load(self):
        with open(self.env_file, 'r') as fh:
            return json.load(fh)

    def go(self):
        LOG.info("Proceeding with {} ENV {}".format(self.db, self.env_file))
        # erase / init DB's
        LOG.info("Running INIT RDS")
        self.drop_db()
        self.create_db()
        try:
            self.create_user()
            self.write_new_user_pass()
        except sqlalchemy.exc.OperationalError as e:
            LOG.warn("User: {} already exists, skipping create: {}".format(
                self.sql_user,
                e,
            ))
        self.create_all()


def get_args(test_args=None):
    files = filter(lambda x: not x.startswith(constants.IGNORE_FILE_PREFIX), glob.glob('*.json'))
    envs = map(lambda x: x.replace('.json', ''), files)
    program_desc = "Initialize DB based on environment json file"
    ##############################
    # Parent parser
    ##############################
    parent_parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parent_parser.add_argument(
        '-D',
        '--debug',
        action='store_true',
        required=False,
        default=False,
    )
    parent_parser.add_argument(
        '--environment',
        choices=envs,
        required=True,
    )
    ##############################
    # Base parser
    ##############################
    base_parser = argparse.ArgumentParser(
        description=program_desc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )
    subparsers = base_parser.add_subparsers(dest='operation')
    ##############################
    # init subparsers
    ##############################
    p_init = subparsers.add_parser(
        OPERATION_INIT,
        parents=[parent_parser],
        help='export data from all databases in environment',
    )
    p_init.add_argument(
        '--sql_user',
        required=False,
        default=DEFAULT_SQLUSER,
    )
    ##############################
    # do thing
    ##############################
    if test_args:
        args = type(str('args'), (), {})()
        [setattr(args, k, v) for k, v in test_args.items()]
    else:
        args = base_parser.parse_args()
    args.env_file = files[envs.index(args.environment)]
    if not args.env_file:
        raise Exception(" ".join([
            "Error, could not determine env_file",
            "from files: {}".format(files),
        ]))
    return args


if __name__ == '__main__':
    os.chdir(CONFIG_PATH)
    """
    args_test = {
        'environment': 'dev',
        'operation': OPERATION_INIT,
        'debug': False,
        'sql_user': DEFAULT_SQLUSER,
    }
    args = get_args(args_test)
    """
    args = get_args()
    os.chdir(ORIG_PATH)
    if args.debug:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        logging.getLogger().setLevel(logging.DEBUG)
    if args.operation == OPERATION_INIT:
        try:
            obj = InitDB(args.env_file, args.sql_user)
            obj.go()
        except Exception as e:
            LOG.exception("Error, running init")
            sys.exit(-1)
    else:
        raise Exception(" ".join([
            "Error, invalid operation: {}".format(args.operation)
        ]))
