from campusflow.validation import validate_urgency, validate_affected_users

def calculate_priority(urgency, affected_users):
        valid_urgency = validate_urgency(urgency)
        users = validate_affected_users(affected_users)

        if valid_urgency == "high" and users >= 10:
            return "critical"

        elif valid_urgency == "high" or users >= 10:
            return "high"

        elif valid_urgency == "medium" or users >= 3:
            return "medium"

        else:
            return "low"