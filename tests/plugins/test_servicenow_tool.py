"""Unit tests for the ServiceNow tool execution layer."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from plugins.servicenow_pipeline.models import ExecutionResult, VerificationResult
from plugins.servicenow_pipeline.tools import (
    check_servicenow_requirements,
    handle_servicenow_create_incident,
)


def test_check_servicenow_requirements_empty_env(monkeypatch):
    """check_servicenow_requirements returns False when env vars are missing."""
    monkeypatch.delenv("SERVICENOW_INSTANCE_URL", raising=False)
    assert check_servicenow_requirements() is False


def test_check_servicenow_requirements_valid_basic_auth(monkeypatch):
    """check_servicenow_requirements returns True with valid basic credentials."""
    monkeypatch.setenv("SERVICENOW_INSTANCE_URL", "https://dev12345.service-now.com")
    monkeypatch.setenv("SERVICENOW_AUTHENTICATION_TYPE", "basic")
    monkeypatch.setenv("SERVICENOW_USERNAME", "admin")
    monkeypatch.setenv("SERVICENOW_PASSWORD", "password")
    assert check_servicenow_requirements() is True


def test_check_servicenow_requirements_invalid_url(monkeypatch):
    """check_servicenow_requirements returns False if instance URL is invalid."""
    monkeypatch.setenv("SERVICENOW_INSTANCE_URL", "not-a-url")
    assert check_servicenow_requirements() is False


def test_handle_servicenow_create_incident_validation_error():
    """handle_servicenow_create_incident returns tool_error for missing required fields."""
    res = json.loads(handle_servicenow_create_incident({}))
    assert res.get("error") is not None
    assert "short_description is required" in res["error"]

    res_desc = json.loads(handle_servicenow_create_incident({"short_description": "title"}))
    assert res_desc.get("error") is not None
    assert "description is required" in res_desc["error"]


@patch("plugins.servicenow_pipeline.tools.create_incident")
def test_handle_servicenow_create_incident_success(mock_create_incident):
    """handle_servicenow_create_incident executes the pipeline and verifier successfully."""
    # Setup mock verification result (returned by create_incident)
    mock_verification_result = VerificationResult(
        verified=True,
        message="Verified successfully",
        incident_number="INC0010001",
        sys_id="sys_id_12345",
    )
    mock_create_incident.return_value = mock_verification_result

    args = {
        "short_description": "Test Incident Title",
        "description": "Test Incident Detail Description",
        "priority": "3",
    }

    # Call the tool handler
    response_str = handle_servicenow_create_incident(args)
    response = json.loads(response_str)

    # Assertions
    assert response["success"] is True
    assert response["verified"] is True
    assert response["incident_number"] == "INC0010001"
    assert response["sys_id"] == "sys_id_12345"

    # Verify create_incident was called with correct IncidentRequest
    mock_create_incident.assert_called_once()
    called_request = mock_create_incident.call_args[0][0]
    assert called_request.short_description == "Test Incident Title"
    assert called_request.description == "Test Incident Detail Description"
    assert called_request.priority == "3"


@patch("plugins.servicenow_pipeline.tools.create_incident")
def test_handle_servicenow_create_incident_failure(mock_create_incident):
    """handle_servicenow_create_incident returns error when verification fails."""
    mock_verification_result = VerificationResult(
        verified=False,
        message="Verification failed: missing sys_id",
    )
    mock_create_incident.return_value = mock_verification_result

    args = {
        "short_description": "Test Incident Title",
        "description": "Test Incident Detail Description",
    }

    response_str = handle_servicenow_create_incident(args)
    response = json.loads(response_str)

    assert response["error"] is not None
    assert "Verification failed: missing sys_id" in response["error"]


@patch("plugins.servicenow_pipeline.tools.create_incident")
def test_handle_servicenow_create_incident_runtime_error(mock_create_incident):
    """handle_servicenow_create_incident returns error when runtime raises exception."""
    mock_create_incident.side_effect = RuntimeError("ServiceNow connection failed")

    args = {
        "short_description": "Test Incident Title",
        "description": "Test Incident Detail Description",
    }

    response_str = handle_servicenow_create_incident(args)
    response = json.loads(response_str)

    assert response["error"] is not None
    assert "ServiceNow incident creation failed" in response["error"]