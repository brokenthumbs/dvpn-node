from aws_cdk import (
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  App, Stack
)
import boto3
import os

app = App()
stack = Stack(
  app, f"{os.environ.get("AWS_REGION")}-update"
  env={
    "account": os.environ.get("AWS_ACCOUNT_ID"),
    "region": os.environ.get("AWS_REGION")
  }
)

ssm_client = boto3.client("ssm", region_name=os.environ.get("AWS_REGION"))

def wallet_key(number: int) -> str:
  return f"{os.environ.get("AWS_REGION")}-{format(number, "04d")}"

def exist_ssm_parameter(param_name: str) -> bool:
  try:
    ssm_client.get_parameter(Name=param_name)
    return True
  except ssm_client.exceptions.ParameterNotFound:
    return False

vpc = ec2.Vpc.from_lookup(stack, "Vpc", vpc_id=os.environ.get("AWS_REGION"))

cluster = ecs.Cluster(
  stack, "EcsCluster",
  vpc=vpc,
  cluster_name=os.environ.get("CLUSTER_NAME"),
  enable_fargate_capacity_providers=True
)

wallet_number = 1
while exist_ssm_parameter(wallet_key(wallet_number)):
  print(f"creating fargate service for wallet: {wallet_key(wallet_number)}")
  fargate_task_definition = ecs.FargateTaskDefinition(
    stack, f"FargateTaskDefinition-{wallet_key(wallet_number)}",
    memory_limit_mib=512,
    cpu=256,
  )
  fargate_task_definition.add_container(
    os.environ.get("REPOSITORY_NAME"),
    image=ecs.ContainerImage.from_ecr_repository(
      repository=os.environ.get("REPOSITORY_NAME"),
      tag="latest"
    ),
    secrets={
      "PASSWORD": ecs.Secret.from_ssm_parameter("PASSWORD"),
      "BIP39_MNEMONIC": ecs.Secret.from_ssm_parameter(wallet_key(wallet_number))
    },
    command="start",
    logging=None,
    port_mappings=[
      ecs.PortMapping(container_port=int(os.environ.get("API_PORT"))),
      ecs.PortMapping(container_port=int(os.environ.get("V2RAY_PORT")))
    ]
  )
  # service = ecs.FargateService(
  #   stack, f"FargateService-{wallet_key(wallet_number)}",
  #   cluster=cluster,
  #   task_definition=fargate_task_definition,
  #   enable_execute_command=True,
  #   desired_count=1
  # )
  wallet_number += 1

app.synth()
