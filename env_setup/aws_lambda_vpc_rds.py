#!/usr/bin/env python
# -*- coding: utf-8 -*-
from troposphere import (
    Sub,
    Select,
    GetAZs,
    Join,
    GetAtt,
    Output
)
from troposphere import (
    Parameter,
    Ref,
    Tags,
    Template
)
from troposphere.s3 import Bucket
from troposphere.rds import (
    DBInstance,
    DBParameterGroup,
    DBSubnetGroup,
)
from troposphere.ec2 import (
    InternetGateway,
    NatGateway,
    Route,
    RouteTable,
    SecurityGroup,
    Subnet,
    SubnetRouteTableAssociation,
    VPC,
    VPCGatewayAttachment
)

OUTPUT_DBINSTANCE = 'dbinstance'
OUTPUT_RDSPORT = 'dbport'
OUTPUT_IGWSUB1 = 'igwsub1'
OUTPUT_IGWSUB2 = 'igwsub2'
OUTPUT_PRIVSUB1 = 'privsub1'
OUTPUT_PRIVSUB2 = 'privsub2'
OUTPUT_S3BUCKET = 's3bucket'
OUTPUT_SGLAMBDA = 'sglambda'
OUTPUT_SGRDSEXTERNAL = 'sgrdsexternal'
OUTPUT_SGRDSINTERNAL = 'sgrdsinternal'
OUTPUT_VPC = 'vpc'

PARAM_EXTERNALIPACL = 'ExternalNetworkACL'
PARAM_ENVIRONMENTNAME = 'EnvironmentName'
PARAM_PRIVATE2CIDR = 'Private2CIDR'
PARAM_PRIVATE1CIDR = 'Private1CIDR'
PARAM_IGWSUBNET2EIP = 'IgwSubnet2Eip'
PARAM_IGWSUBNET2CIDR = 'IgwSubnet2CIDR'
PARAM_RDSDBUSER = 'RDSDBUser'
PARAM_VPCCIDR = 'VpcCIDR'
PARAM_IGWSUBNET1EIP = 'IgwSubnet1Eip'
PARAM_RDSTEMPORARYDBPASSWORD = 'RDSTemporaryDBPassword'
PARAM_RDSENGINE = 'RDSEngine'
PARAM_RDSMULTIAZDATABASE = 'RDSMultiAZDatabase'
PARAM_RDSENGINEVERSION = 'RDSEngineVersion'
PARAM_RDSDBCLASS = 'RDSDBClass'
PARAM_RDSDBALLOCATEDSTORAGE = 'RDSDBAllocatedStorage'
PARAM_IGWSUBNET1CIDR = 'IgwSubnet1CIDR'
PARAM_RDSPORT = 'RDSPort'
PARAM_RDSDBNAME = 'RDSDBName'


##############################
# TEMPLATE INIT
##############################
template = Template()
template.add_description("Create a Lambda Setup with RDS Capability")

##############################
# Parameters
##############################
EnvironmentName = template.add_parameter(Parameter(
    PARAM_ENVIRONMENTNAME,
    Type="String",
    Description="An environment name that will be prefixed to resource names",
))

RDSDBUser = template.add_parameter(Parameter(
    PARAM_RDSDBUSER,
    Default="sqlmaster",
    Type="String",
    Description="Master DB User",
))

ExternalIpACL = template.add_parameter(Parameter(
    PARAM_EXTERNALIPACL,
    Type="String",
    Description="External CIDR entry",
))

Private1CIDR = template.add_parameter(Parameter(
    PARAM_PRIVATE1CIDR,
    Default="172.16.2.0/24",
    Type="String",
    Description="Please enter the IP range (CIDR notation) for the private subnet in the 1st Availability Zone",
))

RDSTemporaryDBPassword = template.add_parameter(Parameter(
    PARAM_RDSTEMPORARYDBPASSWORD,
    Type="String",
    Description="Randomized Password - this will be changed in a later script",
))

IgwSubnet2CIDR = template.add_parameter(Parameter(
    PARAM_IGWSUBNET2CIDR,
    Default="172.16.1.0/24",
    Type="String",
    Description="Please enter the IP range (CIDR notation) for the public subnet in the 2nd Availability Zone",
))

Private2CIDR = template.add_parameter(Parameter(
    PARAM_PRIVATE2CIDR,
    Default="172.16.3.0/24",
    Type="String",
    Description="Please enter the IP range (CIDR notation) for the private subnet in the 2nd Availability Zone",
))

