"""
Security Tests for Handover Authorization

Tests authorization validation and security constraints for handovers.
"""

import os
import sys
import unittest

# Add the src directory to the path
module_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, module_path)

from orchestration.handover_service import HandoverService
from orchestration.handover_policy import HandoverPolicy, PolicyViolation


class TestAuthorizationValidation(unittest.TestCase):
    """Test authorization validation in handovers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_valid_authorization(self):
        """Test that valid authorization passes validation."""
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
                "goal": "Modify payment client",
                "requested_outcome": "Changes",
                "definition_of_done": ["Changes implemented"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:read", "repository:write:src/payments/**"],
                "forbidden_actions": ["deploy", "publish"],
                "expires_at": "2026-07-23T10:00:00Z",
            },
            "next_action": {"instruction": "Implement", "expected_first_tool": "repository.read"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        # Should pass
        result = self.service.validate_handover(handover)
        self.assertTrue(result)
    
    def test_missing_principal(self):
        """Test that missing principal fails validation."""
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
                # Missing principal
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("MISSING_PRINCIPAL", str(context.exception))
    
    def test_missing_delegated_scopes(self):
        """Test that missing delegated_scopes fails validation."""
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
                # Missing delegated_scopes
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("MISSING_DELEGATED_SCOPES", str(context.exception))
    
    def test_empty_delegated_scopes(self):
        """Test that empty delegated_scopes fails validation."""
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
                "delegated_scopes": [],  # Empty
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("EMPTY_DELEGATED_SCOPES", str(context.exception))
    
    def test_missing_forbidden_actions(self):
        """Test that missing forbidden_actions fails validation."""
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
                # Missing forbidden_actions
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("MISSING_FORBIDDEN_ACTIONS", str(context.exception))
    
    def test_excessive_permissions_in_least_privilege_mode(self):
        """Test that excessive permissions are rejected in least-privilege mode."""
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
                "goal": "Modify payment client",
                "requested_outcome": "Changes",
                "definition_of_done": ["Changes implemented"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],  # Too broad
                "forbidden_actions": ["deploy"],
            },
            "next_action": {"instruction": "Implement", "expected_first_tool": "repository.read"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        # The default policy uses least-privilege mode
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("EXCESSIVE_PERMISSIONS", str(context.exception))
    
    def test_expired_authorization(self):
        """Test that expired authorization is rejected."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-20T08:30:00Z",
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
                "delegated_scopes": ["repository:read", "repository:write:src/test/**"],
                "forbidden_actions": [],
                "expires_at": "2026-07-20T10:00:00Z",  # Already expired
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("EXPIRED_AUTHORIZATION", str(context.exception))
    
    def test_invalid_expiration_format(self):
        """Test that invalid expiration format is rejected."""
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
                "delegated_scopes": ["repository:write:src/test/**"],
                "forbidden_actions": [],
                "expires_at": "invalid-date-format",
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("INVALID_EXPIRATION", str(context.exception))
    
    def test_delegation_depth_exceeded(self):
        """Test that exceeding delegation depth is rejected."""
        policy = HandoverPolicy(max_handover_depth=3)
        service = HandoverService(policy=policy)
        
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
                "delegated_scopes": ["repository:write:src/test/**"],
                "forbidden_actions": [],
                "delegation_depth": 3,  # Already at max
                "max_delegation_depth": 3,
            },
            "next_action": {"instruction": "Test", "expected_first_tool": "test"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            service.validate_handover(handover)
        
        self.assertIn("DELEGATION_DEPTH_EXCEEDED", str(context.exception))
    
    def test_high_risk_action_without_approval(self):
        """Test that high-risk actions require approval."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Deployment needed"},
            },
            "task": {
                "goal": "Deploy to production",
                "requested_outcome": "Deployment",
                "definition_of_done": ["Deployed"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:read", "repository:write", "deploy"],
                "forbidden_actions": [],
                "approval_required": [],  # deploy is high-risk but not in approval_required
            },
            "next_action": {"instruction": "Deploy", "expected_first_tool": "deploy"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("MISSING_HUMAN_APPROVAL", str(context.exception))
    
    def test_high_risk_action_with_approval(self):
        """Test that high-risk actions with approval pass validation."""
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Deployment needed"},
            },
            "task": {
                "goal": "Deploy to staging",
                "requested_outcome": "Staging deployment",
                "definition_of_done": ["Deployed to staging"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["deploy:staging"],
                "forbidden_actions": [],
                "approval_required": ["deploy"],  # deploy is in approval_required
            },
            "next_action": {"instruction": "Deploy to staging", "expected_first_tool": "deploy"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        # Should pass because deploy is in approval_required
        result = self.service.validate_handover(handover)
        self.assertTrue(result)
    
    def test_no_approval_required_disabled(self):
        """Test that disabling approval requirement allows high-risk actions."""
        policy = HandoverPolicy(
            require_human_approval_for_high_risk_actions=False
        )
        service = HandoverService(policy=policy)
        
        handover = {
            "schema_version": "1.0",
            "handover": {
                "id": "ho_test001ABCD",
                "created_at": "2026-07-23T08:30:00Z",
                "source": {"agent": "planner", "run_id": "run_123", "task_id": "task_456"},
                "destination": {"agent": "implementer", "capability": "repository.change"},
                "reason": {"code": "SPECIALIST_REQUIRED", "summary": "Deployment needed"},
            },
            "task": {
                "goal": "Deploy to staging",
                "requested_outcome": "Staging deployment",
                "definition_of_done": ["Deployed"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["deploy"],
                "forbidden_actions": [],
                "approval_required": [],  # Empty, but approval not required
            },
            "next_action": {"instruction": "Deploy", "expected_first_tool": "deploy"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
        }
        
        # Should pass because approval requirement is disabled
        result = service.validate_handover(handover)
        self.assertTrue(result)
    
    def test_contains_secrets_rejected(self):
        """Test that handovers containing secrets are rejected."""
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
                "goal": "Configure API",
                "requested_outcome": "Configuration",
                "definition_of_done": ["Configured"],
            },
            "state": {"status": "ready", "completed": [], "current": [], "remaining": []},
            "authorization": {
                "principal": "user_789",
                "delegated_scopes": ["repository:write"],
                "forbidden_actions": [],
            },
            "next_action": {"instruction": "Configure", "expected_first_tool": "repository.read"},
            "return_contract": {"return_to": "planner", "required_outputs": [], "success_status": "done"},
            "evidence": [],
            "security": {
                "data_classification": "internal",
                "contains_secrets": True,  # Contains secrets
            },
        }
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("FORBIDDEN_SECRETS", str(context.exception))


class TestContextFilteringSecurity(unittest.TestCase):
    """Test context filtering for security."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_remove_secrets(self):
        """Test that secrets are removed from text."""
        filter = self.service.context_filter
        
        text = "The API key is sk-1234567890abcdef"
        filtered = filter.remove_secrets(text)
        
        self.assertNotIn("sk-1234567890abcdef", filtered)
        self.assertIn("[REDACTED]", filtered)
    
    def test_remove_api_keys(self):
        """Test that API keys are removed."""
        filter = self.service.context_filter
        
        text = "Use api_key=abc123xyz for authentication"
        filtered = filter.remove_secrets(text)
        
        self.assertNotIn("abc123xyz", filtered)
    
    def test_remove_passwords(self):
        """Test that passwords are removed."""
        filter = self.service.context_filter
        
        text = "The password is mysecret123"
        filtered = filter.remove_secrets(text)
        
        self.assertNotIn("mysecret123", filtered)
    
    def test_remove_bearer_tokens(self):
        """Test that bearer tokens are removed."""
        filter = self.service.context_filter
        
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.test"
        filtered = filter.remove_secrets(text)
        
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", filtered)
    
    def test_remove_pii_emails(self):
        """Test that PII (emails) are removed."""
        filter = self.service.context_filter
        
        text = "Contact user@example.com for more information"
        filtered = filter.remove_pii(text)
        
        self.assertNotIn("user@example.com", filtered)
        self.assertIn("[PII_REDACTED]", filtered)
    
    def test_remove_pii_phone_numbers(self):
        """Test that PII (phone numbers) are removed."""
        filter = self.service.context_filter
        
        text = "Call +1-555-123-4567 for support"
        filtered = filter.remove_pii(text)
        
        self.assertNotIn("555-123-4567", filtered)


class TestArtifactValidation(unittest.TestCase):
    """Test artifact validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_valid_artifact(self):
        """Test that a valid artifact passes validation."""
        artifact = {
            "id": "artifact_test001abc123",
            "name": "Test Artifact",
            "type": "implementation_plan",
            "media_type": "text/markdown",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "version": 1,
            "digest": "sha256:abc123def456ghi789jkl012mno345pqr678",
            "size_bytes": 1024,
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
            "metadata": {
                "parent_handover_id": "ho_test001",
                "task_id": "task_123",
                "tags": ["plan", "implementation"],
            },
        }
        
        result = self.service.validate_artifact(artifact)
        self.assertTrue(result)
    
    def test_invalid_artifact_id(self):
        """Test that invalid artifact ID fails validation."""
        artifact = {
            "id": "invalid",
            "type": "implementation_plan",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
        }
        
        with self.assertRaises(Exception):
            self.service.validate_artifact(artifact)
    
    def test_invalid_digest_format(self):
        """Test that invalid digest format fails validation."""
        artifact = {
            "id": "artifact_test001abc123",
            "type": "implementation_plan",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "digest": "invalid-digest",
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
        }
        
        with self.assertRaises(Exception):
            self.service.validate_artifact(artifact)
    
    def test_valid_digest_format(self):
        """Test that valid digest format passes validation."""
        artifact = {
            "id": "artifact_test001abc123",
            "type": "implementation_plan",
            "uri": "repo://.agent-artifacts/run_123/plan.md",
            "digest": "sha256:abc123def456ghi789jkl012mno345pqr678stu901",
            "produced_by": "planner",
            "produced_at": "2026-07-23T08:30:00Z",
        }
        
        result = self.service.validate_artifact(artifact)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
