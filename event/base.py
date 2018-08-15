#!/usr/bin/env python
# -*- coding: utf-8 -*-
from slack_data_objects import Event


class BaseEventProcess(Event):
    def process_event(self):
        raise Exception("Error, this class needs to be overriden")
