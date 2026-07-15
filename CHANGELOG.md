# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-15

### Fixed
- Fix dashboard crash-loop when used with Hermes Agent 0.18+.
  Hermes 0.18+ requires an auth provider for non-loopback dashboard binds
  (the `--insecure` flag was deprecated after a security advisory). The
  previous `--host=0.0.0.0 --insecure` flags caused the dashboard to exit
  immediately and be respawned by `jupyter-server-proxy` every ~1.5s.
  Changed `--host=0.0.0.0` to `--host=127.0.0.1` (loopback, no auth required)
  and removed the deprecated `--insecure` flag. `jupyter-server-proxy` already
  handles external access through the Jupyter server.

- Fix "Invalid Host header" error when the dashboard is accessed through
  `jupyter-server-proxy` behind a reverse proxy (e.g. JupyterHub). Hermes 0.18+
  validates the `Host` header against the bind address as DNS-rebinding
  defence. `jupyter-server-proxy` forwards the browser's `Host` header
  (e.g. `socratic.cs.cityu.edu.hk`), which doesn't match the loopback bind
  (`127.0.0.1`). Added `request_headers_override` to the server spec so
  `jupyter-server-proxy` rewrites the `Host` header to `127.0.0.1:{port}`
  before forwarding, making the host check pass naturally.

## [0.2.0] - 2026-07-14

### Changed
- Bump version to 0.2.0.

## [0.1.0] - 2026-07-13

### Added
- Initial release: env-var-first `HERMES_BIN_PATH` support.
- URL mode via `HERMES_DASHBOARD_URL` environment variable.
- Tests and README.
