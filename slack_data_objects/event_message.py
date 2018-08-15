#!/usr/bin/env python
# -*- coding: utf-8 -*-


class EventMessage(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.channel = data.get('channel')
        self.channel_type = data.get('channel_type')
        self.client_msg_id = data.get('client_msg_id')
        self.event_ts = data.get('event_ts')
        self.text = data.get('text')
        self.ts = data.get('ts')
        self.type = data.get('type')
        self.user = data.get('user')


# Sample Object
SAMPLE_OBJECT = {
    "client_msg_id" : "fc9370a3-fd8f-4512-aac2-5eccbfaa6500",
    "event_ts" : "1529795647.000077",
    "text" : "test",
    "ts" : "1529795647.000077",
    "channel_type" : "channel",
    "user" : "UAXAH4T52",
    "type" : "message",
    "channel" : "CBCPVHK4J"
}


if __name__ == '__main__':
    obj = EventMessage(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
