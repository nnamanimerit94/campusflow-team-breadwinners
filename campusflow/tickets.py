from campusflow.validation import (
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
)

from campusflow.priority import calculate_priority

tickets = {}

def generate_ticket_id(tickets):
    if not tickets:
        return "T001"

    highest = 0
    for key in tickets:
        number = int(key[1:])
        if number > highest:
            highest = number

    next_number = highest+1
    return f"T{next_number:03d}"

    
def create_ticket(tickets, title, category, urgency,affected_users):
   titled = validate_title(title)
   categorize = validate_category(category)
   urgent = validate_urgency(urgency)
   affected = validate_affected_users(affected_users)

   ticket = {
    "id": generate_ticket_id(tickets),
    "title": titled,
    "category": categorize,
    "urgency": urgent,
    "affected_users": affected,
    "priority": calculate_priority(urgent, affected),
    "status": "open",
    "assigned_to": None
   }

   tickets[ticket["id"]] = ticket

   return ticket