# CampusFlow Design Decisions

## Decision 1: Ticket Collection

CampusFlow stores tickets in a dictionary, using each ticket ID as its key (for example, `T001`). Dictionary lookup by key has average-case O(1) time complexity, whereas searching a list typically requires checking entries one by one. This keeps ticket lookup simple and efficient.

## Decision 2: Input Validation

Input validation is separated from CLI input collection. Validation functions enforce business rules and return cleaned values or raise exceptions; `main.py` collects input, displays errors, and lets users retry invalid fields. This avoids repeating validation rules throughout the application.

### Validation Function Contracts

#### `validate_affected_users(value)`
- **Accepts:** Positive integers (1 or greater), excluding booleans.
- **Returns:** The validated integer.
- **Raises `TypeError`:** When the value is not exactly an integer.
- **Raises `ValueError`:** When the integer is less than 1.
- **Side effects:** None.

#### `validate_urgency(value)`
- **Accepts:** Strings representing `low`, `medium`, or `high`.
- **Normalization:** Removes surrounding whitespace and converts to lowercase.
- **Returns:** The normalized urgency string.
- **Raises `TypeError`:** For non-string inputs.
- **Raises `ValueError`:** For invalid urgency values.
- **Side effects:** None.

#### `validate_title(value)`
- **Accepts:** A nonempty string describing a ticket.
- **Normalization:** Removes surrounding whitespace while preserving capitalization.
- **Returns:** The cleaned title.
- **Raises `TypeError`:** For non-string inputs.
- **Raises `ValueError`:** For empty or whitespace-only titles.
- **Side effects:** None.

#### `validate_category(value)`
- **Accepts:** A category representing `Network`, `Hardware`, `Software`, or `Other`.
- **Returns:** A validated, normalized category.
- **Raises `TypeError` or `ValueError`:** For invalid inputs.
- **Side effects:** None.

## Decision 3: Ticket ID Generation

CampusFlow generates a ticket ID using the highest existing numeric ID plus one.

- The first ticket receives `T001`.
- Subsequent IDs follow `T002`, `T003`, and so on.
- Gaps below the highest existing ID are not reused.
- Ticket deletion is not supported in the MVP.

**Trade-off:** This approach is straightforward, but deleting the highest-numbered ticket could allow that ID to be reused. A persistent ID counter could address this in a future version.

## Decision 4: Ticket Creation

### Function Contract: `create_ticket(tickets, title, category, urgency, affected_users)`

**Purpose:** Validate ticket details, calculate priority, generate an ID, and add a new ticket to the in-memory collection.

**Parameters:**
- `tickets`: Dictionary containing existing tickets.
- `title`: Nonempty description of the issue.
- `category`: `Network`, `Hardware`, `Software`, or `Other`.
- `urgency`: `low`, `medium`, or `high`.
- `affected_users`: Positive integer, excluding booleans.

**Behavior:**
1. Validates and normalizes the supplied values.
2. Generates the next ticket ID.
3. Calculates priority from urgency and affected-user count.
4. Creates a ticket with status `open` and `assigned_to` set to `None`.
5. Adds the ticket to the supplied dictionary.

**Returns:** The newly created ticket dictionary.

**Errors:** Invalid input raises `TypeError` or `ValueError`. Validation failure does not create a ticket.

**Side effects:** Adds a ticket to the in-memory dictionary; it does not write to JSON itself.

**Limitations:** Ticket IDs assume existing IDs follow the expected format. The application manages tickets in memory while running; the CLI uses JSON persistence to preserve them between sessions.

## Decision 5: JSON Persistence

### Functions
- `load_tickets(file_path)`
- `save_tickets(tickets, file_path)`

**Purpose:** Preserve ticket records between application sessions without an external database.

### Function Contract: `load_tickets(file_path)`

- **Parameter:** Path to the JSON file.
- **Returns:** Parsed JSON data, expected to be a dictionary of tickets; returns `{}` when the file does not exist.
- **Behavior:** Reads and deserializes JSON without modifying the file.
- **Raises `ValueError`:** For malformed JSON.
- **Raises `OSError`:** For other filesystem read failures.
- **Limitation:** Does not fully validate the structure or individual fields of loaded records. The CLI checks that the top-level result is a dictionary.

### Function Contract: `save_tickets(tickets, file_path)`

