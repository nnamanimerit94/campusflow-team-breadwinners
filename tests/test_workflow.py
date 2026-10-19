import unittest

from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    reopen_ticket,
    update_ticket_status,
)


class TestTicketAssignment(unittest.TestCase):

    def setUp(self):
        self.tickets = {
            "T001": {
                "id": "T001",
                "title": "Internet not working",
                "status": "open",
                "assigned_to": None,
            },
            "T002": {
                "id": "T002",
                "title": "Laptop issue",
                "status": "resolved",
                "assigned_to": "Grace",
            },
        }

    def test_find_existing_ticket(self):
        ticket = find_ticket(self.tickets, "T001")

        self.assertEqual(ticket["id"], "T001")

    def test_find_nonexistent_ticket(self):
        with self.assertRaises(KeyError):
            find_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        ticket = assign_ticket(self.tickets, "T001", "David")

        self.assertEqual(ticket["assigned_to"], "David")

    def test_assignment_does_not_change_status(self):
        ticket = assign_ticket(self.tickets, "T001", "David")

        self.assertEqual(ticket["status"], "open")

    def test_assignment_updates_original_dictionary(self):
        assign_ticket(self.tickets, "T001", "David")

        self.assertEqual(self.tickets["T001"]["assigned_to"], "David")

    def test_assignment_strips_whitespace(self):
        ticket = assign_ticket(self.tickets, "T001", "  David  ")

        self.assertEqual(ticket["assigned_to"], "David")

    def test_rejects_empty_mentor(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")

    def test_rejects_non_string_mentor(self):
        with self.assertRaises(TypeError):
            assign_ticket(self.tickets, "T001", 123)

    def test_rejects_assignment_to_resolved_ticket(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T002", "David")

    def test_rejects_unknown_ticket(self):
        with self.assertRaises(KeyError):
            assign_ticket(self.tickets, "T999", "David")

    def test_allows_reassignment(self):
        assign_ticket(self.tickets, "T001", "David")

        ticket = assign_ticket(self.tickets, "T001", "Grace")

        self.assertEqual(ticket["assigned_to"], "Grace")


class TestTicketStatusWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = {
            "T001": {"id": "T001", "status": "open", "assigned_to": None},
            "T002": {"id": "T002", "status": "open", "assigned_to": "David"},
            "T003": {"id": "T003", "status": "in_progress", "assigned_to": "Grace"},
            "T004": {"id": "T004", "status": "resolved", "assigned_to": "David"},
        }

    def test_start_work_on_assigned_ticket(self):
        ticket = update_ticket_status(self.tickets, "T002", "in_progress")
        self.assertEqual(ticket["status"], "in_progress")

    def test_cannot_start_unassigned_ticket(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets["T001"]["status"], "open")

    def test_resolve_in_progress_ticket(self):
        ticket = update_ticket_status(self.tickets, "T003", "resolved")
        self.assertEqual(ticket["status"], "resolved")

    def test_cannot_resolve_open_ticket(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T002", "resolved")

    def test_cannot_modify_resolved_ticket_directly(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T004", "in_progress")

    def test_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T002", "pending")

    def test_rejects_non_string_status(self):
        with self.assertRaises(TypeError):
            update_ticket_status(self.tickets, "T002", 123)

    def test_rejects_unknown_ticket(self):
        with self.assertRaises(KeyError):
            update_ticket_status(self.tickets, "T999", "in_progress")

    def test_cannot_move_in_progress_back_to_open(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T003", "open")

    def test_reopen_resolved_ticket(self):
        ticket = reopen_ticket(self.tickets, "T004")
        self.assertEqual(ticket["status"], "open")

    def test_reopen_preserves_assignment(self):
        ticket = reopen_ticket(self.tickets, "T004")
        self.assertEqual(ticket["assigned_to"], "David")

    def test_cannot_reopen_open_ticket(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")

    def test_cannot_reopen_in_progress_ticket(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T003")

    def test_reopen_unknown_ticket(self):
        with self.assertRaises(KeyError):
            reopen_ticket(self.tickets, "T999")
            
    def test_cannot_repeat_in_progress_status(self):
        with self.assertRaises(ValueError):
            update_ticket_status(
            self.tickets, "T003", "in_progress"
        )
            self.assertEqual(
                self.tickets["T003"]["status"],
                "in_progress"
        )
            
    def test_cannot_repeat_open_status(self):
        with self.assertRaises(ValueError):
            update_ticket_status(
            self.tickets, "T002", "open"
            )
            self.assertEqual(
                self.tickets["T002"]["status"],
                "open"
            )
