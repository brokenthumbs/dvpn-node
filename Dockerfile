FROM ghcr.io/sentinel-official/dvpn-node:v0.7.1

RUN apk add curl
RUN apk add git
RUN apk add jq
RUN apk add openssl
RUN apk add tmux
RUN apk add v2ray==5.12.1-r1

ARG SENTINEL_NODE_DIR=/root/.sentinelnode
ENV SENTINEL_NODE_DIR=${SENTINEL_NODE_DIR}

RUN mkdir -p ${SENTINEL_NODE_DIR}
WORKDIR ${SENTINEL_NODE_DIR}
COPY ./entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
