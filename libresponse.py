#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import make_response
import hooker
import json
import logging
import botconfig
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

NO_RETRY = {"X-Slack-No-Retry": 1}


def json_normalize(obj):
    try:
        json.dump(obj)
        return obj
    except Exception:
        return str(obj)


def ok_say(msg='', headers={}):
    return make_response(
        msg,
        200,
        headers
    )


def error(msg="I don't know what went wrong :(", headers={}):
    print("ERROR: {}".format(msg))
    headers.update(NO_RETRY)
    return make_response(
        msg,
        510,
        headers,
    )


def not_found(msg='IDK what you\'re talking about'):
    print("404: {}".format(msg))
    return make_response(
        msg,
        404,
        NO_RETRY,
    )


def get_request_breakdown(request):
    """ try to breakdown request into something human readable that can be read in slack """
    attrs = {}
    for i in [i for i in dir(request) if hasattr(request, i) and not i.startswith('_')]:
        ga = getattr(request, i)
        try:
            val = json.loads(ga)
        except Exception:
            """ let's try one more time """
            val = str(ga)
            try:
                val = json.loads(val)
            except Exception:
                val = str(val)
        """ ok set the value, we're done... fuck it """
        attrs[i] = val
    """ dump the results as a json text """
    return json.dumps(attrs, indent=4, separators=(',', ' : '))


def bad_token(request=None):
    """ you've given me a bad token and should feel bad, dump to slack or gripe """
    if request:
        try:
            h = hooker.Hooker(botconfig.CHANNEL_BADUNS)
            req_body = get_request_breakdown(request)
            h.send("somethings fucky...", req_body)
        except Exception:
            LOG.exception("God Dammit! {} / {}".format(
                request,
                request.headers,
            ))
            raise

    return make_response(
        "fuck off...",
        403,
        NO_RETRY,
    )
