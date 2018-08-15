#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from libsqlalchemy import DbConfig
import constants
from base import Base
Base

CONN_TYPE = os.environ.get(constants.ENV_CONNECTION_TYPE)
if not CONN_TYPE:
    raise Exception(" ".join([
        "Error, could not detect connection from",
        "Env variable: '{}'".format(constants.ENV_CONNECTION_TYPE),
    ]))
DB_NAME = constants.DB_NAME
DB_CONFIG = DbConfig(CONN_TYPE, DB_NAME)
engine = DB_CONFIG.engine
session = DB_CONFIG.session
inspector = DB_CONFIG.inspector
