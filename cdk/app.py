from aws_cdk import (
  aws_autoscaling as autoscaling,
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  aws_ecr_assets as DockerImageAsset,
  App, Stack, RemovalPolicy
)
import * as ecrdeploy from "cdk-ecr-deployment";
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
    image_tag_mutability=ecr.TagMutability.MUTABLE,
    removal_policy=RemovalPolicy.DESTROY,
    repository_name="dvpn-node"
)
repository.add_lifecycle_rule(max_image_count=1)

image = DockerImageAsset(stack, "CDKDockerImage",
    directory=path.join(__dirname, "../")
)

ecrdeploy.ECRDeployment(stack, "DeployDockerImage1",
    src=ecrdeploy.DockerImageName(image.image_uri),
    dest=ecrdeploy.DockerImageName(f"{repository.repository_uri}:latest")
)

app.synth()
