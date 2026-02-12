"""Tests for the scheduler module."""

import pytest
from datetime import datetime, timedelta
from ness_automation.scheduler import Scheduler, ScheduledTask
from ness_automation.task import Task, TaskStatus


def sample_task_func():
    """Sample task function."""
    return "Executed"


def test_scheduled_task_creation():
    """Test scheduled task creation."""
    task = Task("test", sample_task_func)
    scheduled_task = ScheduledTask(task)
    
    assert scheduled_task.task == task
    assert scheduled_task.last_run is None


def test_scheduled_task_is_due():
    """Test checking if a task is due."""
    task = Task("test", sample_task_func)
    
    # Task scheduled for the past
    past_time = datetime.now() - timedelta(seconds=10)
    scheduled_task = ScheduledTask(task, schedule_time=past_time)
    assert scheduled_task.is_due() is True
    
    # Task scheduled for the future
    future_time = datetime.now() + timedelta(seconds=10)
    scheduled_task = ScheduledTask(task, schedule_time=future_time)
    assert scheduled_task.is_due() is False


def test_scheduler_creation():
    """Test scheduler creation."""
    scheduler = Scheduler(check_interval=30)
    
    assert scheduler.check_interval == 30
    assert len(scheduler.scheduled_tasks) == 0
    assert scheduler.running is False


def test_schedule_task():
    """Test scheduling a task."""
    scheduler = Scheduler()
    task = Task("test", sample_task_func)
    
    scheduled_task = scheduler.schedule_task(task)
    
    assert len(scheduler.scheduled_tasks) == 1
    assert scheduler.scheduled_tasks[0] == scheduled_task


def test_run_once():
    """Test running scheduler once."""
    scheduler = Scheduler()
    task = Task("test", sample_task_func)
    
    # Schedule task for immediate execution
    past_time = datetime.now() - timedelta(seconds=1)
    scheduler.schedule_task(task, schedule_time=past_time)
    
    scheduler.run_once()
    
    assert task.status == TaskStatus.COMPLETED


def test_get_pending_tasks():
    """Test getting pending tasks."""
    scheduler = Scheduler()
    
    task1 = Task("test1", sample_task_func)
    task2 = Task("test2", sample_task_func)
    
    scheduler.schedule_task(task1)
    scheduler.schedule_task(task2)
    
    pending = scheduler.get_pending_tasks()
    assert len(pending) == 2


def test_clear_completed_tasks():
    """Test clearing completed tasks."""
    scheduler = Scheduler()
    task = Task("test", sample_task_func)
    
    past_time = datetime.now() - timedelta(seconds=1)
    scheduler.schedule_task(task, schedule_time=past_time, repeat=False)
    
    # Run the task
    scheduler.run_once()
    
    # Task should be removed after execution (non-repeating)
    assert len(scheduler.scheduled_tasks) == 0
