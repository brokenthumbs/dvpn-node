from aws_cdk import (
  aws_autoscaling as autoscaling,
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  aws_ecr_assets as ecr_assets,
  App, Stack, RemovalPolicy
)
import boto3
import os

app = App()
stack = Stack(app, f"{os.environ.get("AWS_REGION")}-update")

ssm_client = boto3.client("ssm", region_name=os.environ.get("AWS_REGION"))

def wallet_key(number: int) -> str:
  return f"{os.environ.get("AWS_REGION")}:{format(number, "04d")}"

def exist_ssm_param(param_name: str) -> bool:
  try:
    ssm_client.get_parameter(Name=param_name)
    return True
  except ssm_client.exceptions.ParameterNotFound:
    return False

def get_ssm_param(param_name: str) -> str:
  return ssm_client.get_parameter(Name=param_name, WithDecryption=True)

wallet_number = 1
while exist_ssm_param(wallet_key(wallet_number)):
  bip39_mnemonic = get_ssm_param(wallet_key(wallet_number))
  print(f"found wallet: {wallet_key(wallet_number)}")
  wallet_number += 1

app.synth()