VpcCIDR = template.add_parameter(Parameter(
    PARAM_VPCCIDR,
    Default="172.16.0.0/22",
    Type="String",
    Description="Please enter the IP range (CIDR notation) for this VPC",
))

IgwSubnet1Eip = template.add_parameter(Parameter(
    PARAM_IGWSUBNET1EIP,
    Type="String",
    Description="Eip For IgwSubnet1",
))

IgwSubnet2Eip = template.add_parameter(Parameter(
    PARAM_IGWSUBNET2EIP,
    Type="String",
    Description="Eip For IgwSubnet2",
))

RDSEngine = template.add_parameter(Parameter(
    PARAM_RDSENGINE,
    Default="MySQL",
    Type="String",
    Description="DB Engine",
))

RDSMultiAZDatabase = template.add_parameter(Parameter(
    PARAM_RDSMULTIAZDATABASE,
    Default='True',
    Type="String",
    Description="Has Multiple Availability Zones",
))

RDSDBClass = template.add_parameter(Parameter(
    PARAM_RDSDBCLASS,
    Default="db.t2.micro",
    Type="String",
    Description="DB Instance Class",
))

RDSEngineVersion = template.add_parameter(Parameter(
    PARAM_RDSENGINEVERSION,
    Default="5.7",
    Type="String",
    Description="DB Engine Version",
))

RDSDBName = template.add_parameter(Parameter(
    PARAM_RDSDBNAME,
    Default="default_db",
    Type="String",
    Description="Initial Database Name",
))

RDSDBAllocatedStorage = template.add_parameter(Parameter(
    PARAM_RDSDBALLOCATEDSTORAGE,
    Default=5,
    Type="Number",
    Description="Allocate Storage in GB",
))

IgwSubnet1CIDR = template.add_parameter(Parameter(
    PARAM_IGWSUBNET1CIDR,
    Default="172.16.0.0/24",
    Type="String",
    Description="Please enter the IP range (CIDR notation) for the public subnet in the 1st Availability Zone",
))

RDSPort = template.add_parameter(Parameter(
    PARAM_RDSPORT,
    Default='3306',
    Type="String",
    Description="SQL Port Number",
))

##############################
# RESOURCES
##############################
Igw = template.add_resource(InternetGateway(
    "Igw",
    Tags=Tags(
        Name=Sub("${EnvironmentName} Igw"),
    ),
))

PrivateRoute2Default = template.add_resource(Route(
    "PrivateRoute2Default",
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("PrivateRoute2Table"),
    NatGatewayId=Ref("NatGateway2"),
    DependsOn="NatGateway2",
))

RDSInternalSecurityGroup = template.add_resource(SecurityGroup(
    "RDSInternalSecurityGroup",
    SecurityGroupIngress=[
        {
            "ToPort": Ref(RDSPort),
            "IpProtocol": "tcp",
            "CidrIp": Ref(VpcCIDR),
            "FromPort": Ref(RDSPort)
        }
    ],
    GroupName=Sub("${EnvironmentName}_rds_internal_sg"),
    VpcId=Ref("VPC"),
    GroupDescription=Sub("${EnvironmentName} Internal Security Group"),
    Tags=Tags(
        Name=Sub("${EnvironmentName} RDS Internal Security Group"),
    ),
))

IgwAttachment = template.add_resource(VPCGatewayAttachment(
    "IgwAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref(Igw),
))

PrivateRoute1Table = template.add_resource(RouteTable(
    "PrivateRoute1Table",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Sub("${EnvironmentName} Private1 Route (AZ1)"),
    ),
))

PrivateRoute1Default = template.add_resource(Route(
    "PrivateRoute1Default",
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref(PrivateRoute1Table),
    NatGatewayId=Ref("NatGateway1"),
    DependsOn="NatGateway1",
))

Private1RouteTableAssociation = template.add_resource(SubnetRouteTableAssociation(
    "Private1RouteTableAssociation",
    SubnetId=Ref("Private1"),
    RouteTableId=Ref(PrivateRoute1Table),
    DependsOn="PrivateRoute1Default",
))

IgwRouteTable = template.add_resource(RouteTable(
    "IgwRouteTable",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Sub("${EnvironmentName} Igw Routes"),
    ),
    DependsOn="IgwAttachment",
))

IgwRouteDefault = template.add_resource(Route(
    "IgwRouteDefault",
    GatewayId=Ref(Igw),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref(IgwRouteTable),
    DependsOn="IgwRouteTable",
))

