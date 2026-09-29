# gods-eye-view: the keyless JSON data plane of God's Eye View as a SEPARATE,
# network-internal service.
#
# Operator rule: an external service never boots inside the workstation image.
# The workstation reaches this container over the compose network through the
# thin `spatial-tools` plugin; no GEV code runs in the workstation image.
#
# PINNED UPSTREAM (see README.md for the deliberate-bump table):
#   repo https://github.com/bilawalsidhu/gods-eye-view
#   sha  e7707d9a0f34d9fbffc300023c319f95caa5be30  (main, 2026-09-29T00:33:34Z)
# The upstream MIT LICENSE and THIRD_PARTY_NOTICES.md stay in the image at /app.
#
# SCOPE: keyless layers only. No Google Maps, Cesium ion, OpenAI, NASA FIRMS,
# TomTom, AISStream or Launch Library token is baked in or accepted at build
# time. The visual/imagery half of the app is out of scope (Google Maps Content
# may not be cached/stored/rehosted).
FROM node:24-bookworm-slim

LABEL org.opencontainers.image.title="gods-eye-view" \
      org.opencontainers.image.description="God's Eye View local server, keyless JSON data plane (no keys, no visual/imagery tools)" \
      org.opencontainers.image.source="https://github.com/bilawalsidhu/gods-eye-view" \
      org.opencontainers.image.revision="e7707d9a0f34d9fbffc300023c319f95caa5be30" \
      org.opencontainers.image.licenses="MIT"

ARG GEV_REPO=https://github.com/bilawalsidhu/gods-eye-view
ARG GEV_SHA=e7707d9a0f34d9fbffc300023c319f95caa5be30

# git for the pinned clone; wget for the compose healthcheck. ca-certificates
# for the https upstreams. No build toolchain: every dependency ships a prebuilt
# linux-x64 binary (sharp) or is wasm/pure JS.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates wget \
 && rm -rf /var/lib/apt/lists/*

# The JSON data plane needs no Chromium: skip the ~150 MB puppeteer download.
# Do NOT set NODE_ENV=production before `npm ci`: vite is a devDependency and
# the build/preview/dev scripts need it.
ENV PUPPETEER_SKIP_DOWNLOAD=1 \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

WORKDIR /app
RUN git clone --depth 1 "$GEV_REPO" /app \
 && git -C /app fetch --depth 1 origin "$GEV_SHA" \
 && git -C /app checkout -q "$GEV_SHA" \
 && test "$(git -C /app rev-parse HEAD)" = "$GEV_SHA" \
 && rm -rf /app/.git

RUN npm ci
RUN npm run build

ENV HOST=0.0.0.0 \
    PORT=4173
EXPOSE 4173

# `npm run dev` (vite serve), NOT `npm run preview`: the pinned upstream mounts
# /api/setup/status and /api/setup/keys only under `command==='serve' && !isPreview`
# (server/standalone/key-setup.js), so under `vite preview` those two routes are
# 404 by design. The `spatial status` tool needs /api/setup/status, so the
# service runs the dev server. Evidence: /opt/workspace/tmp/gods-eye-view-gate/
# (preview: setup/status=404; dev: setup/status=200).
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"]
