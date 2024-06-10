# Multistage dockerfile
# https://docs.docker.com/build/building/multi-stage

# Since official foundry image is built to run only on amd64 and
# doesn't support arm64 we are making our own foundry image
FROM ubuntu:22.04 as foundry

# install packages that are required for foundry installation
RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends \
  	curl \
    ca-certificates \
    git && \
  apt-get clean && \
  rm -rf \
  	/tmp/* \
  	/var/lib/apt/lists/* \
  	/var/tmp/*
ENV FOUNDRY_DIR /opt/foundry
RUN curl -sS https://raw.githubusercontent.com/foundry-rs/foundry/master/foundryup/install | bash && /opt/foundry/bin/foundryup

# Base image with compiled contracts that is used by anvil and by deploy scripts
FROM ubuntu:22.04 as contracts

# install packages that are required for building contracts
RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends \
  	make \
    git \
    curl \
    jq \
    linux-headers-generic \
    ca-certificates && \
  apt-get clean && \
  rm -rf \
  	/tmp/* \
  	/var/lib/apt/lists/* \
  	/var/tmp/*

COPY --from=foundry /opt/foundry/bin /opt/foundry
ENV PATH="${PATH}:/opt/foundry/"

COPY . /app
WORKDIR /app

#COPY entrypoint.sh /entrypoint.sh

# image with local chain - anvil
FROM contracts as chain-rpc
#ENTRYPOINT ["/entrypoint.sh"]
CMD ["anvil", "--host", "0.0.0.0"]
