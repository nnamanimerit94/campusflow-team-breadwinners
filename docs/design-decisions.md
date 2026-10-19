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