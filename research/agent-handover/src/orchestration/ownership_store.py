"""
Ownership Store

Store for managing task ownership state. Provides atomic ownership transfers
and prevents concurrent modification conflicts.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from typing import Set


class OwnershipError(Exception):
    """Base exception for ownership errors."""
    pass


class OwnershipConflict(OwnershipError):
    """Raised when there is an ownership conflict."""
    pass


class TaskNotFoundError(OwnershipError):
    """Raised when a task is not found."""
    pass


@dataclass
class TaskOwnership:
    """Represents the ownership state of a task."""
    
    task_id: str
    owner: str
    state: str = "not_started"
    handover_id: Optional[str] = None
    ownership_version: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "owner": self.owner,
            "state": self.state,
            "handover_id": self.handover_id,
            "ownership_version": self.ownership_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskOwnership":
        """Create from dictionary."""
        return cls(
            task_id=data["task_id"],
            owner=data["owner"],
            state=data.get("state", "not_started"),
            handover_id=data.get("handover_id"),
            ownership_version=data.get("ownership_version", 0),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
        )


class OwnershipStore:
    """
    Store for managing task ownership with atomic transfers.
    
    Uses a compare-and-swap pattern to ensure atomic ownership transfers
    and prevent concurrent modification conflicts.
    """
    
    def __init__(self):
        """Initialize the ownership store."""
        self._tasks: Dict[str, TaskOwnership] = {}
        self._lock = threading.RLock()
        self._history: Dict[str, List[Dict[str, Any]]] = {}  # task_id -> [ownership records]
    
    def create_task(
        self,
        task_id: str,
        owner: str,
        state: str = "not_started",
        handover_id: Optional[str] = None,
    ) -> TaskOwnership:
        """
        Create a new task with initial ownership.
        
        Args:
            task_id: Unique task identifier
            owner: Initial owner agent
            state: Initial task state
            handover_id: Optional initial handover ID
            
        Returns:
            The created TaskOwnership
        """
        with self._lock:
            if task_id in self._tasks:
                raise OwnershipError(f"Task {task_id} already exists")
            
            ownership = TaskOwnership(
                task_id=task_id,
                owner=owner,
                state=state,
                handover_id=handover_id,
                ownership_version=1,
            )
            
            self._tasks[task_id] = ownership
            self._record_history(task_id, ownership)
            
            return ownership
    
    def get_ownership(self, task_id: str) -> Optional[TaskOwnership]:
        """
        Get the current ownership for a task.
        
        Args:
            task_id: The task ID to query
            
        Returns:
            The current TaskOwnership, or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_owner(self, task_id: str) -> Optional[str]:
        """
        Get the current owner of a task.
        
        Args:
            task_id: The task ID to query
            
        Returns:
            The current owner, or None if not found
        """
        ownership = self.get_ownership(task_id)
        if ownership:
            return ownership.owner
        return None
    
    def get_ownership_version(self, task_id: str) -> int:
        """
        Get the current ownership version for a task.
        
        Args:
            task_id: The task ID to query
            
        Returns:
            The current ownership version, or 0 if not found
        """
        ownership = self.get_ownership(task_id)
        if ownership:
            return ownership.ownership_version
        return 0
    
    def transfer_ownership(
        self,
        task_id: str,
        new_owner: str,
        handover_id: str,
        expected_owner: Optional[str] = None,
        expected_version: Optional[int] = None,
        new_state: str = "working",
    ) -> TaskOwnership:
        """
        Transfer ownership of a task atomically.
        
        This implements compare-and-swap semantics to prevent:
        - Two agents believing they own the same task
        - An old handover overwriting newer work
        - Duplicate state-changing tool calls
        - Circular transfers
        
        Args:
            task_id: The task ID
            new_owner: The new owner agent
            handover_id: The handover ID for this transfer
            expected_owner: Optional expected current owner (for CAS)
            expected_version: Optional expected version (for CAS)
            new_state: The new task state
            
        Returns:
            The updated TaskOwnership
            
        Raises:
            TaskNotFoundError: If task not found
            OwnershipConflict: If ownership cannot be transferred
        """
        with self._lock:
            current = self._tasks.get(task_id)
            
            if current is None:
                raise TaskNotFoundError(f"Task {task_id} not found")
            
            # Check expected owner
            if expected_owner is not None and current.owner != expected_owner:
                raise OwnershipConflict(
                    f"Expected owner {expected_owner}, but current owner is {current.owner}"
                )
            
            # Check expected version
            if expected_version is not None and current.ownership_version != expected_version:
                raise OwnershipConflict(
                    f"Expected version {expected_version}, but current version is {current.ownership_version}"
                )
            
            # Create new ownership
            new_ownership = TaskOwnership(
                task_id=task_id,
                owner=new_owner,
                state=new_state,
                handover_id=handover_id,
                ownership_version=current.ownership_version + 1,
                created_at=current.created_at,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            
            # Update store
            self._tasks[task_id] = new_ownership
            self._record_history(task_id, new_ownership)
            
            return new_ownership
    
    def compare_and_swap(
        self,
        task_id: str,
        old_owner: str,
        old_version: int,
        new_owner: str,
        handover_id: str,
        new_state: str = "working",
    ) -> bool:
        """
        Perform a compare-and-swap ownership transfer.
        
        Atomically transfers ownership only if:
        - Current owner matches old_owner
        - Current ownership_version matches old_version
        
        Args:
            task_id: The task ID
            old_owner: Expected current owner
            old_version: Expected current version
            new_owner: New owner
            handover_id: The handover ID
            new_state: New task state
            
        Returns:
            True if transfer succeeded, False otherwise
        """
        try:
            self.transfer_ownership(
                task_id=task_id,
                new_owner=new_owner,
                handover_id=handover_id,
                expected_owner=old_owner,
                expected_version=old_version,
                new_state=new_state,
            )
            return True
        except (TaskNotFoundError, OwnershipConflict):
            return False
    
    def get_history(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get the ownership history for a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            List of ownership records (newest first)
        """
        with self._lock:
            return list(self._history.get(task_id, []))
    
    def _record_history(self, task_id: str, ownership: TaskOwnership) -> None:
        """Record an ownership change in history."""
        if task_id not in self._history:
            self._history[task_id] = []
        
        self._history[task_id].append(ownership.to_dict())
    
    def list_tasks(self) -> List[str]:
        """List all task IDs in the store."""
        with self._lock:
            return list(self._tasks.keys())
    
    def get_tasks_by_owner(self, owner: str) -> List[str]:
        """Get all task IDs owned by a specific agent."""
        with self._lock:
            return [
                task_id for task_id, ownership in self._tasks.items()
                if ownership.owner == owner
            ]
    
    def clear(self) -> None:
        """Clear all tasks from the store. For testing only."""
        with self._lock:
            self._tasks.clear()
            self._history.clear()
    
    def get_state(self, task_id: str) -> Optional[str]:
        """Get the current state of a task."""
        ownership = self.get_ownership(task_id)
        if ownership:
            return ownership.state
        return None
    
    def set_state(self, task_id: str, state: str) -> None:
        """
        Update the state of a task.
        
        Args:
            task_id: The task ID
            state: The new state
            
        Raises:
            TaskNotFoundError: If task not found
        """
        with self._lock:
            current = self._tasks.get(task_id)
            if current is None:
                raise TaskNotFoundError(f"Task {task_id} not found")
            
            current.state = state
            current.updated_at = datetime.now(timezone.utc).isoformat()
            self._record_history(task_id, current)
    
    def get_active_agent(self, task_id: str) -> Optional[str]:
        """Get the active agent for a task."""
        return self.get_owner(task_id)
