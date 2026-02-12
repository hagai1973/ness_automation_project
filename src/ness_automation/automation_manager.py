"""
Main automation manager for the Ness automation system.
"""

import logging
from typing import List, Dict, Any, Callable
from .config import Config
from .task import Task, TaskStatus
from .scheduler import Scheduler

logger = logging.getLogger(__name__)


class AutomationManager:
    """Main manager for automation tasks."""

    def __init__(self, config_path: str = None):
        """
        Initialize the automation manager.

        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self._setup_logging()
        self.scheduler = Scheduler(
            check_interval=self.config.get('scheduler.check_interval', 60)
        )
        self.tasks: Dict[str, Task] = {}
        logger.info("AutomationManager initialized")

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        log_level = self.config.get('automation.log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def create_task(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        description: str = ""
    ) -> Task:
        """
        Create a new task.

        Args:
            name: Task name
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            description: Task description

        Returns:
            Created Task object
        """
        task = Task(name, func, args, kwargs, description)
        self.tasks[name] = task
        logger.info(f"Created task: {name}")
        return task

    def execute_task(self, name: str) -> Any:
        """
        Execute a task immediately.

        Args:
            name: Task name

        Returns:
            Task result

        Raises:
            KeyError: If task not found
        """
        if name not in self.tasks:
            raise KeyError(f"Task not found: {name}")

        task = self.tasks[name]
        return task.execute()

    def schedule_task(
        self,
        name: str,
        schedule_time=None,
        interval: int = None,
        repeat: bool = False
    ) -> None:
        """
        Schedule a task for execution.

        Args:
            name: Task name
            schedule_time: When to run the task
            interval: Interval in seconds for recurring tasks
            repeat: Whether to repeat the task

        Raises:
            KeyError: If task not found
        """
        if name not in self.tasks:
            raise KeyError(f"Task not found: {name}")

        task = self.tasks[name]
        self.scheduler.schedule_task(task, schedule_time, interval, repeat)

    def get_task_status(self, name: str) -> str:
        """
        Get the status of a task.

        Args:
            name: Task name

        Returns:
            Task status

        Raises:
            KeyError: If task not found
        """
        if name not in self.tasks:
            raise KeyError(f"Task not found: {name}")

        return self.tasks[name].status

    def list_tasks(self) -> List[str]:
        """
        List all registered tasks.

        Returns:
            List of task names
        """
        return list(self.tasks.keys())

    def start_scheduler(self) -> None:
        """Start the task scheduler."""
        logger.info("Starting scheduler")
        self.scheduler.run()

    def stop_scheduler(self) -> None:
        """Stop the task scheduler."""
        logger.info("Stopping scheduler")
        self.scheduler.stop()
