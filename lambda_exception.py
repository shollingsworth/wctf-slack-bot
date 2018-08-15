#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import botconfig
import traceback
import libslackresponder
from bgtask import task
import hooker
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(botconfig.DEFAULT_LOGGING)


def json_normalize(obj):
    try:
        json.dump(obj)
        return obj
    except Exception:
        return str(obj)


class LambdaContextVars(object):
    def __init__(
        self,
        context_dict,
    ):
        self.aws_request_id = context_dict['aws_request_id']
        self.log_stream_name = context_dict['log_stream_name']
        self.invoked_function_arn = context_dict['invoked_function_arn']
        self.client_context = context_dict['client_context']
        self.log_group_name = context_dict['log_group_name']
        self.function_name = context_dict['function_name']
        self.function_version = context_dict['function_version']
        self.identity = context_dict['identity']
        self.memory_limit_in_mb = context_dict['memory_limit_in_mb']


def uncaughttest():
    raise ValueError("Error testing")


def caughttest():
    try:
        raise ValueError("Caught Error Test")
    except Exception as e:
        data = {
            'foo': 'bar',
            'bar': 'baz',
        }
        caught(e, data)


@task
def __caughtbg(tb, emessage, data, response_url):
    if response_url:
        libslackresponder.errresp(response_url, emessage)
    h = hooker.Hooker(botconfig.CHANNEL_EXCEPTION)
    h.add_field(
        'Data',
        '```{}```'.format(
            json.dumps(data, indent=4, separators=(',', ' : '), default=json_normalize)
        ),
    )
    h.send('CAUGHT Exception', tb)


def caught(e, data, response_url=None):
    tb = traceback.format_exc(e)
    emessage = e.message
    __caughtbg(tb, emessage, data, response_url)


def uncaughthandler(e, event, context):
    # context = https://gist.github.com/gene1wood/c0d37dfcb598fc133a8c
    ctx = LambdaContextVars(context.__dict__)
    tb = traceback.format_exc(e)
    h = hooker.Hooker()
    field_arr = [
        {
            "title": 'Event',
            "value": '```{}```'.format(json.dumps(event, indent=4, separators=(',', ' : '), default=json_normalize)),
            "short": False,
        },
        {
            "title": 'AWS Request ID',
            "value": '`{}`'.format(ctx.aws_request_id),
            "short": False,
        },
        {
            "title": 'Client Context',
            "value": '```{}```'.format(ctx.client_context),
            "short": False,
        },
        {
            "title": 'ARN',
            "value": '`{}`'.format(ctx.invoked_function_arn),
            "short": False,
        },
    ]
    for i in field_arr:
        h.add_field(**i)
    return h.send('UNCAUGHT Exception', tb)
