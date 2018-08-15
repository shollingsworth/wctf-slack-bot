#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Event(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.api_app_id = data.get('api_app_id')
        self.authed_users = data.get('authed_users')
        self.event = data.get('event')
        self.event_event_ts = data.get('event', {}).get('event_ts')
        self.event_id = data.get('event_id')
        self.event_time = data.get('event_time')
        self.event_type = data.get('event', {}).get('type')
        self.event_subtype = data.get('event', {}).get('subtype')
        self.event_user = data.get('event', {}).get('user')
        self.team_id = data.get('team_id')
        self.token = data.get('token')
        self.type = data.get('type')


# Sample Object
SAMPLE_OBJECT = {
    "event_time" : 1234567890,
    "api_app_id" : "AXXXXXXXXX",
    "event_id" : "Ev08MFMKH6",
    "authed_users" : [
        "UXXXXXXX1",
        "UXXXXXXX2"
    ],
    "team_id" : "TXXXXXXXX",
    "token" : "XXYYZZ",
    "type" : "event_callback",
    "event" : {
        "event_ts" : "1234567890.123456",
        "type" : "name_of_event",
        "user" : "UXXXXXXX1"
    }
}


if __name__ == '__main__':
    obj = Event(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
