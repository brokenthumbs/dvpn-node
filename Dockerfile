FROM ghcr.io/sentinel-official/dvpn-node:v0.7.1

RUN apk add curl

ARG SENTINEL_NODE_DIR=/root/.sentinelnode
ENV SENTINEL_NODE_DIR=${SENTINEL_NODE_DIR}

RUN mkdir -p ${SENTINEL_NODE_DIR}
COPY .sentinelnode/ ${SENTINEL_NODE_DIR}/

WORKDIR ${SENTINEL_NODE_DIR}
ENTRYPOINT ["./entrypoint.sh"]
