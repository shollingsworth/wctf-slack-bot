#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import aws_stack_base
import aws_lambda_vpc_rds
import constants
import argparse
import os
from StringIO import StringIO
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

# absolute current path
MYPATH = os.path.dirname(os.path.abspath(__file__))
PROGRAM_DESC = """
Create RDS and VPC Entry for bot/api
""".strip()


class LambdaVpcRdsCreate(aws_stack_base.StackBase):
    def set_parameters(
            self,
            eip1,
            eip2,
            acl,
            db_storage_size_gb=5,
    ):
        tag_eip1 = [{'Key': 'Name', 'Value': '{}-eip1'.format(self.base_name)}]
        tag_eip2 = [{'Key': 'Name', 'Value': '{}-eip2'.format(self.base_name)}]
        self.ec2.create_tags(Resources=[eip1], Tags=tag_eip1)
        self.ec2.create_tags(Resources=[eip2], Tags=tag_eip2)
        self.parameters = [
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_EXTERNALIPACL,
                'ParameterValue': acl,
            },
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_ENVIRONMENTNAME,
                'ParameterValue': self.base_name,
            },
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_IGWSUBNET1EIP,
                'ParameterValue': eip1,
            },
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_IGWSUBNET2EIP,
                'ParameterValue': eip2,
            },
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_RDSTEMPORARYDBPASSWORD,
                'ParameterValue': self.pw_generator(30),
            },
            {
                'ParameterKey': aws_lambda_vpc_rds.PARAM_RDSDBALLOCATEDSTORAGE,
                'ParameterValue': str(db_storage_size_gb),
            },
        ]

    def output(self, file_name=None):
        self.save = self.get_stack_outputs()
        dbinstance = self.save.get(constants.FIELD_SQL_INSTANCE_TYPE)
        res = self.rds.describe_db_instances(
            DBInstanceIdentifier=dbinstance
        ).get('DBInstances')[0]
        master_user = res.get('MasterUsername')
        endpoint_address = res.get('Endpoint', {}).get('Address')
        newpass = self.pw_generator(40)
        self.rds.modify_db_instance(
            DBInstanceIdentifier=dbinstance,
            MasterUserPassword=newpass,
        )
        self.save[constants.FIELD_SQL_MASTER_PASS] = newpass
        self.save[constants.FIELD_SQL_ENDPOINT] = endpoint_address
        self.save[constants.FIELD_SQL_MASTER_USER] = master_user
        self.save[constants.FIELD_LAMBDA_PROFILE_NAME] = self.profile
        self.save[constants.FIELD_LAMBDA_BASE_NAME] = self.base_name
        self.save[constants.FIELD_LAMBDA_REGION] = self.region
        key_populate = constants.ENV_MAP.values()
        empty_keys = {k: "" for k in key_populate if not self.save.get(k)}
        self.save.update(empty_keys)
        outs = json.dumps(self.save, indent=4, separators=(',', ' : '))
        if file_name:
            with open(file_name, 'wb') as fh:
                fh.write(outs)
            print(outs)
        else:
            print(outs)


def get_args(test_args=None):
    def usage(parser, help_block=''):
        out = StringIO()
        parser.print_usage(out)
        contents = out.getvalue()
        out.close()
        return "\n".join([help_block, contents])

    parser = argparse.ArgumentParser(
        description=PROGRAM_DESC,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--base_name",
        help="lambda / decriptive prefix",
        default='wctf-vpc-rds',
    )
    parser.add_argument(
        "--region",
        help="aws region",
        default='us-east-2',
    )
    parser.add_argument(
        "--environment",
        help="environment name i.e. dev/production",
        required=True,
    )
    parser.add_argument(
        "--profile",
        help="aws profile name in ~/.aws/credentials",
        required=True,
    )
    parser.add_argument(
        "--acl",
        help="external ACL address CIDR (i.e. 5.5.5.5/32)",
        required=True,
    )
    parser.add_argument(
        "--eip1",
        help="eip1 id",
        required=True,
    )
    parser.add_argument(
        "--eip2",
        help="eip2 id",
        required=True,
    )
    parser.add_argument(
        "--timeout",
        help="stack creation timeout in minutes",
        default=40,
    )
    parser.add_argument(
        "--debug",
        help="enable debug / logging",
        action='store_true',
        default=False,
    )
    parser.add_argument(
        "--size",
        help="db storage size",
        default=5,
    )
    parser.usage = usage(parser, "additional help")
    if test_args:
        args = type(str('args'), (), {})()
        [setattr(args, k, v) for k, v in test_args.items()]
    else:
        args = parser.parse_args()
    return args


if __name__ == '__main__':
    """
    arg_dict = {
        'base_name': 'wctf-vpc-rds',
        'region': 'us-east-2',
        'profile': 'personal',
        'environment': 'dev',
        'timeout': 40,  # minutes
        'debug': False,
    }
    args = get_args(arg_dict)
    """
    args = get_args()
    dest_file = "{}/{}.json".format(MYPATH, args.environment)
    obj = LambdaVpcRdsCreate(
        base_name = args.base_name,
        stack_template_text = aws_lambda_vpc_rds.template.to_json(),
        region = args.region,
        profile = args.profile,
        timeout = args.timeout,
        debug = args.debug,
    )
    try:
        obj.get_stack_outputs()
    except Exception as e:
        LOG.info("Lambda {} Doesn't exist, I'm creating it!".format(obj.base_name))
        obj.set_parameters(
            args.eip1,
            args.eip2,
            args.acl,
            args.size,
        )
        obj.create_stack()
        obj.output(dest_file)
