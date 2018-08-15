#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import CommandBase
import botconfig
import logging
from bgtask import task
from db_wctf.tables import FoxTrack
import libfox
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

HELP = "List foxes"


@task
def send(command_data):
    cmd = CommandBase(command_data)
    client = botconfig.get_slacker(cmd, 'bot')
    foxes = libfox.get_foxes()
    text_arr = ["invoked by: <@{}>".format(cmd.user_id)]
    for fox in foxes:
        bssid = fox.get(FoxTrack.bssid.name)
        ssid = fox.get(FoxTrack.ssid.name)
        lu = fox.get(FoxTrack.updated.name)
        pass_ = fox.get(FoxTrack.passphrase.name)
        if pass_:
            captured = 'Captured'
        else:
            captured = 'OUT'
        txt = " ".join([
            "captured: `{}`".format(captured),
            "bssid: `{}`".format(bssid),
            "ssid: `{}`".format(ssid),
            "last update: `{}`".format(lu),
        ])
        text_arr.append(txt)

    if not foxes:
        text_arr.append("NO FOXES Yet...")
    client.chat.post_message(
        cmd.channel_id,
        "\n".join(text_arr),
    )


class Process(CommandBase):
    def cmd(self):
        send(self.raw_data_json)
