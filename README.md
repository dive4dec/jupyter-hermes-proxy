# jupyter-hermes-proxy

Launch the [Hermes Agent](https://github.com/nousresearch/hermes-agent) dashboard from JupyterLab as a native launcher entry.

## Features

- One-click launch from the JupyterLab launcher panel with a custom Hermes icon
- Automatic port management via [jupyter-server-proxy](https://github.com/jupyter-server/jupyter-server-proxy)
- Works behind reverse proxies (no manual port forwarding needed)
- **Two modes**: spawn a new dashboard, or connect to an existing one
- Configurable Hermes executable path via `HERMES_BIN_PATH`

## Installation

```bash
pip install jupyter-hermes-proxy
```

Then restart JupyterLab. The "Hermes Dashboard" launcher entry will appear automatically.

## Configuration

### Spawn mode (default)

By default the proxy searches for `hermes` in `PATH` and spawns a new dashboard process when you click the launcher.

Override the binary path:

```bash
export HERMES_BIN_PATH=/path/to/hermes
```

### URL mode (connect to existing dashboard)

When Hermes dashboard is already running (e.g. supervised by s6 in Docker), point the proxy at it:

```bash
export HERMES_DASHBOARD_URL=http://127.0.0.1:9119
```

In this mode the proxy **does not spawn a new process** — it simply proxies traffic to the existing dashboard. No `hermes` binary on PATH is required.

### Building the Hermes dashboard web UI (required)

The Hermes Agent pip package does not ship with the compiled web UI frontend. The dashboard will crash with `ModuleNotFoundError: No module named 'hermes_cli.dashboard_auth'` or show a blank page if `web_dist` is missing.

**You must build the web UI before the dashboard will work:**

```bash
# Clone the hermes-agent source
git clone --depth 1 --branch v2026.5.29.2 https://github.com/NousResearch/hermes-agent.git /tmp/hermes-agent

# Build the web UI
cd /tmp/hermes-agent/web && npm install && npm run build

# Copy the built assets into your Python environment
cp -r hermes_cli/web_dist $(python -c "import site; print(site.getsitepackages()[0])")/hermes_cli/
```

**In Dockerfile contexts**, this is typically done inline:

```dockerfile
RUN git clone --depth 1 --branch v2026.5.29.2 https://github.com/NousResearch/hermes-agent.git /tmp/hermes-agent && \
    cd /tmp/hermes-agent/web && npm install && npm run build && \
    cp -r hermes_cli/web_dist /path/to/conda/site-packages/hermes_cli/ && \
    rm -rf /tmp/hermes-agent
```

Once built, `hermes dashboard --skip-build` will use the pre-built assets instead of attempting a live build.

## Related Packages

- **[jupyter-ai-hermes](https://github.com/dive4dec/jupyter-ai-hermes)** — Hermes Agent as an ACP persona for Jupyter AI chat, with live notebook context injection and MCP tools for cell management.

Both packages share the same `HERMES_BIN_PATH` environment variable convention.

## Development

```bash
git clone git@github.com:dive4dec/jupyter-hermes-proxy.git
cd jupyter-hermes-proxy
pip install -e .
```

## How It Works

This package registers a server spec under the `jupyter_serverproxy_servers` entry point.

- **Spawn mode**: `jupyter-server-proxy` calls `setup_hermes()` which returns a command that spawns `hermes dashboard` on an ephemeral port and proxies it through the Jupyter server.
- **URL mode**: `setup_hermes()` returns the pre-existing dashboard URL directly, so jupyter-server-proxy connects to it without spawning anything.

## License

MIT
