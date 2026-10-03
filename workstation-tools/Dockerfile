# workstation-tools: himalaya + the general Linux toolbox set, for exec-based use.
#
# The external-interaction tooling of the omni stack, as a SEPARATE versioned
# image (operator decision 2026-09-26, threads 3165/3166): himalaya moves OUT of
# the omni toolbox into this image, which the workstation reaches through the
# `container` transport (`docker compose exec -T workstation-tools sh -c ...`).
#
# It contains tools/CLIs/commands that RUN AND FINISH - NOT services that keep
# running permanently. The whole lifecycle is `sleep infinity` (the compose
# service passes the same command), so the container stays up for exec-based use.
#
# Package reference: omni-stack/services/toolbox/Dockerfile ("just like omni
# toolbox"). Pins: himalaya = Alpine apk (v1.2.0), oathtool = Alpine apk,
# pyotp = PyPI 2.10.0, plus the datastore/scanner CLIs added for audit gap G6
# (2026-09-30): mysql, redis-cli, mongosh, zip, gitleaks, trivy, semgrep, and
# the PDF-verification pair qpdf + poppler-utils (pdfinfo) for the office
# pipeline re-run outside the office container. Added 2026-10-03 (follow-up of
# audit gap G6, thread 4017): the database CLI sqlite3 (apk `sqlite`), the
# YAML/JSON processor yq (apk `yq-go`) and the Node runtime (apk `nodejs`); all
# three are plain apk packages, so they follow the base image with no pin (see
# README.md for the full table and each pinned source).

FROM alpine:latest

# The toolbox package set (minus the toolbox's own backup scripts) + himalaya.
#   himalaya email CLI: Alpine package (v1.2.0, apk-managed).
#   oathtool CLI (TOTP/HOTP): Alpine package oath-toolkit-oathtool (the
#   oath-toolkit meta package alone ships only pskctool, not oathtool).
#   mysql client: Alpine `mysql-client` is a dummy migration package that
#   depends on `mariadb-client` (11.8.8-r0), which ships /usr/bin/mysql.
#   redis-cli: Alpine `redis` package (8.8.0-r0; it also ships redis-server).
#   zip: Alpine `zip` package.
#   qpdf: Alpine package (PDF structural repair/inspection).
#   poppler-utils: Alpine package (pdfinfo/pdftotext/pdftoppm); gives the
#   tools image an independent pdfinfo so a PDF can be re-verified outside the
#   office container.
#   sqlite3: Alpine `sqlite` package (database CLI at /usr/bin/sqlite3; there
#   is no package named `sqlite3` and `sqlite-tools` does not ship the binary).
#   yq: Alpine `yq-go` package (mikefarah Go yq 4.x YAML/JSON processor at
#   /usr/bin/yq; there is no package named `yq` and `yq-python` is the unrelated
#   kislyuk jq wrapper, so it is NOT used here).
#   node: Alpine `nodejs` package (Node runtime at /usr/bin/node; `npm` is a
#   separate community package and is not required here). Added 2026-10-03 with
#   sqlite3 and yq as the follow-up of audit gap G6 (thread 4017).
#   gcompat + libstdc++ + libgcc: needed to run the glibc-linked mongosh build
#   on Alpine's musl libc (see the mongosh block below).
#   git: required by gitleaks git-history mode. `gitleaks detect --log-opts=--all`
#   shells out to git; without it gitleaks FTLs with
#   "exec: git: executable file not found in $PATH" (pre-release gate gap).
RUN apk add --no-cache \
    bash tini dcron curl wget \
    git \
    rclone \
    postgresql-client postgresql \
    docker-cli docker-compose \
    python3 py3-pip \
    py3-psycopg2 \
    jq \
    sqlite yq-go nodejs \
    himalaya \
    oath-toolkit-oathtool \
    mysql-client \
    redis \
    zip \
    qpdf \
    poppler-utils \
    gcompat libstdc++ libgcc

# Pinned versions and checksums for the tools that are NOT in the Alpine repos.
# Each RUN below verifies the download against its pinned sha256 before use.
#   mongosh: MongoDB does not publish a .sha256 sidecar next to the tgz (only a
#   .sig), so the digest was computed from the official CDN download and
#   cross-checked against the identical GitHub release asset before pinning.
ARG MONGSH_VERSION=2.12.0
ARG MONGSH_SHA256=aa42cb826b7b8e655c5481293f5365ddaf1a23e43af07520326e5bbc957838ad
ARG GITLEAKS_VERSION=8.30.1
ARG GITLEAKS_SHA256=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
# sha256 of the gitleaks v8.30.1 default config at
# https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
# (consumed by the gate config block below).
ARG GITLEAKS_DEFAULT_CONFIG_SHA256=e163e53b9e7e8a8511e77271e2b323ed057759542a6d988258afe3a1fa329caf
ARG TRIVY_VERSION=0.74.0
ARG TRIVY_SHA256=2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a
ARG SEMGREP_VERSION=1.178.0

