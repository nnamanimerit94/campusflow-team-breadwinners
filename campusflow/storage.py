import json
import os
import tempfile
from pathlib import Path


def load_tickets(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON: {error}") from error


def save_tickets(tickets, file_path):
    file_path = Path(file_path)

    temporary_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False,
        ) as file:

            temporary_file = file.name

            json.dump(tickets, file, indent=4)

            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_file, file_path)

    finally:
        if temporary_file is not None and os.path.exists(temporary_file):
            os.remove(temporary_file)