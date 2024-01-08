FROM ghcr.io/sentinel-official/dvpn-node:v0.7.1

ARG USERNAME=sentinel
ARG SENTINEL_NODE_DIR=/home/${USERNAME}/.sentinelnode

RUN addgroup -S ${USERNAME} && adduser -S ${USERNAME} -G ${USERNAME}
USER ${USERNAME}
RUN mkdir -p ${SENTINEL_NODE_DIR}
WORKDIR ${SENTINEL_NODE_DIR}
COPY --chown=${USERNAME}:${USERNAME} .sentinelnode/ ${SENTINEL_NODE_DIR}/

ENTRYPOINT ["./entrypoint.sh"]
