#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MenuResponse(object):
    def __init__(
        self,
        data,
    ):
        self.name = data.get('name')
        self.callback_id = data.get('callback_id')
        self.team_id = data.get('team', {}).get('id')
        self.channel_id = data.get('channel', {}).get('id')
        self.user_id = data.get('user', {}).get('id')
        self.message_ts = data.get('message_ts')
        self.attachment_id = data.get('attachment_id')
