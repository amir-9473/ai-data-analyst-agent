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
