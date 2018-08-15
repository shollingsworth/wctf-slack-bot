#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import constants
import os
from sys import modules
import logging
import libsqlalchemy
import json
import glob
import argparse
import jsonpickle
from importlib import import_module

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARN)
logging.getLogger().setLevel(logging.INFO)

ME = modules[__name__]
CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
ORIG_PATH = os.getcwd()

DB_NAME = constants.DB_NAME

IMPORTS_REF = {
    'db_wctf',
}

F_IMPORT = 'import'
F_EXPORT = 'export'

IGNORE_FILE_PREFIX = ('zappa', 'authdata')


class ImportExport(object):
    def __init__(self, test_args=None):
        # first change into config dir
        os.chdir(CONFIG_PATH)
        args = self.get_args(test_args)
        self.debug = args.debug
        self.environment = args.environment
        self.destination_directory = None
        if args.operation == F_IMPORT:
            self.import_file = args.import_file
            self.func = self.do_import
        elif args.operation == F_EXPORT:
            self.import_file = None
            self.destination_directory = args.destination_directory
            self.func = self.do_export
        else:
            raise ValueError(" ".join([
                "Error, invalid function, need one the",
                " following types: {}".format([F_IMPORT, F_EXPORT]),
            ]))
        with open(constants.ZAPPA_FN, 'r') as fh:
            zappa_config = json.load(fh)

        # set back to original path
        os.chdir(ORIG_PATH)

        if args.environment not in zappa_config:
            raise ValueError("Error, could not find: {} in zappa config".format(
                self.args.environment,
            ))
        my_config = zappa_config[args.environment]
        env_key = 'environment_variables'
        if env_key not in my_config:
            raise ValueError(" ".join([
                "Error, could not find '{}'".format(env_key),
                "in file: {} and environment: {}".format(constants.ZAPPA_FN, self.environment),
            ]))

        # set environment
        for k, v in my_config[env_key].items():
            os.environ[k] = v

        if self.debug:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
            logging.getLogger().setLevel(logging.DEBUG)

    def get_args(self, test_args):
        files = filter(lambda x: not x.startswith(IGNORE_FILE_PREFIX), glob.glob('*.json'))
        envs = map(lambda x: x.replace('.json', ''), files)
        program_desc = "Import / Export Data Dictionary"
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
            '-e',
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
        # import subparsers
        ##############################
        p_import = subparsers.add_parser(
            F_IMPORT,
            parents=[parent_parser],
            help='export data from all databases in environment',
        )
        p_import.add_argument(
            "-i",
            "--import_file",
            help="import file",
            required=True,
        )
        ##############################
        # export subparsers
        ##############################
        p_export = subparsers.add_parser(
            F_EXPORT,
            parents=[parent_parser],
            help='export data from all databases in environment',
        )
        p_export.add_argument(
            "-d",
            "--destination_directory",
            help="Export destination directory",
            default=ORIG_PATH,
        )
        ##############################
        # do thing
        ##############################
        if test_args:
            args = type(str('args'), (), {})()
            [setattr(args, k, v) for k, v in test_args.items()]
        else:
            args = base_parser.parse_args()
        return args

    def process_db_export(self, db_module):
        retdict = {}
        db = db_module.db
        data_objects = {t.__tablename__: t for t in db.Base.__subclasses__()}
        for table, table_obj in data_objects.items():
            LOG.info("Processing table: {}".format(table))
            results = libsqlalchemy.get_all(db, table_obj)
            try:
                results = filter(lambda x: x.pop('id'), results)
            except Exception:
                LOG.debug("table: {} has no 'id' column".format(table))
            retdict[table] = results
        return retdict

    def process_db_import(self, db_module, iter_values):
        db = db_module.db
        data_objects = {t.__tablename__: t for t in db.Base.__subclasses__()}
        for table, values in iter_values.items():
            Data = data_objects[table]
            LOG.info("working on table: {}".format(table))
            LOG.info("Deleting all records...")
            db.session.query(Data).delete()
            LOG.info("Importing Data to table: {}".format(table))
            libsqlalchemy.insert_bulk(db, Data, values)

    def do_export(self):
        output_dict = {}
        for db_ref in IMPORTS_REF:
            mod = import_module(db_ref)
            output_dict[db_ref] = self.process_db_export(mod)
            dest_base = os.path.join(*[
                self.destination_directory,
                self.environment,
            ])
            dest_file = '{}-{}.json'.format(dest_base, DB_NAME)
            with open(dest_file , 'w') as fh:
                LOG.info("Writing to file: {}".format(dest_file))
                nice_pickle = json.loads(jsonpickle.encode(output_dict))
                fh.write(json.dumps(nice_pickle, indent=4, separators=(',', ' : ')))

    def do_import(self):
        with open(self.import_file, 'r') as fh:
            raw_values = jsonpickle.decode(fh.read())
        if len(raw_values.keys()) == 0:
            raise Exception(" ".join([
                "Error, file: {} is empty".format(self.import_file),
                "or not a dictionary",
            ]))
        no_keys = [i for i in raw_values.keys() if i not in IMPORTS_REF]
        if no_keys:
            raise Exception(" ".join([
                "Error, I don't know how to handle these keys",
                "{}".format(no_keys),
                "The following keys are accepted: {}".format(IMPORTS_REF),
            ]))
        elif len(raw_values.keys()) > 1:
            raise Exception(" ".join([
                "Error, file: {}".format(self.import_file),
                "has more than 1 valid key in the import stack.",
            ]))
        operate_key = raw_values.keys()[0]
        mod = import_module(operate_key)
        iter_values = raw_values[operate_key]
        self.process_db_import(mod, iter_values)

    def run(self):
        self.func()


if __name__ == '__main__':
    obj = ImportExport()
    obj.run()
