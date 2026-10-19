def validate_affected_users(value):
    if type(value) is not int:
        raise TypeError("affected users must be an integer")
    if value < 1:
        raise ValueError("affected users must be greater than 0")

    return value