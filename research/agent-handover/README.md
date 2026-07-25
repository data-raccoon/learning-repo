# Agent Handover Implementation

This directory contains the implementation of the agent handover protocol as specified in the research document `research/agent-handover.md`.

## Structure

```
agent-handover/
├── docs/
│   └── agent-handovers.md          # Complete documentation of the handover protocol
│
├── schemas/
│   ├── handover.schema.json        # JSON Schema for handover envelopes
│   ├── handover-ack.schema.json    # JSON Schema for handover acknowledgements
│   └── artifact.schema.json        # JSON Schema for artifacts
│
├── src/orchestration/
│   ├── __init__.py                 # Package initialization
│   ├── handover_service.py         # Core handover service
│   ├── handover_policy.py          # Policy enforcement
│   ├── ownership_store.py          # Ownership state management
│   └── context_filter.py           # Context filtering for handovers
│
├── prompts/
│   ├── prepare-handover.md         # Prompt template for sending agents
│   └── accept-handover.md          # Prompt template for receiving agents
│
├── evals/handovers/
│   ├── routing.jsonl               # Routing accuracy test scenarios
│   ├── context-quality.jsonl       # Context selection test scenarios
│   ├── authorization.jsonl         # Authorization test scenarios
│   └── loops.jsonl                 # Loop detection test scenarios
│
└── tests/
    ├── contract/
    │   └── test_handover_schema.py  # Schema validation tests
    ├── integration/
    │   └── test_handover_lifecycle.py # Lifecycle tests
    └── security/
        └── test_handover_authorization.py # Authorization tests
```

## Key Features

### 1. Structured Handover Envelope
The handover protocol uses structured JSON envelopes with the following key properties:
- **Typed**: Machine-readable and schema-validated
- **Minimal**: Contains relevant state, not indiscriminate history
- **Scoped**: Transfers responsibility and least-privilege authority explicitly
- **Acknowledged**: Receiver accepts or rejects before ownership changes
- **Auditable**: Decisions, artifacts, evidence and lifecycle transitions remain inspectable

### 2. Handover Lifecycle
The lifecycle follows: `Prepare -> Validate -> Offer -> Accept -> Activate -> Execute -> Close/Return`

### 3. Authorization
- Least-privilege delegation
- Explicit forbidden actions
- Resource-specific scopes
- Time-limited permissions
- Human approval for high-risk actions

### 4. Safety Features
- Schema validation for all handovers
- Policy enforcement (transitions, capabilities, authorization)
- Atomic ownership transfer (compare-and-swap)
- Loop and depth detection
- Secret and PII filtering
- Context size limits

## Python Dependencies

The implementation requires the following Python packages:
- `jsonschema` - For JSON schema validation
- Standard library: `json`, `uuid`, `datetime`, `re`, `threading`, `os`, `sys`

Install with:
```bash
pip install jsonschema
```

## Running Tests

To run the tests:

```bash
cd research/agent-handoover

# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/contract/test_handover_schema.py
python -m pytest tests/integration/test_handoover_lifecycle.py
python -m pytest tests/security/test_handover_authorization.py

# Or use unittest directly
python -m unittest discover -s tests -v
```

## Usage Example

```python
from orchestration.handover_service import HandoverService
from orchestration.ownership_store import OwnershipStore
from datetime import datetime, timezone

# Initialize services
service = HandoverService()

# Prepare a handover
handover = service.prepare_handover(
    source_agent="planner",
    run_id="run_123",
    task_id="task_456",
    destination_agent="implementer",
    capability="repository.change",
    goal="Add retry handling to payment client",
    requested_outcome="Implementation and tests",
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
        ],
        "forbidden_actions": ["deploy", "publish"],
    },
    next_action={
        "instruction": "Inspect the referenced files and implement",
        "expected_first_tool": "repository.read",
    },
    return_contract={
        "return_to": "reviewer",
        "required_outputs": ["changed_files", "verification_results"],
        "success_status": "implementation_complete",
    },
    evidence=[
        {"type": "file", "reference": "src/payments/client.py", "relevance": "Implementation target"},
    ],
)

# Validate the handover
service.validate_handover(handover)

# Create acknowledgement
acknowledgement = {
    "handover_id": handover["handover"]["id"],
    "receiver": "implementer",
    "decision": "accepted",
    "understanding": {
        "goal": "Add retry handling to payment client",
        "deliverables": ["implementation", "tests"],
    },
    "accepted_scopes": ["repository:read", "repository:write:src/infrastructure/payments/**"],
    "rejected_scopes": [],
    "accepted_at": datetime.now(timezone.utc).isoformat(),
}

# Validate acknowledgement
service.validate_acknowledgement(acknowledgement)

# Accept and transfer ownership
result = service.accept_handover(handover, acknowledgement)
```

## Implementation Notes

1. **Ownership Store**: Uses in-memory storage with threading locks. For production, replace with a persistent database.

2. **Schema Loading**: The service loads schemas from the `schemas/` directory. Ensure the files are present.

3. **ID Generation**: Uses UUID for generating unique handover and artifact IDs.

4. **Time Handling**: Uses ISO 8601 format with timezone for all timestamps.

5. **Policy Configuration**: The `HandoverPolicy` class contains configurable settings for:
   - Allowed agent transitions
   - Required fields
   - Authorization constraints
   - Loop detection
   - Context filtering rules

## Files Created

All files specified in section 8 of the research document have been created:

- ✅ `docs/agent-handovers.md` - Complete documentation
- ✅ `schemas/handover.schema.json` - Handover envelope schema
- ✅ `schemas/handover-ack.schema.json` - Acknowledgement schema
- ✅ `schemas/artifact.schema.json` - Artifact schema
- ✅ `src/orchestration/handover_service.py` - Core service
- ✅ `src/orchestration/handover_policy.py` - Policy enforcer
- ✅ `src/orchestration/ownership_store.py` - Ownership store
- ✅ `src/orchestration/context_filter.py` - Context filter
- ✅ `prompts/prepare-handover.md` - Sender prompt template
- ✅ `prompts/accept-handover.md` - Receiver prompt template
- ✅ `evals/handovers/routing.jsonl` - Routing scenarios
- ✅ `evals/handovers/context-quality.jsonl` - Context quality scenarios
- ✅ `evals/handovers/authorization.jsonl` - Authorization scenarios
- ✅ `evals/handovers/loops.jsonl` - Loop detection scenarios
- ✅ `tests/contract/test_handover_schema.py` - Schema tests
- ✅ `tests/integration/test_handover_lifecycle.py` - Lifecycle tests
- ✅ `tests/security/test_handover_authorization.py` - Authorization tests

## Next Steps

1. Install dependencies: `pip install jsonschema`
2. Run tests to verify functionality
3. Integrate with your agent framework
4. Configure policy settings as needed
5. Implement persistent storage for ownership tracking (currently in-memory)
