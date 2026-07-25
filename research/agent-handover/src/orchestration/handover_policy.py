"""
Handover Policy

Policy enforcement for agent handovers. Validates handover requests against
configured policies to ensure safety, security, and correctness.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


class PolicyViolation(Exception):
    """Raised when a handover violates policy."""
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(f"{code}: {message}")


@dataclass
class HandoverPolicy:
    """
    Policy configuration for handover validation.
    
    This class defines and enforces policies for agent handovers including:
    - Allowed agent transitions
    - Required fields
    - Authorization constraints
    - Loop detection
    - Context filtering rules
    """
    
    # Default policy configuration
    prefer_delegation_over_transfer: bool = True
    require_structured_envelope: bool = True
    require_receiver_acknowledgement: bool = True
    transfer_full_transcript: bool = False
    require_definition_of_done: bool = True
    require_evidence_for_completion_claims: bool = True
    authorization_mode: str = "least-privilege"
    atomic_ownership_transfer: bool = True
    max_handover_depth: int = 3
    reject_cycles: bool = True
    handover_timeout_seconds: int = 30
    require_human_approval_for_high_risk_actions: bool = True
    persist_handover_receipts: bool = True
    
    # Allowed transitions: source_agent -> [allowed_destination_agents]
    allowed_transitions: Dict[str, Set[str]] = field(default_factory=lambda: {
        "planner": {"implementer", "reviewer", "human"},
        "implementer": {"reviewer", "tester", "human"},
        "reviewer": {"planner", "implementer", "human"},
        "tester": {"reviewer", "human"},
        "human": set(),  # Human doesn't handover to agents
        "*": {"human"},  # Any agent can escalate to human
    })
    
    # High-risk actions requiring approval
    high_risk_actions: Set[str] = field(default_factory=lambda: {
        "deploy",
        "publish",
        "access_production",
        "modify_dependencies",
        "change_public_api",
        "modify_authentication",
        "delete_data",
        "execute_arbitrary_code",
    })
    
    # Required capabilities by agent
    agent_capabilities: Dict[str, Set[str]] = field(default_factory=lambda: {
        "planner": {"planning", "analysis", "design"},
        "implementer": {"repository.change", "code_generation", "testing"},
        "reviewer": {"code_review", "quality_assurance"},
        "tester": {"testing", "verification"},
        "human": {"*"},  # Human can do anything
    })
    
    # Forbidden delegation patterns
    forbidden_delegations: Set[str] = field(default_factory=lambda: {
        "human->*",  # Human to any agent (use explicit transitions)
    })
    
    def validate_handover(self, handover: Dict[str, Any]) -> None:
        """
        Validate a handover against all policy rules.
        
        Args:
            handover: The handover to validate
            
        Raises:
            PolicyViolation: If any policy rule is violated
        """
        # Check schema version
        self._validate_schema_version(handover)
        
        # Check required fields
        self._validate_required_fields(handover)
        
        # Check source and destination
        self._validate_source_destination(handover)
        
        # Check goal and definition of done
        self._validate_goal_and_done(handover)
        
        # Check authorization
        self._validate_authorization(handover)
        
        # Check no forbidden data
        self._validate_no_forbidden_data(handover)
        
        # Check hop and cycle limits
        self._validate_delegation_limits(handover)
        
        # Check task ownership
        self._validate_task_ownership(handover)
        
        # Check human approval requirements
        self._validate_human_approval(handover)
    
    def _validate_schema_version(self, handover: Dict[str, Any]) -> None:
        """Validate schema version is supported."""
        version = handover.get("schema_version", "1.0")
        if not re.match(r"^[0-9]+\.[0-9]+$", version):
            raise PolicyViolation(
                "INVALID_SCHEMA_VERSION",
                f"Schema version '{version}' is not valid",
                "Version must match pattern ^[0-9]+\\.[0-9]+$"
            )
        
        # For now, we only support 1.0
        major = int(version.split(".")[0])
        if major != 1:
            raise PolicyViolation(
                "UNSUPPORTED_SCHEMA_VERSION",
                f"Schema version {version} is not supported",
                "Only version 1.x is currently supported"
            )
    
    def _validate_required_fields(self, handover: Dict[str, Any]) -> None:
        """Validate all required fields are present."""
        required_fields = [
            "schema_version",
            "handover",
            "task",
            "state",
            "authorization",
            "next_action",
            "return_contract",
        ]
        
        missing = [f for f in required_fields if f not in handover]
        if missing:
            raise PolicyViolation(
                "MISSING_REQUIRED_FIELDS",
                f"Missing required fields: {', '.join(missing)}",
            )
        
        # Check handover subfields
        handover_data = handover.get("handover", {})
        handover_required = ["id", "created_at", "source", "destination", "reason"]
        missing_handover = [f for f in handover_required if f not in handover_data]
        if missing_handover:
            raise PolicyViolation(
                "MISSING_HANDOVER_FIELDS",
                f"Missing handover fields: {', '.join(missing_handover)}",
            )
        
        # Check task subfields
        task = handover.get("task", {})
        task_required = ["goal", "requested_outcome", "definition_of_done"]
        missing_task = [f for f in task_required if f not in task]
        if missing_task:
            raise PolicyViolation(
                "MISSING_TASK_FIELDS",
                f"Missing task fields: {', '.join(missing_task)}",
            )
        
        # Check definition of done
        if self.require_definition_of_done:
            definition = task.get("definition_of_done", [])
            if not definition:
                raise PolicyViolation(
                    "MISSING_DEFINITION_OF_DONE",
                    "Definition of done is required",
                )
    
    def _validate_source_destination(self, handover: Dict[str, Any]) -> None:
        """Validate source and destination agents."""
        handover_data = handover.get("handover", {})
        source = handover_data.get("source", {})
        destination = handover_data.get("destination", {})
        
        source_agent = source.get("agent", "")
        dest_agent = destination.get("agent", "")
        
        # Check both are specified
        if not source_agent:
            raise PolicyViolation(
                "MISSING_SOURCE_AGENT",
                "Source agent is required",
            )
        if not dest_agent:
            raise PolicyViolation(
                "MISSING_DESTINATION_AGENT",
                "Destination agent is required",
            )
        
        # Check transition is allowed
        if not self._is_transition_allowed(source_agent, dest_agent):
            raise PolicyViolation(
                "FORBIDDEN_TRANSITION",
                f"Transition from {source_agent} to {dest_agent} is not allowed",
                f"Check allowed_transitions policy"
            )
        
        # Check destination capability
        required_capability = destination.get("capability", "")
        if required_capability:
            if not self._has_capability(dest_agent, required_capability):
                raise PolicyViolation(
                    "MISSING_CAPABILITY",
                    f"Destination agent {dest_agent} does not have required capability: {required_capability}",
                )
    
    def _is_transition_allowed(self, source: str, destination: str) -> bool:
        """Check if a transition from source to destination is allowed."""
        # Check direct mapping
        if source in self.allowed_transitions:
            if destination in self.allowed_transitions[source]:
                return True
        
        # Check wildcard
        if "*" in self.allowed_transitions:
            if destination in self.allowed_transitions["*"]:
                return True
        
        # Check destination wildcard
        for src, dests in self.allowed_transitions.items():
            if src == source or src == "*":
                if "*" in dests:
                    return True
                if destination in dests:
                    return True
        
        return False
    
    def _has_capability(self, agent: str, capability: str) -> bool:
        """Check if an agent has a capability."""
        if agent not in self.agent_capabilities:
            return False
        
        agent_caps = self.agent_capabilities[agent]
        
        # Check direct match
        if capability in agent_caps:
            return True
        
        # Check wildcard
        if "*" in agent_caps:
            return True
        
        return False
    
    def _validate_goal_and_done(self, handover: Dict[str, Any]) -> None:
        """Validate goal and definition of done."""
        task = handover.get("task", {})
        
        goal = task.get("goal", "")
        if not goal or len(goal.strip()) < 1:
            raise PolicyViolation(
                "INVALID_GOAL",
                "Goal must be a non-empty string",
            )
        
        if self.require_definition_of_done:
            definition = task.get("definition_of_done", [])
            if not definition:
                raise PolicyViolation(
                    "MISSING_DEFINITION_OF_DONE",
                    "Definition of done is required",
                )
            
            # Check each criterion is non-empty
            for i, criterion in enumerate(definition):
                if not criterion or len(criterion.strip()) < 1:
                    raise PolicyViolation(
                        "INVALID_DEFINITION_OF_DONE",
                        f"Definition of done criterion {i} is empty",
                    )
    
    def _validate_authorization(self, handover: Dict[str, Any]) -> None:
        """Validate authorization section."""
        auth = handover.get("authorization", {})
        
        # Check required fields
        if "principal" not in auth:
            raise PolicyViolation(
                "MISSING_PRINCIPAL",
                "Principal is required in authorization",
            )
        
        if "delegated_scopes" not in auth:
            raise PolicyViolation(
                "MISSING_DELEGATED_SCOPES",
                "Delegated scopes are required in authorization",
            )
        
        if "forbidden_actions" not in auth:
            raise PolicyViolation(
                "MISSING_FORBIDDEN_ACTIONS",
                "Forbidden actions are required in authorization",
            )
        
        # Check scopes are not empty
        scopes = auth.get("delegated_scopes", [])
        if not scopes:
            raise PolicyViolation(
                "EMPTY_DELEGATED_SCOPES",
                "At least one delegated scope is required",
            )
        
        # Check for excessive permissions in least-privilege mode
        if self.authorization_mode == "least-privilege":
            self._check_least_privilege(auth)
        
        # Check expiration
        expires_at = auth.get("expires_at")
        if expires_at:
            from datetime import datetime, timezone
            try:
                expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expires < datetime.now(timezone.utc):
                    raise PolicyViolation(
                        "EXPIRED_AUTHORIZATION",
                        "Authorization has already expired",
                    )
            except ValueError:
                raise PolicyViolation(
                    "INVALID_EXPIRATION",
                    f"Invalid expiration format: {expires_at}",
                )
        
        # Check delegation depth
        delegation_depth = auth.get("delegation_depth", 0)
        max_depth = auth.get("max_delegation_depth", self.max_handover_depth)
        if delegation_depth >= max_depth:
            raise PolicyViolation(
                "DELEGATION_DEPTH_EXCEEDED",
                f"Delegation depth {delegation_depth} exceeds maximum {max_depth}",
            )
    
    def _check_least_privilege(self, auth: Dict[str, Any]) -> None:
        """Check for excessive permissions in least-privilege mode."""
        scopes = auth.get("delegated_scopes", [])
        
        # Check for overly broad scopes
        broad_patterns = [
            r"^\*$",
            r"^.*:.*$",
            r"^repository:.*$",
            r"^\w+:\*$",
        ]
        
        for scope in scopes:
            for pattern in broad_patterns:
                if re.match(pattern, scope):
                    raise PolicyViolation(
                        "EXCESSIVE_PERMISSIONS",
                        f"Scope '{scope}' is too broad for least-privilege mode",
                    )
    
    def _validate_no_forbidden_data(self, handover: Dict[str, Any]) -> None:
        """Validate that no forbidden data is included."""
        # This is a placeholder - in a real implementation, we would
        # scan the handover for secrets, PII, etc.
        
        # Check security section
        security = handover.get("security", {})
        contains_secrets = security.get("contains_secrets", False)
        
        if contains_secrets:
            raise PolicyViolation(
                "FORBIDDEN_SECRETS",
                "Handover contains secrets",
                "Remove all secrets before sending handover"
            )
        
        # In a real implementation, we would also:
        # - Scan for API keys, tokens, passwords
        # - Check for PII (emails, phone numbers, etc.)
        # - Validate against DLP policies
    
    def _validate_delegation_limits(self, handover: Dict[str, Any]) -> None:
        """Validate delegation depth and loop detection."""
        handover_data = handover.get("handover", {})
        parent_id = handover_data.get("parent_handover_id")
        
        # Track the chain (in a real implementation, this would query a store)
        # For now, we just check the delegation depth in authorization
        auth = handover.get("authorization", {})
        delegation_depth = auth.get("delegation_depth", 0)
        
        if delegation_depth >= self.max_handover_depth:
            raise PolicyViolation(
                "MAX_HANDOVER_DEPTH_EXCEEDED",
                f"Delegation depth {delegation_depth} exceeds maximum {self.max_handover_depth}",
            )
        
        # Loop detection would trace parent_handover_id chain
        # This is a simplified check
        if self.reject_cycles:
            # In a real implementation, we would trace the chain
            # and detect if we're back to a previous agent
            pass
    
    def _validate_task_ownership(self, handover: Dict[str, Any]) -> None:
        """Validate task ownership."""
        # In a real implementation, this would query the ownership store
        # to verify the source agent still owns the task
        
        # For now, we assume this is handled by the service layer
        pass
    
    def _validate_human_approval(self, handover: Dict[str, Any]) -> None:
        """Validate human approval requirements."""
        if not self.require_human_approval_for_high_risk_actions:
            return
        
        auth = handover.get("authorization", {})
        approval_required = auth.get("approval_required", [])
        
        # Check if any high-risk actions are in delegated scopes
        delegated_scopes = auth.get("delegated_scopes", [])
        
        for scope in delegated_scopes:
            for high_risk in self.high_risk_actions:
                if high_risk in scope:
                    if high_risk not in approval_required:
                        raise PolicyViolation(
                            "MISSING_HUMAN_APPROVAL",
                            f"High-risk action '{high_risk}' requires human approval",
                            f"Add '{high_risk}' to approval_required"
                        )
    
    def get_allowed_destinations(self, source_agent: str) -> Set[str]:
        """Get the set of allowed destination agents for a source."""
        if source_agent in self.allowed_transitions:
            return self.allowed_transitions[source_agent].copy()
        if "*" in self.allowed_transitions:
            return self.allowed_transitions["*"].copy()
        return set()
    
    def is_high_risk(self, action: str) -> bool:
        """Check if an action is high-risk."""
        return action in self.high_risk_actions
    
    def get_capabilities(self, agent: str) -> Set[str]:
        """Get the capabilities of an agent."""
        return self.agent_capabilities.get(agent, set())
