#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import BaseEventProcess
import logging
import botconfig
import json
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)


class Process(BaseEventProcess):
    def process_event(self):
        channel_id = self.event.get('channel')
        channel_type = self.event.get('channel_type')
        if not channel_id:
            raise Exception("Error could not determine channel from:\n{}".format(
                self.raw_data_json
            ))
        client = botconfig.get_slacker(self, 'user')
        bot_user = botconfig.get_bot_user(self)
        LOG.debug("event:\n{}".format(
            json.dumps(self.raw_data_json, indent=4, separators=(',', ' : '))
        ))
        client
        bot_user
        channel_type
