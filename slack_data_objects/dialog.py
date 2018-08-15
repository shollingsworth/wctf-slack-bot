#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Dialog(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.action_ts = data.get('action_ts')
        self.callback_id = data.get('callback_id')
        self.channel = data.get('channel')
        self.channel_id = data.get('channel', {}).get('id')
        self.channel_name = data.get('channel', {}).get('name')
        self.response_url = data.get('response_url')
        self.submission = data.get('submission', {})
        self.team = data.get('team')
        self.team_domain = data.get('team', {}).get('domain')
        self.team_id = data.get('team', {}).get('id')
        self.token = data.get('token')
        self.type = data.get('type')
        self.user = data.get('user')
        self.user_id = data.get('user', {}).get('id')
        self.user_name = data.get('user', {}).get('name')


# Sample Object
SAMPLE_OBJECT = {
    "submission" : {
        "comment" : "No sour cream please",
        "name" : "Sigourney Dreamweaver",
        "team_channel" : "C0LFFBKPB",
        "email" : "sigdre@example.com",
        "phone" : "+1 800-555-1212",
        "who_should_sing" : "U0MJRG1AL",
        "meal" : "burrito"
    },
    "response_url" : "https://hooks.slack.com/app/T012AB0A1/123456789/JpmK0yzoZDeRiqfeduTBYXWQ",
    "action_ts" : "936893340.702759",
    "callback_id" : "employee_offsite_1138b",
    "token" : "M1AqUUw3FqayAbqNtsGMch72",
    "user" : {
        "id" : "W12A3BCDEF",
        "name" : "dreamweaver"
    },
    "team" : {
        "domain" : "coverbands",
        "id" : "T1ABCD2E12"
    },
    "type" : "dialog_submission",
    "channel" : {
        "id" : "C1AB2C3DE",
        "name" : "coverthon-1999"
    }
}


if __name__ == '__main__':
    obj = Dialog(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
