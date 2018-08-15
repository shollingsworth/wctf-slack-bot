#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Team(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.domain = data.get('domain')
        self.email_domain = data.get('email_domain')
        self.icon = data.get('icon')
        self.icon_image_102 = data.get('icon', {}).get('image_102')
        self.icon_image_132 = data.get('icon', {}).get('image_132')
        self.icon_image_230 = data.get('icon', {}).get('image_230')
        self.icon_image_34 = data.get('icon', {}).get('image_34')
        self.icon_image_44 = data.get('icon', {}).get('image_44')
        self.icon_image_68 = data.get('icon', {}).get('image_68')
        self.icon_image_88 = data.get('icon', {}).get('image_88')
        self.icon_image_default = data.get('icon', {}).get('image_default')
        self.id = data.get('id')
        self.name = data.get('name')

        self.url = "https://{}.slack.com".format(self.domain)

    def get_archive_link(self, channel_id, message_ts=None):
        if message_ts:
            message_ts = str(message_ts).replace('.', '')
        return "{}/archives/{}/p{}".format(
            self.url,
            channel_id,
            message_ts,
        )
