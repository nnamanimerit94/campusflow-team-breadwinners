from copy import deepcopy

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

def next_note_id(ticket):
    """
    Generate the next note ID for a specific ticket.
    """
    notes = ticket.get("notes",[])

    if not notes:
        return "N001"

    high = 0

    for note in notes:

        number = int(note["note_id"][1:])

        if number > high:

            high = number

    note_id = high+1

    return f"N{note_id:03d}"



def add_note(tickets, ticket_id, author, message):
    """
    Add a validated follow-up note to an existing ticket.
    """

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError("Cannot add note to a resolved ticket unless it is reopened")

    if not isinstance(author, str):
        raise TypeError("author name must be a string")

    if not isinstance(message, str):
        raise TypeError("message must be a string")

    cleaned_author = author.strip()
    cleaned_message = message.strip()

    if cleaned_author == "":
        raise ValueError("Author's name must not be empty")

    if cleaned_message =="":
        raise ValueError("Message must not be empty")

    if len(cleaned_message) < 5 or len(cleaned_message) > 300:
        raise ValueError("Message characters must be greater than or equal to 5 and less than or equal to 300")

    new_note = {
        "note_id": next_note_id(ticket),
        "author": cleaned_author,
        "message": cleaned_message
    }
    ticket.setdefault("notes",[])
    ticket["notes"].append(new_note)
    return new_note

def get_notes(tickets, ticket_id):
    """
    Return the notes belonging to a specific ticket.
    """
    ticket = find_ticket(tickets, ticket_id)

    if not ticket.get("notes"):
        return []

    if not isinstance(ticket["notes"], list):
        raise TypeError("notes must be a list")
    copied_notes= deepcopy(ticket["notes"])

    copied_notes.sort(key=lambda note: int(note["note_id"][1:]))

    return copied_notes