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