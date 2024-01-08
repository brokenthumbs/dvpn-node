#!/usr/bin/env bash

SENTINEL_CONFIG=/home/sentinel/.sentinelnode/config.toml
V2RAY_CONFIG=/home/sentinel/.sentinelnode/v2ray.toml
IPV4_ADDRESS_CHECKER="https://checkip.amazonaws.com"
MONIKER=$(cat /etc/hostname)

if [[ -n ${ECS_CONTAINER_METADATA_URI} ]]; then
  IPV4_ADDRESS_CHECKER="http://169.254.169.254/latest/meta-data/public-ipv4"
  EC2_AVAILABILITY_ZONE=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
  EC2_REGION=$(echo "${EC2_AVAILABILITY_ZONE}" | sed 's/[a-z]$//')
  MONIKER="${EC2_REGION}-${MONIKER}"
fi

main() {
  configure
  case ${1} in
    initialize|wallet|operator|start|bash) "$@" ;;
    *) ;;
  esac
}

configure() {
  if [[ -z ${API_PORT} ]]; then exit 1; fi
  if [[ -z ${V2RAY_PORT} ]]; then exit 1; fi
  IPV4_ADDRESS=$(wget -qO- ${IPV4_ADDRESS_CHECKER})
  sed -i"" -r "s/__IPV4_ADDRESS__/${IPV4_ADDRESS}/" ${SENTINEL_CONFIG}
  sed -i"" -r "s/__MONIKER__/${MONIKER}/" ${SENTINEL_CONFIG}
  sed -i"" -r "s/__API_PORT__/${API_PORT}/" ${SENTINEL_CONFIG}
  sed -i"" -r "s/__V2RAY_PORT__/${V2RAY_PORT}/" ${V2RAY_CONFIG}
}

initialize() {
  if [[ -z ${PASSWORD} ]]; then exit 1; fi
  export BIP39_MNEMONIC=$(process keys add < <(echo -e "${PASSWORD}\n${PASSWORD}\n") 2>&1 | head -2 | tail -1)
  echo ${BIP39_MNEMONIC}
}

wallet() {
  if [[ -z ${PASSWORD} ]]; then exit 1; fi
  if [[ -z ${BIP39_MNEMONIC} ]]; then exit 1; fi
  export WALLET_ADDRESS=$(process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") 2>&1)
  echo ${WALLET_ADDRESS##* }
}

operator() {
  if [[ -z ${PASSWORD} ]]; then exit 1; fi
  if [[ -z ${BIP39_MNEMONIC} ]]; then exit 1; fi
  export OPERATOR_ADDRESS=$(process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") 2>&1)
  echo ${OPERATOR_ADDRESS} | rev | cut -d ' ' -f 2 | rev
}

start() {
  if [[ -z ${PASSWORD} ]]; then exit 1; fi
  if [[ -z ${BIP39_MNEMONIC} ]]; then exit 1; fi
  process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n")
  process start < <(echo -e "${PASSWORD}\n")
}

main "$@"
