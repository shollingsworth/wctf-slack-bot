#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"fallback": "Required plain-text summary of the attachment.",
"color": "#2eb886",
"pretext": "Optional text that appears above the attachment block",
"author_name": "Bobby Tables",
"author_link": "http://flickr.com/bobby/",
"author_icon": "http://flickr.com/icons/bobby.jpg",
"title": "Slack API Documentation",
"title_link": "https://api.slack.com/",
"text": "Optional text that appears within the attachment",
"fields": [
    {
        "title": "Priority",
        "value": "High",
        "short": false
    }
],
"image_url": "http://my-website.com/path/to/image.jpg",
"thumb_url": "http://example.com/path/to/thumb.png",
"footer": "Slack API",
"footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
"ts": 123456789
"""


class BuildAttachment(object):
    def __init__(
        self,
    ):
        self.fallback = None
        self.color = None
        self.pretext = None
        self.author_name = None
        self.author_link = None
        self.author_icon = None
        self.title = None
        self.title_link = None
        self.text = None
        self.fields = []
        self.image_url = None
        self.thumb_url = None
        self.footer = None
        self.footer_icon = None
        self.ts = None
        self.actions = []

    def add_field(self, title, value, short=False):
        self.fields.append({
            'title': title,
            'value': value,
            'short': short,
        })

    def get_out(self):
        retval = {k: v for k, v in self.__dict__.items() if v}
        if not retval:
            raise Exception("Error, {} has no data set")
        return retval
