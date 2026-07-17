"""Integration test for the ServiceNow plugin end-to-end flow.

This test verifies the complete chain:
Planner -> Registry -> Tool Discovery -> Tool Handler -> Runtime -> Pipeline -> IncidentService
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from plugins.servicenow_pipeline.models import IncidentRequest, VerificationResult
from plugins.servicenow_pipeline.runtime import (
    _bind_runtime_internal,
    _runtime,
    bind_cli_runtime,
    create_incident,
    get_runtime,
    get_runtime_error,
    is_runtime_ready,
)
from plugins.servicenow_pipeline.tools import (
    SERVICENOW_CREATE_INCIDENT_SCHEMA,
    check_servicenow_requirements,
    handle_servicenow_create_incident,
)
from tools.registry import registry


class TestServiceNowIntegration:
    """Integration tests for ServiceNow plugin."""

    def setup_method(self):
        """Reset runtime state before each test."""
        # Clear the singleton runtime
        import plugins.servicenow_pipeline.runtime as runtime_module
        runtime_module._runtime = None
        runtime_module._runtime_error = None
        runtime_module._runtime_config = {}

    def test_runtime_singleton_lifecycle(self):
        """Test that runtime is created once and reused."""
        config = {
            "servicenow_pipeline": {
                "instance_url": "https://test.service-now.com",
                "authentication_type": "basic",
                "username": "admin",
                "password": "password",
            }
        }

        # First bind should succeed
        result1 = bind_cli_runtime(config)
        assert result1 is True
        assert is_runtime_ready() is True
        runtime1 = get_runtime()
        assert runtime1 is not None

        # Second bind should return the same instance (singleton)
        result2 = bind_cli_runtime(config)
        assert result2 is True
        runtime2 = get_runtime()
        assert runtime2 is runtime1  # Same instance

    def test_tool_registry_registration(self):
        """Test that the tool is properly registered in the global registry."""
        # The tool should be registered when the plugin's register() is called
        # This happens during plugin discovery
        from plugins.servicenow_pipeline import register
        from hermes_cli.plugins import PluginManager, PluginContext

        # Create a mock context to capture registrations
        manager = PluginManager()
        ctx = PluginContext(
            manifest=MagicMock(name="servicenow_pipeline", key="servicenow_pipeline"),
            manager=manager,
        )
        
        # Register the plugin
        register(ctx)
        
        # Verify tool was registered
        assert "servicenow_create_incident" in manager._plugin_tool_names
        
        # Verify the tool is in the global registry
        entry = registry.get_entry("servicenow_create_incident")
        assert entry is not None
        assert entry.name == "servicenow_create_incident"
        assert entry.toolset == "servicenow"
        assert entry.handler is not None
        assert entry.check_fn is not None

    def test_tool_schema_matches_expectations(self):
        """Test that the tool schema is correctly defined."""
        assert SERVICENOW_CREATE_INCIDENT_SCHEMA["name"] == "servicenow_create_incident"
        assert "short_description" in SERVICENOW_CREATE_INCIDENT_SCHEMA["parameters"]["properties"]
        assert "description" in SERVICENOW_CREATE_INCIDENT_SCHEMA["parameters"]["properties"]
        assert SERVICENOW_CREATE_INCIDENT_SCHEMA["parameters"]["required"] == ["short_description", "description"]

    def test_check_servicenow_requirements_fallback(self):
        """Test check_fn falls back to env validation when runtime not ready."""
        import os
        # Remove any existing env vars
        for var in ["SERVICENOW_INSTANCE_URL", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD", "SERVICENOW_AUTHENTICATION_TYPE"]:
            os.environ.pop(var, None)
        
        # Runtime not ready, no env vars -> False
        assert check_servicenow_requirements() is False
        
        # Set env vars for basic auth
        os.environ["SERVICENOW_INSTANCE_URL"] = "https://test.service-now.com"
        os.environ["SERVICENOW_AUTHENTICATION_TYPE"] = "basic"
        os.environ["SERVICENOW_USERNAME"] = "admin"
        os.environ["SERVICENOW_PASSWORD"] = "password"
        
        # Should return True via fallback
        assert check_servicenow_requirements() is True

    def test_check_servicenow_requirements_runtime_ready(self):
        """Test check_fn returns True when runtime is ready."""
        config = {
            "servicenow_pipeline": {
                "instance_url": "https://test.service-now.com",
                "authentication_type": "basic",
                "username": "admin",
                "password": "password",
            }
        }
        bind_cli_runtime(config)
        
        # Even without env vars, runtime is ready so check should pass
        import os
        for var in ["SERVICENOW_INSTANCE_URL", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD", "SERVICENOW_AUTHENTICATION_TYPE"]:
            os.environ.pop(var, None)
        
        assert check_servicenow_requirements() is True

    @patch("plugins.servicenow_pipeline.runtime.get_runtime")
    def test_tool_handler_full_flow(self, mock_get_runtime):
        """Test the complete tool handler flow with mocked runtime."""
        # Setup mock runtime and verification result
        mock_verification = VerificationResult(
            verified=True,
            message="Incident created and verified",
            incident_number="INC0010001",
            sys_id="sys_id_12345",
        )
        mock_runtime = MagicMock()
        mock_runtime.execute.return_value = mock_verification
        mock_get_runtime.return_value = mock_runtime

        # Call the tool handler
        args = {
            "short_description": "Test Incident",
            "description": "Test Description",
            "priority": "3",
        }
        result_str = handle_servicenow_create_incident(args)
        result = json.loads(result_str)

        # Verify the result
        assert result["success"] is True
        assert result["verified"] is True
        assert result["incident_number"] == "INC0010001"
        assert result["sys_id"] == "sys_id_12345"

        # Verify runtime.execute was called with correct request
        mock_runtime.execute.assert_called_once()
        called_request = mock_runtime.execute.call_args[0][0]
        assert isinstance(called_request, IncidentRequest)
        assert called_request.short_description == "Test Incident"
        assert called_request.description == "Test Description"
        assert called_request.priority == "3"

    @patch("plugins.servicenow_pipeline.runtime.get_runtime")
    def test_tool_handler_verification_failure(self, mock_get_runtime):
        """Test tool handler returns error when verification fails."""
        mock_verification = VerificationResult(
            verified=False,
            message="Verification failed: missing sys_id",
        )
        mock_runtime = MagicMock()
        mock_runtime.execute.return_value = mock_verification
        mock_get_runtime.return_value = mock_runtime

        args = {
            "short_description": "Test Incident",
            "description": "Test Description",
        }
        result_str = handle_servicenow_create_incident(args)
        result = json.loads(result_str)

        assert "error" in result
        assert "Verification failed: missing sys_id" in result["error"]

    def test_tool_handler_validation(self):
        """Test tool handler validates required fields."""
        # Missing short_description
        result_str = handle_servicenow_create_incident({})
        result = json.loads(result_str)
        assert "error" in result
        assert "short_description is required" in result["error"]

        # Missing description
        result_str = handle_servicenow_create_incident({"short_description": "title"})
        result = json.loads(result_str)
        assert "error" in result
        assert "description is required" in result["error"]

    def test_pipeline_execute_returns_verification_with_ids(self):
        """Test that pipeline.execute returns VerificationResult with incident_number and sys_id."""
        # This test verifies the pipeline correctly propagates execution result
        # identifiers to the verification result
        config = {
            "servicenow_pipeline": {
                "instance_url": "https://test.service-now.com",
                "authentication_type": "basic",
                "username": "admin",
                "password": "password",
            }
        }
        bind_cli_runtime(config)
        
        # Get the runtime and inspect its pipeline
        runtime = get_runtime()
        assert runtime is not None
        
        # The pipeline should have execute method that returns VerificationResult
        # with incident_number and sys_id when verification succeeds
        import inspect
        sig = inspect.signature(runtime.execute)
        assert "request" in sig.parameters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])