# workstation-office: the office/OCR/render concern for exec-based use.
#
# One concern image per domain (operator decision M, gap-analysis report
# E4/E5 + section 5.4): pandoc, tesseract-ocr + poppler-utils (pdftotext), the
# Python document libraries (python-docx/openpyxl/reportlab/pptx/pypdf) and
# (added 2026-09-30, audit gap G6) the render/PDF toolchain: LibreOffice
# (ODF/legacy rendering), TeX Live latex/pdflatex, graphviz dot, qpdf,
# ghostscript gs and plantuml (UML diagrams; pulls default-jre-headless).
#
# LibreOffice used to stay OUT on the 350 MB budget; audit gap G6 measured the
# missing ODF/legacy rendering as a real interface gap, so it is added on
# purpose now even though it makes the image large (expected).
#
# It contains tools/CLIs that RUN AND FINISH - NOT services that keep running
# permanently. The whole lifecycle is `sleep infinity` (the compose service
# passes the same command), so the container stays up for exec-based use.
#
# The workstation reaches it through the `container` transport of the
# general-service seam (`docker compose exec -T workstation-office sh -c ...`
# or `docker run --rm -i <image> sh -c ...`).
#
# Pins (2026-09-30): python:3.11-slim (Debian) apt packages + PyPI cp311 wheels.

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Office/OCR/render CLIs (Debian, --no-install-recommends: no
# doc/locale packages in the runtime stage).
#   pandoc                     document conversion
#   tesseract-ocr              OCR engine
#   poppler-utils              pdftotext / pdfinfo / pdftoppm
#   libreoffice                ODF/legacy rendering (libreoffice + soffice)
#   texlive-latex-base         latex + pdflatex
#   texlive-fonts-recommended  the fonts the LaTeX base expects
#   lmodern                    Latin Modern (lmodern.sty): pandoc's default
#                              LaTeX template emits \usepackage{lmodern} for
#                              T1 fontenc, so pandoc -> pdflatex needs it
#   graphviz                   dot
#   qpdf                       PDF structural repair/inspection
#   ghostscript                gs (PostScript/PDF rendering)
#   plantuml + default-jre-headless  UML diagrams (plantuml is Java)
#   file                       file(1) type identification, for the PDF
#                              verification interface
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      pandoc \
      tesseract-ocr \
      poppler-utils \
      libreoffice \
      texlive-latex-base \
      texlive-fonts-recommended \
      lmodern \
      graphviz \
      qpdf \
      ghostscript \
      plantuml \
      file \
      default-jre-headless \
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
