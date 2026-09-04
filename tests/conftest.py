"""
Pytest configuration and shared fixtures for fetal-ultrasound-biometry-agent tests.
"""
import os
import secrets


def pytest_configure(config):
    """Set a deterministic test key before any test imports agents.base."""
    if not os.getenv("AUDIT_SECRET_KEY"):
        os.environ["AUDIT_SECRET_KEY"] = "test-audit-secret-key-for-testing-only-0000000000"
