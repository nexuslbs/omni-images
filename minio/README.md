# minio (nexuslbs/omni-images)

MinIO object-storage server used as the **local S3 endpoint** for the
omni-deployer S3 backup/restore/checkpoint test
(`omni-deployer/docker-compose.minio.yml`, `deploy.py test_s3_backup_restore()`).

## Why we build it ourselves

No upstream MinIO image is anonymously pullable any more, and the "borrow
somebody else's build" workaround was exactly the hack that could pass in
hybrid and fail in CI:

| Upstream source | Status (verified 2026-09-25) |
|---|---|
| `docker.io/minio/minio` | repository does not exist (HTTP 404) |
| `quay.io/minio/minio` | "no such manifest" for every tag |
| `dl.min.io/server/minio/release/...` | **HTTP 410 Gone** - "The open-source MinIO Server, MinIO Client (mc) and MinIO KES projects are archived and no longer maintained ... These files are no longer served from this site." |
| `github.com/minio/minio` **release assets** | still served (the binaries published with `RELEASE.2025-09-07T16-13-09Z`) |

So this image is built from the **official upstream MinIO release binary**,
downloaded at build time from the official GitHub release asset and verified
against the official checksum. It does not re-tag a third-party fork and it
does not consume a third-party registry.

## Pinned upstream source

| Field | Value |
|---|---|
| Upstream project | `github.com/minio/minio` |
| Pinned version | `RELEASE.2025-09-07T16-13-09Z` |
| Binary | `minio.linux-amd64.RELEASE.2025-09-07T16-13-09Z` |
| Download URL | `https://github.com/minio/minio/releases/download/RELEASE.2025-09-07T16-13-09Z/minio.linux-amd64.RELEASE.2025-09-07T16-13-09Z` |
| Official sha256 | `7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f` |
| Base image | `debian:bookworm-slim` (pinned by digest in the Dockerfile, never `:latest`) |

Both the version and the checksum are `ARG`s at the top of the `Dockerfile` and
the build **fails closed** (`sha256sum -c -`) if the downloaded binary does not
match. Verified by downloading the binary and comparing against the official
`.sha256sum` asset published next to it:

```
7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f  minio.RELEASE.2025-09-07T16-13-09Z
```

### Why not the newest release?

`RELEASE.2025-10-15T17-29-55Z` (the CVE fix for the service-account/STS
privilege escalation, GHSA-jjjj-jwhf-8rgr) is the newest upstream release but it
ships **no binary assets** - MinIO only documents `go install
github.com/minio/minio@<tag>` for it. `RELEASE.2025-09-07T16-13-09Z` is the
newest release with a downloadable, checksummed binary. The image is used only
as an ephemeral, in-network S3 endpoint for the deploy's own test, never
exposed publicly. Move to a source build of a newer tag if that ever changes.

## Interface the deploy relies on

* entrypoint `minio`, default command `server /data --console-address ":9001"`
  (the compose overlay passes the same command explicitly),
* serves S3 on **:9000** (`expose`, never published to the host),
* **`curl` is present in the image** - the compose healthcheck and deploy.py's
  readiness probe both exec `curl -f http://localhost:9000/minio/health/live`,
  which returns 200 once the server is live,
* console on :9001, data volume `/data`.

## Published reference

`ghcr.io/nexuslbs/omni-images/minio` - **public**, no credentials required.

Consumers may pin the immutable digest, e.g. in `omni-deployer/docker-compose.minio.yml`:

```yaml
image: ghcr.io/nexuslbs/omni-images/minio@sha256:<digest>
```

Tags produced per release (see the root README, operator correction 2026-09-26):
`latest` (the rolling alias) **and** the version tag derived from the `minio-*`
git tag (e.g. `minio-1.0.0` -> `minio:1.0.0`). The upstream version
(`RELEASE.2025-09-07T16-13-09Z`) stays pinned inside the Dockerfile/README;
consumers that need immutability pin the digest or the version tag.

## How to bump

1. Pick the new upstream release **that has binary assets**:
   `curl -fsSL https://api.github.com/repos/minio/minio/releases | grep -A2 browser_download_url`.
2. Read its official checksum:
   `curl -fsSL https://github.com/minio/minio/releases/download/<version>/minio.linux-amd64.<version>.sha256sum`.
3. Update `MINIO_VERSION` + `MINIO_SHA256` in `Dockerfile`.
4. Update the pinned version/sha256 table above.
5. Tag a new release of this repo (`git tag minio-1.0.1 && git push origin
   minio-1.0.1`); CI builds, verifies the checksum at build time, publishes to
   GHCR as `minio:1.0.1` AND `minio:latest`, and re-pulls the result
   anonymously to prove public availability.
6. Update the digest pin in `omni-deployer/docker-compose.minio.yml` to the
   digest CI just printed (or `docker manifest inspect <ref>`), and note the
   bump in the file's provenance comment.

## Local build / verification

```
docker build -t omni-images/minio:test .
docker run --rm --entrypoint sh omni-images/minio:test -c 'command -v minio; command -v curl; minio --version'
```
