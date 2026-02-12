"""Tests for the task module."""

import pytest
from ness_automation.task import Task, TaskStatus


def sample_function(x, y):
    """Sample function for testing."""
    return x + y


def failing_function():
    """Function that raises an exception."""
    raise ValueError("Test error")


def test_task_creation():
    """Test task creation."""
    task = Task(
        name="test_task",
        func=sample_function,
        args=(5, 3),
        description="Test task"
    )
    
    assert task.name == "test_task"
    assert task.status == TaskStatus.PENDING
    assert task.description == "Test task"
    assert task.result is None


def test_task_execution():
    """Test task execution."""
    task = Task(
        name="test_task",
        func=sample_function,
        args=(5, 3)
    )
    
    result = task.execute()
    
    assert result == 8
    assert task.status == TaskStatus.COMPLETED
    assert task.result == 8
    assert task.started_at is not None
    assert task.completed_at is not None


def test_task_execution_with_kwargs():
    """Test task execution with keyword arguments."""
    task = Task(
        name="test_task",
        func=sample_function,
        kwargs={"x": 10, "y": 20}
    )
    
    result = task.execute()
    assert result == 30


def test_task_failure():
    """Test task failure handling."""
    task = Task(
        name="failing_task",
        func=failing_function
    )
    
    with pytest.raises(ValueError):
        task.execute()
    
    assert task.status == TaskStatus.FAILED
    assert task.error is not None
    assert "Test error" in task.error


def test_task_cancel():
    """Test task cancellation."""
    task = Task(
        name="test_task",
        func=sample_function,
        args=(1, 2)
    )
    
    task.cancel()
    assert task.status == TaskStatus.CANCELLED


def test_task_duration():
    """Test task duration calculation."""
    task = Task(
        name="test_task",
        func=sample_function,
        args=(1, 2)
    )
    
    # Before execution
    assert task.get_duration() is None
    
    # After execution
    task.execute()
    duration = task.get_duration()
    assert duration is not None
    assert duration >= 0
