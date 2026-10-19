import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

import main


class TestCampusFlowCLI(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.test_file = (
            Path(self.temp_directory.name) / "tickets.json"
        )

        self.file_patch = patch.object(
            main,
            "FILE_PATH",
            str(self.test_file)
        )

        self.file_patch.start()

    def tearDown(self):
        self.file_patch.stop()
        self.temp_directory.cleanup()

    def run_cli(self, inputs):
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                main.main()

    def read_tickets(self):
        with open(self.test_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def sample_ticket(self, status="open", assigned_to=None):
        return {
            "id": "T001",
            "title": "Wi-Fi is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 5,
            "priority": "high",
            "status": status,
            "assigned_to": assigned_to,
        }

    def save_sample_ticket(self, status="open", assigned_to=None):
        ticket = self.sample_ticket(status, assigned_to)

        with open(self.test_file, "w", encoding="utf-8") as file:
            json.dump({"T001": ticket}, file)

    # TEST 1: EXIT APPLICATION
    def test_exit_application(self):
        self.run_cli(["0"])

        self.assertFalse(self.test_file.exists())

    # TEST 2: CREATE TICKET
    def test_create_ticket(self):
        self.run_cli([
            "1",
            "Wi-Fi is down",
            "Network",
            "high",
            "5",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertIn("T001", tickets)
        self.assertEqual(
            tickets["T001"]["title"],
            "Wi-Fi is down"
        )
        self.assertEqual(
            tickets["T001"]["status"],
            "open"
        )

    # TEST 3: INVALID TITLE
    def test_invalid_title_then_valid_title(self):
        self.run_cli([
            "1",
            "",
            "Wi-Fi is down",
            "Network",
            "high",
            "5",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets["T001"]["title"],
            "Wi-Fi is down"
        )

    # TEST 4: INVALID CATEGORY
    def test_invalid_category_then_valid_category(self):
        self.run_cli([
            "1",
            "Wi-Fi is down",
            "Invalid",
            "Network",
            "high",
            "5",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertEqual(
            tickets["T001"]["category"],
            "Network"
        )

    # TEST 5: INVALID URGENCY
    def test_invalid_urgency_then_valid_urgency(self):
        self.run_cli([
            "1",
            "Wi-Fi is down",
            "Network",
            "urgent",
            "high",
            "5",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertEqual(
            tickets["T001"]["urgency"],
            "high"
        )

    # TEST 6: INVALID AFFECTED USERS
    def test_invalid_affected_users_then_valid_number(self):
        self.run_cli([
            "1",
            "Wi-Fi is down",
            "Network",
            "high",
            "abc",
            "0",
            "5",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertEqual(
            tickets["T001"]["affected_users"],
            5
        )

    # TEST 7: LOAD EXISTING TICKETS
    def test_load_existing_tickets(self):
        self.save_sample_ticket()

        self.run_cli(["0"])

        tickets = self.read_tickets()

        self.assertIn("T001", tickets)

    # TEST 8: CREATE TICKET WITHOUT LOSING EXISTING DATA
    def test_create_ticket_preserves_existing_tickets(self):
        self.save_sample_ticket()

        self.run_cli([
            "1",
            "Computer not working",
            "Hardware",
            "medium",
            "2",
            "0",
        ])

        tickets = self.read_tickets()

        self.assertIn("T001", tickets)
        self.assertIn("T002", tickets)
        self.assertEqual(len(tickets), 2)
