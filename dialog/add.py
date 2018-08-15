#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botconfig
from slack_data_objects import Dialog
from db_wctf.tables import FoxTrack
from bgtask import task
import logging
import libverify
import libfox
import json
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

CALLBACK = ".".join([__name__, 'validate'])


def validate(data):
    cols = [
        k for k, v in FoxTrack.__dict__.items() if not k.startswith('_')
    ]
    error_list = []
    form = Dialog(data)
    bad_keys = [f for f in form.submission.keys() if f not in cols]
    if bad_keys:
        error_list.append({
            'name': FoxTrack.bssid.name,
            'error': "the following keys are invalid: {}".format(bad_keys),
        })

    bssid = form.submission.get(FoxTrack.bssid.name)
    if not bssid and FoxTrack.bssid.name not in [i.get('name') for i in error_list]:
        error_list.append({
            'name': FoxTrack.bssid.name,
            'error': "bssid is blank",
        })
    try:
        libverify.verify_bssid(bssid)
    except Exception as e:
        if FoxTrack.bssid.name not in [i.get('name') for i in error_list]:
            error_list.append({
                'name': FoxTrack.bssid.name,
                'error': e.message,
            })
    return {
        'error_list': error_list,
        'func': ProcessDialog,
        'data': data,
    }


@task
def ProcessDialog(data):
    form = Dialog(data)
    # user_client = botconfig.get_slacker(form, 'user')
    bot_client = botconfig.get_slacker(form, 'bot')
    res = libfox.add_fox(form.submission, form.raw_data_json)
    LOG.debug("JSON:\n{}".format(json.dumps(res, indent=4, separators=(',', ' : '))))
    form.channel_name
    # @TODO put in prod
    post_chan = '#general'
    post_chan = form.channel_id
    bot_client.chat.post_message(
        post_chan,
        "Fox `{}` has been added by <@{}> in <#{}|{}>".format(
            form.submission.get(FoxTrack.bssid.name),
            form.user_id,
            form.channel_id,
            form.channel_name,
        )
    )


def get_dialog_interface(self):
    retval = {
        "callback_id": CALLBACK,
        "title": "Add Fox",
        "submit_label": "Go!",
        "elements": [
            {
                "label": "BSSID (mac)",
                "type": "text",
                "placeholder": "00:00:00:00:00:00",
                # "value": libfox.get_rand_mac_address(),  # for testing
                "name": FoxTrack.bssid.name,
            },
            {
                "label": "SSID (ap name)",
                "type": "text",
                "optional": True,
                "name": FoxTrack.ssid.name,
            },
        ]
    }
    LOG.debug("dialog: {}".format(json.dumps(retval, indent=4, separators=(',', ' : '))))
    return retval
