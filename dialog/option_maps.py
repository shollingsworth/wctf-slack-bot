#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_wctf import db
import libdt


def get_key_values(Data):
    data = db.session.query(Data).all()
    arr = [
        {'label': i.value, 'value': i.key}
        for i in data
    ]
    return sorted(arr, key=lambda x: x.get('label'))


TIMEZONES = [{'label': i, 'value': i} for i in libdt.get_tz_included_zones()]
PERCENTAGE_STEP = 1
PERCENTAGE = [
    {'value' : i, 'label': '{:02d}%'.format(i)}
    for i in range(1, 100 + PERCENTAGE_STEP, PERCENTAGE_STEP)
]
