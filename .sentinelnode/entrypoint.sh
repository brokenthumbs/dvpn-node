#!/usr/bin/env bash

SENTINEL_CONFIG=${SENTINEL_NODE_DIR}/.sentinelnode/config.toml
V2RAY_CONFIG=${SENTINEL_NODE_DIR}/.sentinelnode/v2ray.toml
IPV4_ADDRESS_CHECKER=https://checkip.amazonaws.com
MONIKER=${MONIKER:-"dvpn-node"}

main() {
  case ${1} in
    bash) "$@" ;;
    initialize|wallet|operator|start) configure; "$@" ;;
    *) ;;
  esac
}

configure() {
  if [[ -z ${API_PORT} ]]; then exit 1; fi
  if [[ -z ${V2RAY_PORT} ]]; then exit 1; fi
  IPV4_ADDRESS=$(curl --silent ${IPV4_ADDRESS_CHECKER})
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
  process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") > /dev/null
  process start < <(echo -e "${PASSWORD}\n")
}

main "$@"
