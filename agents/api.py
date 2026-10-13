"""
FastAPI REST API Server for Fetal Ultrasound Biometry Agent.
"""
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from biometry import estimate_fetal_weight
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Fetal Ultrasound Biometry Agent API",
    description="Numerical fetal weight estimation and legacy demonstration audit endpoints",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class BiometryRequest(BaseModel):
    hc_mm: float = Field(gt=0, le=1000, allow_inf_nan=False)
    ac_mm: float = Field(gt=0, le=1000, allow_inf_nan=False)
    fl_mm: float = Field(gt=0, le=1000, allow_inf_nan=False)
    bpd_mm: Optional[float] = Field(default=None, gt=0, le=1000, allow_inf_nan=False)


def verify_admin_token(authorization: Optional[str] = Header(None)) -> None:
    """Simple bearer-token check for sensitive admin endpoints.
    Set API_ADMIN_TOKEN env var to enable; if not set, endpoint is disabled.
    """
    expected = os.getenv("API_ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API not configured (set API_ADMIN_TOKEN)")
    if not authorization or not authorization.startswith("Bearer ") or not secrets.compare_digest(authorization[7:], expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin token")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "fetal-ultrasound-biometry-agent", "domain": "Clinical & Biomedical AI", "standard": "Legacy nonclinical demonstration thresholds", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="The chat request could not be completed")


@app.get("/api/audit/logs")
def api_audit_logs(_=Depends(verify_admin_token)):
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


@app.post("/api/biometry")
def api_biometry(req: BiometryRequest):
    """Numerical estimate; does not diagnose growth abnormalities."""
    return estimate_fetal_weight(req.hc_mm, req.ac_mm, req.fl_mm, req.bpd_mm)


# Local server exposes the same static UI hosted by GitHub Pages.
# Mount last so all declared API routes take precedence.
web_directory = Path(__file__).resolve().parents[1] / "web"
if web_directory.is_dir():
    app.mount("/", StaticFiles(directory=str(web_directory), html=True), name="web")
