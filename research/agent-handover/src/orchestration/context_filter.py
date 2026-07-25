"""
Context Filter

Filters context for handover based on target agent capabilities and requirements.
Removes sensitive information, internal reasoning, and irrelevant data.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Pattern, Set


@dataclass
class ContextFilter:
    """
    Context filter for agent handovers.
    
    Filters context based on:
    - Target agent capabilities
    - Sensitivity of data
    - Relevance to the task
    - Policy rules
    
    Uses a hierarchy:
    1. Structured handover fields
    2. Referenced durable artifacts
    3. Selected source evidence
    4. Concise conversation summary
    5. Raw transcript only when specifically needed
    """
    
    # Patterns for sensitive data that should be removed
    sensitive_patterns: List[Pattern[str]] = field(default_factory=lambda: [
        re.compile(r'(?i)(api[_-]?key|apikey)', re.IGNORECASE),
        re.compile(r'(?i)(secret|password|passwd|pwd)', re.IGNORECASE),
        re.compile(r'(?i)(token|auth[_-]?token|access[_-]?token)', re.IGNORECASE),
        re.compile(r'(?i)(bearer\s+[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+)', re.IGNORECASE),
        re.compile(r'(?i)(aws[_-]?access[_-]?key[_-]?id)', re.IGNORECASE),
        re.compile(r'(?i)(aws[_-]?secret[_-]?access[_-]?key)', re.IGNORECASE),
        re.compile(r'(?i)(private[_-]?key)', re.IGNORECASE),
        re.compile(r'(?i)(ssh[_-]?key)', re.IGNORECASE),
        re.compile(r'(?i)(database[_-]?password)', re.IGNORECASE),
    ])
    
    # Patterns for PII that should be removed
    pii_patterns: List[Pattern[str]] = field(default_factory=lambda: [
        re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email
        re.compile(r'\b(\+?\d{1,3}[- \.]?)?\(?\d{3}\)?[- \.]?\d{3}[- \.]?\d{4}\b'),  # Phone
        re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # SSN
        re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b'),  # Credit card
    ])
    
    # Internal reasoning markers
    internal_reasoning_patterns: List[Pattern[str]] = field(default_factory=lambda: [
        re.compile(r'^(###|\*\*\*)\s*(Internal|Private|Reasoning|Thought|Analysis)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'<internal>.*?</internal>', re.IGNORECASE | re.DOTALL),
        re.compile(r'\[INTERNAL\].*?\[/INTERNAL\]', re.IGNORECASE | re.DOTALL),
        re.compile(r'<!--.*?-->', re.DOTALL),
    ])
    
    # Tool call patterns (to preserve structure)
    tool_call_patterns: List[Pattern[str]] = field(default_factory=lambda: [
        re.compile(r'^\[TOOL\]\s*(\w+)', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^\[TOOL_RESULT\]\s*(\w+)', re.IGNORECASE | re.MULTILINE),
    ])
    
    # Maximum context size for different agent types
    max_context_sizes: Dict[str, int] = field(default_factory=lambda: {
        "planner": 16000,
        "implementer": 32000,
        "reviewer": 24000,
        "tester": 32000,
        "human": 64000,
        "*": 16000,  # Default
    })
    
    # Fields to always include in handover
    always_include_fields: Set[str] = field(default_factory=lambda: {
        "schema_version",
        "handover",
        "task",
        "state",
        "authorization",
        "next_action",
        "return_contract",
        "evidence",
        "artifacts",
        "decisions",
        "assumptions",
    })
    
    # Fields to conditionally include
    conditional_fields: Dict[str, Callable[[Dict[str, Any]], bool]] = field(default_factory=lambda: {})
    
    def filter(
        self,
        context: Dict[str, Any],
        target_agent: str,
        include_transcript: bool = False,
    ) -> Dict[str, Any]:
        """
        Filter context for a target agent.
        
        Args:
            context: The context to filter
            target_agent: The agent receiving the context
            include_transcript: Whether to include transcript
            
        Returns:
            Filtered context
        """
        # Start with an empty context
        filtered = {}
        
        # Always include structured handover fields
        for field_name in self.always_include_fields:
            if field_name in context:
                filtered[field_name] = self._filter_field(
                    context[field_name],
                    target_agent,
                    field_name,
                )
        
        # Conditionally include fields
        for field_name, condition in self.conditional_fields.items():
            if field_name in context and condition(context):
                filtered[field_name] = self._filter_field(
                    context[field_name],
                    target_agent,
                    field_name,
                )
        
        # Handle transcript separately
        if include_transcript and "transcript" in context:
            filtered["transcript"] = self._filter_transcript(
                context["transcript"],
                target_agent,
            )
        
        # Apply size limits
        filtered = self._apply_size_limit(filtered, target_agent)
        
        return filtered
    
    def _filter_field(
        self,
        value: Any,
        target_agent: str,
        field_name: str,
    ) -> Any:
        """Filter a single field value."""
        if isinstance(value, dict):
            return {k: self._filter_field(v, target_agent, k) 
                    for k, v in value.items()}
        elif isinstance(value, list):
            return [self._filter_field(v, target_agent, field_name) 
                    for v in value]
        elif isinstance(value, str):
            return self._filter_string(value, field_name)
        else:
            return value
    
    def _filter_string(self, text: str, field_name: str) -> str:
        """Filter a string value based on field name."""
        filtered = text
        
        # Remove sensitive data
        for pattern in self.sensitive_patterns:
            filtered = pattern.sub("[REDACTED]", filtered)
        
        # Remove PII
        for pattern in self.pii_patterns:
            filtered = pattern.sub("[PII_REDACTED]", filtered)
        
        # Remove internal reasoning
        for pattern in self.internal_reasoning_patterns:
            filtered = pattern.sub("", filtered)
        
        # Preserve tool call structure
        # (In a real implementation, we'd validate tool call pairs)
        
        return filtered.strip()
    
    def _filter_transcript(
        self,
        transcript: Any,
        target_agent: str,
    ) -> Any:
        """Filter transcript data."""
        if isinstance(transcript, str):
            # Split into messages and filter each
            # This is a simplified approach
            return self._filter_string(transcript, "transcript")
        elif isinstance(transcript, list):
            return [self._filter_message(msg, target_agent) 
                    for msg in transcript]
        else:
            return transcript
    
    def _filter_message(
        self,
        message: Dict[str, Any],
        target_agent: str,
    ) -> Dict[str, Any]:
        """Filter a single message from the transcript."""
        filtered = {}
        
        # Preserve role and content
        if "role" in message:
            filtered["role"] = message["role"]
        
        if "content" in message:
            filtered["content"] = self._filter_string(message["content"], "message_content")
        
        # Handle tool calls and results
        if "tool_calls" in message:
            filtered["tool_calls"] = [
                self._filter_tool_call(tc) for tc in message["tool_calls"]
            ]
        
        if "tool_results" in message:
            filtered["tool_results"] = [
                self._filter_tool_result(tr) for tr in message["tool_results"]
            ]
        
        return filtered
    
    def _filter_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Filter a tool call."""
        filtered = {}
        
        if "id" in tool_call:
            filtered["id"] = tool_call["id"]
        if "name" in tool_call:
            filtered["name"] = tool_call["name"]
        if "arguments" in tool_call:
            # Filter sensitive data from arguments
            filtered["arguments"] = self._filter_string(
                str(tool_call["arguments"]),
                "tool_arguments"
            )
        
        return filtered
    
    def _filter_tool_result(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """Filter a tool result."""
        filtered = {}
        
        if "id" in tool_result:
            filtered["id"] = tool_result["id"]
        if "content" in tool_result:
            filtered["content"] = self._filter_string(
                str(tool_result["content"]),
                "tool_result"
            )
        if "error" in tool_result:
            filtered["error"] = self._filter_string(
                str(tool_result["error"]),
                "tool_error"
            )
        
        return filtered
    
    def _apply_size_limit(
        self,
        context: Dict[str, Any],
        target_agent: str,
    ) -> Dict[str, Any]:
        """Apply size limits to the context."""
        max_size = self.max_context_sizes.get(
            target_agent,
            self.max_context_sizes.get("*", 16000)
        )
        
        # Convert context to JSON to measure size
        import json
        json_str = json.dumps(context)
        
        if len(json_str) > max_size:
            # Truncate if too large
            # In a real implementation, we'd be smarter about what to remove
            context = self._truncate_context(context, max_size)
        
        return context
    
    def _truncate_context(
        self,
        context: Dict[str, Any],
        max_size: int,
    ) -> Dict[str, Any]:
        """Truncate context to fit within size limit."""
        # Simplified: just truncate string fields
        import json
        
        def truncate_value(value: Any, remaining: int) -> Any:
            if remaining <= 0:
                return None
            
            if isinstance(value, str):
                if len(value) > remaining:
                    return value[:remaining - 10] + "...[TRUNC]"
                return value
            elif isinstance(value, dict):
                result = {}
                for k, v in value.items():
                    key_size = len(json.dumps(k))
                    if key_size >= remaining:
                        break
                    result[k] = truncate_value(v, remaining - key_size - 2)
                    remaining -= len(json.dumps(result[k])) + key_size + 2
                return result
            elif isinstance(value, list):
                result = []
                for v in value:
                    result.append(truncate_value(v, remaining - 2))
                    remaining -= len(json.dumps(result[-1])) + 2
                return result
            else:
                return value
        
        return truncate_value(context, max_size)
    
    def remove_secrets(self, text: str) -> str:
        """Remove secrets from text."""
        filtered = text
        for pattern in self.sensitive_patterns:
            filtered = pattern.sub("[REDACTED]", filtered)
        return filtered
    
    def remove_pii(self, text: str) -> str:
        """Remove PII from text."""
        filtered = text
        for pattern in self.pii_patterns:
            filtered = pattern.sub("[PII_REDACTED]", filtered)
        return filtered
    
    def remove_internal_reasoning(self, text: str) -> str:
        """Remove internal reasoning from text."""
        filtered = text
        for pattern in self.internal_reasoning_patterns:
            filtered = pattern.sub("", filtered)
        return filtered
    
    def create_summary(
        self,
        context: Dict[str, Any],
        max_length: int = 500,
    ) -> str:
        """
        Create a concise summary of the context.
        
        Args:
            context: The context to summarize
            max_length: Maximum length of the summary
            
        Returns:
            A concise summary
        """
        parts = []
        
        # Extract key information
        handover = context.get("handover", {})
        if handover:
            parts.append(f"Handover: {handover.get('id', 'N/A')}")
        
        task = context.get("task", {})
        if task:
            parts.append(f"Goal: {task.get('goal', 'N/A')}")
        
        state = context.get("state", {})
        if state:
            completed = state.get("completed", [])
            remaining = state.get("remaining", [])
            if completed:
                parts.append(f"Completed: {len(completed)} items")
            if remaining:
                parts.append(f"Remaining: {len(remaining)} items")
        
        summary = "; ".join(parts)
        
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary
    
    def select_evidence(
        self,
        evidence: List[Dict[str, Any]],
        target_agent: str,
        max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Select the most relevant evidence for the target agent.
        
        Args:
            evidence: List of evidence items
            target_agent: The target agent
            max_items: Maximum number of evidence items to include
            
        Returns:
            Filtered list of evidence items
        """
        # In a real implementation, this would use agent capabilities
        # and task requirements to select the most relevant evidence
        
        # For now, just limit the number and remove sensitive fields
        selected = []
        for item in evidence[:max_items]:
            filtered_item = {k: v for k, v in item.items() 
                           if k not in ["accessed_at", "digest"]}
            selected.append(filtered_item)
        
        return selected
