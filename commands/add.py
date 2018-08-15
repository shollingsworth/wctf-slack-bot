#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import CommandBase
import dialog
import botconfig
import logging
from bgtask import task
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

HELP = "Create a SSID"


@task
def send_form(command_data):
    self = CommandBase(command_data)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    client = botconfig.get_slacker(self, 'bot')
    LOG.debug("Send Form {}".format(self.__dict__))
    _dialog = dialog.add.get_dialog_interface(self)
    client.dialog.open(
        _dialog,
        self.trigger_id,
    )


class Process(CommandBase):
    def cmd(self):
        send_form(self.raw_data_json)
