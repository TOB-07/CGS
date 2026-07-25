def check_password(password: str) -> str:
    if not (8 <= len(password) <= 16):
        return "Password must contain atleast 8-16 characters"
    if not any(char.islower() for char in password):
        return "Password must contain a small letter"
    if not any(char.isupper() for char in password):
        return "Password must contain a capital letter"
    if not any(char.isdigit() for char in password):
        return "Password must contain a digit"
    if not any(not char.isalnum() for char in password):
        return "Password must contain a special character"

    return "Correct"
