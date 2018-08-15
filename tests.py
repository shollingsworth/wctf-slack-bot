#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict
from db_wctf.tables import FoxTrack
import json
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
from webfox import (
    gen_mac_address,
    get_foxes,
    add_fox,
    mod_fox,
    delete_fox,
)


if __name__ == '__main__':
    mod_mac = gen_mac_address()
    good_add = {
        FoxTrack.bssid.name: mod_mac,
        FoxTrack.ssid.name: 'foobar',
    }

    bad_add = {
        'blarg': 'i dont exist',
    }

    good_mod = {
        'bssid': mod_mac,
        'ssid': 'other_thing',
        'passphrase': 'super_secret',
    }

    bad_mod1 = {
        'bssid': '00:00:00:00:00:00',
        'ssid': 'i dont exist',
    }

    bad_mod2 = {
        'bssid': 'foo bar baz',
    }

    bad_mod3 = {
        'bssid': 'foo bar baz',
    }

    delete = {
        'bssid': mod_mac,
    }

    TEST_DICT = OrderedDict()
    TEST_DICT['existing'] = get_foxes()
    TEST_DICT['good_add'] = add_fox(good_add)
    TEST_DICT['bad_add'] = add_fox(bad_add)
    TEST_DICT['post_add_foxes'] = get_foxes()
    TEST_DICT['good_mod'] = mod_fox(good_mod)
    TEST_DICT['badmods'] = [
        mod_fox(bad_mod1),
        mod_fox(bad_mod2),
        mod_fox(bad_mod3),
    ]
    TEST_DICT['good_mod_foxes'] = get_foxes()
    TEST_DICT['delete'] = delete_fox(delete)
    for k, v in TEST_DICT.items():
        print("{} {}".format('*' * 20, k))
        print(json.dumps(v, indent=4, separators=(',', ' : ')))
