import unittest

from campusflow.workflow import add_note
from copy import deepcopy
from campusflow.workflow import get_notes
from campusflow.workflow import (
    assign_ticket,
    find_ticket,
    reopen_ticket,
    update_ticket_status,
)
import copy

class TestAddNote(unittest.TestCase):

    def test_add_note_preserves_existing_notes(self):

        tickets = {
            "T001": {
                "id": "T001",
                "title": "pebbles",
                "category": "Other",
                "urgency": "low",
                "affected_users": 3,
                "priority": "medium",
                "status": "open",
                "assigned_to": None,
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "John",
                        "message": "The computer is faulty"
                    },
                    {
                        "note_id": "N002",
                        "author": "Mary",
                        "message": "Technician has been contacted"
                    }
                ]
            }
        }

        # Preserve the original notes before adding another
        original_notes = copy.deepcopy(tickets["T001"]["notes"])

        # Add a new note
        new_note = add_note(
            tickets,
            "T001",
            "David",
            "Technician has arrived"
        )

        # 1. Verify that the number of notes increased to 3
        self.assertEqual(
            len(tickets["T001"]["notes"]),
            3
        )

        # 2. Verify that all previous notes remain unchanged
        self.assertEqual(
            tickets["T001"]["notes"][:2],
            original_notes
        )

        # 3. Verify that the new note has the correct ID
        self.assertEqual(
            new_note["note_id"],
            "N003"
        )

        # 4. Verify that the new note was appended at the end
        self.assertEqual(
            tickets["T001"]["notes"][-1],
            new_note
        )

        # 5. Verify the new note's author and message
        self.assertEqual(
            new_note["author"],
            "David"
        )

        self.assertEqual(
            new_note["message"],
            "Technician has arrived"
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

    def test_resolved_ticket_assignment_preserves_entire_collection(self):
        before = deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            assign_ticket(
                self.tickets,
                "T002",
                "Another Mentor"
                )
        self.assertEqual(self.tickets, before)


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

    def test_unassigned_ticket_transition_preserves_entire_collection(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            update_ticket_status(
                self.tickets,
                "T001",
                "in_progress"
                )
        self.assertEqual(self.tickets, before)

class TestTicketNotes(unittest.TestCase):

    def setUp(self):
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

    def test_add_first_note_to_ticket(self):
        note = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Wi-Fi router reboot attempted"
        )

        expected_note = {
            "note_id": "N001",
            "author": "Mentor A",
            "message": "Wi-Fi router reboot attempted"
        }

        self.assertEqual(note, expected_note)

        self.assertEqual(
            self.tickets["T001"]["notes"],
            [expected_note]
        )
class TestNoteValidation(unittest.TestCase):

    def setUp(self):
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
            },
            "T002": {
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
        }

    def test_first_note_id_is_independent_per_ticket(self):
        first = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Checking the router"
        )

        second = add_note(
            self.tickets,
            "T002",
            "Mentor B",
            "Checking the projector"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N001")

    def test_second_note_receives_next_id(self):
        add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Router restarted"
        )

        second = add_note(
            self.tickets,
            "T001",
            "Mentor B",
            "Connection restored"
        )

        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(len(self.tickets["T001"]["notes"]), 2)

    def test_resolved_ticket_rejects_note_without_mutation(self):
        self.tickets["T001"]["status"] = "resolved"

        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Mentor A",
                "Trying another fix"
            )

        self.assertEqual(self.tickets, before)

    def test_blank_author_is_rejected_without_mutation(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "   ",
                "Checking the router"
            )

        self.assertEqual(self.tickets, before)

    def test_message_shorter_than_five_characters_is_rejected(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Mentor A",
                "abcd"
            )

        self.assertEqual(self.tickets, before)

    def test_message_with_exactly_five_characters_is_accepted(self):
        note = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "abcde"
        )

        self.assertEqual(note["message"], "abcde")
        self.assertEqual(note["note_id"], "N001")

    def test_message_with_exactly_300_characters_is_accepted(self):
        message = "a" * 300

        note = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            message
        )

        self.assertEqual(len(note["message"]), 300)
        self.assertEqual(note["message"], message)

    def test_message_with_301_characters_is_rejected(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Mentor A",
                "a" * 301
            )

        self.assertEqual(self.tickets, before)

    def test_invalid_note_does_not_consume_note_id(self):
        first = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Initial investigation"
        )

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Mentor B",
                "bad"
            )

        second = add_note(
            self.tickets,
            "T001",
            "Mentor B",
            "Investigation completed"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(len(self.tickets["T001"]["notes"]), 2)

    def test_unknown_ticket_does_not_modify_collection(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(KeyError):
            add_note(
                self.tickets,
                "T999",
                "Mentor A",
                "Checking the router"
            )

        self.assertEqual(self.tickets, before)

    def test_author_and_message_are_trimmed(self):
        note = add_note(
            self.tickets,
            "T001",
            "  Mentor A  ",
            "  Router restarted  "
        )

        self.assertEqual(note["author"], "Mentor A")
        self.assertEqual(note["message"], "Router restarted")

    def test_non_string_author_is_rejected(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(TypeError):
            add_note(
                self.tickets,
                "T001",
                123,
                "Checking the router"
            )

        self.assertEqual(self.tickets, before)

    def test_non_string_message_is_rejected(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(TypeError):
            add_note(
                self.tickets,
                "T001",
                "Mentor A",
                123
            )

        self.assertEqual(self.tickets, before)
    def test_add_note_to_legacy_ticket_without_notes_key(self):
        del self.tickets["T001"]["notes"]
        new_note = add_note(
            self.tickets,
            "T001",
            "Mentor A",
            "Router investigation started"
        )
        self.assertEqual(new_note["note_id"], "N001")
        self.assertEqual(new_note["author"], "Mentor A")
        self.assertEqual(
            new_note["message"],
            "Router investigation started"
        )
        self.assertIn("notes", self.tickets["T001"])
        self.assertEqual(
            self.tickets["T001"]["notes"],
            [new_note]
        )

class TestGetNotes(unittest.TestCase):

    def setUp(self):
        self.tickets = {
            "T001": {
                "id": "T001",
                "title": "Wi-Fi unavailable",
                "status": "open",
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "Mentor A",
                        "message": "Router restarted"
                    },
                    {
                        "note_id": "N002",
                        "author": "Mentor B",
                        "message": "Connection restored"
                    }
                ]
            },
            "T002": {
                "id": "T002",
                "title": "Broken projector",
                "status": "open",
                "notes": []
            },
            "T003": {
                "id": "T003",
                "title": "Software installation",
                "status": "resolved"
                # Legacy ticket without a notes key
            }
        }

    def test_get_notes_returns_existing_notes(self):
        notes = get_notes(self.tickets, "T001")

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["note_id"], "N001")
        self.assertEqual(notes[1]["note_id"], "N002")

    def test_get_notes_preserves_note_order(self):
        notes = get_notes(self.tickets, "T001")

        self.assertEqual(
            [note["note_id"] for note in notes],
            ["N001", "N002"]
        )

    def test_get_notes_returns_empty_list_for_ticket_without_notes(self):
        notes = get_notes(self.tickets, "T002")

        self.assertEqual(notes, [])

    def test_get_notes_supports_legacy_ticket(self):
        notes = get_notes(self.tickets, "T003")

        self.assertEqual(notes, [])
        self.assertNotIn("notes", self.tickets["T003"])

    def test_get_notes_rejects_unknown_ticket(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(KeyError):
            get_notes(self.tickets, "T999")

        self.assertEqual(self.tickets, before)

    def test_get_notes_does_not_modify_ticket_collection(self):
        before = deepcopy(self.tickets)

        get_notes(self.tickets, "T001")
        get_notes(self.tickets, "T002")
        get_notes(self.tickets, "T003")

        self.assertEqual(self.tickets, before)

    def test_get_notes_does_not_mix_notes_between_tickets(self):
        notes = get_notes(self.tickets, "T001")

        self.assertEqual(len(notes), 2)

        self.assertEqual(
            get_notes(self.tickets, "T002"),
            []
        )

    def test_get_notes_allows_reading_resolved_ticket(self):
        self.tickets["T001"]["status"] = "resolved"

        notes = get_notes(self.tickets, "T001")

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["note_id"], "N001")


class TestGetNotesBugHunters(unittest.TestCase):

    def setUp(self):
        self.tickets = {
            "T001": {
                "id": "T001",
                "status": "open",
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "Mentor A",
                        "message": "First investigation"
                    },
                    {
                        "note_id": "N002",
                        "author": "Mentor B",
                        "message": "Second investigation"
                    }
                ]
            },
            "T002": {
                "id": "T002",
                "status": "resolved",
                "notes": []
            },
            "T003": {
                "id": "T003",
                "status": "open"
            }
        }

    def test_returned_list_cannot_clear_stored_notes(self):
        notes = get_notes(self.tickets, "T001")

        notes.clear()

        self.assertEqual(len(self.tickets["T001"]["notes"]), 2)

    def test_returned_note_cannot_modify_stored_note(self):
        notes = get_notes(self.tickets, "T001")

        notes[0]["message"] = "Changed without permission"

        self.assertEqual(
            self.tickets["T001"]["notes"][0]["message"],
            "First investigation"
        )

    def test_returned_list_cannot_append_to_stored_notes(self):
        notes = get_notes(self.tickets, "T001")

        notes.append({
            "note_id": "N999",
            "author": "Unknown",
            "message": "Injected note"
        })

        self.assertEqual(len(self.tickets["T001"]["notes"]), 2)

    def test_legacy_ticket_remains_unchanged(self):
        before = deepcopy(self.tickets)

        notes = get_notes(self.tickets, "T003")

        self.assertEqual(notes, [])
        self.assertEqual(self.tickets, before)

    def test_unknown_ticket_preserves_collection(self):
        before = deepcopy(self.tickets)

        with self.assertRaises(KeyError):
            get_notes(self.tickets, "T999")

        self.assertEqual(self.tickets, before)

    def test_large_note_collection(self):
        self.tickets["T001"]["notes"] = [
            {
                "note_id": f"N{i:03d}",
                "author": "Mentor A",
                "message": f"Investigation number {i}"
            }
            for i in range(1, 10001)
        ]

        notes = get_notes(self.tickets, "T001")

        self.assertEqual(len(notes), 10000)
        self.assertEqual(notes[0]["note_id"], "N001")
        self.assertEqual(notes[-1]["note_id"], "N10000")

    def test_notes_from_one_ticket_do_not_affect_another(self):
        first_notes = get_notes(self.tickets, "T001")
        second_notes = get_notes(self.tickets, "T002")

        self.assertEqual(len(first_notes), 2)
        self.assertEqual(second_notes, [])

        first_notes.clear()

        self.assertEqual(
            len(self.tickets["T001"]["notes"]),
            2
        )
        self.assertEqual(self.tickets["T002"]["notes"], [])