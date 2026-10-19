# CampusFlow

## Project Description

CampusFlow is a command-line helpdesk management system built with Python.

It helps campus staff record, organize, prioritize, assign, and track support requests through a ticket management system.

The application automatically calculates ticket priority based on urgency and the number of affected users.

CampusFlow also provides ticket status management, an ordered work queue, reports, and JSON persistence to preserve ticket records between application sessions.

## Problem Statement

Campus staff may receive multiple support requests involving network issues, hardware problems, software issues, and other campus-related concerns.

Without a structured ticket management system, it can be difficult to organize requests, identify urgent problems, assign responsibilities, and track progress.

CampusFlow addresses these challenges by providing a simple system for managing support requests.

## Technologies Used

- Python 3
- Python Standard Library
- JSON for data persistence
- unittest for automated testing
- Git and GitHub for version control and collaboration

No external Python packages are required.

## Project Features

### 1. Ticket Creation

Campus staff can create support tickets by providing:

- Ticket title
- Category
- Urgency level
- Number of affected users

The system validates the information and automatically generates a unique ticket ID.

### 2. Automatic Priority Calculation

CampusFlow calculates ticket priority using:

- Urgency level
- Number of affected users

The supported priority levels are:

- Critical
- High
- Medium
- Low

### 3. Ticket Listing and Details

Users can:

- View all tickets
- View the details of a specific ticket
- Identify each ticket by its unique ID

### 4. Ticket Assignment

Tickets can be assigned to mentors or responsible staff members.

A ticket must be assigned before work can begin.

### 5. Ticket Status Management

CampusFlow supports three ticket statuses:

- `open`
- `in_progress`
- `resolved`

The normal workflow is:

`open → in_progress → resolved`

A resolved ticket must be explicitly reopened before work can begin again.

### 6. Open Work Queue

The system displays open tickets ordered by priority.

This helps staff identify which outstanding requests should receive attention first.

### 7. Ticket Reports

CampusFlow generates reports showing:

- Total number of tickets
- Number of tickets by status
- Number of tickets by priority

Reports also handle situations where no tickets exist.

### 8. JSON Persistence

Ticket records are stored in:

`data/tickets.json`

This allows ticket information to remain available after the application closes.

If the JSON file does not exist, CampusFlow starts with an empty ticket collection.

If the file contains malformed JSON, the application displays an error rather than silently replacing the existing data.

Ticket updates are saved using a temporary file and an atomic replacement operation.

## Project Structure

```text
campusflow-by-merit/
│
├── campusflow/
│   ├── __init__.py
│   ├── validation.py
│   ├── priority.py
│   ├── tickets.py
│   ├── storage.py
│   ├── workflow.py
│   └── queries.py
│
├── tests/
│   ├── __init__.py
│   ├── test_validation.py
│   ├── test_priority.py
│   ├── test_tickets.py
│   ├── test_storage.py
│   ├── test_workflow.py
│   ├── test_queries.py
│   └── test_main.py
│
├── docs/
│   ├── design-doc.md
│   └── ai-learning-log.md
│
├── data/
│
├── main.py
├── README.md
└── .gitignore
```

## How to Run CampusFlow

### 1. Clone the Repository

```bash
git clone https://github.com/nnamanimerit94/campusflow-by-merit.git
```

### 2. Open the Project Directory

```bash
cd campusflow-by-merit
```

### 3. Create the Data Directory

```bash
mkdir -p data
```

### 4. Start the Application

```bash
python3 main.py
```

The application displays the following menu:

```text
====================================
             CAMPUSFLOW
====================================
1. Create Ticket
2. View All Tickets
3. Assign Ticket
4. View Ticket Details
5. Update Ticket Status
6. Reopen Ticket
7. View Open Work Queue
8. View Reports
0. Exit
```

Enter the number corresponding to the operation you want to perform.

## Example Ticket Workflow

A typical ticket follows these steps:

1. Create a ticket.
2. The system calculates its priority.
3. Assign the ticket to a mentor.
4. Update its status to `in_progress`.
5. Update its status to `resolved` when the issue is fixed.
6. Reopen the ticket if the issue needs further attention.

## Running Automated Tests

CampusFlow uses Python's built-in `unittest` framework.

Run all tests with:

```bash
python3 -m unittest discover -s tests -v
```

The project includes tests covering:

- Input validation
- Priority calculation
- Ticket creation
- JSON storage
- Ticket assignment
- Status transitions
- Ticket reopening
- Ticket queries and reports
- CLI operations
- Error handling

At the completion of Phase 7, the project contained 119 automated tests.

## Design Documentation

Additional project documentation is available in the `docs/` directory.

- `design-doc.md` — System design, module responsibilities, function contracts, and implementation decisions.
- `ai-learning-log.md` — Documentation of AI-assisted development and lessons learned.

## Current Project Status

**Development complete — Command-Line MVP**

CampusFlow's planned CLI functionality has been implemented and integrated into the main branch.

The application supports ticket creation, assignment, status management, reopening, priority-based work queues, reports, and JSON persistence.

## Known Limitations

- CampusFlow currently operates through a command-line interface.
- Ticket data is stored locally in a JSON file.
- The application is designed for a single running process.
- It does not currently provide user authentication or role-based access control.
- It does not integrate with external campus management systems.