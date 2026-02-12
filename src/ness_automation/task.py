"""
Task management for the automation system.
"""

from typing import Callable, Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskStatus:
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents an automation task."""

    def __init__(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        description: str = ""
    ):
        """
        Initialize a task.

        Args:
            name: Task name
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            description: Task description
        """
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.description = description
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None

    def execute(self) -> Any:
        """
        Execute the task.

        Returns:
            Task result

        Raises:
            Exception: If task execution fails
        """
        logger.info(f"Executing task: {self.name}")
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
            logger.info(f"Task completed: {self.name}")
            return self.result
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            logger.error(f"Task failed: {self.name} - {e}")
            raise
        finally:
            self.completed_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the task."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.CANCELLED
            logger.info(f"Task cancelled: {self.name}")

    def get_duration(self) -> Optional[float]:
        """
        Get task execution duration in seconds.

        Returns:
            Duration in seconds or None if not completed
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __repr__(self) -> str:
        """String representation of the task."""
        return f"Task(name='{self.name}', status='{self.status}')"
