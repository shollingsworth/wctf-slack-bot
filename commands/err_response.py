#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import CommandBase
import botconfig
import libslackresponder
import logging
import available_commands
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

CMDS = []
for i in dir(available_commands):
    try:
        m = getattr(available_commands, i)
    except AttributeError:
        CMDS.append("ERROR Loading: {} / {}".format(available_commands, i))
        continue

    if hasattr(m, 'HELP'):
        CMDS.append("{} - {}".format(m.__name__.split('.')[-1], m.HELP))


class Process(CommandBase):
    def cmd(self):
        send_text = "\n".join([
            " ".join([
                "Error, invalid command: '{}',".format(self.text),
                "the following commands are available:"
            ]),
            "\n".join(CMDS),
        ])
        LOG.info("Sending Error: cmd: {} - {}".format(self.command, send_text))
        libslackresponder.errresp(self.response_url, send_text)
