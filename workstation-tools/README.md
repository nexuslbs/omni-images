# workstation-tools (nexuslbs/omni-images)

The **external-interaction tooling** image of the omni stack: himalaya (the email
CLI the workstation's `email-himalaya` capability drives) plus the general Linux
toolbox package set, "just like omni toolbox" (the package reference is
`omni-stack/services/toolbox/Dockerfile`), plus (audit gap G6, 2026-09-30) the
datastore and security-scanner CLIs: mysql, redis-cli, mongosh, zip, gitleaks,
trivy and semgrep, plus the PDF-verification pair qpdf and poppler-utils
(`pdfinfo`) so a PDF can be re-verified outside the office container. Since
v0.0.11 it also ships `git` (required by gitleaks git-history mode) and the
pre-release security-gate config at `/etc/gitleaks/gitleaks.toml`.

It is an image of **tools/CLIs/commands that RUN AND FINISH** - NOT services that
keep running permanently. The container's default command is `sleep infinity` (or
the compose service passes the same), so the container stays up purely for
exec-based use: the workstation's `container` transport (docker-impl) runs
`docker compose exec -T workstation-tools sh -c '<cmd>'` into it, exactly like it
used to exec into the omni `toolbox` service.

## Why a separate image (instead of himalaya in the toolbox)

Operator decision (2026-09-26, telegram threads 3165/3166): himalaya moves OUT of
the toolbox into its own `workstation-tools` image. The toolbox keeps its
backup/utility role; the workstation's external-interaction tools get a dedicated,
versioned image published from THIS repo.

## Pinned upstream source

| Field | Value |
|---|---|
| Base image | `alpine:latest` (same as the toolbox reference; apk-managed packages) |
| himalaya | Alpine package `himalaya` (v1.2.0, apk-managed, `/usr/bin/himalaya`) |
| oathtool | Alpine package `oath-toolkit-oathtool` (TOTP/HOTP CLI) |
| pyotp | PyPI `pyotp==2.10.0` (pinned, pure-python TOTP library) |
| mysql | Alpine `mysql-client` (dummy migration package) -> `mariadb-client` 11.8.8-r0, `/usr/bin/mysql` |
| redis-cli | Alpine package `redis` (8.8.0-r0; also ships redis-server) |
| zip | Alpine package `zip` (3.0-r13) |
| qpdf | Alpine package `qpdf` (PDF structural repair/inspection) |
| poppler-utils | Alpine package `poppler-utils` (`pdfinfo`/`pdftotext`/`pdftoppm`) |
| sqlite3 | Alpine package `sqlite` (database CLI, `/usr/bin/sqlite3`; there is no package named `sqlite3` and `sqlite-tools` does not ship the binary) |
| yq | Alpine package `yq-go` (mikefarah Go yq 4.x YAML/JSON processor, `/usr/bin/yq`; the `yq-python` package is the unrelated jq wrapper and is NOT used) |
| node | Alpine package `nodejs` (Node runtime, `/usr/bin/node`; `npm` is a separate community package and is not required) |
| git | Alpine package `git` (required by gitleaks git-history mode: `gitleaks detect --log-opts=--all` shells out to git) |
| gitleaks config | `gitleaks.toml` in this directory, copied to `/etc/gitleaks/gitleaks.toml`; the default base `/etc/gitleaks/gitleaks-defaults.toml` is generated at build time from the pinned gitleaks release (see the gate section below) |
| mongosh | Pinned MongoDB CDN tarball `mongosh-2.12.0-linux-x64.tgz`, sha256 `aa42cb826b7b8e655c5481293f5365ddaf1a23e43af07520326e5bbc957838ad`; glibc binary run through `gcompat` + the checked-in `mongosh-resolv-shim.c` |
| gitleaks | Pinned GitHub binary `v8.30.1` linux_x64, sha256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| trivy | Pinned GitHub binary `v0.74.0` Linux-64bit, sha256 `2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a` |
| semgrep | PyPI `semgrep==1.178.0` (musllinux wheel with bundled semgrep-core) |
| General set | `bash tini dcron curl wget rclone postgresql-client postgresql docker-cli docker-compose python3 py3-pip py3-psycopg2 jq` (the toolbox package reference) |

The image carries **NO entrypoint scripts and NO service**: `CMD ["sleep",
"infinity"]` is the whole lifecycle. The workstation config
(`config/workstation.yml`) targets this image through the `container` transport:

```yaml
general:
  type: container
  params:
    engine: docker-compose
    compose:
      project_dir: /opt/omni
      service: workstation-tools
```

## Published reference

`ghcr.io/nexuslbs/omni-images/workstation-tools` - **public**, no credentials
required. Each publish produces BOTH tags (operator correction 2026-09-26):

* `latest` - the rolling alias,
* `<version>` - the immutable version tag (from the `workstation-tools-*` git tag).

## Interface the workstation relies on

* `himalaya` on PATH (`/usr/bin/himalaya`, v1 syntax: `account list -o json`,
  `envelope list -o json --page-size N`),
* the general tool set (curl, jq, python3, oathtool, docker CLI, psql, ...),
* the datastore/scanner CLIs: `mysql`, `redis-cli`, `mongosh`, `zip`,
  `gitleaks`, `trivy`, `semgrep`,