- **Parameters:** Complete ticket dictionary and destination file path.
- **Returns:** `None` on success.
- **Preconditions:** The destination directory exists, data is JSON-serializable, and the application has write permission.
- **Behavior:**
  1. Creates a temporary file in the destination directory.
  2. Writes formatted JSON with four-space indentation.
  3. Flushes and synchronizes the temporary file with `os.fsync()`.
  4. Replaces the destination file using `os.replace()`.
  5. Cleans up any remaining temporary file.
- **Raises `OSError`:** For filesystem failures.
- **Raises `TypeError`:** For non-serializable data.
- **Side effects:** Replaces the saved JSON file with the complete supplied collection; does not modify the in-memory dictionary.

### Persistence Design Decisions and Limitations

- Uses Python's built-in `json` module, with no external dependencies.
- The active runtime file is `data/tickets.json`.
- Loads existing tickets at startup before making changes.
- Saves after successful ticket mutations, not after read-only operations.
- Malformed JSON stops startup instead of silently erasing potentially recoverable records.
- Temporary-file replacement reduces the risk of incomplete writes; it does not protect against every hardware or filesystem failure.
- Saving replaces the destination with the supplied dictionary; it does not merge with another file automatically.
- Concurrent writers are not supported; the application assumes a single running process.

## Decision 6: Ticket Workflow

### Functions
- `find_ticket(tickets, ticket_id)`
- `assign_ticket(tickets, ticket_id, mentor)`
- `update_ticket_status(tickets, ticket_id, new_status)`
- `reopen_ticket(tickets, ticket_id)`

### Business Rules

- New tickets begin as `open`.
- A ticket must be assigned before moving to `in_progress`.
- Normal transitions are `open` → `in_progress` → `resolved`.
- A ticket cannot move directly from `open` to `resolved`.
- Resolved tickets must be explicitly reopened before work can begin again.
- Reopening changes the status to `open` and preserves the assignment.
- Repeating the same status transition raises `ValueError`.
- Unknown ticket IDs raise `KeyError`.
- Assigning a ticket does not automatically change its status.

**Design decision:** The CLI asks the administrator to enter the desired status and passes it to `update_ticket_status()`. Workflow rules remain inside `campusflow/workflow.py`; the CLI does not duplicate them.

## Decision 7: Ticket Queries and Reporting

### Functions
- `list_tickets(tickets)`
- `get_open_work_queue(tickets)`
- `get_ticket_report(tickets)`

### Design Decisions

- Ticket listing uses ascending numeric ticket IDs.
- The open work queue contains only tickets with status `open`.
- Open tickets are sorted by priority, highest first.
- Tickets with equal priority are sorted by ascending ticket ID.
- Reports provide a total count and breakdowns by status and priority.
- Empty reports include categories with zero counts.
- Query functions do not modify the ticket collection.

## Phase 7: CLI Integration

### Overview

Phase 7 connects the existing CampusFlow modules into a command-line application. It reuses validation, creation, workflow, storage, and query functions instead of reimplementing business logic in `main.py`.

### `main.py` Responsibilities

- Load previously saved tickets at startup.
- Display the menu and collect administrator input.
- Retry invalid ticket-creation fields individually.
- Call the appropriate business-logic functions.
- Display tickets, work queues, reports, and errors.
- Save successful ticket changes to `data/tickets.json`.
- Exit gracefully when the user chooses `0` or interrupts terminal input.

### Function Contract: `display_menu()`

- **Purpose:** Print the CampusFlow menu.
- **Parameters:** None.
- **Returns:** `None`.
- **Behavior:** Displays options 1–8 and 0; does not read input or change tickets.
- **Side effects:** Prints to the terminal.

### Function Contract: `display_ticket(ticket)`

- **Purpose:** Print the details of one ticket.
- **Parameter:** Ticket dictionary with the expected fields.
- **Returns:** `None`.
- **Behavior:** Displays ID, title, category, urgency, affected users, priority, status, and assigned mentor; prints `Unassigned` when appropriate.
- **Raises `KeyError`:** If a required field is absent.
- **Side effects:** Prints to the terminal; does not modify the ticket.

### Function Contract: `save_changes(tickets)`

- **Purpose:** Save the current ticket collection and report whether saving succeeded.
- **Parameter:** Complete in-memory ticket dictionary.
- **Returns:** `True` on success; `False` if an `OSError` prevents saving.
- **Behavior:** Calls `save_tickets(tickets, FILE_PATH)` and displays filesystem errors.
- **Side effects:** Writes to the configured JSON path on success.

