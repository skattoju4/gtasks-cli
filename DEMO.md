# gtasks-cli MVP Demo

This document provides instructions on how to run the MVP demo of the `gtasks-cli` tool.

## Prerequisites

Before running the demo, make sure you have:
1. Installed the project dependencies: `pip install -r requirements.txt`
2. Installed the project in editable mode: `pip install -e .`
3. Authenticated with Google Tasks by providing your `credentials.json` file.

## Running the Demo

To run the demo, execute the following command in your terminal:

```bash
gtasks demo
```

## What the Demo Does

The `demo` command will perform the following actions to showcase the CLI's functionality:

1.  **Creates a new task list:** A new task list named "MVP Demo" will be created.
2.  **Adds tasks:** Two new tasks, "Learn gtasks CLI" and "Present demo", will be added to the "MVP Demo" list.
3.  **Lists tasks:** The tasks in the "MVP Demo" list will be displayed.
4.  **Completes a task:** The "Learn gtasks CLI" task will be marked as complete.
5.  **Lists tasks again:** The tasks in the "MVP Demo" list will be displayed again to show the updated status of the completed task.
6.  **Deletes the task list:** The "MVP Demo" task list will be deleted to clean up the environment.

## Expected Output

When you run the `gtasks demo` command, you should see output similar to the following:

```
Starting gtasks CLI demo...

1. Creating a new task list named 'MVP Demo'...
   Task list 'MVP Demo' created with id: <tasklist_id>

2. Adding tasks to the 'MVP Demo' list...
   - Task 'Learn gtasks CLI' added.
   - Task 'Present demo' added.

3. Listing tasks in 'MVP Demo' list...
Tasks:
- Learn gtasks CLI (id: <task1_id>, status: Needs Action)
- Present demo (id: <task2_id>, status: Needs Action)

4. Marking task 'Learn gtasks CLI' as complete...
Task 'Learn gtasks CLI' marked as complete.

5. Listing tasks again to show the updated status...
Tasks:
- Learn gtasks CLI (id: <task1_id>, status: Completed)
- Present demo (id: <task2_id>, status: Needs Action)

6. Deleting the 'MVP Demo' task list...
Task list with id '<tasklist_id>' deleted.

Demo complete!
```
