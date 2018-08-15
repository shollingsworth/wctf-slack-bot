#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from random import randint
import requests
from os import environ
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


API_KEY = environ['CTFTOKEN']
if not API_KEY:
    raise ValueError("Error, env var: '{}' not set".format('CTFTOKEN'))

BASE_URL = environ.get('BASE_URL')
if not BASE_URL:
        raise ValueError("Error, env var: '{}' not set".format('BASE_URL'))

URL_POST_ADD_FOX = '{}/add_fox'.format(BASE_URL)
URL_POST_UPDATE_FOX = '{}/update_fox'.format(BASE_URL)
URL_POST_UPDATE_FOX = '{}/update_fox'.format(BASE_URL)
URL_POST_DELETE_FOX = '{}/delete_fox'.format(BASE_URL)
URL_GET_FOXES = '{}/foxes'.format(BASE_URL)
HEADER = {
    'CTFTOKEN': API_KEY,
    'Content-Type': 'application/json',
}


def mod_fox(dval):
    r = requests.post(
        URL_POST_UPDATE_FOX,
        json=dval,
        headers=HEADER,
    )
    return r.json()


def add_fox(dval):
    r = requests.post(
        URL_POST_ADD_FOX,
        json=dval,
        headers=HEADER,
    )
    return r.json()


def get_foxes():
    r = requests.get(
        URL_GET_FOXES,
        headers=HEADER,
    )
    return r.json()


def delete_fox(dval):
    r = requests.post(
        URL_POST_DELETE_FOX,
        json=dval,
        headers=HEADER,
    )
    return r.json()


def gen_mac_address():
    return ":".join([
        str('{:02x}'.format(randint(1, 254)))
        for i in range(6)
    ])
