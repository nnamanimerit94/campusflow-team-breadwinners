def find_ticket(tickets, ticket_id):
    if ticket_id not in tickets:
        raise KeyError("Key does not exist ")

    return tickets[ticket_id]


def assign_ticket(tickets, ticket_id, raw_mentor):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(raw_mentor, str):
        raise TypeError("mentor must be a string")

    mentor = raw_mentor.strip()

    if mentor == "":
        raise ValueError("mentor cannot be empty")

    if ticket["assigned_to"] == mentor:
        raise ValueError(f"tickets already assigned to {ticket["assigned_to"]}")
    if ticket["status"] == "resolved":
        raise ValueError(
            "tickets already resolved and has no permissions for modification"
        )

    ticket["assigned_to"] = mentor

    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError(f"ticket still {ticket["status"]}")

    ticket["status"] = "open"

    return ticket


def update_ticket_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise TypeError("new status must be a string")

    cleaned_new_status = new_status.strip()

    current_status = ticket["status"]

    if cleaned_new_status not in ["open", "in_progress", "resolved"]:
        raise ValueError("Invalid new status")

    if current_status == "resolved":
        raise ValueError(
            f"tickets already '{current_status}' and status cannot be changed unless reopened"
        )

    if cleaned_new_status == current_status:
        raise ValueError(f"ticket already {current_status}")

    if current_status == "open" and cleaned_new_status == "in_progress":
        if ticket["assigned_to"] is None:
            raise ValueError("Assign a mentor before starting work")
        ticket["status"] = cleaned_new_status

    elif current_status == "in_progress" and cleaned_new_status == "resolved":
        ticket["status"] = cleaned_new_status

    else:
        raise ValueError(
            "invalid transition from '{current_status}' to '{cleaned_new_status}'"
        )

    return ticket
