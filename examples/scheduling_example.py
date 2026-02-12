"""
Example script demonstrating task scheduling.
"""

from ness_automation import AutomationManager
from datetime import datetime, timedelta
import time


def scheduled_task():
    """A task to be scheduled."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduled task executed!")
    return "Scheduled task result"


def recurring_task():
    """A recurring task."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Recurring task executed!")
    return "Recurring task result"


def main():
    """Main function demonstrating task scheduling."""
    manager = AutomationManager()

    print("=== Task Scheduling Example ===\n")

    # Create tasks
    task1 = manager.create_task(
        name="scheduled_task",
        func=scheduled_task,
        description="One-time scheduled task"
    )

    task2 = manager.create_task(
        name="recurring_task",
        func=recurring_task,
        description="Recurring scheduled task"
    )

    # Schedule task to run in 5 seconds
    schedule_time = datetime.now() + timedelta(seconds=5)
    print(f"Scheduling task to run at {schedule_time.strftime('%H:%M:%S')}")
    manager.schedule_task("scheduled_task", schedule_time=schedule_time)

    # Schedule recurring task every 10 seconds
    print("Scheduling recurring task every 10 seconds")
    manager.schedule_task("recurring_task", interval=10, repeat=True)

    print("\nRunning scheduler for 35 seconds...\n")

    # Run scheduler for a limited time (for demonstration)
    start_time = time.time()
    while time.time() - start_time < 35:
        manager.scheduler.run_once()
        time.sleep(1)

    print("\n=== Scheduler demonstration completed ===")


if __name__ == "__main__":
    main()
