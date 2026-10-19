def validate_affected_users(value):
    if type(value) is not int:
        raise TypeError("affected users must be an integer")
    if value < 1:
        raise ValueError("affected users must be greater than 0")

    return value

def validate_urgency(value):
    categories = ["low","medium","high"]

    if not isinstance(value, str):
        raise TypeError("urgency must be a string")

    valid_value = value.strip().lower()

    if valid_value not in categories:
        raise ValueError(f"please select from these options {categories}")
        
    return valid_value

def validate_title(value):
    if not isinstance(value, str):
        raise TypeError("title must be a string")

    cleaned_title = value.strip()

    if cleaned_title == "":
        raise ValueError("title must not be empty, please enter a valid string")

    return cleaned_title

def validate_category(value):
    categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    if not isinstance(value, str):
        raise TypeError("category must be a string")
    
    new_value = value.strip().lower()

    if new_value not in categories:
        raise ValueError(f"invalid category, please select from this options{list(categories.values())}")
    
    return categories[new_value]

def calculate_priority(urgency, affected_users):
    try:
        valid_urgency = validate_urgency(urgency)
        users = validate_affected_users(affected_users)

        if valid_urgency == "high" and users >= 10:
            return "critical"

        elif valid_urgency == "high" or users >= 10:
            return "high"

        elif valid_urgency == "medium" or users >= 3:
            return "medium"

        else:
            "low"
    except ValueError as error:
        return error
    except TypeError as error:
        return error
