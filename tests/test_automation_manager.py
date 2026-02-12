"""Tests for the automation manager."""

import pytest
from ness_automation.automation_manager import AutomationManager
from ness_automation.task import TaskStatus


def sample_task():
    """Sample task for testing."""
    return "Task completed"


def test_automation_manager_creation():
    """Test automation manager creation."""
    manager = AutomationManager()
    assert manager.config is not None
    assert manager.scheduler is not None
    assert len(manager.tasks) == 0


def test_create_task():
    """Test task creation through manager."""
    manager = AutomationManager()
    
    task = manager.create_task(
        name="test_task",
        func=sample_task,
        description="Test task"
    )
    
    assert task.name == "test_task"
    assert "test_task" in manager.tasks
    assert len(manager.list_tasks()) == 1


def test_execute_task():
    """Test task execution through manager."""
    manager = AutomationManager()
    
    manager.create_task(
        name="test_task",
        func=sample_task
    )
    
    result = manager.execute_task("test_task")
    
    assert result == "Task completed"
    assert manager.get_task_status("test_task") == TaskStatus.COMPLETED


def test_execute_nonexistent_task():
    """Test executing a task that doesn't exist."""
    manager = AutomationManager()
    
    with pytest.raises(KeyError):
        manager.execute_task("nonexistent")


def test_get_task_status():
    """Test getting task status."""
    manager = AutomationManager()
    
    manager.create_task(
        name="test_task",
        func=sample_task
    )
    
    assert manager.get_task_status("test_task") == TaskStatus.PENDING
    
    manager.execute_task("test_task")
    assert manager.get_task_status("test_task") == TaskStatus.COMPLETED


def test_list_tasks():
    """Test listing all tasks."""
    manager = AutomationManager()
    
    manager.create_task("task1", sample_task)
    manager.create_task("task2", sample_task)
    manager.create_task("task3", sample_task)
    
    tasks = manager.list_tasks()
    
    assert len(tasks) == 3
    assert "task1" in tasks
    assert "task2" in tasks
    assert "task3" in tasks
