import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import save_tickets, load_tickets
from campusflow.storage import save_tickets, load_tickets
from campusflow.workflow import add_note

from copy import deepcopy


class TestTicketStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_dictionary(self):
        result = load_tickets(self.file_path)

        self.assertEqual(result, {})

    def test_save_creates_json_file(self):
        tickets = {
            "T001": {
                "id": "T001",
                "title": "Internet issue",
                "status": "open"
            }
        }

        save_tickets(tickets, self.file_path)

        self.assertTrue(self.file_path.exists())

    def test_save_and_load_tickets(self):
        tickets = {
            "T001": {
                "id": "T001",
                "title": "Internet issue",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None
            }
        }

        save_tickets(tickets, self.file_path)
        loaded = load_tickets(self.file_path)

        self.assertEqual(loaded, tickets)

    def test_save_returns_none(self):
        result = save_tickets({}, self.file_path)

        self.assertIsNone(result)

    def test_saved_file_contains_valid_json(self):
        tickets = {"T001": {"title": "Laptop issue"}}

        save_tickets(tickets, self.file_path)

        with open(self.file_path, "r", encoding="utf-8") as file:
            loaded = json.load(file)

        self.assertEqual(loaded, tickets)

    def test_corrupted_json_raises_value_error(self):
        self.file_path.write_text(
            '{"T001": ',
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_corrupted_json_is_not_overwritten(self):
        original_content = '{"T001": '

        self.file_path.write_text(
            original_content,
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            original_content
        )

    def test_empty_dictionary_can_be_saved_and_loaded(self):
        save_tickets({}, self.file_path)

        result = load_tickets(self.file_path)

        self.assertEqual(result, {})


class TestNotesPersistence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

        self.tickets = {
            "T001": {
                "id": "T001",
                "title": "Wi-Fi unavailable",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": []
            }
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_notes_survive_save_and_reload(self):
        add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Router restarted"
        )

        add_note(
            self.tickets,
            "T001",
            "Mentor B",
            "Connection restored"
        )

        save_tickets(self.tickets, self.file_path)

        loaded = load_tickets(self.file_path)

        self.assertEqual(
            loaded["T001"]["notes"],
            self.tickets["T001"]["notes"]
        )

        self.assertEqual(
            len(loaded["T001"]["notes"]),
            2
        )

    def test_note_ids_continue_after_reload(self):
        add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Router restarted"
        )

        save_tickets(self.tickets, self.file_path)

        loaded = load_tickets(self.file_path)

        new_note = add_note(
            loaded,
            "T001",
            "Mentor B",
            "Connection restored"
        )

        self.assertEqual(new_note["note_id"], "N002")

    def test_multiple_tickets_preserve_independent_notes(self):
        self.tickets["T002"] = {
            "id": "T002",
            "title": "Broken projector",
            "category": "Hardware",
            "urgency": "medium",
            "affected_users": 3,
            "priority": "medium",
            "status": "open",
            "assigned_to": None,
            "notes": []
        }

        add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Checking the router"
        )

        add_note(
            self.tickets,
            "T002",
            "Mentor B",
            "Checking the projector"
        )

        save_tickets(self.tickets, self.file_path)

        loaded = load_tickets(self.file_path)

        self.assertEqual(
            loaded["T001"]["notes"][0]["note_id"],
            "N001"
        )

        self.assertEqual(
            loaded["T002"]["notes"][0]["note_id"],
            "N001"
        )

    def test_legacy_ticket_survives_save_and_reload(self):
        del self.tickets["T001"]["notes"]

        save_tickets(self.tickets, self.file_path)

        loaded = load_tickets(self.file_path)

        self.assertEqual(
            loaded["T001"]["id"],
            "T001"
        )

        # Legacy tickets remain readable even without notes.
        self.assertEqual(
            loaded["T001"].get("notes", []),
            []
        )

class TestStorageBugHunters(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

        self.valid_ticket = {
            "id": "T001",
            "title": "Wi-Fi unavailable",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": []
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_json(self, data):
        """Write test data directly, bypassing save_tickets()."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def test_rejects_missing_required_ticket_field(self):
        ticket = deepcopy(self.valid_ticket)

        del ticket["title"]

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_notes_that_are_not_a_list(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["notes"] = "Invalid notes structure"

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_note_missing_required_field(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Mentor A"
                # Missing message
            }
        ]

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_duplicate_note_ids_within_ticket(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "Router restarted"
            },
            {
                "note_id": "N001",
                "author": "Mentor B",
                "message": "Connection restored"
            }
        ]

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_ticket_id_mismatch(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["id"] = "T002"

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_invalid_ticket_collection_type(self):
        self.write_json([
            self.valid_ticket
        ])

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_invalid_note_message_length(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["notes"] = [
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "bad"
            }
        ]

        self.write_json({"T001": ticket})

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_duplicate_ticket_keys_in_raw_json(self):
        # json.dump() cannot produce duplicate dictionary keys,
        # so we deliberately write raw JSON.
        raw_json = """
        {
            "T001": {
                "id": "T001",
                "title": "First ticket"
            },
            "T001": {
                "id": "T001",
                "title": "Second ticket"
            }
        }
        """

        self.file_path.write_text(raw_json, encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_rejects_corrupted_json_without_overwriting_file(self):
        corrupted_content = '{"T001": {"id": "T001",'

        self.file_path.write_text(
            corrupted_content,
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            corrupted_content
        )

    def test_rejects_invalid_note_without_changing_valid_file(self):
        ticket = deepcopy(self.valid_ticket)

        ticket["notes"] = "Invalid notes structure"

        self.write_json({"T001": ticket})

        original_content = self.file_path.read_text(
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

        self.assertEqual(
            self.file_path.read_text(encoding="utf-8"),
            original_content
        )