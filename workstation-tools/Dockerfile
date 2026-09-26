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
# pyotp = PyPI 2.10.0 (pinned; see README.md for the full table).

FROM alpine:latest

# The toolbox package set (minus the toolbox's own backup scripts) + himalaya.
#   himalaya email CLI: Alpine package (v1.2.0, apk-managed).
#   oathtool CLI (TOTP/HOTP): Alpine package oath-toolkit-oathtool (the
#   oath-toolkit meta package alone ships only pskctool, not oathtool).
RUN apk add --no-cache \
    bash tini dcron curl wget \
    rclone \
    postgresql-client postgresql \
    docker-cli docker-compose \
    python3 py3-pip \
    py3-psycopg2 \
    jq \
    himalaya \
    oath-toolkit-oathtool

# pyotp: TOTP library for python3. Not packaged in Alpine repos as py3-pyotp
# (Alpine's py3-otp is the unrelated 'otp' library), so install the pinned
# pure-python PyPI release (no build deps needed).
RUN python3 -m pip install --no-cache-dir --break-system-packages pyotp==2.10.0

# NOT a service: stay up for exec-based use (`docker compose exec -T
# workstation-tools sh -c <cmd>`), exactly like the toolbox container.
CMD ["sleep", "infinity"]