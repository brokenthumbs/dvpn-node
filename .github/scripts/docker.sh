#!/usr/bin/env bash

docker build --tag dvpn-node:latest
docker images

aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker tag dvpn-node:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dvpn-node:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dvpn-node:latest

export GIT_HASH=$(git rev-parse HEAD)
if [[ -n ${GIT_HASH} ]]; then
  docker tag dvpn-node:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dvpn-node:${GIT_HASH}
  docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/dvpn-node:${GIT_HASH}
fi