# The mongosh glibc resolver shim (source next to this Dockerfile). gcompat is
# missing __res_nsearch/__dn_expand, so they are provided by this tiny .so. The
# compiler toolchain is installed virtually and removed in the same layer.
COPY mongosh-resolv-shim.c /tmp/mongosh-resolv-shim.c
RUN set -eux; \
    apk add --no-cache --virtual .build-deps build-base; \
    mkdir -p /usr/local/lib; \
    cc -shared -fPIC -O2 -o /usr/local/lib/mongosh-resolv-shim.so /tmp/mongosh-resolv-shim.c; \
    apk del --no-network .build-deps; \
    rm -f /tmp/mongosh-resolv-shim.c

# mongosh: not in the Alpine repos. Prebuilt tarball from the official MongoDB
# CDN, sha256-verified, extracted under /opt/mongosh with a wrapper on PATH. The
# binary is glibc-linked (Alpine is musl), so the wrapper runs it through
# gcompat with the resolver shim LD_PRELOADed.
RUN set -eux; \
    curl -fsSL -o /tmp/mongosh.tgz \
      "https://downloads.mongodb.com/compass/mongosh-${MONGSH_VERSION}-linux-x64.tgz"; \
    echo "${MONGSH_SHA256}  /tmp/mongosh.tgz" | sha256sum -c -; \
    mkdir -p /opt/mongosh; \
    tar -xzf /tmp/mongosh.tgz -C /opt/mongosh --strip-components=1; \
    rm -f /tmp/mongosh.tgz; \
    printf '%s\n' \
      '#!/bin/sh' \
      'export LD_PRELOAD=/usr/local/lib/mongosh-resolv-shim.so' \
      'exec /opt/mongosh/bin/mongosh "$@"' \
      > /usr/local/bin/mongosh; \
    chmod 0755 /usr/local/bin/mongosh

# gitleaks: not in the Alpine repos (main or community). Pinned GitHub release
# binary, sha256-verified against the published checksums.txt.
RUN set -eux; \
    curl -fsSL -o /tmp/gitleaks.tar.gz \
      "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"; \
    echo "${GITLEAKS_SHA256}  /tmp/gitleaks.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks; \
    rm -f /tmp/gitleaks.tar.gz

# The pre-release gate config. gitleaks.toml extends a pinned copy of the
# gitleaks default config (extended by path) plus the shape-based AWS/OpenAI
# rules. The default base is fetched at build time from the SAME pinned release
# and has exactly ONE modification: the global allowlist stopword
# "abcdefghijklmnopqrstuvwxyz" is removed. gitleaks' [extend] mechanism only
# APPENDS an extended config's global allowlists (config.extend() in v8.30.1
# does `c.Allowlists = append(...)`), so `useDefault = true` can never
# un-allowlist that stopword and the canonical placeholder OpenAI value
# (sk-demo1234567890abcdefghijklmnopqrstuvwxyz) would be silently suppressed
# (confirmed with `gitleaks detect -l trace`). Installed under /etc/gitleaks/
# so both files are addressable when gitleaks runs from an arbitrary CWD:
#   gitleaks detect --config /etc/gitleaks/gitleaks.toml ...
RUN set -eux; \
    mkdir -p /etc/gitleaks; \
    curl -fsSL -o /etc/gitleaks/gitleaks-defaults.toml \
      "https://raw.githubusercontent.com/gitleaks/gitleaks/v${GITLEAKS_VERSION}/config/gitleaks.toml"; \
    echo "${GITLEAKS_DEFAULT_CONFIG_SHA256}  /etc/gitleaks/gitleaks-defaults.toml" | sha256sum -c -; \
    sed -i '/^    "abcdefghijklmnopqrstuvwxyz",$/d' /etc/gitleaks/gitleaks-defaults.toml; \
    ! grep -q '^    "abcdefghijklmnopqrstuvwxyz",$' /etc/gitleaks/gitleaks-defaults.toml
COPY gitleaks.toml /etc/gitleaks/gitleaks.toml

# trivy: not in the Alpine repos. Pinned GitHub release binary, sha256-verified
# against the release's published checksums.txt.
RUN set -eux; \
    curl -fsSL -o /tmp/trivy.tar.gz \
      "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz"; \
    echo "${TRIVY_SHA256}  /tmp/trivy.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/trivy.tar.gz -C /usr/local/bin trivy; \
    rm -f /tmp/trivy.tar.gz

# pyotp: TOTP library for python3. Not packaged in Alpine repos as py3-pyotp
# (Alpine's py3-otp is the unrelated 'otp' library), so install the pinned
# pure-python PyPI release (no build deps needed).
RUN python3 -m pip install --no-cache-dir --break-system-packages pyotp==2.10.0

# semgrep: not in the Alpine repos. The PyPI musllinux_1_2_x86_64 wheel bundles
# semgrep-core, so a pinned pip install works on Alpine without a toolchain.
RUN python3 -m pip install --no-cache-dir --break-system-packages "semgrep==${SEMGREP_VERSION}"

# NOT a service: stay up for exec-based use (`docker compose exec -T
# workstation-tools sh -c <cmd>`), exactly like the toolbox container.
CMD ["sleep", "infinity"]
