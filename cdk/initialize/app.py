from aws_cdk import (
  aws_autoscaling as autoscaling,
  aws_ec2 as ec2,
  aws_ecs as ecs,
  App, Stack
)
import os

app = App()
stack = Stack(app, f"{os.environ.get("AWS_REGION")}-initialize")

# Create a cluster
vpc = ec2.Vpc(
  stack, "vpc",
  vpc_name=f"{os.environ.get("AWS_REGION")}",
  create_internet_gateway=True,
  max_azs=2,
  subnet_configuration=[
    ec2.SubnetConfiguration(
      name="public",
      subnet_type=ec2.SubnetType.PUBLIC,
      map_public_ip_on_launch=True,
    )
  ],
  nat_gateways=0,
)
