#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Command(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.channel_id = data.get('channel_id')
        self.channel_name = data.get('channel_name')
        self.command = data.get('command')
        self.response_url = data.get('response_url')
        self.team_domain = data.get('team_domain')
        self.team_id = data.get('team_id')
        self.text = data.get('text')
        self.token = data.get('token')
        self.trigger_id = data.get('trigger_id')
        self.user_id = data.get('user_id')
        self.user_name = data.get('user_name')
