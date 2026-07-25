"""
Contract Tests for Handover Schema

Tests that handovers match the JSON schema specification.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the path so we can import the modules
module_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, module_path)

from orchestration.handover_service import HandoverService
from orchestration.handover_policy import PolicyViolation


class TestHandoverSchema(unittest.TestCase):
    """Test handover schema validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_valid_handover_schema(self):
        """Test that a valid handover passes schema validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {
                    "agent": "planner",
                    "run_id": "run_123",
                    "task_id": "task_456",
                },
                "destination": {
                    "agent": "implementer",
                    "capability": "repository.change",
                },
                "reason": {
                    "code": "SPECIALIST_REQUIRED",
                    "summary": "Implementation needed",
                },
            },
            "task": {
                "goal": "Add retry handling",
                "requested_outcome": "Implementation",
                "definition_of_done": ["Retries work correctly"],
            },
            "state": {
                "status": "ready_for_implementation",
                "completed": [],
                "current": [],
                "remaining": ["Implement retry"],
            },
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": ["deploy"],
            },
            "next_action": {
                "instruction": "Implement retry",
                "expected_first_tool": "repository.read",
            },
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["implementation"],
                "success_status": "implementation_complete",
            },
            "evidence": [
                {
                    "type": "file",
                    "reference": "src/client.py",
                    "relevance": "Implementation target",
                }
            ],
        }
        
        # Should not raise
        result = self.service.validate_handover(handover)
        self.assertTrue(result)
    
    def test_missing_required_field_schema_version(self):
        """Test that missing schema_version fails validation."""
        handover = {
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(Exception):
            self.service.validate_handover(handover)
    
    def test_missing_required_field_handover(self):
        """Test that missing handover field fails validation."""
        handover = {
            "schema_version": "1.0",
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(Exception):
            self.service.validate_handover(handover)
    
    def test_missing_task_fields(self):
        """Test that missing task fields fail validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                # Missing requested_outcome and definition_of_done
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(Exception):
            self.service.validate_handover(handover)
    
    def test_missing_authorization_fields(self):
        """Test that missing authorization fields fail validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                # Missing principal, delegated_scopes, forbidden_actions
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(Exception):
            self.service.validate_handover(handover)
    
    def test_invalid_schema_version_format(self):
        """Test that invalid schema version format fails validation."""
        handover = {
            "schema_version": "invalid",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("INVALID_SCHEMA_VERSION", str(context.exception))
    
    def test_unsupported_schema_version(self):
        """Test that unsupported schema version fails validation."""
        handover = {
            "schema_version": "2.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("UNSUPPORTED_SCHEMA_VERSION", str(context.exception))
    
    def test_invalid_handover_id_format(self):
        """Test that invalid handover ID format fails validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "invalid_id",  # Should be ho_ followed by at least 8 alphanumeric chars
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(Exception):
            self.service.validate_handover(handover)
    
    def test_valid_handover_id_format(self):
        """Test that valid handover ID format passes validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_0123456789ABC",  # Valid format
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        # Should not raise
        result = self.service.validate_handover(handover)
        self.assertTrue(result)
    
    def test_empty_goal_fails(self):
        """Test that empty goal fails validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "",  # Empty goal
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("INVALID_GOAL", str(context.exception))
    
    def test_missing_evidence(self):
        """Test that missing evidence passes validation (it's optional in the schema but required by policy in some cases)."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Test"},
            },
            "task": {
                "goal": "Test",
                "requested_outcome": "Test",
                "definition_of_done": ["Test"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {
                "return_to": "planner",
                "required_outputs": ["test"],
                "success_status": "test",
            },
            # evidence is missing
        }
        
        # In the JSON schema, evidence is not in required fields, so this should pass
        # But we might want to enforce it in policy
        # For now, this should pass schema validation
        result = self.service.validate_handover(handover)
        # This might pass or fail depending on policy - the schema doesn't require evidence
        # But our policy might
    
    def test_valid_artifact_schema(self):
        """Test that a valid artifact passes schema validation."""
        artifact = {
            "id": "artifact_test001",
            "type": "implementation_plan",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
        }
        
        # Should not raise
        result = self.service.validate_artifact(artifact)
        self.assertTrue(result)
    
    def test_invalid_artifact_id(self):
        """Test that invalid artifact ID fails validation."""
        artifact = {
            "id": "invalid_artifact_id",  # Doesn't match pattern
            "type": "implementation_plan",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
        }
        
        with self.assertRaises(Exception):
            self.service.validate_artifact(artifact)


class TestHandoverAcknowledgementSchema(unittest.TestCase):
    """Test handover acknowledgement schema validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_valid_acknowledgement(self):
        """Test that a valid acknowledgement passes validation."""
        ack = {
            "handover_id": "ho_test001ABCD",
            "receiver": "implementer",
            "decision": "accepted",
            "understanding": {
                "goal": "Implement feature",
                "deliverables": ["implementation", "tests"],
            },
            "accepted_scopes": ["repository:read", "repository:write"],
            "rejected_scopes": [],
            "accepted_at": "2026-07-23T08:31:00Z",
        }
        
        # Should not raise
        result = self.service.validate_acknowledgement(ack)
        self.assertTrue(result)
    
    def test_missing_required_field_handover_id(self):
        """Test that missing handover_id fails validation."""
        ack = {
            "receiver": "implementer",
            "decision": "accepted",
            "understanding": {
                "goal": "Implement feature",
                "deliverables": ["implementation"],
            },
            "accepted_scopes": ["repository:write"],
            "rejected_scopes": [],
            "accepted_at": "2026-07-23T08:31:00Z",
        }
        
        with self.assertRaises(Exception):
            self.service.validate_acknowledgement(ack)
    
    def test_invalid_decision(self):
        """Test that invalid decision value fails validation."""
        ack = {
            "handover_id": "ho_test001ABCD",
            "receiver": "implementer",
            "decision": "maybe",  # Not in enum
            "understanding": {
                "goal": "Implement feature",
                "deliverables": ["implementation"],
            },
            "accepted_scopes": ["repository:write"],
            "rejected_scopes": [],
            "accepted_at": "2026-07-23T08:31:00Z",
        }
        
        with self.assertRaises(Exception):
            self.service.validate_acknowledgement(ack)
    
    def test_valid_rejection(self):
        """Test that a valid rejection passes validation."""
        ack = {
            "handover_id": "ho_test001ABCD",
            "receiver": "implementer",
            "decision": "rejected",
            "understanding": {
                "goal": "Implement feature",
                "deliverables": [],
            },
            "accepted_scopes": [],
            "rejected_scopes": [],
            "accepted_at": "2026-07-23T08:31:00Z",
            "rejection_reason": {
                "code": "CAPABILITY_MISMATCH",
                "message": "Cannot implement this",
            },
        }
        
        # Should not raise
        result = self.service.validate_acknowledgement(ack)
        self.assertTrue(result)
    
    def test_valid_clarification_request(self):
        """Test that a valid clarification request passes validation."""
        ack = {
            "handover_id": "ho_test001ABCD",
            "receiver": "implementer",
            "decision": "clarification-required",
            "understanding": {
                "goal": "Implement feature",
                "deliverables": [],
            },
            "accepted_scopes": [],
            "rejected_scopes": [],
            "accepted_at": "2026-07-23T08:31:00Z",
            "clarifications_required": [
                {
                    "field": "definition_of_done",
                    "question": "What does 'works correctly' mean?",
                    "suggestion": "Add specific criteria",
                }
            ],
        }
        
        # Should not raise
        result = self.service.validate_acknowledgement(ack)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
