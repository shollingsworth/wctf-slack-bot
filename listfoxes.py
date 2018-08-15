#!/usr/bin/env python
# -*- coding: utf-8 -*-
import libfox
import json


def json_normalize(obj):
    try:
        json.dump(obj)
        return obj
    except Exception:
        return str(obj)


print(json.dumps(libfox.get_foxes(), indent=4, separators=(',', ' : '), default=json_normalize))
