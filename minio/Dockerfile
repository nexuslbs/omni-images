# MinIO object-storage server, built and published by nexuslbs.
#
# WHY WE BUILD IT OURSELVES: no upstream MinIO image is anonymously pullable any
# more (docker.io/minio/minio -> 404, quay.io/minio/minio -> "no such manifest"),
# and dl.min.io stopped serving the community binaries altogether:
#
#   $ curl -i https://dl.min.io/server/minio/release/linux-amd64/
#   HTTP/2 410
#   "The open-source MinIO Server, MinIO Client (mc) and MinIO KES projects are
#    archived and no longer maintained ... These files are no longer served from
#    this site. This applies to all community releases and to all hotfix builds."
#
# The OFFICIAL GitHub release assets of github.com/minio/minio are still served,
# so the upstream source pinned below (version + official sha256) is the real
# upstream MinIO binary - NOT a third-party fork and NOT a re-tag of somebody
# else's image. Consumers (omni-deployer/docker-compose.minio.yml) pin the
# PUBLISHED image by digest; see minio/README.md for the bump procedure.

# Immutable base (digest-pinned, never :latest).
FROM debian:bookworm-slim@sha256:3783cc01769c7b2b1b83a5c5ad96c815348e28ed7da68e2e3687004faa906251

# Pinned upstream release. Bump BOTH values together (README "How to bump"):
# MINIO_SHA256 is the official checksum published next to the binary as
# minio.linux-amd64.<version>.sha256sum.
ARG MINIO_VERSION=RELEASE.2025-09-07T16-13-09Z
ARG MINIO_SHA256=7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f

# curl      : required interface - the deploy's compose healthcheck and its
#             in-container readiness probe exec
#             `curl -f http://localhost:9000/minio/health/live`.
# ca-certificates: needed to fetch the release asset over https at build time.
# The download FAILS CLOSED: `sha256sum -c -` aborts the build if the fetched
# binary does not match the pinned official checksum.
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    curl -fsSL -o /usr/local/bin/minio \
      "https://github.com/minio/minio/releases/download/${MINIO_VERSION}/minio.linux-amd64.${MINIO_VERSION}"; \
    echo "${MINIO_SHA256}  /usr/local/bin/minio" | sha256sum -c -; \
    chmod 0755 /usr/local/bin/minio; \
    minio --version

VOLUME ["/data"]
# 9000 = S3 API (never published to a host port by the deploy overlay),
# 9001 = web console.
EXPOSE 9000 9001

# Same CLI contract as the upstream server image:
#   minio server /data --console-address ":9001"
ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]
