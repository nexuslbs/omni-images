# gods-eye-view (nexuslbs/omni-images)

The **keyless JSON data plane** of [God's Eye View](https://github.com/bilawalsidhu/gods-eye-view)
(GEV) as a SEPARATE, network-internal service. GEV is a browser app (CesiumJS
globe) whose value to an agent is a side effect: a local Node/vite server that
normalizes ~25 `/api/*` JSON routes over public feeds, with per-source caching and
honesty fields (`source`, `attribution`, `fetchedAt`, `stale`, `unavailable`,
`reason`).

This image runs **only that data plane**, with **zero credentials**. The visual
globe, the Google/Cesium-ion basemap ladder and the imagery CLI tools
(`tools/*.mjs`) are deliberately NOT included: they need metered Google/Cesium
keys and Google Maps Content may not be cached, stored or rehosted.

Operator rule: an external service never boots inside the workstation image.
This service lives in its own container; the thin workstation plugin
`spatial-tools` calls it over the compose network (`http://gods-eye-view:4173`).

## Pinned upstream source

| Field | Value |
|---|---|
| Base image | `node:24-bookworm-slim` (upstream `engines`: `>=24.14.0 <25 \|\| >=26 <27`) |
| Upstream repo | `https://github.com/bilawalsidhu/gods-eye-view` |
| Upstream commit | `e7707d9a0f34d9fbffc300023c319f95caa5be30` (branch `main`, pushed 2026-09-29T00:33:34Z) |
| Build | `git clone --depth 1` at the SHA, `npm ci` (puppeteer Chromium download skipped), `npm run build` |
| Server | `npm run dev -- --host 0.0.0.0 --port 4173` (see "Why dev, not preview") |
| Upstream licence | MIT for the **source code only**; third-party DATA has its own licences (`LICENSE` + `THIRD_PARTY_NOTICES.md` are kept in the image at `/app`) |

## Why dev, not preview

Upstream mounts `/api/setup/status` and `/api/setup/keys` only when
`command === 'serve' && !isPreview` (`server/standalone/key-setup.js`). Measured in
the feasibility gate: under `npm run preview` both routes answer `404
{"error":"Unknown API route"}`; under `npm run dev` `/api/setup/status` answers
`200` with the key registry (`setCount: 0`, `total: 8`). The `spatial status` tool
needs that route, so the image runs the dev server. `vite preview` serves every
other `/api/*` route identically (same `createBrowserViteConfig`).

## Interface the workstation relies on (all GET, all keyless)

| Route | Meaning |
|---|---|
| `/api/cyclones` | NOAA NHC/CPHC storms (honest `stale`/`unavailable`/`reason`) |
| `/api/fire-perimeters` | NIFC WFIGS wildfire perimeters + InciWeb |
| `/api/launches` | Launch Library 2 recent launches |
| `/api/opensky` | live aircraft (anonymous mode; accepts `lat`/`lon` anchor for the adsb.lol fallback) |
| `/api/adsblol/mil` | live military aircraft |
| `/api/ais-live` | live vessels; **503 keyless** with `status:"missing-key"` |
| `/api/cctv/sources` | public camera catalog (austin + caltrans by default) |
| `/api/radio/stations` | Radio Browser station directory |
| `/api/setup/status` | which optional keys are set (all `false` here) |

No `/api/...` route for earthquakes: USGS is fetched client-side by the browser
(`src/layers/earthquakes/source.js`). The `spatial events` tool reports that
absence as a typed error rather than inventing a route.

## Keyless / no-token posture

NO `GOOGLE_MAPS_API_KEY`, NO `CESIUM_ION_TOKEN`, NO `OPENAI_API_KEY`, NO
`FIRMS_MAP_KEY`, NO `TOMTOM_API_KEY`, NO `AISSTREAM_API_KEY`, NO `LL2_API_TOKEN`.
The compose service sets only `HOST`, `PORT` and the `CCTV_*_ENABLED` kill
switches. `/api/setup/status` proves it: `setCount: 0`.

CCTV packs: `austin` and `caltrans` are unconditional in the pinned SHA; every
optional pack is disabled (`CCTV_TFL_ENABLED=0`, `CCTV_DELDOT_ENABLED=0`, ...) to
keep the legal surface and network load down. The catalog is metadata only; no
frame is ever fetched, stored or analysed.

## Licence notes (summary, not legal advice)

Safe with attribution for internal research: NOAA/NHC, USGS, CelesTrak, adsb.lol
(ODbL), NIFC/InciWeb, Launch Library 2, OSM/Overpass, Radio Browser.
Flagged non-commercial: OpenSky Network (anonymous), TeleGeography (bundled NC
data), Google/Cesium personal tiers, Google News RSS. Do not build a commercial
product on the OpenSky/TeleGeography/Google-News layers without re-licensing.

## Local build / verification

```
docker build -t local/gods-eye-view:latest /opt/workspace/omni-images/gods-eye-view
docker run -d --name gev-smoke local/gods-eye-view:latest
docker exec gev-smoke wget -qO- http://127.0.0.1:4173/api/cyclones | head -c 200
docker exec gev-smoke wget -qO- http://127.0.0.1:4173/api/setup/status | head -c 200
docker rm -f gev-smoke
```

## Measured footprint

See the commit message / task report for the measured values: image size and
container RSS at idle. Re-measure on every bump; the VM is memory-constrained.

## How to bump

1. Pick a new upstream commit SHA (`git ls-remote https://github.com/bilawalsidhu/gods-eye-view main`).
2. Update `ARG GEV_SHA` (and the revision label) in `Dockerfile`, and the table above.
3. `docker build` locally and re-run the route smoke checks (the same 8 routes as
   the feasibility gate under `/opt/workspace/tmp/gods-eye-view-gate/`).
4. Tag a release (`git tag gods-eye-view-0.0.1 && git push origin
   gods-eye-view-0.0.1`); CI builds and publishes
   `ghcr.io/nexuslbs/omni-images/gods-eye-view:0.0.1` + `:latest`.
5. Update the versioned ref in the consuming compose files if they pin a version.
