#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
ZAPPA_FN = 'zappa_settings.json'


def get_zappa():
    with open(os.path.join(*[CONFIG_DIR, ZAPPA_FN]), 'r') as fh:
        return json.load(fh)


if __name__ == '__main__':
    import argparse
    program_desc = "Generate Bash Exports for Testing in the local environment"
    parser = argparse.ArgumentParser(
        description=program_desc,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "environment",
        help="emulate environment from: {}".format(ZAPPA_FN),
    )

    args = parser.parse_args()
    """
    class args(object):
        environment = 'ngrok'

    """
    zappa_config = get_zappa()
    if args.environment not in zappa_config:
        raise Exception(" ".join([
            "Error, environment needs to be one of",
            "{}".format(zappa_config.keys()),
        ]))
    env_dict = zappa_config.get(args.environment).get('environment_variables')
    for k, v in env_dict.items():
        if not v:
            LOG.warn("WARNING, key: {} has no value".format(k))
        print("export {}='{}'".format(k, v))
