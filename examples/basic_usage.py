"""
Example automation script demonstrating basic usage.
"""

from ness_automation import AutomationManager
import time


def example_task_1():
    """Example task that performs a simple operation."""
    print("Executing example task 1...")
    time.sleep(1)
    result = "Task 1 completed successfully"
    print(result)
    return result


def example_task_2(message: str):
    """Example task with parameters."""
    print(f"Executing example task 2 with message: {message}")
    time.sleep(1)
    result = f"Task 2 processed: {message}"
    print(result)
    return result


def example_task_3(x: int, y: int):
    """Example task that performs calculation."""
    print(f"Calculating {x} + {y}...")
    result = x + y
    print(f"Result: {result}")
    return result


def main():
    """Main function demonstrating automation usage."""
    # Initialize the automation manager
    manager = AutomationManager()

    print("=== Ness Automation Example ===\n")

    # Create tasks
    print("Creating tasks...")
    task1 = manager.create_task(
        name="task1",
        func=example_task_1,
        description="Simple example task"
    )

    task2 = manager.create_task(
        name="task2",
        func=example_task_2,
        args=("Hello from automation!",),
        description="Task with parameters"
    )

    task3 = manager.create_task(
        name="task3",
        func=example_task_3,
        kwargs={"x": 10, "y": 20},
        description="Calculation task"
    )

    print(f"Created {len(manager.list_tasks())} tasks\n")

    # Execute tasks immediately
    print("Executing tasks immediately...")
    print("-" * 50)
    
    result1 = manager.execute_task("task1")
    print(f"Status: {manager.get_task_status('task1')}\n")

    result2 = manager.execute_task("task2")
    print(f"Status: {manager.get_task_status('task2')}\n")

    result3 = manager.execute_task("task3")
    print(f"Status: {manager.get_task_status('task3')}\n")

    print("-" * 50)
    print("\n=== All tasks completed ===")

    # List all tasks
    print("\nRegistered tasks:")
    for task_name in manager.list_tasks():
        status = manager.get_task_status(task_name)
        print(f"  - {task_name}: {status}")


if __name__ == "__main__":
    main()
