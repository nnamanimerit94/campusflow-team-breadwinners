import json
import os
import tempfile
from pathlib import Path


def validate_tickets(tickets):

    # The entire tickets collection must be a dictionary.
    if not isinstance(tickets, dict):
        raise ValueError("Tickets must be a dictionary")

    # Go through each ticket.
    for ticket_id, ticket in tickets.items():

        # Each ticket must also be a dictionary.
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        # These fields must exist in every ticket.
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

        for field in required_fields:
            if field not in ticket:
                raise ValueError(
                    f"Ticket {ticket_id} is missing {field}"
                )

        # The ticket ID must match its dictionary key.
        if ticket["id"] != ticket_id:
            raise ValueError("Ticket ID does not match")

        # Check that these fields contain strings.
        string_fields = [
            "id",
            "title",
            "category",
            "urgency",
            "priority",
            "status"
        ]

        for field in string_fields:
            if not isinstance(ticket[field], str):
                raise ValueError(
                    f"{field} must be a string"
                )

            if ticket[field].strip() == "":
                raise ValueError(
                    f"{field} cannot be empty"
                )

        # affected_users must be a positive integer.
        if type(ticket["affected_users"]) != int:
            raise ValueError("affected_users must be an integer")

        if ticket["affected_users"] < 1:
            raise ValueError("affected_users must be positive")

        # assigned_to can be None or a non-empty string.
        if ticket["assigned_to"] is not None:

            if not isinstance(ticket["assigned_to"], str):
                raise ValueError("assigned_to must be a string or None")

            if ticket["assigned_to"].strip() == "":
                raise ValueError("assigned_to cannot be empty")

        # Check the ticket status.
        valid_statuses = ["open", "in_progress", "resolved"]

        if ticket["status"] not in valid_statuses:
            raise ValueError("Invalid ticket status")

        # Older tickets may not have notes.
        # But if notes exists, it must be a list.
        if "notes" in ticket:

            notes = ticket["notes"]

            if not isinstance(notes, list):
                raise ValueError("Notes must be a list")

            note_ids = []

            # Check each note.
            for note in notes:

                if not isinstance(note, dict):
                    raise ValueError("Each note must be a dictionary")

                # Check required note fields.
                if "note_id" not in note:
                    raise ValueError("Note is missing note_id")

                if "author" not in note:
                    raise ValueError("Note is missing author")

                if "message" not in note:
                    raise ValueError("Note is missing message")

                # Validate note ID.
                note_id = note["note_id"]

                if not isinstance(note_id, str):
                    raise ValueError("Note ID must be a string")

                if not note_id.startswith("N"):
                    raise ValueError("Invalid note ID")

                number = note_id[1:]

                if len(number) < 3 or not number.isdigit():
                    raise ValueError("Invalid note ID")

                # Prevent duplicate note IDs.
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
    """
    Reject repeated keys when reading JSON.
    """

    result = {}

    for key, value in pairs:

        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")

        result[key] = value

    return result


def load_tickets(file_path):

    try:
        with open(file_path, "r", encoding="utf-8") as file:

            tickets = json.load(
                file,
                object_pairs_hook=check_duplicate_keys
            )

        validate_tickets(tickets)

        return tickets

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {error}") from error


def save_tickets(tickets, file_path):

    # Check the data before saving.
    validate_tickets(tickets)

    file_path = Path(file_path)

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

        os.replace(temporary_file, file_path)

    finally:
        if temporary_file is not None and os.path.exists(temporary_file):
            os.remove(temporary_file)