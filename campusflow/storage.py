import json
import os
import tempfile

from copy import deepcopy
from pathlib import Path

from campusflow.priority import calculate_priority


def validate_tickets(tickets):

    # The entire collection must be a dictionary.
    if not isinstance(tickets, dict):
        raise ValueError("Tickets must be a dictionary")

    # Check every ticket.
    for ticket_id, ticket in tickets.items():

        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        required_fields = [
            "id",
            "title",
            "category",
            "urgency",
            "affected_users",
            "priority",
            "status",
            "assigned_to"
        ]

        # Check that all required fields exist.
        for field in required_fields:
            if field not in ticket:
                raise ValueError(
                    f"Ticket {ticket_id} is missing {field}"
                )

        # Validate ticket ID.
        if not isinstance(ticket_id, str):
            raise ValueError("Ticket ID must be a string")

        if not ticket_id.startswith("T"):
            raise ValueError("Invalid ticket ID")

        number = ticket_id[1:]

        if len(number) < 3 or not number.isascii() or not number.isdigit():
            raise ValueError("Invalid ticket ID")

        if int(number) < 1:
            raise ValueError("Ticket ID must be greater than zero")

        if ticket["id"] != ticket_id:
            raise ValueError("Ticket ID does not match")

        # Validate title.
        if not isinstance(ticket["title"], str):
            raise ValueError("Title must be a string")

        if ticket["title"].strip() == "":
            raise ValueError("Title cannot be empty")

        # Validate category.
        valid_categories = [
            "Network",
            "Hardware",
            "Software",
            "Other"
        ]

        if ticket["category"] not in valid_categories:
            raise ValueError("Invalid ticket category")

        # Validate urgency.
        valid_urgencies = [
            "low",
            "medium",
            "high"
        ]

        if ticket["urgency"] not in valid_urgencies:
            raise ValueError("Invalid ticket urgency")

        # Validate affected users.
        if type(ticket["affected_users"]) != int:
            raise ValueError("affected_users must be an integer")

        if ticket["affected_users"] < 1:
            raise ValueError("affected_users must be positive")

        # Validate priority.
        expected_priority = calculate_priority(
            ticket["urgency"],
            ticket["affected_users"]
        )

        if ticket["priority"] != expected_priority:
            raise ValueError(
                f"Ticket {ticket_id} has an incorrect priority"
            )

        # Validate status.
        valid_statuses = [
            "open",
            "in_progress",
            "resolved"
        ]

        if ticket["status"] not in valid_statuses:
            raise ValueError("Invalid ticket status")

        # Validate assigned mentor.
        if ticket["assigned_to"] is not None:

            if not isinstance(ticket["assigned_to"], str):
                raise ValueError(
                    "assigned_to must be a string or None"
                )

            if ticket["assigned_to"].strip() == "":
                raise ValueError(
                    "assigned_to cannot be empty"
                )

        # Older tickets may not contain notes.
        if "notes" not in ticket:
            continue

        notes = ticket["notes"]

        if not isinstance(notes, list):
            raise ValueError("Notes must be a list")

        note_ids = []

        for note in notes:

            if not isinstance(note, dict):
                raise ValueError("Each note must be a dictionary")

            required_note_fields = [
                "note_id",
                "author",
                "message"
            ]

            for field in required_note_fields:
                if field not in note:
                    raise ValueError(
                        f"Note is missing {field}"
                    )

            # Validate note ID.
            note_id = note["note_id"]

            if not isinstance(note_id, str):
                raise ValueError("Note ID must be a string")

            if not note_id.startswith("N"):
                raise ValueError("Invalid note ID")

            note_number = note_id[1:]

            if (
                len(note_number) < 3
                or not note_number.isascii()
                or not note_number.isdigit()
            ):
                raise ValueError("Invalid note ID")

            if int(note_number) < 1:
                raise ValueError("Invalid note ID")

            # Reject duplicate note IDs.
            if note_id in note_ids:
                raise ValueError("Duplicate note ID")

            note_ids.append(note_id)

            # Validate author.
            if not isinstance(note["author"], str):
                raise ValueError("Author must be a string")

            if note["author"].strip() == "":
                raise ValueError("Author cannot be empty")

            # Validate message.
            if not isinstance(note["message"], str):
                raise ValueError("Message must be a string")

            message = note["message"].strip()

            if len(message) < 5 or len(message) > 300:
                raise ValueError(
                    "Message must contain 5 to 300 characters"
                )

    return tickets


def check_duplicate_keys(pairs):

    result = {}

    for key, value in pairs:

        if key in result:
            raise ValueError(
                f"Duplicate JSON key: {key}"
            )

        result[key] = value

    return result


def load_tickets(file_path):

    try:
        with open(file_path, "r", encoding="utf-8") as file:

            tickets = json.load(
                file,
                object_pairs_hook=check_duplicate_keys
            )

        # Validate everything before returning it.
        validate_tickets(tickets)

        # Create a separate copy for legacy normalization.
        loaded_tickets = deepcopy(tickets)

        for ticket in loaded_tickets.values():

            if "notes" not in ticket:
                ticket["notes"] = []

        return loaded_tickets

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON: {error}"
        ) from error


def save_tickets(tickets, file_path):

    # Reject invalid data before writing anything.
    validate_tickets(tickets)

    file_path = Path(file_path)

    # Create the data directory if it does not exist.
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False
        ) as file:

            temporary_file = file.name

            json.dump(tickets, file, indent=4)

            file.flush()

            os.fsync(file.fileno())

        # Replace the destination only after writing succeeds.
        os.replace(temporary_file, file_path)

    finally:

        if (
            temporary_file is not None
            and os.path.exists(temporary_file)
        ):
            os.remove(temporary_file)