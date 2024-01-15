from aws_cdk import (
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  aws_logs as logs,
  aws_ssm as ssm,
  App, Stack
)
import boto3
import os

app = App()
stack = Stack(
  app, f"{os.environ.get("AWS_REGION")}-update",
  env={
    "account": os.environ.get("AWS_ACCOUNT_ID"),
    "region": os.environ.get("AWS_REGION")
  }
)

ssm_client = boto3.client("ssm", region_name=os.environ.get("AWS_REGION"))
ssm_parameters = []

def wallet_key(number: int) -> str:
  return f"{os.environ.get("AWS_REGION")}-{format(number, "04d")}"

def exist_ssm_parameter(parameter_name: str) -> bool:
  if parameter_name in ssm_parameters:
    return True
  try:
    ssm_client.get_parameter(Name=parameter_name)
    ssm_parameters.append(parameter_name)
    return True
  except ssm_client.exceptions.ParameterNotFound:
    return False

vpc = ec2.Vpc.from_lookup(
  stack, "Vpc",
  vpc_name=os.environ.get("AWS_REGION")
)

security_group = ec2.SecurityGroup(stack, "SecurityGroup",
  vpc=vpc,
  allow_all_outbound=True,
  disable_inline_rules=True
)
security_group.add_ingress_rule(
  ec2.Peer.any_ipv4(),
  ec2.Port.tcp(int(os.environ.get("API_PORT"))),
  "api_port"
)
security_group.add_ingress_rule(
  ec2.Peer.any_ipv4(),
  ec2.Port.tcp(int(os.environ.get("V2RAY_PORT"))),
  "v2ray_port"
)

cluster = ecs.Cluster(
  stack, "EcsCluster",
  vpc=vpc,
  cluster_name=os.environ.get("CLUSTER_NAME"),
  enable_fargate_capacity_providers=True
)

repository = ecr.Repository.from_repository_name(
  stack, "Repository",
  repository_name=os.environ.get("REPOSITORY_NAME")
)

ssm_parameter_password = ssm.StringParameter.from_secure_string_parameter_attributes(
  stack, "StringParameter-password",
  parameter_name="password"
)

wallet_number = 1
while exist_ssm_parameter(wallet_key(wallet_number)):
  fargate_task_definition = ecs.FargateTaskDefinition(
    stack, f"FargateTaskDefinition-{wallet_key(wallet_number)}",
    family=wallet_key(wallet_number),
    memory_limit_mib=512,
    cpu=256,
  )
  log_group = logs.LogGroup(
    stack, f"LogGroup-{wallet_key(wallet_number)}",
    log_group_name=wallet_key(wallet_number),
    retention=logs.RetentionDays.ONE_WEEK
  )
  fargate_task_definition.add_container(
    os.environ.get("REPOSITORY_NAME"),
    image=ecs.ContainerImage.from_ecr_repository(
      repository=repository,
      tag="latest"
    ),
    environment={
      "API_PORT": os.environ.get("API_PORT"),
      "V2RAY_PORT": os.environ.get("V2RAY_PORT"),
      "AWS_REGION": os.environ.get("AWS_REGION"),
      "MONIKER": wallet_key(wallet_number)
    },
    secrets={
      "PASSWORD": ecs.Secret.from_ssm_parameter(
        ssm_parameter_password
      ),
      "BIP39_MNEMONIC": ecs.Secret.from_ssm_parameter(
        ssm.StringParameter.from_secure_string_parameter_attributes(
          stack, f"StringParameter-{wallet_key(wallet_number)}",
          parameter_name=wallet_key(wallet_number)
        )
      )
    },
    command=["start"],
    logging=ecs.LogDrivers.aws_logs(
        # stream_prefix=os.environ.get("REPOSITORY_NAME"),
        mode=ecs.AwsLogDriverMode.NON_BLOCKING,
        log_group=log_group
    ),
    port_mappings=[
      ecs.PortMapping(container_port=int(os.environ.get("API_PORT"))),
      ecs.PortMapping(container_port=int(os.environ.get("V2RAY_PORT")))
    ]
  )
  service = ecs.FargateService(
    stack, f"FargateService-{wallet_key(wallet_number)}",
    service_name=wallet_key(wallet_number),
    cluster=cluster,
    task_definition=fargate_task_definition,
    assign_public_ip=True,
    platform_version=ecs.FargatePlatformVersion.LATEST,
    security_groups=[security_group],
    enable_ecs_managed_tags=True,
    enable_execute_command=True,
    desired_count=1
  )
  wallet_number += 1

app.synth()
