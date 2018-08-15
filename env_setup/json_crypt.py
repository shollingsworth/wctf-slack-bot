#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import shlex
import os
from glob import glob
from subprocess import Popen, PIPE
import logging
from constants import CONFIG_DIR, RECIPIENT_FILE, LOG_LEVEL
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(LOG_LEVEL)


class CryptBase(object):
    def __init__(self):
        self.orig_dir = os.getcwd()
        self.__switch_config_dir()
        self.recipients = "-r {}".format(" -r ".join(self.__get_recipients()))
        self.json_files = [i for i in glob('*.json')]
        self.gpg_files = [i for i in glob('*.json.gpg')]
        crypt_cmd = 'gpg --batch --yes -q -e {} -o {} {}'
        decrypt_cmd = 'gpg --no-tty -q --batch --yes -d -o {} {}'
        self.encrypt_cmds = [
            crypt_cmd.format(*[self.recipients, '{}.gpg'.format(i), i])
            for i in self.json_files
        ]
        self.decrypt_cmds = [
            decrypt_cmd.format(*[i.replace('.gpg', ''), i])
            for i in self.gpg_files
        ]
        self.__switch_orig_dir()

    def __get_recipients(self):
        rfile = os.path.join(*[CONFIG_DIR, RECIPIENT_FILE])
        with open(rfile, 'r') as fh:
            return [
                i.strip() for i in fh.read().split('\n')
                if not i.startswith('#') and
                i
            ]
        self.__switch_orig_dir()

    def __switch_config_dir(self):
        os.chdir(CONFIG_DIR)

    def __switch_orig_dir(self):
        os.chdir(self.orig_dir)

    def encrypt(self):
        self.__switch_config_dir()
        for i in self.encrypt_cmds:
            file_ = i.split()[-1]
            LOG.info("Encrypting file: {}".format(file_))
            LOG.debug("Running command: {}".format(i))
            o, err, _ = self.exec_cmd(i)
            LOG.debug("cmd result: {} {}".format(o.strip(), err.strip()))
        self.__switch_orig_dir()

    def decrypt(self):
        self.__switch_config_dir()
        for i in self.decrypt_cmds:
            file_ = i.split()[-1]
            LOG.info("Decrypting file: {}".format(file_))
            LOG.debug("Running command: {}".format(i))
            o, err, _ = self.exec_cmd(i)
            LOG.debug("cmd result: {} {}".format(o.strip(), err.strip()))
        self.__switch_orig_dir()

    def exec_cmd(self, cmd_str):
        cmd_arr = shlex.split(cmd_str)
        p = Popen(cmd_arr, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
        if rc != 0:
            raise Exception("\n".join([
                "Error running command: {}".format(cmd_str),
                "Return code: {}".format(rc),
                "STDERR:\n{}".format(err),
                "STDOUT:\n{}".format(output),
            ]))
        LOG.debug({
            'output': output,
            'err': err,
            'rc': rc,
        })
        return [output, err, rc]


if __name__ == '__main__':
    obj = CryptBase()
    func_map = {
        'encrypt': obj.encrypt,
        'decrypt': obj.decrypt,
    }
    program_desc = "Encrypt / Decrypt JSON Files for Project"
    parser = argparse.ArgumentParser(
        description=program_desc,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'operation',
        type=str,
        choices=func_map.keys(),
    )
    args = parser.parse_args()
    func_map[args.operation]()
