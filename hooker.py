#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import requests
import botconfig
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)


# return send_request('UNCAUGHT Exception', tb, field_arr)
class Hooker(object):
    def __init__(
        self,
        channel,
    ):
        self.field_arr = []
        if not channel:
            raise ValueError("channel argument cannot be empty")
        self.channel = channel

    def add_field(self, title, body, short=False):
        self.field_arr.append({
            'title': title,
            'value': body,
            'short': short,
        })

    def send(self, title, body):
        if len(body) > botconfig.HOOK_MAX_BODY:
            arg = {
                'title': "Message Body Truncated",
                'body': "shaving off {} bytes, sorry".format(
                    len(body) - botconfig.HOOK_MAX_BODY
                ),
                'short': False,
            }
            self.add_field(**arg)
            body = body[:botconfig.HOOK_MAX_BODY]

        send_json = {
            "attachments": [
                {
                    "title": title,
                    "text": body,
                    "fields": self.field_arr,
                }
            ],
            "channel": self.channel,
            "username": botconfig.HOOK_USER,
            "icon_emoji": botconfig.HOOK_ICON
        }
        response = requests.post(
            botconfig.HOOK_URL,
            data=json.dumps(send_json),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            LOG.error('Request to slack returned an error {}, the response is:\n{}'.format(
                response.status_code,
                response.text,
            ))
        return True  # Prevent invocation retry
