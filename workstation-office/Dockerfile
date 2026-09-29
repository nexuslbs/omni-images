# workstation-office: the office/OCR concern for exec-based use.
#
# One concern image per domain (operator decision M, gap-analysis report
# E4/E5 + section 5.4): pandoc, tesseract-ocr + poppler-utils (pdftotext) and
# the Python document libraries (python-docx/openpyxl/reportlab/pptx/pypdf).
# LibreOffice stays OUT on purpose (it would blow the 350 MB budget; it gets a
# separate opt-in image only if a project demonstrably needs ODF/legacy
# rendering).
#
# It contains tools/CLIs that RUN AND FINISH - NOT services that keep running
# permanently. The whole lifecycle is `sleep infinity` (the compose service
# passes the same command), so the container stays up for exec-based use.
#
# The workstation reaches it through the `container` transport of the
# general-service seam (`docker compose exec -T workstation-office sh -c ...`
# or `docker run --rm -i <image> sh -c ...`).
#
# Pins (2026-09-29): Debian bookworm apt packages + PyPI cp311 wheels.

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Office/OCR CLIs (Debian bookworm, --no-install-recommends: no doc/locale
# packages in the runtime stage).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      pandoc \
      tesseract-ocr \
      poppler-utils \
 && rm -rf /var/lib/apt/lists/*

# The Python document libraries, pinned (cp311 wheels, no build toolchain).
RUN python3 -m pip install --no-cache-dir \
    python-docx==1.1.2 \
    openpyxl==3.1.5 \
    reportlab==4.2.5 \
    python-pptx==1.0.2 \
    pypdf==5.1.0

# NOT a service: stay up for exec-based use, exactly like the
# workstation-tools container.
CMD ["sleep", "infinity"]