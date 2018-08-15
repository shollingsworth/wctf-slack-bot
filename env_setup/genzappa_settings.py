#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import random
import json
import json_crypt
import glob
import os
import logging
import constants
from constants import ENV_MAP, ZAPPA_FN, PROJECT_NAME, CONFIG_DIR
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(constants.LOG_LEVEL)


MEMORY_SIZE = 128


# https://stackoverflow.com/a/14902564/7049363
def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            raise ValueError("duplicate key: {}".format(k))
        else:
            d[k] = v
    return d


class ZappaGen(object):
    def __init__(
        self,
        env_file,
        project_name,
    ):
        self.project_name = project_name
        self.env_file = env_file
        self.env = self.get_cf_data()
        all_keys = ENV_MAP.values() + [getattr(constants, i) for i in dir(constants) if i.startswith('FIELD_')]
        missing = list(set(all_keys) - set(self.env.keys()))
        stragglers = list(set(self.env.keys()).difference(set(all_keys)))
        if missing:
            LOG.error("Error, missing keys: {} in file: {}".format(missing, self.env_file))
        if stragglers:
            LOG.warn("Warning, file: {} has obsolete keys: {}".format(
                self.env_file,
                ",".join(stragglers),
            ))

    def get_env_dict(self):
        retdict = {
            'SECRET_KEY': self.id_generator(),
        }
        for env_key, lookup in ENV_MAP.items():
            val = self.env.get(lookup)
            if not val:
                LOG.error("key {} in file: {} is missing".format(
                    lookup,
                    self.env_file,
                ))
            retdict[env_key] = self.env.get(lookup)
        return retdict

    def get_cf_data(self):
        with open(self.env_file, 'r') as cf:
            cf_data = json.load(cf, object_pairs_hook=dict_raise_on_duplicates)
        return cf_data

    def get_config(self):
        return {
            'log_level': self.env.get(constants.FIELD_LOG_LEVEL),
            'memory_size': MEMORY_SIZE,
            'app_function': 'main.app',
            'aws_region': self.env.get(constants.FIELD_LAMBDA_REGION),
            'project_name': self.project_name,
            'runtime': 'python2.7',
            's3_bucket': self.env.get(constants.FIELD_LAMBDA_BUCKET),
            'profile_name': self.env.get(constants.FIELD_LAMBDA_PROFILE_NAME),
            'environment_variables': self.get_env_dict(),
            'exception_handler': 'lambda_exception.uncaughthandler',
            'events': self.env.get(constants.FIELD_EVENTS),
            'vpc_config': {
                'SubnetIds': [
                    self.env.get(constants.FIELD_LAMBDA_SUB1),
                    self.env.get(constants.FIELD_LAMBDA_SUB2),
                ],
                'SecurityGroupIds': [
                    self.env.get(constants.FIELD_LAMBDA_SG),
                ]
            }
        }

    def id_generator(self, size=200):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for _ in range(size))


if __name__ == '__main__':
    chdir = "{}/..".format(CONFIG_DIR)
    os.chdir(chdir)
    LOG.debug("Changing to directory: {}".format(CONFIG_DIR))
    dest_dir = CONFIG_DIR
    try:
        os.remove(ZAPPA_FN)
        LOG.info("Removing Exsiting Symlink: {}".format(ZAPPA_FN))
    except Exception:
        pass
    dest_file = '{}/{}'.format(dest_dir, ZAPPA_FN)

    files = glob.glob('{}/*.json'.format(dest_dir))
    zappa_dict = {}
    for file_ in files:
        LOG.info("Processing file: {}".format(file_))
        base_name = os.path.basename(file_).replace('.json', '')
        if base_name.startswith(constants.IGNORE_FILE_PREFIX):
            LOG.info("Skipping: {}".format(file_))
            continue
        zobj = ZappaGen(file_, PROJECT_NAME)
        zappa_dict[base_name] = zobj.get_config()
        LOG.info("Done: {}".format(file_))

    LOG.info("Writing to destination file: {}".format(dest_file))
    json_text = json.dumps(zappa_dict, indent=4, separators=(',', ' : '))
    with open(dest_file , 'wb') as fh:
        fh.write(json_text)
    LOG.info("Symlinking {} => {}".format(dest_file, ZAPPA_FN))
    link_path = "{}/{}".format(dest_dir, ZAPPA_FN)
    os.symlink(link_path, ZAPPA_FN)
    LOG.info("Attempting Encryption on json files")
    crypt_obj = json_crypt.CryptBase()
    crypt_obj.encrypt()
    LOG.debug("OUT:\n{}".format(json_text))
