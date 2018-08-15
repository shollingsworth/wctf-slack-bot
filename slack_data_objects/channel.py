#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Channel(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.created = data.get('created')
        self.creator = data.get('creator')
        self.id = data.get('id')
        self.is_archived = data.get('is_archived')
        self.is_channel = data.get('is_channel')
        self.is_general = data.get('is_general')
        self.is_member = data.get('is_member')
        self.is_mpim = data.get('is_mpim')
        self.is_org_shared = data.get('is_org_shared')
        self.is_private = data.get('is_private')
        self.is_shared = data.get('is_shared')
        self.last_read = data.get('last_read')
        self.latest = data.get('latest')
        self.latest_client_msg_id = data.get('latest', {}).get('client_msg_id')
        self.latest_text = data.get('latest', {}).get('text')
        self.latest_ts = data.get('latest', {}).get('ts')
        self.latest_type = data.get('latest', {}).get('type')
        self.latest_user = data.get('latest', {}).get('user')
        self.members = data.get('members')
        self.name = data.get('name')
        self.name_normalized = data.get('name_normalized')
        self.previous_names = data.get('previous_names')
        self.purpose = data.get('purpose')
        self.purpose_creator = data.get('purpose', {}).get('creator')
        self.purpose_last_set = data.get('purpose', {}).get('last_set')
        self.purpose_value = data.get('purpose', {}).get('value')
        self.topic = data.get('topic')
        self.topic_creator = data.get('topic', {}).get('creator')
        self.topic_last_set = data.get('topic', {}).get('last_set')
        self.topic_value = data.get('topic', {}).get('value')
        self.unlinked = data.get('unlinked')
        self.unread_count = data.get('unread_count')
        self.unread_count_display = data.get('unread_count_display')


# Sample Object
SAMPLE_OBJECT = {
    "is_general" : False,
    "name_normalized" : "incidents",
    "last_read" : "1528815107.000881",
    "creator" : "UAXAH4T52",
    "is_member" : True,
    "is_archived" : False,
    "topic" : {
        "last_set" : 1529809135,
        "value" : "STATUS: UNIDENTIFIED\nJIRA: TBD",
        "creator" : "UAXAH4T52"
    },
    "unread_count_display" : 65,
    "id" : "CB63WP8AW",
    "is_org_shared" : False,
    "is_channel" : True,
    "previous_names" : [],
    "is_mpim" : False,
    "purpose" : {
        "last_set" : 1529809134,
        "value" : "STATUS: UNIDENTIFIED\nJIRA: TBD\nSummary: foo\nDescription:\nbar\n",
        "creator" : "UAXAH4T52"
    },
    "members" : [
        "UAWS78848",
        "UAXAH4T52"
    ],
    "is_private" : False,
    "is_shared" : False,
    "name" : "incidents",
    "created" : 1528815107,
    "unread_count" : 66,
    "unlinked" : 0,
    "latest" : {
        "client_msg_id" : "68c55b07-6a2d-453d-8ac9-bbd71150f83e",
        "text" : "test",
        "type" : "message",
        "user" : "UAXAH4T52",
        "ts" : "1529892815.000187"
    }
}


if __name__ == '__main__':
    obj = Channel(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
