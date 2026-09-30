# workstation-office (nexuslbs/omni-images)

The **office/OCR/render concern** image of the workstation equipment layer
(gap-analysis report E4/E5, operator decision D/M; audit gap G6 added
2026-09-30): pandoc, tesseract-ocr + poppler-utils (pdftotext) and the Python
document libraries (python-docx/openpyxl/reportlab/pptx/pypdf) for producing
and parsing docx/xlsx/pptx/PDF artifacts and OCR-ing scanned documents, plus
the render/PDF toolchain: LibreOffice (ODF/legacy), TeX Live latex/pdflatex,
graphviz `dot`, qpdf, ghostscript `gs`, plantuml and `file` (file(1) type
identification for the PDF-verification interface).

It is an image of **tools/CLIs/commands that RUN AND FINISH** - NOT services
that keep running permanently. The container's default command is `sleep
infinity`, so the container stays up purely for exec-based use: the
workstation's `container` transport (docker-impl) runs
`docker compose exec -T workstation-office sh -c '<cmd>'` into it, or launches
the image on demand with `docker run --rm -i <image> sh -c '<cmd>'`.

## Why LibreOffice is IN (audit gap G6)

LibreOffice (~400-700 MB) used to stay OUT to keep the office budget (<= 350 MB,
gap-analysis report section 5.4). Audit gap G6 measured the missing ODF/legacy
rendering as a real interface gap, so the image deliberately grew and now ships
LibreOffice plus the rest of the render/PDF toolchain.

## Pinned upstream source

| Field | Value |
|---|---|
| Base image | `python:3.11-slim` (Debian; the floating tag currently resolves to Debian 13 trixie) |
| pandoc | Debian apt package (apt-managed) |
| tesseract-ocr | Debian apt package (apt-managed) |
| poppler-utils | Debian apt package (pdftotext, apt-managed) |
| libreoffice | Debian apt package (ODF/legacy rendering; large, expected) |
| texlive-latex-base, texlive-fonts-recommended, texlive-latex-recommended | Debian apt packages (`latex` + `pdflatex`; lmodern + xcolor for pandoc's default LaTeX template) |
| graphviz | Debian apt package (`dot`) |
| qpdf | Debian apt package (PDF repair/inspection) |
| ghostscript | Debian apt package (`gs`) |
| plantuml + default-jre-headless | Debian apt packages (plantuml is Java) |
| file | Debian apt package (`file` type identification) |
| python-docx | PyPI `python-docx==1.1.2` (cp311 wheel) |
| openpyxl | PyPI `openpyxl==3.1.5` (cp311 wheel) |
| reportlab | PyPI `reportlab==4.2.5` (cp311 wheel) |
| python-pptx | PyPI `python-pptx==1.0.2` (cp311 wheel) |
| pypdf | PyPI `pypdf==5.1.0` (cp311 wheel) |

The image carries **NO entrypoint scripts and NO service**:
`CMD ["sleep", "infinity"]` is the whole lifecycle. The workstation config
(`config/workstation.yml`) targets this image through the `container` transport
(`service: workstation-office`).

## Published reference

`ghcr.io/nexuslbs/omni-images/workstation-office` - **public**, no credentials
required. Each publish produces BOTH tags: `latest` and the immutable version
tag (from the `workstation-office-*` git tag).

## Interface the workstation relies on

* `pandoc`, `tesseract`, `pdftotext` on PATH,
* `libreoffice`/`soffice`, `latex`/`pdflatex`, `dot`, `qpdf`, `gs` (ghostscript),
  `plantuml` and `file` on PATH,
* `python3` with docx/openpyxl/reportlab/pptx/pypdf importable
  (`python3 -c "import docx,openpyxl,reportlab,pptx,pypdf"`),
* the container stays UP (`sleep infinity`) so
  `docker compose exec -T workstation-office sh -c <cmd>` works at any time.

## Local build / verification

```
docker build -t omni-images/workstation-office:test .
docker run -d --name wso-smoke omni-images/workstation-office:test
docker exec wso-smoke pandoc --version
docker exec wso-smoke tesseract --version
docker exec wso-smoke python3 -c "import docx,openpyxl,reportlab,pptx,pypdf; print('ok')"
docker exec wso-smoke sh -c 'command -v libreoffice soffice latex pdflatex dot plantuml qpdf gs file'
docker exec wso-smoke libreoffice --version
docker exec wso-smoke latex --version
docker exec wso-smoke dot -V
docker exec wso-smoke qpdf --version
docker exec wso-smoke gs --version
docker exec wso-smoke plantuml -version
docker exec wso-smoke file --version
docker rm -f wso-smoke
```

## How to bump

1. Bump the pinned PyPI versions in the Dockerfile (apt packages follow the
   Debian base image of `python:3.11-slim`).
2. Update the pinned-source table above.
3. Tag a new release of this repo (`git tag workstation-office-0.0.1 && git
   push origin workstation-office-0.0.1`); CI builds, publishes
   `ghcr.io/nexuslbs/omni-images/workstation-office:<version>` AND `:latest`,
   and re-pulls the result anonymously to prove public availability.
4. Update the versioned ref in the consuming compose files if they pin the
   version instead of `latest`.