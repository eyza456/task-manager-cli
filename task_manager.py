import json
import os
from datetime import datetime
import sys
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_NAME = "tasks.json"

# Allowed task statuses
STATUS_OPTIONS = ["todo", "in-progress", "done"]

def initializer_file():
    """Initializes the JSON file if it doesn't exist or if it's corrupted."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as file:
            json.dump([], file)
    else:
        try:
            with open(FILE_NAME, "r") as file:
                json.load(file)
        except json.JSONDecodeError:
            logging.error("Error: The JSON file is corrupted. Initializing a new file.")
            with open(FILE_NAME, "w") as file:
                json.dump([], file)

def read_tasks():
    """Reads tasks from the JSON file."""
    with open(FILE_NAME, "r") as file:
        return json.load(file)

def write_tasks(tasks):
    """Writes tasks to the JSON file."""
    with open(FILE_NAME, "w") as file:
        json.dump(tasks, file, indent=4)

def generate_id(tasks):
    """Generates a new unique ID based on existing tasks."""
    return max([task["id"] for task in tasks], default=0) + 1

def add_task(description):
    """Adds a new task."""
    if not description.strip():
        logging.error("Error: The task description cannot be empty.")
        return

    tasks = read_tasks()
    new_task = {
        "id": generate_id(tasks),
        "description": description.strip(),
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    tasks.append(new_task)
    write_tasks(tasks)
    logging.info(f"Task successfully added (ID: {new_task['id']})")

def update_task(task_id, new_description):
    """Updates the description of an existing task."""
    if not new_description.strip():
        logging.error("Error: The new description cannot be empty.")
        return

    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = new_description.strip()
            task["updatedAt"] = datetime.now().isoformat()
            write_tasks(tasks)
            logging.info(f"Task successfully updated (ID: {task_id})")
            return
    logging.error(f"Error: Task with ID {task_id} not found.")

def delete_task(task_id):
    """Deletes a task by its ID."""
    tasks = read_tasks()
    if not any(task["id"] == task_id for task in tasks):
        logging.error(f"Error: Task with ID {task_id} not found.")
        return
    tasks = [task for task in tasks if task["id"] != task_id]
    write_tasks(tasks)
    logging.info(f"Task successfully deleted (ID: {task_id})")

def mark_task(task_id, status):
    """Marks a task with a specific status."""
    if status not in STATUS_OPTIONS:
        logging.error(f"Error: Invalid status '{status}'. Valid options: {', '.join(STATUS_OPTIONS)}")
        return

    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = datetime.now().isoformat()
            write_tasks(tasks)
            logging.info(f"Task marked as '{status}' (ID: {task_id})")
            return
    logging.error(f"Error: Task with ID {task_id} not found.")

def list_tasks(status=None):
    """Lists tasks, filtered by status if specified."""
    tasks = read_tasks()
    filtered_tasks = tasks if status is None else [task for task in tasks if task["status"] == status]
    if not filtered_tasks:
        logging.info("No tasks found.")
        return

    for task in filtered_tasks:
        logging.info(f"[{task['status']}] {task['id']}: {task['description']} (Created: {task['createdAt']}, Updated: {task['updatedAt']})")

def main():
    """Main function to process CLI commands."""
    initializer_file()
    args = sys.argv[1:]

    if not args:
        logging.error("Usage: task_manager <command> [options]")
        logging.info("Example: task_manager add 'Task description'")
        return

    command = args[0].lower()
    commands = ["add", "update", "delete", "mark-in-progress", "mark-done", "list"]

    if command not in commands:
        logging.error(f"Unrecognized command: {command}")
        logging.info(f"Valid commands: {', '.join(commands)}")
        return

    try:
        if command == "add" and len(args) > 1:
            add_task(" ".join(args[1:]))
        elif command == "update" and len(args) > 2:
            update_task(int(args[1]), " ".join(args[2:]))
        elif command == "delete" and len(args) > 1:
            delete_task(int(args[1]))
        elif command == "mark-in-progress" and len(args) > 1:
            mark_task(int(args[1]), "in-progress")
        elif command == "mark-done" and len(args) > 1:
            mark_task(int(args[1]), "done")
        elif command == "list":
            if len(args) > 1 and args[1] in STATUS_OPTIONS:
                list_tasks(args[1])
            else:
                list_tasks()
        else:
            logging.error("Incorrect command usage.")
    except ValueError:
        logging.error("Error: Task ID must be a number.")

if __name__ == "__main__":
    main()
