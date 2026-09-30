# workstation-tools (nexuslbs/omni-images)

The **external-interaction tooling** image of the omni stack: himalaya (the email
CLI the workstation's `email-himalaya` capability drives) plus the general Linux
toolbox package set, "just like omni toolbox" (the package reference is
`omni-stack/services/toolbox/Dockerfile`), plus (audit gap G6, 2026-09-30) the
datastore and security-scanner CLIs: mysql, redis-cli, mongosh, zip, gitleaks,
trivy and semgrep.

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
* the container stays UP (`sleep infinity`) so `docker compose exec -T
  workstation-tools sh -c <cmd>` works at any time.

## Local build / verification

```
docker build -t omni-images/workstation-tools:test .
docker run -d --name wst-smoke omni-images/workstation-tools:test
docker exec wst-smoke himalaya --version
docker exec wst-smoke sh -c 'command -v curl jq python3 oathtool psql docker'
docker exec wst-smoke sh -c 'command -v mysql redis-cli mongosh zip gitleaks trivy semgrep'
docker exec wst-smoke mysql --version
docker exec wst-smoke redis-cli --version
docker exec wst-smoke mongosh --version
docker exec wst-smoke zip -v
docker exec wst-smoke gitleaks version
docker exec wst-smoke trivy --version
docker exec wst-smoke semgrep --version
docker rm -f wst-smoke
```

## How to bump

1. Bump the pinned pieces in the Dockerfile: `pyotp==<version>`,
   `semgrep==<version>`, and the `MONGSH_*`/`GITLEAKS_*`/`TRIVY_*` build args
   (himalaya and the rest of the apk set are apk-managed; the Alpine package
   versions follow the base image).
2. Update the pinned-source table above.
3. Tag a new release of this repo (`git tag workstation-tools-0.0.2 && git push
   origin workstation-tools-0.0.2`); CI builds, publishes
   `ghcr.io/nexuslbs/omni-images/workstation-tools:0.0.2` AND `:latest`, and
   re-pulls the result anonymously to prove public availability.
4. Update the versioned ref in the consuming compose files (.env pins) if they
   pin the version instead of `latest`.