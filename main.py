from campusflow.tickets import create_ticket

from campusflow.storage import load_tickets, save_tickets

from campusflow.validation import (
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
)

from campusflow.workflow import (
    find_ticket,
    assign_ticket,
    update_ticket_status,
    reopen_ticket,
)

from campusflow.queries import (
    list_tickets,
    get_open_work_queue,
    get_ticket_report,
)


FILE_PATH = "data/tickets.json"


def display_menu():
    print("\n====================================")
    print("             CAMPUSFLOW")
    print("====================================")
    print("1. Create Ticket")
    print("2. View All Tickets")
    print("3. Assign Ticket")
    print("4. View Ticket Details")
    print("5. Update Ticket Status")
    print("6. Reopen Ticket")
    print("7. View Open Work Queue")
    print("8. View Reports")
    print("0. Exit")


def display_ticket(ticket):
    print("\n------------------------------------")
    print(f"Ticket ID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected Users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Assigned To: {ticket['assigned_to'] or 'Unassigned'}")
    print("------------------------------------")


def save_changes(tickets):
    try:
        save_tickets(tickets, FILE_PATH)
        return True

    except OSError as error:
        print(f"Error saving tickets: {error}")
        return False


def main():

    try:
        tickets = load_tickets(FILE_PATH)

        if not isinstance(tickets, dict):
            print("Unable to start CampusFlow: ticket data must be a dictionary.")
            return

    except (ValueError, OSError) as error:
        print(f"Unable to start CampusFlow: {error}")
        return

    print("\nWelcome to CampusFlow!")

    while True:

        try:
            display_menu()

            choice = input("\nEnter your choice: ").strip()

            # CREATE TICKET
            if choice == "1":

                print("\n--- Create Ticket ---")

                while True:
                    try:
                        title = validate_title(
                            input("Enter ticket title: ")
                        )
                        break

                    except (ValueError, TypeError) as error:
                        print(f"Error: {error}")

                while True:
                    try:
                        category = validate_category(
                            input(
                                "Enter category (Network/Hardware/Software/Other): "
                            )
                        )
                        break

                    except (ValueError, TypeError) as error:
                        print(f"Error: {error}")

                while True:
                    try:
                        urgency = validate_urgency(
                            input("Enter urgency (low/medium/high): ")
                        )
                        break

                    except (ValueError, TypeError) as error:
                        print(f"Error: {error}")

                while True:
                    try:
                        affected_users = int(
                            input("Enter number of affected users: ")
                        )

                        affected_users = validate_affected_users(
                            affected_users
                        )
                        break

                    except (ValueError, TypeError) as error:
                        print(f"Error: {error}")

                try:
                    ticket = create_ticket(
                        tickets,
                        title,
                        category,
                        urgency,
                        affected_users
                    )

                    if save_changes(tickets):
                        print("\nTicket created successfully!")
                        display_ticket(ticket)

                    else:
                        tickets.pop(ticket["id"], None)
                        print("Ticket creation was not saved.")

                except (ValueError, TypeError) as error:
                    print(f"Unable to create ticket: {error}")

            # VIEW ALL TICKETS
            elif choice == "2":

                all_tickets = list_tickets(tickets)

                if not all_tickets:
                    print("\nNo tickets available.")

                else:
                    print("\n--- All Tickets ---")

                    for ticket in all_tickets:
                        print(
                            f"{ticket['id']} | "
                            f"{ticket['title']} | "
                            f"Priority: {ticket['priority']} | "
                            f"Status: {ticket['status']}"
                        )

            # ASSIGN TICKET
            elif choice == "3":

                ticket_id = input(
                    "Enter ticket ID: "
                ).strip().upper()

                mentor = input("Enter mentor name: ")

                try:
                    ticket = find_ticket(tickets, ticket_id)

                    old_mentor = ticket["assigned_to"]

                    assign_ticket(tickets, ticket_id, mentor)

                    if save_changes(tickets):
                        print("\nTicket assigned successfully!")
                        display_ticket(ticket)

                    else:
                        ticket["assigned_to"] = old_mentor
                        print("Assignment was not saved.")

                except (KeyError, ValueError, TypeError) as error:
                    print(f"Error: {error}")

            # VIEW TICKET DETAILS
            elif choice == "4":

                ticket_id = input(
                    "Enter ticket ID: "
                ).strip().upper()

                try:
                    ticket = find_ticket(tickets, ticket_id)
                    display_ticket(ticket)

                except KeyError:
                    print("Ticket not found.")

            # UPDATE TICKET STATUS
            elif choice == "5":

                ticket_id = input(
                    "Enter ticket ID: "
                ).strip().upper()

                new_status = input(
                    "Enter new status (in_progress/resolved): "
                ).strip().lower()

                try:
                    ticket = find_ticket(tickets, ticket_id)

                    old_status = ticket["status"]

                    update_ticket_status(
                        tickets,
                        ticket_id,
                        new_status
                    )

                    if save_changes(tickets):
                        print("\nTicket status updated successfully!")
                        display_ticket(ticket)

                    else:
                        ticket["status"] = old_status
                        print("Status change was not saved.")

                except (KeyError, ValueError, TypeError) as error:
                    print(f"Error: {error}")

            # REOPEN TICKET
            elif choice == "6":

                ticket_id = input(
                    "Enter ticket ID: "
                ).strip().upper()

                try:
                    ticket = find_ticket(tickets, ticket_id)

                    old_status = ticket["status"]

                    reopen_ticket(tickets, ticket_id)

                    if save_changes(tickets):
                        print("\nTicket reopened successfully!")
                        display_ticket(ticket)

                    else:
                        ticket["status"] = old_status
                        print("Status change was not saved.")

                except (KeyError, ValueError, TypeError) as error:
                    print(f"Error: {error}")

            # VIEW OPEN WORK QUEUE
            elif choice == "7":

                queue = get_open_work_queue(tickets)

                if not queue:
                    print("\nNo open tickets available.")

                else:
                    print("\n--- Open Work Queue ---")

                    for ticket in queue:
                        print(
                            f"{ticket['id']} | "
                            f"{ticket['title']} | "
                            f"Priority: {ticket['priority']} | "
                            f"Assigned: {ticket['assigned_to'] or 'Unassigned'}"
                        )

            # VIEW REPORTS
            elif choice == "8":

                report = get_ticket_report(tickets)

                print("\n========== TICKET REPORT ==========")

                print(f"\nTotal Tickets: {report['total']}")

                print("\nTickets by Status:")

                for status, count in report["by_status"].items():
                    print(f"{status}: {count}")

                print("\nTickets by Priority:")

                for priority, count in report["by_priority"].items():
                    print(f"{priority}: {count}")

                print("===================================")

            # EXIT
            elif choice == "0":

                print("\nThank you for using CampusFlow!")
                break

            else:
                print("\nInvalid choice. Please try again.")

        except (KeyboardInterrupt, EOFError):
            print("\nCampusFlow session ended.")
            break


if __name__ == "__main__":
    main()