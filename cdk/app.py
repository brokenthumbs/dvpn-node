from aws_cdk import (
  aws_autoscaling as autoscaling,
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  aws_ecr_assets as ecr_assets,
  App, Stack, RemovalPolicy
)
from pathlib import Path
import cdk_docker_image_deployment as cdk_docker_image_deployment
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
  repository_name="dvpn-node",
  lifecycle_rules=[
    ecr.LifecycleRule(
      max_image_count=1,
    )
  ]
)

image = ecr_assets.DockerImageAsset(stack, "CDKDockerImage",
  directory=str(Path(__file__).parent.parent)
)


cdk_docker_image_deployment.DockerImageDeployment(
  stack, "DockerImageDeployment",
  source=cdk_docker_image_deployment.Source.directory("."),
  destination=cdk_docker_image_deployment.Destination.ecr(
    repository=repository,
    tag="latest",
  )
)

# ecr_deploy.ECRDeployment(stack, "DeployDockerImage",
#   src=ecr_deploy.DockerImageName(image.image_uri),
#   dest=ecr_deploy.DockerImageName(f"{repository.repository_uri}:latest"),
#   exclude=["cdk.out", "cdk", ".git"]
# )

app.synth()