### Function Contract: `main()`

- **Purpose:** Run the menu loop and coordinate CampusFlow operations.
- **Parameters:** None.
- **Returns:** `None`.
- **Preconditions:** Required modules are available, the `data/` directory exists, and the application has the required file permissions.
- **Startup behavior:** Loads saved data; starts empty when the file is missing; stops with an error for malformed JSON, unreadable files, or a non-dictionary top-level JSON value.
- **Runtime behavior:** Processes menu choices, catches expected input/workflow errors, saves mutations, and continues until exit.

### Supported Menu Operations

| Option | Operation | Functions Used |
|---|---|---|
| 1 | Create Ticket | Validation functions, `create_ticket()`, `save_changes()` |
| 2 | View All Tickets | `list_tickets()` |
| 3 | Assign Ticket | `find_ticket()`, `assign_ticket()`, `save_changes()` |
| 4 | View Ticket Details | `find_ticket()`, `display_ticket()` |
| 5 | Update Ticket Status | `find_ticket()`, `update_ticket_status()`, `save_changes()` |
| 6 | Reopen Ticket | `find_ticket()`, `reopen_ticket()`, `save_changes()` |
| 7 | View Open Work Queue | `get_open_work_queue()` |
| 8 | View Reports | `get_ticket_report()` |
| 0 | Exit | Ends the application loop |

**Option 5:** The administrator enters the new status (`in_progress` or `resolved`); `update_ticket_status()` enforces valid transitions. Resolving a ticket is therefore part of option 5, not a separate menu option.

### Error Handling

- Invalid ticket-creation fields prompt the user to retry that field.
- Invalid menu selections display a message and return to the menu.
- Missing ticket IDs and invalid workflow transitions display errors without closing the program.
- Malformed JSON or an unreadable file prevents startup.
- A failed save does not display a success message; the CLI restores the affected in-memory field for assignment/status operations or removes a newly created unsaved ticket.
- `KeyboardInterrupt` and `EOFError` end the CLI session gracefully.

## Data Flow

```text
Application starts
    |
    v
load_tickets() --> in-memory ticket dictionary
    |
    v
Display menu --> collect user input
    |
    v
Call existing validation / workflow / query functions
    |
    +--> Read-only operation --> display result --> menu
    |
    +--> Ticket mutation --> update in-memory dictionary
                                  |
                                  v
                            save_changes()
                                  |
                                  v
                            save_tickets()
                                  |
                                  v
                       Write and sync temporary file
                                  |
                                  v
                         Replace saved JSON file
                                  |
                                  v
                         Display result --> menu
```

## Design Trade-offs

| Decision | Reason |
|---|---|
| Keep CLI logic in `main.py` | Simple structure suitable for this project |
| Keep validation in `validation.py` | Avoid repeating business rules |
| Keep workflow rules in `workflow.py` | Ensure the same rules apply across callers |
| Keep storage in `storage.py` | Separate persistence from ticket management |
| Retry invalid fields individually | Avoid restarting ticket creation for one mistake |
| Use JSON persistence | Meet project requirements without external dependencies |
| Use temporary-file replacement | Reduce the risk of partial writes |
| Stop startup for corrupted JSON | Avoid overwriting potentially recoverable data |

## Known Limitations

1. The application is a command-line MVP, without a graphical interface.
2. Data is stored in local JSON rather than a database server.
3. Concurrent modifications by multiple running instances are not supported.
4. The loader does not validate every field in saved ticket records.
5. Authentication and role-based permissions are not implemented.
6. Temporary-file replacement reduces, but does not eliminate, filesystem failure risks.
7. The CLI handles expected errors; unexpected programming errors are not intentionally suppressed.

## Testing and Verification

CampusFlow uses Python's built-in `unittest` framework. Tests cover input validation, priority calculation, ticket creation, ID generation, storage, assignment, status transitions, reopening, queries, reporting, CLI navigation, invalid inputs, corrupted JSON, and save failures.

Run the test suite from the project root:

```bash
python3 -m unittest discover -s tests -v
```

### Phase 7 Results

- Existing tests: **96**
- Added CLI tests: **23**
- Total tests: **119**
- Reported result: **All tests passed**

Phase 7 was merged into `main`. The completed CLI supports the planned operations and preserves tickets between application sessions.
