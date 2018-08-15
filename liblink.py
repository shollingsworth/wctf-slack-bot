#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_channel_link(chan_id, chan_name):
    return "<#{}|{}>".format(chan_id, chan_name)


def get_user_link(user_id):
    return "<@{}>".format(user_id)
