import unittest

from campusflow.queries import (
    list_tickets,
    get_open_work_queue,
    get_ticket_report,
)


class TestTicketQueries(unittest.TestCase):

    def setUp(self):
        self.tickets = {
            "T005": {
                "id": "T005",
                "priority": "low",
                "status": "open",
            },
            "T003": {
                "id": "T003",
                "priority": "critical",
                "status": "open",
            },
            "T001": {
                "id": "T001",
                "priority": "medium",
                "status": "open",
            },
            "T004": {
                "id": "T004",
                "priority": "high",
                "status": "resolved",
            },
            "T002": {
                "id": "T002",
                "priority": "high",
                "status": "in_progress",
            },
            "T007": {
                "id": "T007",
                "priority": "critical",
                "status": "open",
            },
        }

    def test_list_all_tickets(self):
        result = list_tickets(self.tickets)

        self.assertEqual(len(result), 6)

    def test_list_tickets_sorted_by_id(self):
        result = list_tickets(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T002", "T003", "T004", "T005", "T007"]
        )

    def test_list_empty_tickets(self):
        self.assertEqual(list_tickets({}), [])

    def test_queue_contains_only_open_tickets(self):
        result = get_open_work_queue(self.tickets)

        self.assertTrue(
            all(ticket["status"] == "open" for ticket in result)
        )

    def test_queue_sorted_by_priority_and_id(self):
        result = get_open_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T003", "T007", "T001", "T005"]
        )

    def test_empty_queue(self):
        self.assertEqual(get_open_work_queue({}), [])

    def test_queue_excludes_resolved_and_in_progress(self):
        result = get_open_work_queue(self.tickets)

        ids = [ticket["id"] for ticket in result]

        self.assertNotIn("T002", ids)
        self.assertNotIn("T004", ids)

    def test_report_total(self):
        report = get_ticket_report(self.tickets)

        self.assertEqual(report["total"], 6)

    def test_report_by_status(self):
        report = get_ticket_report(self.tickets)

        self.assertEqual(
            report["by_status"],
            {
                "open": 4,
                "in_progress": 1,
                "resolved": 1,
            }
        )

    def test_report_by_priority(self):
        report = get_ticket_report(self.tickets)

        self.assertEqual(
            report["by_priority"],
            {
                "critical": 2,
                "high": 2,
                "medium": 1,
                "low": 1,
            }
        )

    def test_empty_report(self):
        report = get_ticket_report({})

        self.assertEqual(
            report,
            {
                "total": 0,
                "by_status": {
                    "open": 0,
                    "in_progress": 0,
                    "resolved": 0,
                },
                "by_priority": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                },
            }
        )

    def test_queries_do_not_modify_original_tickets(self):
        import copy

        original = copy.deepcopy(self.tickets)

        list_tickets(self.tickets)
        get_open_work_queue(self.tickets)
        get_ticket_report(self.tickets)

        self.assertEqual(self.tickets, original)