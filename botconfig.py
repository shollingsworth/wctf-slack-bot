#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os import environ
import libsqlalchemy
from db_wctf.tables import AuthedTeamsData
from db_wctf import db
from extend_slacker import Slacker
from datetime import datetime
import constants
DEFAULT_LOGGING = logging.DEBUG

TEAM_ID = environ.get('TEAM_ID')
if not TEAM_ID:
    raise ValueError("environment variable: TEAM_ID not set")

ENABLE_CALLBACK = False
CHANNEL_MAIN = '#ctf_slackbot'
CHANNEL_EXCEPTION = '#lambda_bot_exceptions'
CHANNEL_BADUNS = '#bad_things'
DC_DATE = datetime(2018, 8, 9, 17, 0, 0)  # UTC
DISABLE_BG = True
if DEFAULT_LOGGING == logging.DEBUG:
    logging.basicConfig(
        format=" ".join([
            '%(asctime)s',
            '%(levelname)s',
            '%(name)s',
            'func: %(funcName)s',
            'line:%(lineno)d',
            '%(message)s',
        ])
    )
else:
    logging.basicConfig(
        format=" ".join([
            '%(asctime)s',
            '%(levelname)s',
            '%(name)s',
            '%(message)s',
        ])
    )


logging.getLogger().setLevel(DEFAULT_LOGGING)
LOG = logging.getLogger(__name__)
LOG.setLevel(DEFAULT_LOGGING)

# Basic bot name / emoji
bot_name    = "WCTF Bot"
bot_emoji   = ":robot_face:"
bot_scope   = "identify,bot,commands,channels:read,channels:write,chat:write:bot"
SERVER_TYPE = environ.get('SERVERTYPE')
SERVER_STAGE = environ.get('STAGE', '')
CTFTOKEN = environ.get('CTFTOKEN')
if not CTFTOKEN:
    raise ValueError("environment variable: CTFTOKEN not set")

HOOK_MAX_BODY = 8000
HOOK_USER = 'WCTF_BOT'
HOOK_ICON = ':dumpster_fire:'
HOOK_URL = environ.get(constants.ENV_EXCEPTION_HOOK_URL)
if not HOOK_URL:
    raise Exception("Error, invalid env variable '{}'".format(constants.ENV_EXCEPTION_HOOK_URL))

IS_LAMBDA = SERVER_TYPE == 'AWS Lambda'
IS_DEV = 'dev' in SERVER_STAGE.lower()

# Environment Variable Names
__env_client_id           = 'SLACK_CLIENT_ID'
__env_verification_token  = 'SLACK_VERIFICATION_TOKEN'
__env_client_secret       = 'SLACK_CLIENT_SECRET'


check_bad_environments = [
    __env_verification_token,
    __env_client_id,
    __env_client_secret,
]

empties = [var for var in check_bad_environments if not environ.get(var)]
if empties:
    raise Exception("Error, empty environment variables detected: {}".format(empties))

verifcation_token = environ.get(__env_verification_token)
client_id = environ.get(__env_client_id)
client_secret = environ.get(__env_client_secret)


cached_slackers = {}
authed_teams = {}
res = libsqlalchemy.get_all(db, AuthedTeamsData)
for team_info in res:
    team_id = team_info.get(AuthedTeamsData.team_id.name)
    json_dat = team_info.get(AuthedTeamsData.team_json.name)
    authed_teams[team_id] = json_dat

# LOG.debug("authed teams:\n{}".format(authed_teams))


def get_bot_user(self):
    if self.team_id not in authed_teams:
        raise ValueError(" ".join([
            "Somethings fucky... couldn't find",
            "team_id: {} in {}".format(self.team_id, authed_teams.keys()),
        ]))
    team = authed_teams.get(self.team_id)
    bot = team.get('bot', {})
    return bot.get('bot_user_id')


def get_tokens(self):
    return {
        'bot': authed_teams.get(self.team_id, {}).get('bot', {}).get('bot_access_token'),
        'user': authed_teams.get(self.team_id, {}).get('access_token'),
    }


def get_bot_token(self):
    return get_tokens(self).get('bot')


def get_user_token(self):
    return get_tokens(self).get('user')


def get_slacker(self, user_type):
    if isinstance(self, dict):
        tmp_self = type(str('tmp_self'), (), {})()
        [setattr(tmp_self, k, v) for k, v in self.items()]
        self = tmp_self

    cached_slackers.setdefault(self.team_id, {})
    required_user_types = get_tokens(self)
    if user_type not in required_user_types:
        raise Exception("Error, user_type must be one of: {}".format(
            required_user_types.keys(),
        ))
    if not self.team_id:
        raise Exception(" ".join([
            "Error object: {}".format(self),
            "Does not have the attribute 'team_id'"
        ]))
    slcached = cached_slackers.get(self.team_id)
    if slcached.get(user_type):
        LOG.debug(
            "Returning cached Slacker team_id: %s type: %s",
            self.team_id,
            user_type,
        )
        return slcached.get(user_type)
    slack_obj = Slacker(required_user_types[user_type])
    slcached[user_type] = slack_obj
    return slack_obj
