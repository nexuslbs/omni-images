# omni-images

Container images that the **omni** stack and its deploy tooling build and
publish **ourselves**, so that neither CI nor a hybrid/deploy host depends on a
third-party image namespace or on an artifact nobody in nexuslbs controls.

Every image in this repo:

* is built from a **pinned upstream source** (version **and** checksum/pin
  recorded in the image's directory README and in its Dockerfile),
* is published by our own CI to **GHCR** as
  `ghcr.io/nexuslbs/omni-images/<name>`,
* is **public** (pullable with no credentials) - the deploy's CI runner and any
  deploy host pull it anonymously,
* is consumed **by digest** (immutable) from the deploy repos, never by a
  floating tag and never with a `:latest` base image.

## Images

| Directory | GHCR package | Consumed by |
|---|---|---|
| [`minio/`](minio/README.md) | `ghcr.io/nexuslbs/omni-images/minio` | `omni-deployer/docker-compose.minio.yml` (local S3 endpoint for the deploy's S3 backup/restore/checkpoint test) |

## Publish workflow

`.github/workflows/publish.yml` builds every image on a **`v*` tag** (that is
this repo's own release tag) and on pushes to `main`, and pushes it to GHCR
with these tags:

* `{{version}}`, `{{major}}.{{minor}}`, `{{major}}` from the repo release tag
  (e.g. tag `v1.0.0` -> `1.0.0`, `1.0`, `1`),
* `sha-<short>` - the exact commit the image was built from,
* `<upstream version>` - the pinned upstream version baked into the image
  (read out of the image's Dockerfile at build time).

There is deliberately **no `latest` tag**: consumers pin the immutable digest.

The workflow's last job re-pulls the just-published image **without
credentials** and prints its digest - that anonymous pull is the upstream
contract the deploy depends on, so it is verified on every publish.
