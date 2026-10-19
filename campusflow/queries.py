def list_tickets(tickets):
    #list tickets by the ticket_id in ascending order
    if not tickets:
        return []

    sorted_list = sorted(tickets.values(), key=lambda ticket: int(ticket["id"][1:]))

    return sorted_list

def get_open_work_queue(tickets):
    tickets_list = list_tickets(tickets)

    ticket_list_with_open_status = []

    rank = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    for ticket in tickets_list:
        if ticket["status"] == "open":
            ticket_list_with_open_status.append(ticket)

    sorted_by_rank = sorted (
        ticket_list_with_open_status,
        key=lambda ticket: (
            -rank[ticket["priority"]],
            int(ticket["id"][1:]))
    )

    return sorted_by_rank

def get_ticket_report(tickets):
    tickets_list = list_tickets(tickets)

    ticket_report = {
        "total": 0,
        "by_status": {
            "open": 0,
            "in_progress": 0,
            "resolved": 0
        },
        "by_priority": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    }

    ticket_report["total"] = len(tickets_list)

    for ticket in tickets_list:

        status = ticket["status"]

        ticket_report["by_status"][status] += 1

        priority = ticket["priority"]

        ticket_report["by_priority"][priority]+=1

    return ticket_report