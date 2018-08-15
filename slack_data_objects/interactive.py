#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Interactive(object):
    def __init__(
        self,
        data,
    ):
        self.raw_data_json = data
        self.action_ts = data.get('action_ts')
        self.actions = data.get('actions', [])
        self.attachment_id = data.get('attachment_id')
        self.callback_id = data.get('callback_id')
        self.channel = data.get('channel')
        self.channel_id = data.get('channel', {}).get('id')
        self.channel_name = data.get('channel', {}).get('name')
        self.message_ts = data.get('message_ts')
        self.original_message = data.get('original_message')
        self.original_message_attachments = data.get('original_message', {}).get('attachments')
        self.original_message_text = data.get('original_message', {}).get('text')
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
    "attachment_id" : "1",
    "response_url" : "https://hooks.slack.com/actions/T47563693/6204672533/x7ZLaiVMoECAW50Gw1ZYAXEM",
    "action_ts" : "1458170917.164398",
    "trigger_id" : "13345224609.738474920.8088930838d88f008e0",
    "original_message" : {
        "text" : "New comic book alert!",
        "attachments" : [
            {
                "fields" : [
                    {
                        "short" : True,
                        "value" : "1",
                        "title" : "Volume"
                    },
                    {
                        "short" : True,
                        "value" : "3",
                        "title" : "Issue"
                    }
                ],
                "author_icon" :
                "https://api.slack.comhttps://a.slack-edge.com/bfaba/img/api/homepage_custom_integrations-2x.png",
                "image_url" : "http://i.imgur.com/OJkaVOI.jpg?1",
                "author_name" : "Stanford S. Strickland",
                "title" : "The Further Adventures of Slackbot"
            },
            {
                "text" : "After @episod pushed exciting changes to a"
                    "devious new branch back in Issue 1, Slackbot notifies"
                    "@don about an unexpected deploy...",
                "title" : "Synopsis"
            },
            {
                "title" : "Would you recommend it to customers?",
                "color" : "#3AA3E3",
                "actions" : [
                    {
                        "text" : "Recommend",
                        "type" : "button",
                        "name" : "recommend",
                        "value" : "recommend"
                    },
                    {
                        "text" : "No",
                        "type" : "button",
                        "name" : "no",
                        "value" : "bad"
                    }
                ],
                "callback_id" : "comic_1234_xyz",
                "fallback" : "Would you recommend it to customers?",
                "attachment_type" : "default"
            }
        ]
    },
    "actions" : [
        {
            "type" : "button",
            "name" : "recommend",
            "value" : "recommend"
        }
    ],
    "callback_id" : "comic_1234_xyz",
    "token" : "xAB3yVzGS4BQ3O9FACTa8Ho4",
    "user" : {
        "id" : "U045VRZFT",
        "name" : "brautigan"
    },
    "team" : {
        "domain" : "watermelonsugar",
        "id" : "T47563693"
    },
    "type" : "interactive_message",
    "message_ts" : "1458170866.000004",
    "channel" : {
        "id" : "C065W1189",
        "name" : "forgotten-works"
    }
}


if __name__ == '__main__':
    obj = Interactive(SAMPLE_OBJECT)
    attributes = [i for i in dir(obj) if not i.startswith('__')]
    for i in attributes:
        print(i, getattr(obj, i))
