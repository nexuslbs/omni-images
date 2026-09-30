# workstation-media (nexuslbs/omni-images)

The **media/transcription concern** image of the workstation equipment layer
(gap-analysis report E6/E8, operator decision F/M; audit gap G6 added
2026-09-30): ffmpeg (MOVED OUT of the main workstation image per decision F),
imagemagick (codec/security cadence -> Zone 2), sox (audio processing) and
faster-whisper as the transcription engine (audio/video -> text,
timestamps/subtitles). It also ships a small `whisper` CLI wrapper around
faster-whisper (`whisper-cli.py`): faster-whisper itself has no command, and
openai-whisper would pull torch (~2 GB) into this thin image.

It is an image of **tools/CLIs/commands that RUN AND FINISH** - NOT services
that keep running permanently. The container's default command is `sleep
infinity`, so the container stays up purely for exec-based use: the
workstation's `container` transport (docker-impl) runs
`docker compose exec -T workstation-media sh -c '<cmd>'` into it, or launches
the image on demand with `docker run --rm -i <image> sh -c '<cmd>'`.

## Pinned upstream source

| Field | Value |
|---|---|
| Base image | `python:3.11-slim` (Debian; the floating tag currently resolves to Debian 13 trixie) |
| ffmpeg | Debian apt package (apt-managed; moved OUT of the main image per decision F) |
| imagemagick | Debian apt package (apt-managed) |
| sox | Debian apt package (apt-managed) |
| faster-whisper | PyPI `faster-whisper==1.1.0` (CPU wheels: CTranslate2 + huggingface-hub) |
| requests | PyPI `requests==2.32.3` (undeclared runtime import of faster_whisper.utils) |
| whisper CLI | `whisper-cli.py` in this directory, COPYed to `/usr/local/bin/whisper` (plain CLI, no agent-specific tooling) |

The image carries **NO entrypoint scripts and NO service**:
`CMD ["sleep", "infinity"]` is the whole lifecycle. The workstation config
(`config/workstation.yml`) targets this image through the `container` transport
(`service: workstation-media`). Model weights download on first use into
`$HOME/.cache/huggingface` (the compose service persists the harness home).

## Published reference

`ghcr.io/nexuslbs/omni-images/workstation-media` - **public**, no credentials
required. Each publish produces BOTH tags: `latest` and the immutable version
tag (from the `workstation-media-*` git tag).

## Interface the workstation relies on

* `ffmpeg`, `magick`/`convert`, `sox` on PATH,
* `whisper` on PATH: `whisper --help`, `whisper <audio> [--model <size>]`
  (default model `tiny`), transcription text on stdout,
* `python3` with `faster_whisper` importable
  (`python3 -c "from faster_whisper import WhisperModel"`),
* the container stays UP (`sleep infinity`) so
  `docker compose exec -T workstation-media sh -c <cmd>` works at any time.

## Local build / verification

```
docker build -t omni-images/workstation-media:test .
docker run -d --name wsm-smoke omni-images/workstation-media:test
docker exec wsm-smoke ffmpeg -version
docker exec wsm-smoke magick -version
docker exec wsm-smoke python3 -c "from faster_whisper import WhisperModel; print('ok')"
docker exec wsm-smoke sh -c 'command -v sox whisper ffmpeg magick'
docker exec wsm-smoke sox --version
docker exec wsm-smoke whisper --help
docker exec wsm-smoke sh -c 'ffmpeg -y -f lavfi -i sine=frequency=440:duration=1 /tmp/t.wav && whisper /tmp/t.wav --model tiny'
docker rm -f wsm-smoke
```

## How to bump

1. Bump the pinned PyPI version (faster-whisper / requests) in the Dockerfile
   (apt packages follow the Debian base image of `python:3.11-slim`).
2. Update the pinned-source table above.
3. Tag a new release of this repo (`git tag workstation-media-0.0.1 && git
   push origin workstation-media-0.0.1`); CI builds, publishes
   `ghcr.io/nexuslbs/omni-images/workstation-media:<version>` AND `:latest`,
   and re-pulls the result anonymously to prove public availability.
4. Update the versioned ref in the consuming compose files if they pin the
   version instead of `latest`.