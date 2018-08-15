#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botconfig
from slack_data_objects import Dialog
from db_wctf.tables import FoxTrack
from db_wctf import db
import libsqlalchemy
import option_maps
from bgtask import task
import logging
import json
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

CALLBACK = ".".join([__name__, 'validate'])


def validate(data):
    error_list = []
    return {
        'error_list': error_list,
        'func': ProcessDialog,
        'data': data,
    }


@task
def ProcessDialog(data):
    form = Dialog(data)
    source_channel_id = form.channel_id
    user_client = botconfig.get_slacker(form, 'user')
    bot_client = botconfig.get_slacker(form, 'bot')
    existing_data = libsqlalchemy.get_by_id(db, FoxTrack, source_channel_id, null_ok=True)
    user_client
    bot_client
    existing_data


def get_dialog_interface(self):
    channel_id = self.channel_id
    res = libsqlalchemy.get_by_id(db, FoxTrack, channel_id, null_ok=True)
    VALUE_MAP = {k : res.get(k) for k in [
        FoxTrack.ssid.name,
    ]}
    retval = {
        "callback_id": CALLBACK,
        "title": "Add SSID",
        "submit_label": "Go!",
        "elements": [
            {
                "label": "SSID",
                "type": "select",
                "value": VALUE_MAP[FoxTrack.ssid.name],
                "name": FoxTrack.ssid.name,
                "options": option_maps.PERCENTAGE,
            },
        ]
    }
    LOG.debug("dialog: {}".format(json.dumps(retval, indent=4, separators=(',', ' : '))))
    return retval