PrivateRoute2Table = template.add_resource(RouteTable(
    "PrivateRoute2Table",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Sub("${EnvironmentName} Private2 Route (AZ2)"),
    ),
))

NatGateway1 = template.add_resource(NatGateway(
    "NatGateway1",
    SubnetId=Ref("IgwSubnet1"),
    AllocationId=Ref(IgwSubnet1Eip),
    Tags=Tags(
        Name=Sub("${EnvironmentName} NatGw (AZ1)"),
    ),
))

NatGateway2 = template.add_resource(NatGateway(
    "NatGateway2",
    SubnetId=Ref("IgwSubnet2"),
    AllocationId=Ref(IgwSubnet2Eip),
    Tags=Tags(
        Name=Sub("${EnvironmentName} NatGw (AZ2)"),
    ),
))

VPC = template.add_resource(VPC(
    "VPC",
    EnableDnsSupport=True,
    CidrBlock=Ref(VpcCIDR),
    EnableDnsHostnames=True,
    Tags=Tags(
        Name=Ref(EnvironmentName),
    ),
))

Private2 = template.add_resource(Subnet(
    "Private2",
    Tags=Tags(
        Name=Sub("${EnvironmentName} Private Subnet (AZ2)"),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(Private2CIDR),
    MapPublicIpOnLaunch=False,
    AvailabilityZone=Select(1, GetAZs("")),
))

Private1 = template.add_resource(Subnet(
    "Private1",
    Tags=Tags(
        Name=Sub("${EnvironmentName} Private Subnet (AZ1)"),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(Private1CIDR),
    MapPublicIpOnLaunch=False,
    AvailabilityZone=Select(0, GetAZs("")),
))

IgwSubnet2 = template.add_resource(Subnet(
    "IgwSubnet2",
    Tags=Tags(
        Name=Sub("${EnvironmentName} Igw Subnet (AZ2)"),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(IgwSubnet2CIDR),
    MapPublicIpOnLaunch=False,
    AvailabilityZone=Select(1, GetAZs("")),
))

IgwSubnet1 = template.add_resource(Subnet(
    "IgwSubnet1",
    Tags=Tags(
        Name=Sub("${EnvironmentName} Igw Subnet (AZ1)"),
    ),
    VpcId=Ref(VPC),
    CidrBlock=Ref(IgwSubnet1CIDR),
    MapPublicIpOnLaunch=False,
    AvailabilityZone=Select(0, GetAZs("")),
))

ZappaLamdbaBucket = template.add_resource(Bucket(
    "ZappaLamdbaBucket",
    BucketName=Join("-", [Ref(EnvironmentName), Ref(VPC)]),
))

RDSDBInstance = template.add_resource(DBInstance(
    "RDSDBInstance",
    Engine=Ref(RDSEngine),
    MultiAZ=Ref(RDSMultiAZDatabase),
    PubliclyAccessible=True,
    Tags=Tags(
        Name=Sub("${EnvironmentName} RDS Instance"),
    ),
    MasterUsername=Ref(RDSDBUser),
    MasterUserPassword=Ref(RDSTemporaryDBPassword),
    VPCSecurityGroups=[GetAtt("RDSExternalSecurityGroup", "GroupId"), GetAtt(RDSInternalSecurityGroup, "GroupId")],
    AllocatedStorage=Ref(RDSDBAllocatedStorage),
    EngineVersion=Ref(RDSEngineVersion),
    DBInstanceClass=Ref(RDSDBClass),
    DBSubnetGroupName=Ref("RDSDBSubnetGroup"),
    DBName=Ref(RDSDBName),
    DependsOn="RDSDBSubnetGroup",
))

RDSExternalSecurityGroup = template.add_resource(SecurityGroup(
    "RDSExternalSecurityGroup",
    SecurityGroupIngress=[
        {
            "ToPort": Ref(RDSPort),
            "IpProtocol": "tcp",
            "CidrIp": Ref(ExternalIpACL),
            "FromPort": Ref(RDSPort)
        },
    ],
    GroupName=Sub("${EnvironmentName}_rds_external_sg"),
    GroupDescription=Sub("${EnvironmentName} RDS External Security Group"),
    VpcId=Ref(VPC),
    Tags=Tags(
        Name=Sub("${EnvironmentName} RDS External Security Group"),
    ),
))

IgwSubnet2RouteAssociation = template.add_resource(SubnetRouteTableAssociation(
    "IgwSubnet2RouteAssociation",
    SubnetId=Ref(IgwSubnet2),
    RouteTableId=Ref(IgwRouteTable),
    DependsOn="IgwRouteDefault",
))

RDSDBParameterGroup = template.add_resource(DBParameterGroup(
    "RDSDBParameterGroup",
    Parameters={"sql_mode": "STRICT_ALL_TABLES,STRICT_TRANS_TABLES", "innodb_strict_mode": 1},
    Description="Custom Parameters Make it strict",
    Family="mysql5.7",
    Tags=Tags(
        Name=Sub("${EnvironmentName} RDS Parameter Group"),
    ),
    DependsOn=["Private1RouteTableAssociation", "Private2RouteTableAssociation"],
))

InternalSecurityGroup = template.add_resource(SecurityGroup(
    "InternalSecurityGroup",
    SecurityGroupIngress=[{"ToPort": "-1", "IpProtocol": "-1", "CidrIp": Ref(VpcCIDR), "FromPort": "-1"}],
    GroupName=Sub("${EnvironmentName}_internal_sg"),
    VpcId=Ref(VPC),
    GroupDescription=Sub("${EnvironmentName} Internal Security Group"),
    Tags=Tags(
        Name=Sub("${EnvironmentName} Internal Security Group"),
    ),
))

IgwSubnet1RouteAssociation = template.add_resource(SubnetRouteTableAssociation(
    "IgwSubnet1RouteAssociation",
    SubnetId=Ref(IgwSubnet1),
    RouteTableId=Ref(IgwRouteTable),
    DependsOn="IgwRouteDefault",
))

Private2RouteTableAssociation = template.add_resource(SubnetRouteTableAssociation(
    "Private2RouteTableAssociation",
    SubnetId=Ref(Private2),
    RouteTableId=Ref(PrivateRoute2Table),
    DependsOn="PrivateRoute2Default",
))

RDSDBSubnetGroup = template.add_resource(DBSubnetGroup(
    "RDSDBSubnetGroup",
    DBSubnetGroupName="String",
    DBSubnetGroupDescription="String",
    SubnetIds=[Ref(IgwSubnet1), Ref(IgwSubnet2)],
    Tags=Tags(
        Name=Sub("${EnvironmentName} RDS Subnet Group"),
    ),
    DependsOn=["RDSDBParameterGroup", "RDSInternalSecurityGroup", "RDSExternalSecurityGroup"],
))

##############################
# OUTPUTS
##############################
sglambda = template.add_output(Output(
    OUTPUT_SGLAMBDA,
    Description="Internal Security Group Id",
    Value=Ref(InternalSecurityGroup),
))

privsub1 = template.add_output(Output(
    OUTPUT_PRIVSUB1,
    Description="A reference to the private subnet in the 1st Availability Zone",
    Value=Ref(Private1),
))

privsub2 = template.add_output(Output(
    OUTPUT_PRIVSUB2,
    Description="A reference to the private subnet in the 2nd Availability Zone",
    Value=Ref(Private2),
))

igwsub2 = template.add_output(Output(
    OUTPUT_IGWSUB2,
    Description="A reference to the public subnet in the 1st Availability Zone",
    Value=Ref(IgwSubnet2),
))

sgrdsinternal = template.add_output(Output(
    OUTPUT_SGRDSINTERNAL,
    Description="RDS Internal Security Group Id",
    Value=Ref(RDSInternalSecurityGroup),
))

igwsub1 = template.add_output(Output(
    OUTPUT_IGWSUB1,
    Description="A reference to the public subnet in the 1st Availability Zone",
    Value=Ref(IgwSubnet1),
))

s3bucket = template.add_output(Output(
    OUTPUT_S3BUCKET,
    Description="Bucket For Zappa Lamdbdas",
    Value=Ref(ZappaLamdbaBucket),
))

sgrdsexternal = template.add_output(Output(
    OUTPUT_SGRDSEXTERNAL,
    Description="RDS External Security Group Id",
    Value=Ref(RDSExternalSecurityGroup),
))

vpc = template.add_output(Output(
    OUTPUT_VPC,
    Description="A reference to the created VPC",
    Value=Ref(VPC),
))

dbinstance = template.add_output(Output(
    OUTPUT_DBINSTANCE,
    Description="A reference to the created VPC",
    Value=Ref(RDSDBInstance),
))

dbinstance = template.add_output(Output(
    OUTPUT_RDSPORT,
    Description="RDS Instance Port Number",
    Value=Ref(RDSPort),
))

if __name__ == '__main__':
    print(template.to_yaml())
