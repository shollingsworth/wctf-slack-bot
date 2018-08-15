#!/usr/bin/env python
# -*- coding: utf-8 -*-
from slack_data_objects import Command


class CommandBase(Command):
    def cmd(self):
        raise Exception("Error, method 'cmd' needs to be overriden")
