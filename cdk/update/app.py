from aws_cdk import (
  aws_autoscaling as autoscaling,
  aws_ec2 as ec2,
  aws_ecr as ecr,
  aws_ecs as ecs,
  aws_ecr_assets as ecr_assets,
  App, Stack, RemovalPolicy
)
import os

app = App()
stack = Stack(app, f"{os.environ.get("AWS_REGION")}-update")

app.synth()
