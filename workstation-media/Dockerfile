# workstation-media: the media/transcription concern for exec-based use.
#
# One concern image per domain (operator decision M, gap-analysis report
# E6/E8 + section 5.4): ffmpeg (MOVED OUT of the main workstation image per
# decision F), imagemagick (codec/security cadence -> Zone 2) and
# faster-whisper as the transcription engine.
#
# It contains tools/CLIs that RUN AND FINISH - NOT services that keep running
# permanently. The whole lifecycle is `sleep infinity` (the compose service
# passes the same command), so the container stays up for exec-based use.
#
# The workstation reaches it through the `container` transport of the
# general-service seam (`docker compose exec -T workstation-media sh -c ...`
# or `docker run --rm -i <image> sh -c ...`).
#
# Pins (2026-09-29): Debian bookworm apt packages + faster-whisper 1.1.0 (CPU
# wheels: ctranslate2 + huggingface-hub; the model weights download on first
# use into $HOME/.cache/huggingface).

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# ffmpeg + imagemagick (Debian bookworm, --no-install-recommends).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      imagemagick \
 && rm -rf /var/lib/apt/lists/*

# faster-whisper: CPU transcription (CTranslate2). Pinned.
RUN python3 -m pip install --no-cache-dir \
    faster-whisper==1.1.0

# NOT a service: stay up for exec-based use, exactly like the
# workstation-tools container.
CMD ["sleep", "infinity"]