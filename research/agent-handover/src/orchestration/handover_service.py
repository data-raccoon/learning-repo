"""
Handover Service

Core service for managing agent-to-agent handovers. Provides the main
interface for preparing, validating, offering, accepting, and executing handovers.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jsonschema

from .handover_policy import HandoverPolicy, PolicyViolation
from .ownership_store import OwnershipStore, OwnershipConflict
from .context_filter import ContextFilter


class HandoverError(Exception):
    """Base exception for handover errors."""
    pass


class SchemaValidationError(HandoverError):
    """Raised when handover data fails schema validation."""
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(f"Schema validation failed: {errors}")


class HandoverNotFoundError(HandoverError):
    """Raised when a handover is not found."""
    pass


class HandoverStateError(HandoverError):
    """Raised when handover is in an invalid state for the operation."""
    pass


class HandoverService:
    """
    Service for managing the complete handover lifecycle.
    
    The service coordinates:
    - Handover preparation and validation
    - Policy enforcement
    - Ownership transfer
    - Context filtering
    - State management
    """
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(
        self,
        policy: Optional[HandoverPolicy] = None,
        ownership_store: Optional[OwnershipStore] = None,
        context_filter: Optional[ContextFilter] = None,
    ):
        """
        Initialize the handover service.
        
        Args:
            policy: Policy enforcer for handover rules
            ownership_store: Store for managing task ownership
            context_filter: Filter for context selection
        """
        self.policy = policy or HandoverPolicy()
        self.ownership_store = ownership_store or OwnershipStore()
        self.context_filter = context_filter or ContextFilter()
        
        # Load schemas
        self._handover_schema = self._load_schema("handover.schema.json")
        self._handover_ack_schema = self._load_schema("handover-ack.schema.json")
        self._artifact_schema = self._load_schema("artifact.schema.json")
    
    def _load_schema(self, filename: str) -> Dict[str, Any]:
        """Load a JSON schema from the schemas directory."""
        import os
        import json
        
        # Get the directory where this file is located
        module_dir = os.path.dirname(os.path.abspath(__file__))
        schemas_dir = os.path.join(module_dir, "..", "..", "schemas")
        schema_path = os.path.join(schemas_dir, filename)
        
        if not os.path.exists(schema_path):
            # Try relative to the module root
            schemas_dir = os.path.join(module_dir, "..", "..", "..", "schemas")
            schema_path = os.path.join(schemas_dir, filename)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_handover_id(self) -> str:
        """Generate a unique handover ID."""
        return f"ho_{uuid.uuid4().hex[:16].upper()}"
    
    def generate_artifact_id(self, prefix: str = "artifact") -> str:
        """Generate a unique artifact ID."""
        return f"{prefix}_{uuid.uuid4().hex[:16]}"
    
    def validate_handover(self, handover: Dict[str, Any]) -> bool:
        """
        Validate a handover against the schema and policy.
        
        Args:
            handover: Handover data to validate
            
        Returns:
            True if valid
            
        Raises:
            SchemaValidationError: If schema validation fails
            PolicyViolation: If policy is violated
        """
        # Validate schema
        try:
            jsonschema.validate(instance=handover, schema=self._handover_schema)
        except jsonschema.ValidationError as e:
            raise SchemaValidationError([str(e)])
        
        # Validate policy
        self.policy.validate_handover(handover)
        
        return True
    
    def validate_acknowledgement(self, ack: Dict[str, Any]) -> bool:
        """
        Validate a handover acknowledgement.
        
        Args:
            ack: Acknowledgement data to validate
            
        Returns:
            True if valid
            
        Raises:
            SchemaValidationError: If schema validation fails
        """
        try:
            jsonschema.validate(instance=ack, schema=self._handover_ack_schema)
        except jsonschema.ValidationError as e:
            raise SchemaValidationError([str(e)])
        return True
    
    def validate_artifact(self, artifact: Dict[str, Any]) -> bool:
        """
        Validate an artifact.
        
        Args:
            artifact: Artifact data to validate
            
        Returns:
            True if valid
            
        Raises:
            SchemaValidationError: If schema validation fails
        """
        try:
            jsonschema.validate(instance=artifact, schema=self._artifact_schema)
        except jsonschema.ValidationError as e:
            raise SchemaValidationError([str(e)])
        return True
    
    def prepare_handover(
        self,
        source_agent: str,
        run_id: str,
        task_id: str,
        destination_agent: str,
        capability: str,
        goal: str,
        requested_outcome: str,
        definition_of_done: list,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Prepare a new handover packet.
        
        Args:
            source_agent: Name of the source agent
            run_id: Run identifier
            task_id: Task identifier
            destination_agent: Name of the destination agent
            capability: Required capability
            goal: Task goal
            requested_outcome: Expected outcome
            definition_of_done: List of completion criteria
            **kwargs: Additional optional fields
            
        Returns:
            Prepared handover dict
        """
        handover_id = self.generate_handover_id()
        now = datetime.now(timezone.utc).isoformat()
        
        handover = {
            "schema_version": self.SCHEMA_VERSION,
            "handover": {
                "id": handover_id,
                "created_at": now,
                "source": {
                    "agent": source_agent,
                    "run_id": run_id,
                    "task_id": task_id,
                },
                "destination": {
                    "agent": destination_agent,
                    "capability": capability,
                },
                "reason": kwargs.get("reason", {
                    "code": "SPECIALIST_REQUIRED",
                    "summary": "Task requires specialist agent.",
                }),
            },
            "task": {
                "goal": goal,
                "requested_outcome": requested_outcome,
                "definition_of_done": definition_of_done,
            },
            "state": kwargs.get("state", {
                "status": "ready_for_implementation",
                "completed": [],
                "current": [],
                "remaining": [],
            }),
            "authorization": kwargs.get("authorization", {
                "principal": "user_default",
                "delegated_scopes": ["repository:read"],
                "forbidden_actions": ["deploy", "publish"],
            }),
            "next_action": kwargs.get("next_action", {
                "instruction": "Please review the task and begin work.",
                "expected_first_tool": "repository.read",
            }),
            "return_contract": kwargs.get("return_contract", {
                "return_to": source_agent,
                "required_outputs": ["changed_files", "verification_results"],
                "success_status": "implementation_complete",
            }),
            "evidence": kwargs.get("evidence", []),
        }
        
        # Apply defaults for optional fields
        if "decisions" not in kwargs:
            handover["decisions"] = []
        if "assumptions" not in kwargs:
            handover["assumptions"] = []
        if "artifacts" not in kwargs:
            handover["artifacts"] = []
        if "security" not in kwargs:
            handover["security"] = {
                "data_classification": "internal",
                "contains_secrets": False,
            }
        
        return handover
    
    def offer_handover(
        self,
        handover: Dict[str, Any],
        receiver_agent: str,
    ) -> Dict[str, Any]:
        """
        Offer a handover to a receiver agent.
        
        This validates the handover and sends it to the receiver for evaluation.
        
        Args:
            handover: The handover to offer
            receiver_agent: Name of the receiver agent
            
        Returns:
            Offer response with handover and validation results
            
        Raises:
            HandoverError: If offer cannot be made
        """
        # Validate the handover
        self.validate_handover(handover)
        
        # Check destination matches
        if handover["handover"]["destination"]["agent"] != receiver_agent:
            raise HandoverError(
                f"Receiver {receiver_agent} does not match "
                f"destination {handover['handover']['destination']['agent']}"
            )
        
        # Check policy allows this handover
        self.policy.validate_handover(handover)
        
        return {
            "status": "offered",
            "handover": handover,
            "receiver": receiver_agent,
            "offered_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def accept_handover(
        self,
        handover: Dict[str, Any],
        acknowledgement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Accept a handover and transfer ownership.
        
        This performs the atomic ownership transfer.
        
        Args:
            handover: The original handover
            acknowledgement: The receiver's acknowledgement
            
        Returns:
            Acceptance result with new ownership state
            
        Raises:
            HandoverError: If acceptance fails
        """
        # Validate acknowledgement
        self.validate_acknowledgement(acknowledgement)
        
        # Check decision is acceptance
        if acknowledgement["decision"] != "accepted":
            raise HandoverStateError(
                f"Cannot accept with decision: {acknowledgement['decision']}"
            )
        
        handover_id = handover["handover"]["id"]
        task_id = handover["handover"]["source"]["task_id"]
        receiver = acknowledgement["receiver"]
        
        # Transfer ownership atomically
        try:
            self.ownership_store.transfer_ownership(
                task_id=task_id,
                new_owner=receiver,
                handover_id=handover_id,
            )
        except OwnershipConflict as e:
            raise HandoverError(f"Ownership conflict: {e}")
        
        return {
            "status": "accepted",
            "handover_id": handover_id,
            "task_id": task_id,
            "new_owner": receiver,
            "accepted_at": acknowledgement["accepted_at"],
            "ownership_version": self.ownership_store.get_ownership_version(task_id),
        }
    
    def reject_handover(
        self,
        handover: Dict[str, Any],
        acknowledgement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Reject a handover.
        
        Args:
            handover: The original handover
            acknowledgement: The receiver's acknowledgement
            
        Returns:
            Rejection result
        """
        self.validate_acknowledgement(acknowledgement)
        
        return {
            "status": "rejected",
            "handover_id": handover["handover"]["id"],
            "receiver": acknowledgement["receiver"],
            "rejection_reason": acknowledgement.get("rejection_reason", {}),
            "rejected_at": acknowledgement["accepted_at"],
        }
    
    def request_clarification(
        self,
        handover: Dict[str, Any],
        acknowledgement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Request clarification for a handover.
        
        Args:
            handover: The original handover
            acknowledgement: The receiver's acknowledgement
            
        Returns:
            Clarification request result
        """
        self.validate_acknowledgement(acknowledgement)
        
        return {
            "status": "clarification_required",
            "handover_id": handover["handover"]["id"],
            "receiver": acknowledgement["receiver"],
            "clarifications": acknowledgement.get("clarifications_required", []),
            "requested_at": acknowledgement["accepted_at"],
        }
    
    def close_handover(
        self,
        handover: Dict[str, Any],
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Close a handover with results.
        
        This is used for return handovers when work is complete.
        
        Args:
            handover: The original handover
            result: The result data
            
        Returns:
            Closure result
        """
        # Create return handover
        return_handover = {
            "schema_version": self.SCHEMA_VERSION,
            "handover": {
                "id": self.generate_handover_id(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "parent_handover_id": handover["handover"]["id"],
                "source": {
                    "agent": handover["handover"]["destination"]["agent"],
                    "run_id": "",
                    "task_id": handover["handover"]["source"]["task_id"],
                },
                "destination": {
                    "agent": handover["return_contract"]["return_to"],
                    "capability": "",
                },
                "reason": {
                    "code": "STAGE_COMPLETE",
                    "summary": "Stage complete, returning results.",
                },
            },
            "task": {
                "goal": f"Review results from {handover['handover']['destination']['agent']}",
                "requested_outcome": "Validation and next steps",
                "definition_of_done": ["Review complete"],
            },
            "state": {
                "status": "implementation_complete",
                "completed": handover.get("state", {}).get("completed", []),
                "current": ["Work complete, awaiting review"],
                "remaining": handover.get("state", {}).get("remaining", []),
            },
            "result": result,
            "authorization": handover["authorization"],
            "next_action": {
                "instruction": "Review the delivered results and provide feedback.",
                "expected_first_tool": "repository.read",
            },
            "return_contract": {
                "return_to": handover["handover"]["source"]["agent"],
                "required_outputs": ["review_result"],
                "success_status": "review_complete",
            },
            "evidence": handover.get("evidence", []),
        }
        
        # Validate return handover
        self.validate_handover(return_handover)
        
        return {
            "status": "closed",
            "original_handover_id": handover["handover"]["id"],
            "return_handover": return_handover,
            "closed_at": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_handover_status(self, handover_id: str) -> Dict[str, Any]:
        """
        Get the status of a handover.
        
        Args:
            handover_id: The handover ID to check
            
        Returns:
            Status information
            
        Raises:
            HandoverNotFoundError: If handover not found
        """
        # In a real implementation, this would query a persistent store
        # For now, return a placeholder
        return {
            "handover_id": handover_id,
            "status": "unknown",
            "message": "Status tracking not yet implemented",
        }
    
    def filter_context(
        self,
        context: Dict[str, Any],
        target_agent: str,
    ) -> Dict[str, Any]:
        """
        Filter context for a target agent.
        
        Args:
            context: The context to filter
            target_agent: The agent receiving the context
            
        Returns:
            Filtered context
        """
        return self.context_filter.filter(context, target_agent)
