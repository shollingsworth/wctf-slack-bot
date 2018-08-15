#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import current_app
import slack_data_objects
import logging
import botconfig
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)


@current_app.cache.memoize(timeout=120)
def get_user_info(client, user_id):
    LOG.debug(
        "Getting user_info Cache for %s/%s",
        client,
        user_id,
    )
    user = slack_data_objects.User(client.users.info(user_id).body.get('user'))
    return user


@current_app.cache.memoize(timeout=60 * 60)
def get_team(client):
    LOG.debug(
        "Getting team_info Cache for %s",
        client,
    )
    team = slack_data_objects.Team(client.team.info().body.get('team'))
    return team


@current_app.cache.memoize(timeout=60)
def get_channel(client, channel_id):
    LOG.debug(
        "Getting channel info Cache for %s",
        client,
    )
    channel = slack_data_objects.Channel(client.channels.info(channel_id).body.get('channel'))
    return channel
