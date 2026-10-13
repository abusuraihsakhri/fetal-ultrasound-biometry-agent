"""Independent regression checks and input boundary tests for Hadlock-3."""
import math
import pytest
from biometry import estimate_fetal_weight


def test_published_hadlock_3_equation_and_units():
    # 30, 28 and 5.5 cm entered as mm.
    expected = 10 ** (1.326 - 0.00326 * 28 * 5.5 + 0.0107 * 30 + 0.0438 * 28 + 0.158 * 5.5)
    result = estimate_fetal_weight(300, 280, 55, 78)
    assert result["estimated_fetal_weight_g"] == round(expected, 1)
    assert result["measurements_mm"]["BPD"] == 78
    assert "Hadlock-3" in result["method"]


def test_bpd_not_used_in_three_parameter_equation():
    assert estimate_fetal_weight(300, 280, 55)["estimated_fetal_weight_g"] == (
        estimate_fetal_weight(300, 280, 55, 80)["estimated_fetal_weight_g"]
    )


@pytest.mark.parametrize("bad", [-2, 0, float("nan"), float("inf"), float("-inf"), 1001, "n/a", None, True])
def test_rejects_invalid_measurements(bad):
    with pytest.raises(ValueError):
        estimate_fetal_weight(bad, 280, 55)


def test_estimate_contains_no_percentile_or_diagnosis():
    result = estimate_fetal_weight(300, 280, 55)
    assert "percentile" not in result
    assert "not gestational age" in result["interpretation"].lower()


def test_api_biometry_matches_python_calculator():
    from fastapi.testclient import TestClient
    from agents.api import app

    with TestClient(app) as client:
        response = client.post("/api/biometry", json={"hc_mm": 300, "ac_mm": 280, "fl_mm": 55, "bpd_mm": 78})
        assert response.status_code == 200
        assert response.json()["estimated_fetal_weight_g"] == estimate_fetal_weight(300, 280, 55, 78)["estimated_fetal_weight_g"]
        assert client.post("/api/biometry", json={"hc_mm": 300, "ac_mm": 0, "fl_mm": 55}).status_code == 422
        assert client.post("/api/biometry", json={"hc_mm": 300, "ac_mm": "NaN", "fl_mm": 55}).status_code == 422
        page = client.get("/")
        assert page.status_code == 200
        assert "Hadlock-3" in page.text


def test_audit_integrity_detects_last_entry_modification():
    from agents.base import AuditTrail

    trail = AuditTrail(secret_key="independent-test-key-32-characters-minimum")
    trail.log("system", "worker", "EVENT", {"status": "OK"})
    assert trail.verify_integrity() is True
    trail.logs[-1]["event_type"] = "FORGED"
    assert trail.verify_integrity() is False


def test_audit_snapshot_cannot_modify_signed_internal_entries():
    from agents.base import AuditTrail

    trail = AuditTrail(secret_key="independent-test-key-32-characters-minimum")
    trail.log("system", "worker", "EVENT", {"status": "OK"})
    snapshot = trail.get_trail()
    snapshot[0]["current_hash"] = "FORGED"
    assert trail.verify_integrity() is True


def test_task_metadata_phi_is_screened():
    from agents.models import SystemTaskPayload
    from agents.supervisor import SystemSupervisor
    from agents.base import SecurityException

    task = SystemTaskPayload(
        task_id="TASK-01", target_identifier="NONPHI-01",
        primary_metric=12.0, attributes={"contact": "person@example.org"}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(task)
