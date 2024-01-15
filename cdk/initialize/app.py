from aws_cdk import (
  aws_ec2 as ec2,
  aws_ecr as ecr,
  App, Stack, RemovalPolicy
)
import os

app = App()
stack = Stack(
  app, f"{os.environ.get("AWS_REGION")}-initialize",
  env={
    "account": os.environ.get("AWS_ACCOUNT_ID"),
    "region": os.environ.get("AWS_REGION")
  }
)

vpc = ec2.Vpc(
  stack, "Vpc",
  vpc_name=os.environ.get("AWS_REGION"),
  create_internet_gateway=True,
  max_azs=2,
  subnet_configuration=[
    ec2.SubnetConfiguration(
      name="Public",
      subnet_type=ec2.SubnetType.PUBLIC,
      map_public_ip_on_launch=True,
    )
  ],
  nat_gateways=0,
)

repository = ecr.Repository(
  stack, "Repository",
  image_scan_on_push=False,
  empty_on_delete=False,
  image_tag_mutability=ecr.TagMutability.MUTABLE,
  removal_policy=RemovalPolicy.DESTROY,
  repository_name=os.environ.get("REPOSITORY_NAME"),
  lifecycle_rules=[
    ecr.LifecycleRule(
      description="Retain only latest image.",
      rule_priority=1,
      max_image_count=1,
    )
  ]
)

app.synth()
