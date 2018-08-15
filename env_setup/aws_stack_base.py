#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto3
import logging
from itertools import chain
import string
import random
import datetime
logging.basicConfig()


MAX_SIZE = 51200


class StackBase(object):
    def __init__(
        self,
        base_name,
        stack_template_text,
        region,
        profile=None,
        access_id=None,
        access_key=None,
        timeout = 5,
        debug = False
    ):

        if len(stack_template_text) >= MAX_SIZE + 1:
            raise Exception("Error, templates size: {} >= {}".format(
                len(stack_template_text),
            ))
        self.timeout = timeout
        self.log = logging.getLogger(__name__)
        if debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
        self.debug = debug
        self.stack_template = stack_template_text
        self.parameters = None
        self.base_name = base_name
        self.profile = profile
        self.access_id = access_id
        self.access_key = access_key
        self.region = region
        self.session = self.__get_session()
        self.region = region
        self.cloudformation = self.session.client('cloudformation')
        self.ec2 = self.session.client('ec2')
        self.rds = self.session.client('rds')
        if self.debug:
            self.set_debug()

    def __get_session(self):
        if self.profile:
            arg_dict = {
                'profile_name': self.profile,
                'region_name': self.region,
            }
        elif self.access_id and self.access_key:
            arg_dict = {
                'profile_name': self.profile,
                'aws_access_key_id': self.access_id,
                'aws_secret_access_key': self.access_key,
                'region_name': self.region,
            }
        else:
            raise Exception(" ".join([
                "Error, the following args were passed",
                "But I couldn't find a access_id / access_key, or profile",
                "Args: {}".format("\n".join([
                    'profile: {}'.format(self.profile),
                    'access_id: {}'.format(self.access_id),
                    'access_key: {}'.format(self.access_key),
                ]))
            ]))
        return boto3.Session(**arg_dict)

    def set_parameters(self):
        raise Exception("Error, self.get_parameters needs to be defined in a subclass")

    def pw_generator(self, size=40):
        chars = list(chain(
            string.ascii_uppercase,
            string.ascii_lowercase,
            string.digits,
        ))
        """
            string.punctuation
        chars.remove('@')
        chars.remove('"')
        chars.remove('/')
        chars.remove("'")
        """
        return ''.join(random.choice(chars) for _ in range(size))

    def set_debug(self):
        boto3.set_stream_logger('boto3', level=boto3.logging.DEBUG)
        boto3.set_stream_logger('botocore', level=boto3.logging.DEBUG)
        boto3.set_stream_logger('boto3.resources', level=boto3.logging.DEBUG)

    def create_stack(self):
        if not self.parameters:
            raise Exception("Error, self.set_parameters was not set or parameters are blank?")
        self.log.info("Creating Stack: {}".format(self.base_name))
        start = datetime.datetime.now()
        self.cloudformation.create_stack(
            StackName=self.base_name,
            TemplateBody=self.stack_template,
            Parameters=self.parameters,
            TimeoutInMinutes=self.timeout,
            OnFailure='ROLLBACK',
            Tags=[
                {
                    'Key': 'Name',
                    'Value': self.base_name,
                },
            ],
        )
        waiter = self.cloudformation.get_waiter('stack_create_complete')
        try:
            waiter.wait(StackName=self.base_name)
            end = datetime.datetime.now()
            self.log.info("Stack Creation a success: {} duration: {}".format(
                self.base_name,
                end - start,
            ))
            self.log.info("Done!")
        except Exception:
            self.log.exception("Stack Create Failed!")

    def get_stack_outputs(self):
        res = self.cloudformation.describe_stacks(
            StackName=self.base_name
        ).get('Stacks')[0].get('Outputs')
        ret_dict = {i.get('OutputKey'): i.get('OutputValue') for i in res}
        return ret_dict
