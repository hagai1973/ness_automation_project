# Ness Automation Project

A Python-based automation framework for managing and scheduling tasks efficiently.

## Features

- **Task Management**: Create, execute, and monitor automation tasks
- **Scheduling**: Schedule tasks for one-time or recurring execution
- **Configuration**: Flexible YAML-based configuration system
- **Logging**: Built-in logging for tracking task execution
- **Extensible**: Easy to extend with custom tasks and functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hagai1973/ness_automation_project.git
cd ness_automation_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from ness_automation import AutomationManager

# Initialize the automation manager
manager = AutomationManager()

# Create a task
def my_task():
    return "Task completed!"

manager.create_task(
    name="my_task",
    func=my_task,
    description="My first automation task"
)

# Execute the task
result = manager.execute_task("my_task")
print(result)  # Output: Task completed!
```

### Scheduling Tasks

```python
from ness_automation import AutomationManager
from datetime import datetime, timedelta

manager = AutomationManager()

# Create a task
def scheduled_task():
    return "Scheduled task executed!"

manager.create_task(
    name="scheduled_task",
    func=scheduled_task
)

# Schedule the task to run in 5 minutes
schedule_time = datetime.now() + timedelta(minutes=5)
manager.schedule_task("scheduled_task", schedule_time=schedule_time)

# Or schedule a recurring task (every 60 seconds)
manager.schedule_task("scheduled_task", interval=60, repeat=True)

# Start the scheduler
manager.start_scheduler()
```

## Examples

The `examples/` directory contains sample scripts:

- `basic_usage.py`: Demonstrates basic task creation and execution
- `scheduling_example.py`: Shows how to schedule tasks

Run examples:
```bash
python examples/basic_usage.py
python examples/scheduling_example.py
```

## Configuration

Configuration is managed through YAML files. The default configuration is in `config/config.yaml`:

```yaml
automation:
  enabled: true
  log_level: INFO
  max_retries: 3

scheduler:
  check_interval: 60

tasks:
  default_timeout: 300
```

You can create custom configuration files and load them:

```python
manager = AutomationManager(config_path="path/to/custom_config.yaml")
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=src/ness_automation tests/
```

## Project Structure

```
ness_automation_project/
├── src/
│   └── ness_automation/
│       ├── __init__.py
│       ├── automation_manager.py
│       ├── config.py
│       ├── scheduler.py
│       └── task.py
├── tests/
│   ├── __init__.py
│   ├── test_automation_manager.py
│   ├── test_config.py
│   ├── test_scheduler.py
│   └── test_task.py
├── examples/
│   ├── basic_usage.py
│   └── scheduling_example.py
├── config/
│   └── config.yaml
├── docs/
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

## API Documentation

### AutomationManager

Main class for managing automation tasks.

**Methods:**
- `create_task(name, func, args=(), kwargs=None, description="")`: Create a new task
- `execute_task(name)`: Execute a task immediately
- `schedule_task(name, schedule_time=None, interval=None, repeat=False)`: Schedule a task
- `get_task_status(name)`: Get the status of a task
- `list_tasks()`: List all registered tasks
- `start_scheduler()`: Start the task scheduler
- `stop_scheduler()`: Stop the task scheduler

### Task

Represents an automation task.

**Attributes:**
- `name`: Task name
- `status`: Current status (pending, running, completed, failed, cancelled)
- `result`: Task execution result
- `error`: Error message if task failed

**Methods:**
- `execute()`: Execute the task
- `cancel()`: Cancel a pending task
- `get_duration()`: Get task execution duration

### Scheduler

Manages task scheduling and execution.

**Methods:**
- `schedule_task(task, schedule_time=None, interval=None, repeat=False)`: Schedule a task
- `run_once()`: Check and run due tasks once
- `run()`: Run the scheduler continuously
- `stop()`: Stop the scheduler

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.