from aws_cdk import (
  aws_autoscaling as autoscaling,
  core as cdk,
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  App, Stack
)
import os

app = App()
stack = Stack(app, f"{os.environ.get("AWS_REGION")}")

# Create a cluster
vpc = ec2.Vpc(
  stack, "vpc",
  vpc_name=f"{os.environ.get("AWS_REGION")}",
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

cluster = ecs.Cluster(
    stack, "EcsCluster",
    vpc=vpc,
    cluster_name="dvpn-node",
    enable_fargate_capacity_providers=True
)

repository = ecr.Repository(
    stack, "Repository",
    image_scan_on_push=False,
    empty_on_delete=False,
    auto_delete_images=True,
    image_tag_mutability=ecr.TagMutability.MUTABLE,
    removal_policy=cdk.RemovalPolicy.DESTROY,
    repository_name="dvpn-node"
)
repository.add_lifecycle_rule(max_image_count=1)

app.synth()
