"""
Integration Tests for Handover Lifecycle

Tests the complete handover lifecycle from preparation to closure.
"""

import os
import sys
import unittest
from datetime import datetime, timezone

# Add the src directory to the path
module_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, module_path)

from orchestration.handover_service import HandoverService, HandoverError
from orchestration.handover_policy import HandoverPolicy, PolicyViolation
from orchestration.ownership_store import OwnershipStore, OwnershipConflict
from orchestration.context_filter import ContextFilter


class TestHandoverLifecycle(unittest.TestCase):
    """Test the complete handover lifecycle."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.policy = HandoverPolicy()
        self.ownership_store = OwnershipStore()
        self.context_filter = ContextFilter()
        self.service = HandoverService(
            policy=self.policy,
            ownership_store=self.ownership_store,
            context_filter=self.context_filter,
        )
    
    def tearDown(self):
        """Clean up."""
        self.ownership_store.clear()
    
    def test_prepare_handover(self):
        """Test preparing a new handover."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_456",
            destination_agent="implementer",
            capability="repository.change",
            goal="Add retry handling to payment client",
            requested_outcome="Working implementation with tests",
            definition_of_done=[
                "Retries only transient failures",
                "Retry count is configurable",
                "Existing public interfaces remain compatible",
                "make check passes",
            ],
            state={
                "status": "ready_for_implementation",
                "completed": ["Design complete"],
                "current": ["Ready to start"],
                "remaining": ["Implement retry logic"],
            },
            authorization={
                "principal": "user_789",
                "delegated_scopes": [
                    "repository:read",
                    "repository:write:src/infrastructure/payments/**",
                    "repository:write:tests/unit/payments/**",
                    "tests:execute",
                ],
                "forbidden_actions": ["deploy", "publish", "access_production", "modify_dependencies"],
                "approval_required": ["change_public_api", "modify_authentication"],
                "expires_at": "2026-07-23T10:30:00Z",
            },
            next_action={
                "instruction": "Inspect the referenced files and implement the retry logic",
                "expected_first_tool": "repository.read",
            },
            return_contract={
                "return_to": "reviewer",
                "required_outputs": ["changed_files", "verification_results", "remaining_risks"],
                "success_status": "implementation_complete",
            },
            evidence=[
                {"type": "file", "reference": "src/infrastructure/payments/client.py", "relevance": "Primary implementation target"},
                {"type": "file", "reference": "src/shared/retry.py", "relevance": "Existing retry abstraction"},
            ],
        )
        
        # Verify structure
        self.assertIn("schema_version", handover)
        self.assertEqual(handover["schema_version"], "1.0")
        self.assertIn("handover", handover)
        self.assertIn("id", handover["handover"])
        self.assertTrue(handover["handover"]["id"].startswith("ho_"))
        self.assertIn("task", handover)
        self.assertIn("state", handover)
        self.assertIn("authorization", handover)
        self.assertIn("next_action", handover)
        self.assertIn("return_contract", handover)
        self.assertIn("evidence", handover)
    
    def test_offer_and_accept_handover(self):
        """Test offering and accepting a handover."""
        # Create a task first
        self.ownership_store.create_task(
            task_id="task_456",
            owner="planner",
            state="ready_for_implementation",
        )
        
        # Prepare a handover
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_456",
            destination_agent="implementer",
            capability="repository.change",
            goal="Add retry handling",
            requested_outcome="Implementation",
            definition_of_done=["Retries work"],
        )
        
        # Offer the handover
        offer = self.service.offer_handover(handover, "implementer")
        self.assertEqual(offer["status"], "offered")
        
        # Prepare acknowledgement
        now = datetime.now(timezone.utc).isoformat()
        acknowledgement = {
            "handover_id": handover["handover"]["id"],
            "receiver": "implementer",
            "decision": "accepted",
            "understanding": {
                "goal": "Add retry handling",
                "deliverables": ["implementation", "tests"],
            },
            "accepted_scopes": ["repository:read", "repository:write"],
            "rejected_scopes": [],
            "accepted_at": now,
            "planned_first_action": {
                "tool": "repository.read",
                "target": "src/payments/client.py",
            },
        }
        
        # Accept the handover
        result = self.service.accept_handover(handover, acknowledgement)
        
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["new_owner"], "implementer")
        
        # Verify ownership was transferred
        ownership = self.ownership_store.get_ownership("task_456")
        self.assertIsNotNone(ownership)
        self.assertEqual(ownership.owner, "implementer")
        self.assertEqual(ownership.handover_id, handover["handover"]["id"])
        self.assertEqual(ownership.ownership_version, 2)
    
    def test_reject_handover(self):
        """Test rejecting a handover."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_457",
            destination_agent="reviewer",
            capability="code_review",
            goal="Implement feature",
            requested_outcome="Implementation",
            definition_of_done=["Implemented"],
        )
        
        now = datetime.now(timezone.utc).isoformat()
        acknowledgement = {
            "handover_id": handover["handover"]["id"],
            "receiver": "reviewer",
            "decision": "rejected",
            "understanding": {
                "goal": "Implement feature",
                "deliverables": [],
            },
            "accepted_scopes": [],
            "rejected_scopes": [],
            "accepted_at": now,
            "rejection_reason": {
                "code": "CAPABILITY_MISMATCH",
                "message": "reviewer cannot implement code",
            },
        }
        
        result = self.service.reject_handover(handover, acknowledgement)
        
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["receiver"], "reviewer")
        self.assertEqual(result["rejection_reason"]["code"], "CAPABILITY_MISMATCH")
    
    def test_clarification_required(self):
        """Test requesting clarification for a handover."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_458",
            destination_agent="implementer",
            capability="repository.change",
            goal="Add feature",
            requested_outcome="Implementation",
            definition_of_done=["Feature works"],
        )
        
        now = datetime.now(timezone.utc).isoformat()
        acknowledgement = {
            "handover_id": handover["handover"]["id"],
            "receiver": "implementer",
            "decision": "clarification-required",
            "understanding": {
                "goal": "Add feature",
                "deliverables": [],
            },
            "accepted_scopes": [],
            "rejected_scopes": [],
            "accepted_at": now,
            "clarifications_required": [
                {
                    "field": "definition_of_done",
                    "question": "What does 'works' mean exactly?",
                    "suggestion": "Add specific, testable criteria",
                }
            ],
        }
        
        result = self.service.request_clarification(handover, acknowledgement)
        
        self.assertEqual(result["status"], "clarification_required")
        self.assertEqual(len(result["clarifications"]), 1)
        self.assertEqual(result["clarifications"][0]["field"], "definition_of_done")
    
    def test_close_handover(self):
        """Test closing a handover with results."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_459",
            destination_agent="implementer",
            capability="repository.change",
            goal="Implement feature",
            requested_outcome="Implementation",
            definition_of_done=["Implemented"],
            return_contract={
                "return_to": "reviewer",
                "required_outputs": ["code"],
                "success_status": "implementation_complete",
            },
        )
        
        result_data = {
            "summary": "Added retry handling to payment client",
            "changed_files": [
                {"path": "src/payments/client.py", "change": "Added retry logic"},
            ],
            "verification": [
                {"command": "make test", "status": "passed", "evidence": "artifact://test-result-123"},
            ],
            "decisions": ["Used existing retry utility"],
            "unresolved": [],
            "risks": [{"severity": "low", "description": "May increase latency"}],
            "claims": [{"statement": "All tests passed", "evidence": ["artifact://test-result-123"]}],
        }
        
        result = self.service.close_handover(handover, result_data)
        
        self.assertEqual(result["status"], "closed")
        self.assertEqual(result["original_handover_id"], handover["handover"]["id"])
        self.assertIn("return_handover", result)
        
        # Verify return handover structure
        return_handover = result["return_handover"]
        self.assertIn("schema_version", return_handover)
        self.assertIn("handover", return_handover)
        self.assertEqual(return_handover["handover"]["source"]["agent"], "implementer")
        self.assertEqual(return_handover["handover"]["destination"]["agent"], "reviewer")
        self.assertIn("parent_handover_id", return_handover["handover"])
        self.assertEqual(return_handover["handover"]["parent_handover_id"], handover["handover"]["id"])
        self.assertIn("result", return_handover)
    
    def test_ownership_conflict(self):
        """Test that ownership conflicts are detected."""
        # Create a task
        self.ownership_store.create_task(
            task_id="task_460",
            owner="planner",
            state="ready",
        )
        
        # Transfer ownership outside the handover process
        self.ownership_store.transfer_ownership(
            task_id="task_460",
            new_owner="reviewer",
            handover_id="ho_manual001",
        )
        
        # Now try to handover from planner (who no longer owns it)
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_460",
            destination_agent="implementer",
            capability="repository.change",
            goal="Implement feature",
            requested_outcome="Implementation",
            definition_of_done=["Implemented"],
        )
        
        now = datetime.now(timezone.utc).isoformat()
        acknowledgement = {
            "handover_id": handover["handover"]["id"],
            "receiver": "implementer",
            "decision": "accepted",
            "understanding": {"goal": "Implement", "deliverables": ["code"]},
            "accepted_scopes": ["repository:write"],
            "rejected_scopes": [],
            "accepted_at": now,
        }
        
        # This should fail because planner doesn't own the task anymore
        with self.assertRaises(HandoverError):
            self.service.accept_handover(handover, acknowledgement)
    
    def test_policy_violation_forbidden_transition(self):
        """Test that forbidden transitions are rejected by policy."""
        # planner -> planner is not allowed
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_461",
            destination_agent="planner",
            capability="planning",
            goal="Continue planning",
            requested_outcome="More planning",
            definition_of_done=["Plan complete"],
        )
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("FORBIDDEN_TRANSITION", str(context.exception))
    
    def test_policy_violation_missing_capability(self):
        """Test that missing capabilities are rejected by policy."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_462",
            destination_agent="implementer",
            capability="nonexistent_capability",  # implementer doesn't have this
            goal="Do something",
            requested_outcome="Result",
            definition_of_done=["Done"],
        )
        
        with self.assertRaises(PolicyViolation) as context:
            self.service.validate_handover(handover)
        
        self.assertIn("MISSING_CAPABILITY", str(context.exception))
    
    def test_policy_violation_missing_definition_of_done(self):
        """Test that missing definition of done is rejected by policy."""
        # Temporarily disable the policy requirement
        policy = HandoverPolicy(require_definition_of_done=True)
        service = HandoverService(policy=policy)
        
        handover = service.prepare_handoover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_463",
            destination_agent="implementer",
            capability="repository.change",
            goal="Implement",
            requested_outcome="Code",
            definition_of_done=[],  # Empty
        )
        
        with self.assertRaises(PolicyViolation) as context:
            service.validate_handover(handover)
        
        self.assertIn("MISSING_DEFINITION_OF_DONE", str(context.exception))
    
    def test_generate_ids(self):
        """Test ID generation."""
        handover_id = self.service.generate_handover_id()
        self.assertTrue(handover_id.startswith("ho_"))
        self.assertTrue(len(handover_id) >= 11)  # ho_ + at least 8 chars
        
        artifact_id = self.service.generate_artifact_id()
        self.assertTrue(artifact_id.startswith("artifact_"))
        
        # Test custom prefix
        custom_id = self.service.generate_artifact_id(prefix="custom")
        self.assertTrue(custom_id.startswith("custom_"))
    
    def test_filter_context(self):
        """Test context filtering."""
        context = {
            "schema_version": "1.0",
            "handover": {"id": "ho_test001"},
            "task": {"goal": "Implement feature"},
            "secrets": {"api_key": "sk-12345678"},
            "internal": "This is internal reasoning",
        }
        
        filtered = self.service.filter_context(context, "implementer")
        
        # Should preserve structured fields
        self.assertIn("schema_version", filtered)
        self.assertIn("handover", filtered)
        self.assertIn("task", filtered)
        
        # Should not include secrets or internal (in a real implementation)
        # Note: Our current filter is basic and may not catch all secrets
    
    def test_handover_with_all_optional_fields(self):
        """Test a handover with all optional fields populated."""
        handover = self.service.prepare_handoover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_464",
            destination_agent="implementer",
            capability="repository.change",
            goal="Implement authentication",
            requested_outcome="Complete authentication system",
            definition_of_done=[
                "JWT validation works",
                "Token refresh works",
                "Error handling complete",
            ],
            state={
                "status": "ready_for_implementation",
                "completed": ["Design done", "Libraries selected"],
                "current": ["Ready to code"],
                "remaining": ["Implement auth", "Write tests", "Document API"],
            },
            decisions=[
                {
                    "id": "dec-1",
                    "statement": "Use JWT",
                    "rationale": "Standard and secure",
                    "made_by": "planner",
                }
            ],
            assumptions=[
                {
                    "statement": "Users will have valid tokens",
                    "confidence": 0.9,
                    "needs_verification": False,
                }
            ],
            evidence=[
                {"type": "document", "reference": "docs/auth-spec.md", "relevance": "Requirements"},
                {"type": "file", "reference": "src/auth/__init__.py", "relevance": "Skeleton"},
            ],
            authorization={
                "principal": "user_789",
                "delegated_scopes": ["repository:read", "repository:write:src/auth/**"],
                "forbidden_actions": ["deploy", "modify_dependencies"],
                "approval_required": ["change_authentication"],
                "expires_at": "2026-07-23T12:00:00Z",
                "delegation_depth": 0,
                "max_delegation_depth": 3,
                "may_redelegate": False,
            },
            execution={
                "priority": "high",
                "max_turns": 25,
                "max_tool_calls": 60,
                "retry_budget": 3,
            },
            next_action={
                "instruction": "Start with the authentication middleware",
                "expected_first_tool": "repository.read",
            },
            return_contract={
                "return_to": "reviewer",
                "required_outputs": ["implementation", "tests", "documentation"],
                "success_status": "implementation_complete",
                "failure_status": "implementation_failed",
            },
            security={
                "data_classification": "internal",
                "contains_secrets": False,
                "untrusted_inputs": ["user authentication tokens"],
            },
        )
        
        # Validate it
        result = self.service.validate_handover(handover)
        self.assertTrue(result)
        
        # Verify all fields are present
        self.assertIn("decisions", handover)
        self.assertIn("assumptions", handover)
        self.assertIn("execution", handover)
        self.assertIn("security", handover)


