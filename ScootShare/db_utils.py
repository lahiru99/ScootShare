import bcrypt


def hash_password(password: str) -> str:
    # Generate a random salt
    salt = bcrypt.gensalt()
    if password is not None:
        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        # Return the hashed password as bytes
        return hashed_password


def verify_password(stored_password: str, password_attempt: str) -> bool:
    # Encode passwords as bytes
    encode_attempt = password_attempt.encode('utf-8')
    stored_password = stored_password.encode('utf-8')
    # Compare attempt to stored hash, return result
    return bcrypt.checkpw(encode_attempt, stored_password)
