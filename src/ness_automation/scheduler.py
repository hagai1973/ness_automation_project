"""
Scheduler for automation tasks.
"""

import time
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
from .task import Task, TaskStatus

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Represents a scheduled task."""

    def __init__(
        self,
        task: Task,
        schedule_time: datetime = None,
        interval: int = None,
        repeat: bool = False
    ):
        """
        Initialize a scheduled task.

        Args:
            task: Task to schedule
            schedule_time: When to run the task
            interval: Interval in seconds for recurring tasks
            repeat: Whether to repeat the task
        """
        self.task = task
        self.schedule_time = schedule_time or datetime.now()
        self.interval = interval
        self.repeat = repeat
        self.last_run = None

    def is_due(self) -> bool:
        """Check if the task is due to run."""
        now = datetime.now()
        if self.last_run is None:
            return now >= self.schedule_time
        elif self.interval and self.repeat:
            next_run = self.last_run + timedelta(seconds=self.interval)
            return now >= next_run
        return False

    def should_run(self) -> bool:
        """Check if the task should run."""
        return self.task.status != TaskStatus.RUNNING and self.is_due()


class Scheduler:
    """Manages task scheduling and execution."""

    def __init__(self, check_interval: int = 60):
        """
        Initialize the scheduler.

        Args:
            check_interval: Interval in seconds to check for due tasks
        """
        self.check_interval = check_interval
        self.scheduled_tasks: List[ScheduledTask] = []
        self.running = False

    def schedule_task(
        self,
        task: Task,
        schedule_time: datetime = None,
        interval: int = None,
        repeat: bool = False
    ) -> ScheduledTask:
        """
        Schedule a task for execution.

        Args:
            task: Task to schedule
            schedule_time: When to run the task
            interval: Interval in seconds for recurring tasks
            repeat: Whether to repeat the task

        Returns:
            ScheduledTask object
        """
        scheduled_task = ScheduledTask(task, schedule_time, interval, repeat)
        self.scheduled_tasks.append(scheduled_task)
        logger.info(f"Scheduled task: {task.name}")
        return scheduled_task

    def run_once(self) -> None:
        """Check and run any due tasks once."""
        for scheduled_task in self.scheduled_tasks:
            if scheduled_task.should_run():
                try:
                    scheduled_task.task.execute()
                    scheduled_task.last_run = datetime.now()

                    if not scheduled_task.repeat:
                        self.scheduled_tasks.remove(scheduled_task)
                except Exception as e:
                    logger.error(f"Error executing scheduled task: {e}")

    def run(self) -> None:
        """Run the scheduler continuously."""
        self.running = True
        logger.info("Scheduler started")

        while self.running:
            self.run_once()
            time.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        logger.info("Scheduler stopped")

    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get list of pending scheduled tasks."""
        return [
            st for st in self.scheduled_tasks
            if st.task.status == TaskStatus.PENDING
        ]

    def clear_completed_tasks(self) -> None:
        """Remove completed non-recurring tasks."""
        self.scheduled_tasks = [
            st for st in self.scheduled_tasks
            if st.repeat or st.task.status != TaskStatus.COMPLETED
        ]
