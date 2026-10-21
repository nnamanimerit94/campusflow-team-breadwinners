# CampusFlow — AI Learning Log

## 1. Project Overview

CampusFlow is a Python command-line helpdesk management system designed to help campus staff create, prioritize, assign, and track support requests.

The project was developed as a team software engineering exercise.

AI was used as a learning and development assistant throughout the project.

Its role included helping us understand technical concepts, review implementation approaches, identify potential errors, and improve code quality.

## 2. How We Used AI

### Understanding the Project Requirements

AI helped us break down the project requirements into smaller, manageable tasks.

We identified the main components of CampusFlow:

- Input validation
- Priority calculation
- Ticket creation
- JSON storage
- Ticket workflow management
- Ticket queries and reporting
- Command-line integration
- Automated testing

This helped us organize the development process and divide responsibilities.

### Understanding Python Concepts

During development, AI helped explain Python concepts relevant to our implementation.

These included:

- Dictionaries and key-based lookups
- Functions and parameters
- Exception handling
- JSON serialization and deserialization
- File handling
- Python modules and imports
- Unit testing
- Git branches and pull requests

These explanations helped us understand why particular approaches were suitable for the project.

### Reviewing Code and Debugging

AI assisted with reviewing code, identifying possible errors, and suggesting corrections.

We used it to examine how different modules interacted and how to handle invalid inputs and unexpected failures.

AI suggestions were evaluated against the project's existing requirements and function contracts.

### CLI Integration

AI assisted with integrating the existing modules into `main.py`.

The CLI connects ticket creation, validation, assignment, status management, queries, reporting, and JSON persistence.

One important design correction involved ticket status management.

An earlier implementation introduced separate menu options for starting work and resolving tickets.

However, our existing function contract was:

`update_ticket_status(tickets, ticket_id, new_status)`

We corrected the CLI so administrators enter the desired status, while the existing workflow function determines whether the transition is valid.

This allowed us to reuse our existing business logic rather than introduce unnecessary duplication.

### Testing

AI assisted with preparing automated CLI tests using Python's built-in `unittest` framework.

The tests covered operations such as:

- Creating tickets
- Handling invalid input
- Assigning tickets
- Updating ticket statuses
- Reopening tickets
- Loading existing data
- Handling corrupted JSON
- Handling file-saving failures

The project had 96 existing tests before the CLI integration tests were added.

An additional 23 CLI tests were introduced, bringing the total to 119 automated tests.

The tests passed during the final Phase 7 verification.

## 3. Important Technical Decisions

### Using Dictionaries for Ticket Storage

We selected a dictionary to store tickets, using each ticket ID as its key.

This supports efficient ticket lookup without searching through a list of every ticket.

### Separating Validation from User Input

We implemented validation functions separately from the CLI.

This allows validation rules to be reused across the application.

The CLI collects input and displays errors, while the validation functions determine whether the supplied values are acceptable.

### Separating Business Logic into Modules

Instead of implementing all functionality in one file, we organized the application into modules.

Each module handles a specific responsibility.

This made it easier to develop, test, and integrate the different components.

### Using JSON Persistence

We used JSON because it is supported by Python's standard library and was suitable for the project's scope.

During integration, we improved the saving process by writing data to a temporary file before replacing the destination file.

This reduces the risk of damaging existing data if a write fails.

### Reusing Existing Functions

We decided that the CLI should call existing functions rather than recreate their logic.

For example, the CLI uses the workflow module to validate ticket status transitions.

This helps maintain consistent behavior across the application.



### Engineer A Bug-Hunter Finding — Query Result Aliasing

**Module reviewed:** campusflow/queries.py

**Test:** test_query_results_cannot_modify_original_tickets

**Observation:**

The list_tickets function returns ticket dictionaries that share
references with the original ticket collection.

When a returned ticket's status was changed from "open" to
"resolved", the original ticket's status also changed.

**Test result:** FAILED (1 failure).

**Potential impact:**

A caller could unintentionally modify stored ticket information
by changing a returned query result.

**Review required:**

Engineer B should confirm whether query functions are required
to return independent copies or whether shared references are
intentional.

No changes were made to Engineer B's implementation.

