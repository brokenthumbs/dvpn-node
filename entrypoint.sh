#!/usr/bin/env bash

# trigger a new deploy
# .

SENTINEL_CONFIG_PATH=${SENTINEL_NODE_DIR}/config.toml
V2RAY_CONFIG_PATH=${SENTINEL_NODE_DIR}/v2ray.toml

MONIKER=${MONIKER:-"dvpn-node"}
HANDSHAKE=${HANDSHAKE:-"false"}
TYPE=${TYPE:-"v2ray"}

IPV4_ADDRESS=$(curl --silent https://checkip.amazonaws.com)
API_ADDRESS="0.0.0.0:${API_PORT}"
REMOTE_URL="https://${IPV4_ADDRESS}:${API_PORT}"

# --- declab/sentinel_dvpn

# Variables to update in the config.toml.
declare -A CONFIG_MAPPINGS=(
  ["GAS"]="gas"
  ["GAS_ADJUSTMENT"]="gas_adjustment"
  ["GAS_PRICES"]="gas_prices"
  ["CHAIN"]="id"
  ["RPC_ADDRESS"]="rpc_addresses"
  ["SIMULATE_AND_EXECUTE"]="simulate_and_execute"
  ["HANDSHAKE"]="enable"
  ["PEERS"]="peers"
  ["BACKEND"]="backend"
  ["INTERVAL_SET_SESSIONS"]="interval_set_sessions"
  ["INTERVAL_UPDATE_SESSIONS"]="interval_update_sessions"
  ["INTERVAL_UPDATE_STATUS"]="interval_update_status"
  ["IPV4_ADDRESS"]="ipv4_address"
  ["API_ADDRESS"]="listen_on"
  ["MONIKER"]="moniker"
  ["GIGABYTE_PRICES"]="gigabyte_prices"
  ["HOURLY_PRICES"]="hourly_prices"
  ["REMOTE_URL"]="remote_url"
  ["TYPE"]="type"
)

check_var() {
  if [[ -z ${!1} ]]; then
    echo "${1} is not defined."
    exit 1
  fi
}

update_config() {
  local VAR_NAME="${1}"
  local PATTERN="${2}"
  local CONFIG_PATH="${3}"
  if [[ -n ${!VAR_NAME} ]]; then
    sed -i -e "s|^${PATTERN} *=.*|${PATTERN} = \"${!VAR_NAME}\"|;" "${CONFIG_PATH}"
  fi
}

# --- brokenthumbs

main() {
  case ${1} in
    bash) "$@" ;;
    initialize|wallet|operator|start) "$@" ;;
    *) ;;
  esac
}

initialize() {
  check_var "PASSWORD"
  export BIP39_MNEMONIC=$(process keys add < <(echo -e "${PASSWORD}\n${PASSWORD}\n") 2>&1 | head -2 | tail -1)
  echo ${BIP39_MNEMONIC}
}

wallet() {
  check_var "PASSWORD"
  check_var "BIP39_MNEMONIC"
  export WALLET_ADDRESS=$(process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") 2>&1)
  echo ${WALLET_ADDRESS##* }
}

operator() {
  check_var "PASSWORD"
  check_var "BIP39_MNEMONIC"
  export OPERATOR_ADDRESS=$(process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") 2>&1)
  echo ${OPERATOR_ADDRESS} | rev | cut -d ' ' -f 2 | rev
}

set_rpc_address() {
  IFS=',' read -r -a UNSORTED_RPC_ADDRESS <<< "${RPC_ADDRESS}"

  declare -A EXECUTION_TIMES

  # Loop through each node
  for NODE in "${UNSORTED_RPC_ADDRESS[@]}"; do
    START_TIME=$(date +%s%N)
    curl --silent "${NODE}/block" > /dev/null
    END_TIME=$(date +%s%N)
    EXECUTION_TIME=$(echo "${END_TIME} - ${START_TIME}" | bc)
    EXECUTION_TIMES["${NODE}"]="${EXECUTION_TIME}"
    # echo "Finished testing ${NODE}, Execution took: ${EXECUTION_TIME}"
  done

  SORTED_NODES=($(for NODE in "${UNSORTED_RPC_ADDRESS[@]}"; do echo "${NODE} ${EXECUTION_TIMES["${NODE}"]}"; done | sort -k2 -n | awk '{print $1}'))
  # for NODE in "${SORTED_NODES[@]}"; do
  #   echo "Node: ${NODE}, Execution Time: ${EXECUTION_TIMES["${NODE}"]}"
  # done

  NEW_ADDRS=()
  for ((a = 0; a <= 4; a++)); do
    NEW_ADDRS+=("${SORTED_NODES[$a]}")
  done

  SORTED_RPC_ADDRESS=$(IFS=,; echo "${NEW_ADDRS[*]}")
  echo ${SORTED_RPC_ADDRESS}
}

start() {
  check_var "PASSWORD"
  check_var "BIP39_MNEMONIC"
  check_var "API_PORT"
  check_var "V2RAY_PORT"
  process config init
  process v2ray config init
  export RPC_ADDRESS=$(set_rpc_address)
  for VAR in "${!CONFIG_MAPPINGS[@]}"; do
    update_config "${VAR}" "${CONFIG_MAPPINGS[${VAR}]}" "${SENTINEL_CONFIG_PATH}"
  done
  sed -i -e "s|^listen_port *=.*|listen_port = ${V2RAY_PORT}|;" "${V2RAY_CONFIG_PATH}"
  (echo;echo;echo;echo;echo;echo;echo;) | openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -x509 -sha256 -days 365 -nodes -out ./tls.crt -keyout ./tls.key 1>/dev/null 2>&1
  process keys add --recover < <(echo -e "${BIP39_MNEMONIC}\n${PASSWORD}\n${PASSWORD}\n") 1>/dev/null 2>&1
  process start < <(echo -e "${PASSWORD}\n")
}

main "$@"
