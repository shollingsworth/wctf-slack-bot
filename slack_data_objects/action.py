#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Action(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.callback_id = data.get('callback_id')
        self.channel = data.get('channel')
        self.channel_id = data.get('channel', {}).get('id')
        self.channel_name = data.get('channel', {}).get('name')
        self.message = data.get('message')
        self.message_text = data.get('message', {}).get('text')
        self.message_ts = data.get('message', {}).get('ts')
        self.message_type = data.get('message', {}).get('type')
        self.message_user = data.get('message', {}).get('user')
        self.response_url = data.get('response_url')
        self.team = data.get('team')
        self.team_domain = data.get('team', {}).get('domain')
        self.team_id = data.get('team', {}).get('id')
        self.token = data.get('token')
        self.trigger_id = data.get('trigger_id')
        self.type = data.get('type')
        self.user = data.get('user')
        self.user_id = data.get('user', {}).get('id')
        self.user_name = data.get('user', {}).get('name')


# Sample Object
SAMPLE_OBJECT = {
    "response_url" : "https://hooks.slack.com/app-actions/T0MJR11A4/21974584944/yk1S9ndf35Q1flupVG5JbpM6",
    "trigger_id" : "13345224609.8534564800.6f8ab1f53e13d0cd15f96106292d5536",
    "callback_id" : "chirp_message",
    "token" : "Nj2rfC2hU8mAfgaJLemZgO7H",
    "user" : {
        "id" : "U0D15K92L",
        "name" : "dr_maomao"
    },
    "team" : {
        "domain" : "pandamonium",
        "id" : "T0MJRM1A7"
    },
    "message" : {
        "text" : "World's smallest big cat! <https://youtube.com/watch?v=W86cTIoMv2U>",
        "type" : "message",
        "user" : "U0MJRG1AL",
        "ts" : "1516229207.000133"
    },
    "type" : "message_action",
    "channel" : {
        "id" : "D0LFFBKLZ",
        "name" : "cats"
    }
}


if __name__ == '__main__':
    obj = Action(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
