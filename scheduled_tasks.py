#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import botconfig
import json
from datetime import datetime
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def show_countdown():
    client = botconfig.get_slacker({'team_id': botconfig.TEAM_ID}, 'bot')
    diff = botconfig.DC_DATE - datetime.now()
    days, hours = [diff.days, int(diff.seconds / 60 / 60)]
    time_til_defcon = "`{}` days, `{}` hours until DefCon 26(`{} UTC`)".format(
        days,
        hours,
        botconfig.DC_DATE,
    )
    client.chat.post_message(botconfig.CHANNEL_MAIN, text=time_til_defcon)


def show_authed_teams():
    LOG.warn("Show authed teams invoked!")
    return json.dumps(botconfig.authed_teams, indent=4, separators=(',', ' : '))


if __name__ == '__main__':
    show_countdown()