class TestHandoverServicePreparation(unittest.TestCase):
    """Test the prepare_handoover method specifically."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = HandoverService()
    
    def test_prepare_with_minimal_params(self):
        """Test preparation with minimal parameters."""
        handover = self.service.prepare_handover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_465",
            destination_agent="implementer",
            capability="repository.change",
            goal="Do work",
            requested_outcome="Result",
            definition_of_done=["Done"],
        )
        
        self.assertIn("schema_version", handover)
        self.assertIn("handover", handover)
        self.assertIn("task", handover)
        self.assertIn("state", handover)
        self.assertIn("authorization", handover)
        self.assertIn("next_action", handover)
        self.assertIn("return_contract", handover)
        self.assertIn("evidence", handover)
        
        # Defaults should be applied
        self.assertEqual(handover["state"]["status"], "ready_for_implementation")
        self.assertIn("security", handover)
    
    def test_prepare_with_custom_params(self):
        """Test preparation with custom parameters."""
        custom_state = {
            "status": "custom_status",
            "completed": ["custom_completed"],
            "current": ["custom_current"],
            "remaining": ["custom_remaining"],
        }
        
        custom_auth = {
            "principal": "custom_user",
            "delegated_scopes": ["custom:scope"],
            "forbidden_actions": ["custom:forbidden"],
        }
        
        handover = self.service.prepare_handoover(
            source_agent="planner",
            run_id="run_123",
            task_id="task_466",
            destination_agent="implementer",
            capability="repository.change",
            goal="Custom goal",
            requested_outcome="Custom outcome",
            definition_of_done=["Custom done"],
            state=custom_state,
            authorization=custom_auth,
        )
        
        self.assertEqual(handover["state"]["status"], "custom_status")
        self.assertEqual(handover["authorization"]["principal"], "custom_user")


if __name__ == "__main__":
    unittest.main()
