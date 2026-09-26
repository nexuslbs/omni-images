# browser (nexuslbs/omni-images)

The **browser service image** of the omni stack - a SEPARATE image from the
workstation/workbench core images (`ghcr.io/nexuslbs/deepseek-harness`,
`ghcr.io/nexuslbs/workbench`), which stay BROWSER-FREE. It carries **no
workstation/workbench code and no dependency on either**: chromium (from the
official playwright image), a raw TCP forwarder that publishes chromium's
loopback CDP endpoint on `0.0.0.0`, a live-view (x11vnc + websockify + noVNC)
that is OFF unless a deployment asks for it, and a tiny entrypoint
(`start-browser` / `cdp-forward.js`).

Operator decision (2026-09-20): *"the browser image is a separate image, not the
workbench image. It could be accessible using GeneralService"*. The
`browser-use-playwright` provider only ATTACHES to this service over CDP
(`browserService.endpoint` -> `http://browser:9222`); the workstation/workbench
images never launch a local browser.

## Pinned upstream source

| Field | Value |
|---|---|
| Upstream image | `mcr.microsoft.com/playwright:v1.63.0-noble` (chromium + node + Xvfb baked in) |
| Chromium | the version shipped in that playwright image (measured: Chromium 153) |
| Live-view packages | `x11vnc novnc websockify` (apt, from the base image's distribution) |

The base image is pinned by tag (`v1.63.0-noble`), never `:latest`. The
Dockerfile FAILS CLOSED on the critical pieces: it asserts `Xvfb` + `node` (the
headful default and the CDP forwarder), and `x11vnc` + `websockify` +
`/usr/share/novnc/vnc.html` (the live view).

## Files

| file | what it is |
| --- | --- |
| `Dockerfile` | `FROM mcr.microsoft.com/playwright:v1.63.0-noble` + entrypoint + forwarder, `EXPOSE 9222` |
| `start-browser.sh` | the entrypoint: finds chromium, runs it on a loopback port, runs the forwarder on `0.0.0.0:9222`, refuses to report success until the CDP endpoint really answers, then supervises both; owns the on-demand live view (`vnc-start` / `vnc-stop` / `vnc-status`) |
| `cdp-forward.js` | a raw TCP proxy (`0.0.0.0:9222` -> `127.0.0.1:9223`); chromium binds loopback only, so the forwarder is required |

## Interface the deployment relies on

* CDP endpoint on **:9222** (`/json/version` answers 200 once chromium is up) -
  what the `browser-use-playwright` provider attaches to,
* live view on **:8080** (`/vnc.html`), ON DEMAND only (`start-browser
  vnc-start` / `vnc-stop`, or `BROWSER_VNC=1` at boot) - a phone-usable noVNC
  stream of the SAME display the agent's chromium draws on, with NO password of
  ours (`x11vnc -nopw`; the tunnel + its access policy are the boundary),
* `start-browser --background` exits 0 only after the CDP endpoint answers (for
  launchers that must not block on a foreground child).

Full env contract and the live-view security note: see the Dockerfile comments
and the workbench-plugins browser docs history. Key envs: `BROWSER_CDP_PORT`
(9222), `BROWSER_CDP_INTERNAL_PORT` (9223), `BROWSER_HEADLESS` (0 = headful on
Xvfb, the default), `BROWSER_DISPLAY`/`BROWSER_SCREEN`/`BROWSER_WINDOW_SIZE`,
`BROWSER_VNC` (0 = live view off by default), `BROWSER_VNC_PORT` (5900),
`BROWSER_NOVNC_PORT` (8080), `BROWSER_NOVNC_WEB` (/usr/share/novnc).

## Published reference

`ghcr.io/nexuslbs/omni-images/browser` - **public**, no credentials required.
Each publish produces BOTH tags (operator correction 2026-09-26):

* `latest` - the rolling alias,
* `<version>` - the immutable version tag (from the `browser-*` git tag).

Consumers that pin use the version tag, e.g.
`ghcr.io/nexuslbs/omni-images/browser:0.0.4` (the compose default of the
workstation browser service).

## How to bump

1. Pick a new playwright base tag (`mcr.microsoft.com/playwright:vX.Y.Z-noble`)
   and update `FROM` in the Dockerfile.
2. Update the pinned-source table above.
3. Tag a new release of this repo (`git tag browser-0.0.5 && git push origin
   browser-0.0.5`); CI builds, smoke-tests (CDP `/json/version` must answer),
   publishes `ghcr.io/nexuslbs/omni-images/browser:0.0.5` AND `:latest`, and
   re-pulls the result anonymously to prove public availability.
4. Update the versioned refs that pin it (compose defaults / .env pins).

## Local build / verification

```
docker build -t omni-images/browser:test .
docker run -d --name browser-smoke -p 9222:9222 omni-images/browser:test
curl -fsS http://127.0.0.1:9222/json/version      # {"Browser":"Chrome/153...."}
docker rm -f browser-smoke
```