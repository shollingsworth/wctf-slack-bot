#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botconfig

if botconfig.IS_LAMBDA:
    from zappa.async import task
elif botconfig.DISABLE_BG:
    def task(func):
        return func
else:
    def task(func):
        from threading import Thread
        from functools import wraps

        @wraps(func)
        def async_func(*args, **kwargs):
            func_hl = Thread(target = func, args = args, kwargs = kwargs)
            func_hl.start()
            return func_hl
        return async_func
