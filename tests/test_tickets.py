import unittest

from campusflow.tickets import generate_ticket_id, create_ticket

class TestGenerateTicketID(unittest.TestCase):

    def test_first_ticket_id(self):
        tickets = {}

        result = generate_ticket_id(tickets)

        self.assertEqual(result, "T001")

    def test_next_sequential_id(self):
        tickets = {
            "T001": {},
            "T002": {},
            "T003": {}
        }

        result = generate_ticket_id(tickets)

        self.assertEqual(result, "T004")

    def test_does_not_fill_gaps(self):
        tickets = {
            "T001": {},
            "T002": {},
            "T005": {}
        }

        result = generate_ticket_id(tickets)

        self.assertEqual(result, "T006")

    def test_id_format_after_nine(self):
        tickets = {
            "T009": {}
        }

        result = generate_ticket_id(tickets)

        self.assertEqual(result, "T010")

    def test_id_format_after_ninety_nine(self):
        tickets = {
            "T099": {}
        }

        result = generate_ticket_id(tickets)

        self.assertEqual(result, "T100")

    def test_does_not_modify_existing_tickets(self):
        tickets = {
            "T001": {"title": "Internet issue"}
        }

        original = {
            "T001": {"title": "Internet issue"}
        }

        generate_ticket_id(tickets)

        self.assertEqual(tickets, original)

class TestCreateTicket(unittest.TestCase):

    def test_creates_ticket_with_correct_fields(self):
        tickets = {}

        ticket = create_ticket(
            tickets,
            "Internet not working",
            "network",
            "high",
            15
        )

        self.assertEqual(ticket, {
            "id": "T001",
            "title": "Internet not working",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None
        })

    def test_creates_sequential_tickets(self):
        tickets = {}

        first = create_ticket(
            tickets, "Internet issue", "network", "low", 1
        )

        second = create_ticket(
            tickets, "Laptop issue", "hardware", "medium", 3
        )

        self.assertEqual(first["id"], "T001")
        self.assertEqual(second["id"], "T002")
        self.assertEqual(len(tickets), 2)

    def test_stores_created_ticket(self):
        tickets = {}

        ticket = create_ticket(
            tickets, "Software issue", "software", "low", 2
        )

        self.assertIn("T001", tickets)
        self.assertEqual(tickets["T001"], ticket)

    def test_rejects_invalid_title(self):
        tickets = {}

        with self.assertRaises(ValueError):
            create_ticket(tickets, " ", "network", "high", 5)

        self.assertEqual(tickets, {})

    def test_rejects_invalid_category(self):
        tickets = {}

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Internet issue", "finance", "high", 5)

        self.assertEqual(tickets, {})

    def test_rejects_invalid_urgency(self):
        tickets = {}

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Internet issue", "network", "urgent", 5)

        self.assertEqual(tickets, {})

    def test_rejects_invalid_affected_users(self):
        tickets = {}

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Internet issue", "network", "high", 0)

        self.assertEqual(tickets, {})