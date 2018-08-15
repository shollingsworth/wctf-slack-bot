#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import jsonify
from .base import MenuResponse
from db_wctf import db
from db_wctf.tables import FoxTrack
import libsqlalchemy

DictData = ''  # placeholder


def add_wrapper(data, colname, SqlData, DictData):
    mr = MenuResponse(data)
    existing_arr = libsqlalchemy.get_filtered(
        db,
        SqlData,
        SqlData.channel_id.name,
        mr.channel_id,
    )
    all_vals = libsqlalchemy.get_all(db, DictData)
    exists = [i.get(colname) for i in existing_arr]
    av = [i for i in all_vals if i.get('key') not in exists]
    VALS = [
        {'value' : i.get('key'), 'text': i.get('value')}
        for i in av
    ]
    return jsonify({
        'options': VALS,
    })


def remove_wrapper(data, colname, SqlData, DictData):
    all_vals = {i.get('key'): i.get('value') for i in libsqlalchemy.get_all(db, DictData)}
    mr = MenuResponse(data)
    existing_arr = libsqlalchemy.get_filtered(
        db,
        SqlData,
        SqlData.channel_id.name,
        mr.channel_id,
    )
    VALS = [
        {'value' : i.get('uid'), 'text': all_vals.get(i.get(colname))}
        for i in existing_arr
    ]
    return jsonify({
        'options': VALS,
    })


def add_thing(data):
    return add_wrapper(
        data,
        FoxTrack.ssid.name,
        FoxTrack,
        DictData,
    )


def remove_thing(data):
    return remove_wrapper(
        data,
        FoxTrack.ssid.name,
        FoxTrack,
        DictData,
    )
