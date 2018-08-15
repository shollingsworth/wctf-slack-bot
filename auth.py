#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botconfig
import json
from slackclient import SlackClient
import libsqlalchemy
from db_wctf.tables import AuthedTeamsData
from db_wctf import db
import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)


def application_auth(code):
    client = SlackClient("")
    if not code:
        raise Exception("Error, code is empty")

    auth_send = {
        'client_id': botconfig.client_id,
        'client_secret': botconfig.client_secret,
        'code': code,
    }
    LOG.debug("AUTH SEND: %s", json.dumps(auth_send, indent=5))

    auth_response = client.api_call(
        "oauth.access",
        **auth_send
    )
    LOG.debug("AUTH RESPONSE: %s", json.dumps(auth_response, indent=5))

    if not auth_response.get('ok'):
        raise Exception("Error, auth response had an error: {}".format(auth_response.get('error')))

    team_id = auth_response.get('team_id')
    botconfig.authed_teams[team_id] = auth_response
    update_data = {
        AuthedTeamsData.team_json.name: auth_response,
    }
    insert_data = {
        AuthedTeamsData.team_json.name: auth_response,
        AuthedTeamsData.team_id.name: team_id,
    }
    exists = True
    try:
        libsqlalchemy.get_by_id(db, AuthedTeamsData, team_id)
    except Exception:
        exists = False

    if exists:
        LOG.info('Auth Team Update (exists): {}/{}'.format(db, update_data))
        libsqlalchemy.add_update_one(
            db,
            AuthedTeamsData,
            update_data,
            team_id,
        )
    else:
        LOG.info('Auth Team ADDITION!: {}/{}'.format(db, update_data))
        libsqlalchemy.add_update_one(
            db,
            AuthedTeamsData,
            insert_data,
        )
    botconfig.authed_teams[team_id] = auth_response
