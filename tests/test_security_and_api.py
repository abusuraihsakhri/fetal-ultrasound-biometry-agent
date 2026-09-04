"""
Focused security and API tests for fetal-ultrasound-biometry-agent.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    AuditTrail,
    PHIGuard,
    SecurityException,
    AuditLogger,
)


class TestAuditTrailSecurity:
    def test_audit_trail_requires_secret_key(self):
        """AuditTrail must reject initialization without a key."""
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with pytest.raises(SecurityException, match="AUDIT_SECRET_KEY environment variable is required"):
                AuditTrail()
        finally:
            if original:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_audit_trail_rejects_short_key(self):
        """AuditTrail must reject keys shorter than 32 characters."""
        with pytest.raises(SecurityException, match="at least 32 characters"):
            AuditTrail(secret_key="short-key")

    def test_audit_trail_accepts_valid_key(self):
        """AuditTrail initializes successfully with a 32+ char key."""
        trail = AuditTrail(secret_key="a" * 32)
        assert trail.secret_key == b"a" * 32

    def test_audit_trail_chained_integrity(self):
        """Multiple log entries form a valid chain."""
        trail = AuditTrail(secret_key="test-integrity-key-000000000000000000")
        trail.log("actor1", "tier1", "EVENT_A", {"data": 1})
        trail.log("actor2", "tier2", "EVENT_B", {"data": 2})
        trail.log("actor3", "tier1", "EVENT_C", {"data": 3})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 3

    def test_audit_trail_detects_tampering(self):
        """Tampered entries break chain verification."""
        trail = AuditTrail(secret_key="test-tamper-key-0000000000000000000")
        trail.log("actor1", "tier1", "EVENT_A", {"data": 1})
        trail.log("actor2", "tier2", "EVENT_B", {"data": 2})
        # Tamper with the first entry's current_hash
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False


class TestPHIGuardEnforcement:
    def test_detects_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_detects_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN 123-45-6789 found in record")

    def test_detects_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact: (555) 123-4567")

    def test_detects_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Send results to doctor@hospital.org")

    def test_detects_dob(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_redact_phi(self):
        text = "Patient John Doe MRN-994827 phone (555) 123-4567"
        redacted = PHIGuard.redact_phi(text)
        assert "[REDACTED_IDENTIFIER]" in redacted
        assert "MRN-" not in redacted

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Specimen KEY-001 within normal parameters")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")


class TestCLI:
    def test_batch_path_traversal_blocked(self, tmp_path, monkeypatch):
        """Batch command should reject paths outside working directory."""
        from cli import main
        monkeypatch.chdir(tmp_path)
        result = main(["batch", "-i", "/etc/passwd"])
        assert result == 1

    def test_batch_success(self, tmp_path, monkeypatch):
        """Batch command processes valid CSV files."""
        from cli import main
        monkeypatch.chdir(tmp_path)
        csv_file = tmp_path / "input.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-01,TARGET-01,12.0,4.0,False,NOMINAL\n")
        result = main(["batch", "-i", "input.csv", "-o", "output.csv"])
        assert result == 0
        assert (tmp_path / "output.csv").exists()


class TestAPIAuth:
    def test_audit_logs_requires_token(self):
        """Audit logs endpoint requires admin token."""
        os.environ.pop("API_ADMIN_TOKEN", None)
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/api/audit/logs")
        assert response.status_code == 503

    def test_audit_logs_rejects_wrong_token(self):
        """Audit logs endpoint rejects incorrect token."""
        os.environ["API_ADMIN_TOKEN"] = "correct-token-1234567890"
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/api/audit/logs", headers={"Authorization": "Bearer wrong-token"})
        assert response.status_code == 401

    def test_audit_logs_accepts_correct_token(self):
        """Audit logs endpoint accepts correct token."""
        os.environ["API_ADMIN_TOKEN"] = "correct-token-1234567890"
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/api/audit/logs", headers={"Authorization": "Bearer correct-token-1234567890"})
        assert response.status_code == 200
        assert "audit_trail" in response.json()

    def test_health_no_auth_required(self):
        """Health endpoint is publicly accessible."""
        from agents.api import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "HEALTHY"
