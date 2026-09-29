# workstation-datasci (nexuslbs/omni-images)

The **data-science concern** image of the workstation equipment layer
(gap-analysis report E2, operator decision B/M): numpy/pandas/scipy/matplotlib/
sklearn (+jupyter) for notebook analysis, statistics, plotting and model work.

It is an image of **tools/CLIs/commands that RUN AND FINISH** - NOT services
that keep running permanently. The container's default command is `sleep
infinity`, so the container stays up purely for exec-based use: the
workstation's `container` transport (docker-impl) runs
`docker compose exec -T workstation-datasci sh -c '<cmd>'` into it, or launches
the image on demand with `docker run --rm -i <image> sh -c '<cmd>'`.

## Why Debian (not Alpine)

`workstation-tools` is Alpine/musl, and the Alpine/musl wheels for
numpy/scipy/sklearn are painful (measured in the gap-analysis report, E2
implementation note). This concern is deliberately built on
`python:3.11-slim` (Debian bookworm) instead of being forced into the Alpine
base.

## Pinned upstream source

| Field | Value |
|---|---|
| Base image | `python:3.11-slim` (Debian bookworm) |
| numpy | PyPI `numpy==1.26.4` (cp311 wheel) |
| pandas | PyPI `pandas==2.2.3` (cp311 wheel) |
| scipy | PyPI `scipy==1.13.1` (cp311 wheel) |
| matplotlib | PyPI `matplotlib==3.9.2` (cp311 wheel) |
| scikit-learn | PyPI `scikit-learn==1.5.2` (cp311 wheel) |
| jupyter | PyPI `jupyter==1.0.0` (cp311 wheel) |

The image carries **NO entrypoint scripts and NO service**:
`CMD ["sleep", "infinity"]` is the whole lifecycle. The workstation config
(`config/workstation.yml`) targets this image through the `container` transport
(`service: workstation-datasci`).

## Published reference

`ghcr.io/nexuslbs/omni-images/workstation-datasci` - **public**, no credentials
required. Each publish produces BOTH tags: `latest` and the immutable version
tag (from the `workstation-datasci-*` git tag).

## Interface the workstation relies on

* `python3` with numpy/pandas/scipy/matplotlib/sklearn importable
  (`python3 -c "import numpy,pandas,scipy,matplotlib,sklearn"`),
* `jupyter` on PATH,
* the container stays UP (`sleep infinity`) so
  `docker compose exec -T workstation-datasci sh -c <cmd>` works at any time.

## Local build / verification

```
docker build -t omni-images/workstation-datasci:test .
docker run -d --name wsds-smoke omni-images/workstation-datasci:test
docker exec wsds-smoke python3 -c "import numpy,pandas,scipy,matplotlib,sklearn; print('ok')"
docker exec wsds-smoke jupyter --version
docker rm -f wsds-smoke
```

## How to bump

1. Bump the pinned PyPI versions in the Dockerfile.
2. Update the pinned-source table above.
3. Tag a new release of this repo (`git tag workstation-datasci-0.0.1 && git
   push origin workstation-datasci-0.0.1`); CI builds, publishes
   `ghcr.io/nexuslbs/omni-images/workstation-datasci:<version>` AND `:latest`,
   and re-pulls the result anonymously to prove public availability.
4. Update the versioned ref in the consuming compose files if they pin the
   version instead of `latest`.