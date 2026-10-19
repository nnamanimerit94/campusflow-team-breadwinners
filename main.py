from campusflow.tickets import create_ticket
from campusflow.storage import load_tickets, save_tickets
from campusflow.validation import (
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
)
from campusflow.workflow import find_ticket


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
    print("\n------------------------------")
    print(f"Ticket ID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected Users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Assigned To: {ticket['assigned_to']}")
    print("------------------------------")


def save_changes(tickets):
    try:
        save_tickets(tickets, FILE_PATH)
        print("Changes saved successfully.")
        return True
    except OSError as error:
        print(f"Error saving tickets: {error}")
        return False


def main():
    try:
        tickets = load_tickets(FILE_PATH)

        if not isinstance(tickets, dict):
            print("Invalid ticket storage format.")
            return

    except (ValueError, OSError) as error:
        print(f"Unable to load tickets: {error}")
        return

    while True:
        display_menu()

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            print("\nCREATE NEW TICKET")

            try:
                title = validate_title(input("Title: "))
                category = validate_category(input("Category: "))
                urgency = validate_urgency(input("Urgency (low/medium/high): "))
                affected_users = validate_affected_users(
                    input("Number of affected users: ")
                )

                previous_tickets = tickets.copy()

                ticket = create_ticket(
                    tickets,
                    title,
                    category,
                    urgency,
                    affected_users,
                )

                if save_changes(tickets):
                    print("\nTicket created successfully.")
                    display_ticket(ticket)
                else:
                    tickets = previous_tickets

            except (ValueError, TypeError) as error:
                print(f"Invalid ticket input: {error}")

        elif choice == "2":
            print("\nALL TICKETS")

            if not tickets:
                print("No tickets available.")
            else:
                for ticket in tickets.values():
                    display_ticket(ticket)

        elif choice == "3":
            print("\nTicket assignment will be integrated by Engineer B.")

        elif choice == "4":
            ticket_id = input("Enter ticket ID: ").strip()

            try:
                ticket = find_ticket(tickets, ticket_id)
                display_ticket(ticket)
            except (ValueError, KeyError) as error:
                print(f"Unable to find ticket: {error}")

        elif choice == "5":
            print("\nTicket status management will be integrated by Engineer B.")

        elif choice == "6":
            print("\nTicket reopening will be integrated by Engineer B.")

        elif choice == "7":
            print("\nOpen work queue will be integrated by Engineer B.")

        elif choice == "8":
            print("\nTicket reporting will be integrated by Engineer B.")

        elif choice == "0":
            print("Exiting CampusFlow.")
            break

        else:
            print("Invalid menu option. Please try again.")


if __name__ == "__main__":
    main()