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
* is published with **BOTH tags** (operator correction 2026-09-26, telegram
  threads 3165/3166): `latest` (the rolling alias) **and** the version tag
  (the immutable ref consumers may pin). Consumers that need immutability pin
  the version tag or the digest; `latest` is the rolling alias.

## Images


## Conventions

* **New focused images live here too** (operator policy, telegram 2026-09-29): if a
  new focused image is ever needed - e.g. a future `workstation-datasci` - its
  Dockerfile and README are defined in this repo, exactly like
  `workstation-tools/`, with its own GHCR package
* **Dev-overlay build row** (operator policy, telegram 2026-09-29): every new
  focused image also gets ONE build row with a `local/<name>:latest` tag in
  `docker-compose.dev.yml` (the dev overlay of omni-root), exactly like
  `workstation-tools` and `browser` - so it is locally built and tested in
  omnidev before any release. Never the published ghcr.io name in the dev
  overlay.
  (`ghcr.io/nexuslbs/omni-images/<name>`), its own tag prefix in
  `.github/workflows/publish.yml` and its own version tag.
* **Split, don't grow** (operator policy, telegram 2026-09-29): the trigger for
  such a new image is an existing one becoming too big or too disorganized -
  then it is better to split into more focused images than to keep growing the
  existing one.
* **Release in the end-of-chain task** (operator policy, telegram 2026-09-29):
  when such a new image is created, its release (image publish - tag push /
  CI build) happens in the release/deploy task at the end of the chain, not
  ad-hoc.
| Directory | GHCR package | Consumed by |
|---|---|---|
| [`browser/`](browser/README.md) | `ghcr.io/nexuslbs/omni-images/browser` | the `browser` compose service of omni-stack / omni-root (CDP endpoint the workstation/workbench `browser-use-playwright` provider attaches to) |
| [`workstation-tools/`](workstation-tools/README.md) | `ghcr.io/nexuslbs/omni-images/workstation-tools` | the `workstation-tools` compose service of omni-stack / omni-root (himalaya + the general tool set + mysql/redis-cli/mongosh/zip/gitleaks/trivy/semgrep/qpdf/pdfinfo the workstation execs into) |
| [`workstation-datasci/`](workstation-datasci/README.md) | `ghcr.io/nexuslbs/omni-images/workstation-datasci` | the `workstation-datasci` compose service (data-science stack: numpy/pandas/scipy/matplotlib/sklearn + jupyter, Debian base) |
| [`workstation-office/`](workstation-office/README.md) | `ghcr.io/nexuslbs/omni-images/workstation-office` | the `workstation-office` compose service (pandoc, tesseract-ocr, poppler-utils + the Python document libs + LibreOffice/TeX Live/graphviz/qpdf/ghostscript/plantuml/file) |
| [`workstation-media/`](workstation-media/README.md) | `ghcr.io/nexuslbs/omni-images/workstation-media` | the `workstation-media` compose service (ffmpeg moved out of the main image, imagemagick, sox, faster-whisper + the whisper CLI) |
| [`minio/`](minio/README.md) | `ghcr.io/nexuslbs/omni-images/minio` | `omni-deployer/docker-compose.minio.yml` (local S3 endpoint for the deploy's S3 backup/restore/checkpoint test) |

## Publish workflow

`.github/workflows/publish.yml` publishes **tag-only** - an image is built and
pushed ONLY when a tag of its own prefix is pushed:

| Pushed tag | Published image | Tags pushed to GHCR |
|---|---|---|
| `browser-<version>` | `ghcr.io/nexuslbs/omni-images/browser` | `:<version>` + `:latest` |
| `workstation-tools-<version>` | `ghcr.io/nexuslbs/omni-images/workstation-tools` | `:<version>` + `:latest` |
| `workstation-datasci-<version>` | `ghcr.io/nexuslbs/omni-images/workstation-datasci` | `:<version>` + `:latest` |
| `workstation-office-<version>` | `ghcr.io/nexuslbs/omni-images/workstation-office` | `:<version>` + `:latest` |
| `workstation-media-<version>` | `ghcr.io/nexuslbs/omni-images/workstation-media` | `:<version>` + `:latest` |
| `minio-<version>` | `ghcr.io/nexuslbs/omni-images/minio` | `:<version>` + `:latest` |

The image version is the git tag with the prefix stripped (`browser-0.0.4` ->
`browser:0.0.4`). **There is NO publish on a plain `main` push** (the old
sha-tag publish on main is gone) and no manual dispatch: a tag push is the only
way an image is published.

Every publish job builds the image **once**, smoke-tests the built image against
the interface the consumers rely on (browser: CDP `/json/version`; workstation-
tools: himalaya + the tool set present and the container up; minio:
`/minio/health/live`), pushes the **tested** image under both tags, and then
re-pulls the just-published image **without credentials** and prints its digest -
that anonymous pull is the upstream contract the deploy depends on, so it is
verified on every publish.