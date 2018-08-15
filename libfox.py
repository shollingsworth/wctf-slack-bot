# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import libsqlalchemy
import botconfig
from db_wctf import db
import json
import libverify
from db_wctf.tables import FoxTrack
from random import randint
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)

FIELD_RESULT = 'result'


def json_normalize(obj):
    try:
        json.dump(obj)
        return obj
    except Exception:
        return str(obj)


def get_rand_mac_address():
    return ":".join([
        str('{:02x}'.format(randint(1, 254)))
        for i in range(6)
    ])


def get_bssid(data):
    bssid = data.get(FoxTrack.bssid.name)
    if not bssid:
        raise ValueError("No 'bssid' field given")
    return libverify.verify_bssid(bssid)


def add_fox(data, source):
    """ add new fox """
    bssid = get_bssid(data)
    ssid = data.get(FoxTrack.ssid.name)

    # Im dumb, so lets avoid issues with bad json objects
    jdump = json.dumps(source, default=json_normalize)
    ins_source = json.loads(jdump)

    ins_data = {
        FoxTrack.bssid.name: bssid,
        FoxTrack.ssid.name: ssid,
        FoxTrack.source.name: ins_source,
    }
    res = libsqlalchemy.add_update_one(
        db,
        FoxTrack,
        ins_data,
    )
    data[FIELD_RESULT] = str(res)
    return data


def update_fox(data):
    """ update fox """
    bssid = get_bssid(data)
    # make sure its an existing record
    libsqlalchemy.get_by_id(db, FoxTrack, bssid)
    ssid = data.get(FoxTrack.ssid.name)
    passphrase = data.get(FoxTrack.passphrase.name)
    ins_data = {
        FoxTrack.bssid.name: bssid,
        FoxTrack.ssid.name: ssid,
        FoxTrack.passphrase.name: passphrase,
    }
    res = libsqlalchemy.add_update_one(
        db,
        FoxTrack,
        ins_data,
        bssid,  # key to update
    )
    data[FIELD_RESULT] = str(res)
    return data


def delete_fox(data):
    """ delete fox entry """
    bssid = get_bssid(data)
    return {
        FIELD_RESULT: libsqlalchemy.delete(db, FoxTrack, bssid),
        'deleted': bssid,
    }


def get_foxes():
    """ return a json list of all foxes """
    return libsqlalchemy.get_all(db, FoxTrack)
