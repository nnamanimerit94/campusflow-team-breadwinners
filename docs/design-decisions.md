**# CampusFlow Design Decisions**

**## Decision 1: Ticket Collection**
we decided to use a dictionary to store our tickets using the id as the key. This is because of the O(1)n time complexity in terms of lookup, as it is more easier to search a dictionary of dictionary using a key to get its values and in this case the values are a dictionary.

**## Decision 2: Input Validation**
we decided to create a function that specifically handles validating the input separated from the cli input handling first to ensure and have a clear separation of functions that handles it and also keeping the code free from unnecessary repetitive validation check

**## Decision 3: Function Contracts**

Purpose: to have a clear separated function that checks if value of affected_users is an int and the number is greated than or equal to 1 , else if valueerror or typeerror raises an exception

Parameter: it receives the value of the affected&

Accepted values: positive numbers

Return value:first it checks if its a number and it returns the number back if positive

Errors: if theres an error it returns a the actual error raised&#x20;

Side effects:

### Ticket ID Generation

Decision: Generate the next ticket ID using the highest existing ID + 1.

Rules:
- First ticket receives T001.
- IDs use the format T001, T002, T003, etc.
- Missing numbers are not reused while higher IDs exist.
- Ticket deletion is not supported in the MVP.

Trade-off:
This approach is simple but could reuse the highest ID if that
ticket were deleted. A persistent counter may be added later.
## Ticket Creation Contract

### Function
create_ticket(tickets, title, category, urgency, affected_users)

### Purpose
Create a new helpdesk ticket, validate its inputs, calculate
its priority, assign a unique ID, and store it in memory.

### Inputs
- tickets: Dictionary containing existing tickets.
- title: Non-empty string describing the issue.
- category: Network, Hardware, Software, or Other.
- urgency: low, medium, or high.
- affected_users: Positive integer greater than zero.
  Boolean values are not accepted.

### Validation
- Title is stripped of surrounding whitespace.
- Category is validated and normalized.
- Urgency is validated and converted to lowercase.
- Affected users must be a positive integer.
- Invalid inputs raise TypeError or ValueError.

### Generated Fields
- id: Generated using the highest existing ticket ID + 1.
- priority: Calculated from urgency and affected_users.
- status: Initially "open".
- assigned_to: Initially None.

### Output
Returns the newly created ticket as a dictionary.

### Side Effects
- Adds the new ticket to the supplied tickets dictionary.
- Does not modify existing tickets.
- Does not create a ticket if validation fails.

### ID Generation Decision
- First ticket ID is T001.
- Subsequent IDs increase sequentially.
- Missing numbers are not reused while higher IDs exist.
- Ticket deletion is not supported in the MVP.

### Limitations
- Tickets are currently stored in memory.
- Closing the application loses the tickets until JSON
  persistence is implemented.
- The ID generation approach assumes existing IDs are valid.
- Deleting the highest-numbered ticket could cause ID reuse.

## JSON Persistence Contract

### Functions
- save_tickets(tickets, file_path)
- load_tickets(file_path)

### Purpose
Persist tickets between application sessions using JSON files.

### Save Behavior
- Accepts a dictionary of tickets and a destination file path.
- Saves tickets as readable JSON with four-space indentation.
- Returns None on success.
- Allows file-writing and serialization errors to propagate.

### Load Behavior
- Returns saved tickets as a dictionary.
- Returns an empty dictionary if the file does not exist.
- Raises ValueError when the JSON is malformed.
- Does not modify the file during loading.

### Design Decision
Use Python's built-in json module to avoid external dependencies.

### Limitations
- Saving directly to a file can overwrite existing data.
- Atomic file replacement is not yet implemented.
- The current loader checks JSON syntax but does not fully validate
  the structure of saved ticket records.

  Decision 7: Ticket Queries and Reporting

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
