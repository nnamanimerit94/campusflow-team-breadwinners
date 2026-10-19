import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import save_tickets, load_tickets


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