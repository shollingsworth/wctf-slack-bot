#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests


def delete_message(response_url, response_type='ephemeral'):
    payload = {
        "response_type": response_type,
        "delete_original": True,
    }
    r = requests.post(
        response_url,
        json=payload,
    )
    scode = r.status_code
    if not str(scode).startswith('2'):
        raise Exception("Bad Error response: {}".format(
            r.__dict__,
        ))
    return str(r.__dict__)


def replace_msg(response_url, message, attachments=[], response_type='ephemeral'):
    payload = {
        "response_type": response_type,
        "replace_original": True,
        "attachments": attachments,
        "text": message,
    }
    r = requests.post(
        response_url,
        json=payload,
    )
    scode = r.status_code
    if not str(scode).startswith('2'):
        raise Exception("Bad Error response: {}".format(
            r.__dict__,
        ))
    return str(r.__dict__)


def errresp(response_url, message, response_type='ephemeral'):
    payload = {
        "response_type": response_type,
        "replace_original": False,
        "text": message,
    }
    r = requests.post(
        response_url,
        json=payload,
    )
    scode = r.status_code
    if not str(scode).startswith('2'):
        raise Exception("Bad Error response: {}".format(
            r.__dict__,
        ))
    return str(r.__dict__)
