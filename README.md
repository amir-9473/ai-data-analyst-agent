# AI Data Analyst Agent

[English](README.md) | [فارسی](README.fa.md)

A compact multilingual agent that reads CSV, Excel, or JSON files, understands multi-part questions in Persian or English, runs statistical tools, and returns Markdown plus charts.

## What it can do

- Match column names despite case, spacing, minor typos, or common Persian/English equivalents.
- Complete several analyses and charts in one request through a multi-round tool loop.
- Run descriptive, missing-value, correlation, outlier, frequency, grouped, and trend analyses.
- Draw histogram, box, scatter, line, bar, pie, and correlation charts.
- Render mixed Persian, English, and numbers with bidirectional web styling; Persian chart labels are reshaped correctly.
- Read standard CSV delimiters plus the unusual separator used by the Persian sample in `uploads`.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env
# Put your OpenRouter key in .env
.venv\Scripts\streamlit run streamlit_app.py
```

`run_app.bat` performs the last command on Windows. The optional FastAPI interface remains available with `run_backend.bat` and exposes interactive docs at `http://127.0.0.1:8000/docs`.

## Publish a free web demo

The Streamlit app reads and analyzes files in one process, so the public demo needs no separate backend, VM, or paid host:

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io), create an app and select `streamlit_app.py` as the entry point.
3. Add these values under **Advanced settings > Secrets**:

```toml
OPENROUTER_API_KEY = "your-openrouter-key"
LLM_MODEL = "qwen/qwen3-8b"
```

4. Deploy and share the generated HTTPS URL. Never commit the real key.

## Example request

> Describe age, detect its outliers, create a histogram and a box plot, and then analyze the relationship between age and BMI.

The model receives the real schema first, maps informal or translated concepts to actual column names, executes every required tool, and summarizes the results in the user's language.

## Project layout

```text
app/
  agent/orchestrator.py   # LLM multi-tool loop
  tools/                  # analysis and visualization
  loaders/                # CSV, Excel and JSON
  api/                    # optional FastAPI endpoints
streamlit_app.py          # local and cloud web demo
notebooks/ai_data_analyst_demo.ipynb
tests/
```

## Test

```powershell
.venv\Scripts\python -m pytest -q -p no:cacheprovider
```

Tests cover Persian file loading, fuzzy/semantic column matching, all analysis modes, all chart types, multiple tool calls, the API health endpoint, and Streamlit startup.

The bundled [Vazirmatn](https://github.com/rastikerdar/vazirmatn) font is distributed under the SIL Open Font License 1.1; its license is included in `assets/fonts/OFL.txt`.

## Docker Deployment

Docker Engine and Docker Compose v2 are the only host prerequisites. The image runs the existing
Streamlit application as a non-root user on port `8501` inside the application container. Uploaded
files and generated charts use dedicated Docker volumes.

Create a private runtime environment file from the tracked template and add the required provider
credential:

```bash
cp .env.example .env
chmod 600 .env
```

`OPENROUTER_API_KEY` is required for AI-generated analyses. `LLM_MODEL` selects the OpenRouter model.
Deployment variables are `SITE_ADDRESS`, `PUBLIC_HTTP_PORT`, and `STREAMLIT_HOST_PORT`. Never commit
the `.env` file, API keys, passwords, Streamlit secrets, certificates, or private keys.

Build and start the Streamlit application and Caddy reverse proxy:

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f
```

Verify Streamlit through its loopback-only host binding:

```bash
curl http://127.0.0.1:8601/_stcore/health
```

Stop the deployment with:

```bash
docker compose down
```

Both services use `restart: unless-stopped`, so they start again after a server restart when the
Docker service is enabled and the containers were not stopped manually.

## VPS Deployment

The default Compose configuration implements this path:

```text
Internet
  -> Caddy / Reverse Proxy (:8080)
  -> Docker network
  -> Streamlit (:8501)
  -> Data Analyst Agent
```

The current VPS deployment is available at:

```text
http://82.22.175.58:8080
```

For another server, replace the IP address and choose an unused `PUBLIC_HTTP_PORT` in the private
`.env` file. Streamlit remains private on `127.0.0.1:STREAMLIT_HOST_PORT`; do not publish its port
directly. When several projects share one VPS, give each project a different public and loopback
port. Allow the selected public TCP port in both the VPS firewall and any provider firewall.

Without a domain, open the application at:

```text
http://SERVER_PUBLIC_IP:PUBLIC_HTTP_PORT
```

When a domain becomes available, point its DNS record to the server and route it through a shared
Caddy, Nginx, or other reverse proxy. The Docker application does not need to change. The shared
proxy can provide HTTPS with Let's Encrypt or another ACME issuer; never commit certificate keys.

Update an existing deployment with:

```bash
git pull
docker compose up -d --build
```

Basic troubleshooting commands are:

```bash
docker compose ps
docker compose logs
docker inspect ai-data-analyst-app
curl http://127.0.0.1:8601/_stcore/health
curl http://SERVER_PUBLIC_IP:PUBLIC_HTTP_PORT/_stcore/health
```
