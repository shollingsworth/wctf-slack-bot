#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from dateutil.tz import tz
from dateutil.parser import parse
import pytz
TZ_ALL_ZONES = pytz.all_timezones_set
TZ_INCLUDE_STARTSWITH_FILTER = [
    'US',
    'India',
    'UTC',
    'Zulu',
    'Israel',
    'Japan',
    'Hongkong',
]
TZ_FILTERED_INCLUDES = [
    val for val in TZ_ALL_ZONES
    for excl in TZ_INCLUDE_STARTSWITH_FILTER
    if (
        val.startswith(excl) and
        not val.endswith('-New')
    )
]


def get_tz_included_zones():
    return sorted(list(set(TZ_ALL_ZONES).intersection(set(TZ_FILTERED_INCLUDES))))


def get_tz_excluded_zones():
    return sorted(list(set(TZ_ALL_ZONES).difference(set(TZ_FILTERED_INCLUDES))))


def get_utc_to_local(parse_str, local_timezone_name):
    utc_tz = pytz.utc
    local_tz = pytz.timezone(local_timezone_name)
    dt = parse(str(parse_str), ignoretz=True)
    local_dt = utc_tz.localize(dt, is_dst=None)
    return local_dt.astimezone(local_tz)


def get_local_to_utc(parse_str, local_timezone_name):
    local_tz = pytz.timezone(local_timezone_name)
    dt = parse(parse_str, ignoretz=True)
    local_dt = local_tz.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.utc)


if __name__ == '__main__':
    """
    import json
    print(json.dumps(get_tz_included_zones(), indent=4, separators=(',', ' : ')))
    my_tz = 'US/Eastern'
    my_tz = 'US/Pacific'
    parse_val = '6/9/2018 18:12:22'
    parse_val = 'Sat Jun  9 18:12:22 PDT 2018'
    parse_val = '2018.06.09 18:12:22'
    parse_val = '2018-06-09 18:12:22'
    print(get_utc_time(parse_val, my_tz))
    """
