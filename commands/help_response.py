#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import CommandBase
import botconfig
import libslackresponder
import logging
import available_commands
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

HELP = 'Show Help Menu'


def get_cmds():
    CMDS = {}
    for i in dir(available_commands):
        try:
            m = getattr(available_commands, i)
        except AttributeError:
            CMDS.append("ERROR Loading: {} / {}".format(available_commands, i))
            continue

        if hasattr(m, 'HELP'):
            name = m.__name__.split('.')[-1]
            name = name.replace('_response', '') if name.endswith('_response') else name
            CMDS[name] = "{} - {}".format(name , m.HELP)
    return CMDS


class Process(CommandBase):
    def cmd(self):
        CMDS = get_cmds()
        LOG.info("Sending Help: cmd: {} - {}".format(self.command, "\n".join(CMDS.values())))
        libslackresponder.errresp(self.response_url, "{}\n{}".format('Help: ', "\n".join(CMDS.values())))
