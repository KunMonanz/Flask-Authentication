ALLOWED_PRIORITIES = {"high", "medium", "low", "default"}

def validate_priority(priority):
    if priority not in ALLOWED_PRIORITIES:
        allowed = "', '".join(ALLOWED_PRIORITIES)
        return False, f"Invalid priority entry '{priority}': must be one of '{allowed}'"
    return True, None
