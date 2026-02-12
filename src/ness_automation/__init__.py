"""
Ness Automation Package
A framework for automating Ness security system tasks.
"""

__version__ = "0.1.0"
__author__ = "Ness Automation Team"

from .automation_manager import AutomationManager
from .task import Task
from .scheduler import Scheduler

__all__ = ["AutomationManager", "Task", "Scheduler"]
