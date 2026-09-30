# workstation-media: the media/transcription concern for exec-based use.
#
# One concern image per domain (operator decision M, gap-analysis report
# E6/E8 + section 5.4): ffmpeg (MOVED OUT of the main workstation image per
# decision F), imagemagick (codec/security cadence -> Zone 2), sox (audio
# processing/format conversion) and faster-whisper as the transcription engine.
# The `whisper` CLI wrapper is added by this image (whisper-cli.py): faster-
# whisper ships no command of its own, and openai-whisper would pull torch
# (~2 GB) into this thin image.
#
# It contains tools/CLIs that RUN AND FINISH - NOT services that keep running
# permanently. The whole lifecycle is `sleep infinity` (the compose service
# passes the same command), so the container stays up for exec-based use.
#
# The workstation reaches it through the `container` transport of the
# general-service seam (`docker compose exec -T workstation-media sh -c ...`
# or `docker run --rm -i <image> sh -c ...`).
#
# Pins (2026-09-30): python:3.11-slim (Debian) apt packages + faster-whisper 1.1.0 (CPU
# wheels: ctranslate2 + huggingface-hub; the model weights download on first
# use into $HOME/.cache/huggingface).

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# ffmpeg + imagemagick + sox (Debian, --no-install-recommends).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      imagemagick \
      sox \
 && rm -rf /var/lib/apt/lists/*

# faster-whisper: CPU transcription (CTranslate2). Pinned. `requests` is an
# undeclared runtime import of faster_whisper.utils (model download), so it is
# pinned explicitly.
RUN python3 -m pip install --no-cache-dir \
    faster-whisper==1.1.0 \
    requests==2.32.3

# The `whisper` command: a plain wrapper around faster_whisper (no agent-specific
# tooling). The source lives in this repo next to the Dockerfile.
COPY whisper-cli.py /usr/local/bin/whisper
RUN chmod 0755 /usr/local/bin/whisper

# NOT a service: stay up for exec-based use, exactly like the
# workstation-tools container.
CMD ["sleep", "infinity"]
