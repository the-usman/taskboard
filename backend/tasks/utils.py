def display_name(user):
    """A user's first name, or their username if they haven't set one."""
    return user.first_name or user.username