* the database CLI `sqlite3`, the YAML/JSON processor `yq` and the `node`
  runtime (added 2026-10-03, the database/zip/scanner enrichment follow-up of
  audit gap G6, thread 4017),
* `git` on PATH (so gitleaks git-history mode works),
* the pre-release gate config `/etc/gitleaks/gitleaks.toml` (and its pinned
  base `/etc/gitleaks/gitleaks-defaults.toml`),
* the PDF-verification pair `qpdf` and `pdfinfo`,
* the container stays UP (`sleep infinity`) so `docker compose exec -T
  workstation-tools sh -c <cmd>` works at any time.

## Pre-release security gate (gitleaks)

The image ships a **custom gitleaks config** at `/etc/gitleaks/gitleaks.toml`
that is a **superset** of the gitleaks defaults. It loads every built-in rule
(including the marker-based `openai-api-key` rule and `github-pat`) from the
pinned `/etc/gitleaks/gitleaks-defaults.toml` and adds three shape-based rules
with **no allowlist**, so the canonical placeholder values are still flagged:

| Rule ID | Shape |
|---|---|
| `aws-access-key-id-strict` | `\bAKIA[0-9A-Z]{16}\b` (e.g. `AKIAIOSFODNN7EXAMPLE`) |
| `aws-secret-access-key` | `\b[A-Za-z0-9/+=]{40}\b`, keyword-gated on `aws`/`secret`/`access` (e.g. `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`) |
| `openai-api-key` | `\bsk-[A-Za-z0-9_\-]{20,}\b` (e.g. `sk-demo...`) |

The gate command (git-history mode, so `git` must be present, which it is since
v0.0.11):

```sh
gitleaks detect \
  --config /etc/gitleaks/gitleaks.toml \
  --source /path/to/repo \
  --log-opts=--all \
  --report-format=json \
  --report-path=/tmp/gitleaks-report.json
```

`gitleaks-defaults.toml` is built from the gitleaks **v8.30.1** default config
(`https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml`,
sha256-verified in the Dockerfile) with exactly one modification: the global
allowlist stopword `abcdefghijklmnopqrstuvwxyz` is removed. gitleaks' `[extend]`
mechanism only appends an extended config's global allowlists (`config.extend()`
in v8.30.1 does `c.Allowlists = append(...)`), so `useDefault = true` can never
un-allowlist that stopword, and the canonical placeholder OpenAI value
(`sk-demo1234567890abcdefghijklmnopqrstuvwxyz`) would be silently suppressed.
The custom config therefore extends the pinned file by path. A trace run shows
the suppression this avoids:

```
DBG extending config with default config
TRC skipping finding: global allowlist allowed-stopword=abcdefghijklmnopqrstuvwxyz condition=OR finding=sk-demo... rule-id=openai-api-key
```

## Local build / verification

```
docker build -t omni-images/workstation-tools:test .
docker run -d --name wst-smoke omni-images/workstation-tools:test
docker exec wst-smoke himalaya --version
docker exec wst-smoke sh -c 'command -v curl jq python3 oathtool psql docker'
docker exec wst-smoke sh -c 'command -v git mysql redis-cli mongosh zip gitleaks trivy semgrep qpdf pdfinfo'
docker exec wst-smoke git --version
docker exec wst-smoke mysql --version
docker exec wst-smoke redis-cli --version
docker exec wst-smoke mongosh --version
docker exec wst-smoke zip -v
docker exec wst-smoke gitleaks version
docker exec wst-smoke trivy --version
docker exec wst-smoke semgrep --version
docker exec wst-smoke qpdf --version
docker exec wst-smoke pdfinfo -v
docker exec wst-smoke sqlite3 --version
docker exec wst-smoke yq --version
docker exec wst-smoke node --version
docker rm -f wst-smoke
```

## How to bump

1. Bump the pinned pieces in the Dockerfile: `pyotp==<version>`,
   `semgrep==<version>`, and the `MONGSH_*`/`GITLEAKS_*`/`TRIVY_*` build args
   (himalaya and the rest of the apk set are apk-managed; the Alpine package
   versions follow the base image). The three added 2026-10-03 tools (`sqlite3`
   = apk `sqlite`, `yq` = apk `yq-go`, `node` = apk `nodejs`) are apk-managed
   too, so there is no version pin to bump for them: they follow the base image.
2. Update the pinned-source table above. When `GITLEAKS_VERSION` changes, update
   the `GITLEAKS_DEFAULT_CONFIG_SHA256` build arg with the sha256 of
   `https://raw.githubusercontent.com/gitleaks/gitleaks/v<VERSION>/config/gitleaks.toml`
   (the Dockerfile strips the global allowlist stopword
   `abcdefghijklmnopqrstuvwxyz` from it at build time).
3. Tag a new release of this repo (`git tag workstation-tools-0.0.2 && git push
   origin workstation-tools-0.0.2`); CI builds, publishes
   `ghcr.io/nexuslbs/omni-images/workstation-tools:0.0.2` AND `:latest`, and
   re-pulls the result anonymously to prove public availability.
4. Update the versioned ref in the consuming compose files (.env pins) if they
   pin the version instead of `latest`.