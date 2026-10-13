# Fetal Ultrasound Biometry Agent

Numerical fetal **estimated weight (EFW)** calculator using the Hadlock-3 equation (head circumference, abdominal circumference and femur length). Includes a standalone browser interface, Python function, and FastAPI endpoint. Other legacy audit and simulator interfaces remain available but are **not clinical growth classifiers**.

## Browser calculator

Open `web/index.html` in a modern browser, or use the GitHub Pages deployment when available. Enter ultrasound measurements in **millimeters**:

- HC — head circumference (required)
- AC — abdominal circumference (required)
- FL — femur diaphysis length (required)
- BPD — biparietal diameter (optional, recorded but **not** used by Hadlock-3)

Select **Calculate EFW** to view the weight in grams and kilograms. **Export result as CSV** downloads the measurement values, method and EFW. Fictional example values populate the form on first load.

The implementation converts millimeters to centimeters and calculates:

```text
log10(EFW in g) = 1.326 - 0.00326 × AC × FL
                 + 0.0107 × HC + 0.0438 × AC + 0.158 × FL
```

HC, AC and FL in the equation are **centimeters**. BPD is recorded for reference only.

**Clinical limitation:** This is a formula demonstration, not a validated clinical decision-support system. No image measurement, gestational age determination, percentile calculation, growth-restriction classification, anomaly screening, or other diagnosis is performed. Ultrasound acquisition quality, accurate dating, appropriate centile reference and clinical interpretation remain essential. Do not use output alone for medical decisions.

References: [Hadlock et al., *Am J Obstet Gynecol* 1985;151:333–337](https://pubmed.ncbi.nlm.nih.gov/3881966/); [ISUOG routine mid-trimester scan guidelines (2022)](https://doi.org/10.1002/uog.24888).

## Privacy

The GitHub Pages calculator performs all calculations and CSV export **within your browser**. It makes no application API requests and does not store entered measurements. It loads no third-party fonts, scripts, or analytics. A reference link leads to an external website only if clicked.

**Do not enter identifiable patient information.** The optional backend has a limited pattern-based identifier check; this does *not* establish HIPAA compliance, complete de-identification, or suitability for real patient records. The backend retains audit data in process memory during runtime.

## Python and API

Requirements: Python 3.9+ (CI exercises 3.10–3.12).

```bash
git clone https://github.com/abusuraihsakhri/fetal-ultrasound-biometry-agent.git
cd fetal-ultrasound-biometry-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Direct calculation:

```python
from biometry import estimate_fetal_weight

result = estimate_fetal_weight(hc_mm=300, ac_mm=280, fl_mm=55, bpd_mm=78)
print(result["estimated_fetal_weight_g"])
```

For API requests and the same browser UI served locally:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
# Open http://127.0.0.1:8000/ or POST /api/biometry
```

```bash
curl -s http://127.0.0.1:8000/api/biometry \
  -H 'Content-Type: application/json' \
  -d '{"hc_mm":300,"ac_mm":280,"fl_mm":55,"bpd_mm":78}'
```

Endpoints: `GET /health`, `POST /api/biometry`, `POST /api/audit`, `POST /api/chat`, `GET /metrics`, and authenticated `GET /api/audit/logs`. `API_ADMIN_TOKEN` controls audit-log access; without it, the endpoint is disabled. The chat backend is a deterministic mock, **not a medical reasoning or validated AI model**.

The legacy `agents/`, `fetal_echo_ai/` and `enrichment.py` components implement generic threshold demonstrations. Their clinical/standards labels, critical status flags and named feature modules do **not** imply validated fetal biometry, imaging, FGR or anomaly-detection capabilities. The legacy CLI supports `audit`, `chat`, `batch`, `verify-audit` and `serve`:

```bash
python cli.py audit --primary 28 --secondary 14
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
```

A missing `AUDIT_SECRET_KEY` in the local CLI generates an **ephemeral** session signing key; persist a strong key in production to avoid invalidating audit records between restarts. Never commit this key. Audit records remain in memory and are not a durable compliance archive.

## Tests

```bash
python -m pytest -q
python -m pip check
node --test web/biometry.test.js   # Node 22+ for development only
```

GitHub Actions tests Python 3.10, 3.11, 3.12 and the standalone JavaScript calculation. The static calculator needs no Python runtime, Pyodide, account, server or third-party script.

## Docker

```bash
printf 'AUDIT_SECRET_KEY=%s\n' "$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
docker compose up --build
```

Open `http://localhost:8000/`. The root page and API run in the same container. `.env` is excluded from Git. For deployment, configure appropriate authentication, transport security, runtime isolation, and privacy governance independently.

## Technology, browsers and license

- Python, Pydantic 2, FastAPI and Uvicorn for optional backend workflows
- Plain HTML/CSS/JavaScript for offline numerical calculation
- Current desktop/mobile Chrome, Firefox, Safari and Edge (ES2021-capable)
- [MIT License](LICENSE)

The repository has a GitHub Pages deployment workflow for the `web/` directory. Publication depends on the repository's GitHub Pages settings and successful deployment.
