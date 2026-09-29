# workstation-datasci: the data-science stack for exec-based use.
#
# One concern image per domain (operator decision M, gap-analysis report
# E2 + section 5.4): numpy/pandas/scipy/matplotlib/sklearn (+jupyter) in a
# DEBIAN base on purpose - the Alpine/musl wheels for numpy/scipy/sklearn are
# painful (measured report note), so this concern is NOT forced into the Alpine
# `workstation-tools` base.
#
# It contains tools/CLIs that RUN AND FINISH - NOT services that keep running
# permanently. The whole lifecycle is `sleep infinity` (the compose service
# passes the same command), so the container stays up for exec-based use.
#
# The workstation reaches it through the `container` transport of the
# general-service seam (`docker compose exec -T workstation-datasci sh -c ...`
# or `docker run --rm -i <image> sh -c ...`), exactly like himalaya in
# workstation-tools.
#
# Pins (2026-09-29, Python 3.11 wheels): all packages are manylinux wheels for
# cp311 on Debian bookworm; no build toolchain is needed in the runtime stage.

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# The data-science stack, pinned. All pure/manylinux wheels for cp311.
RUN python3 -m pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.2.3 \
    scipy==1.13.1 \
    matplotlib==3.9.2 \
    scikit-learn==1.5.2 \
    jupyter==1.0.0

# NOT a service: stay up for exec-based use (`docker compose exec -T
# workstation-datasci sh -c <cmd>`), exactly like the workstation-tools
# container.
CMD ["sleep", "infinity"]