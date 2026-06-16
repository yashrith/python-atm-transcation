import bcrypt
import db

def hash_pin(pin: str) -> str:
    """Hashes a plaintext PIN using bcrypt and returns a UTF-8 string."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pin.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_pin(pin: str, hashed_pin: str) -> bool:
    """Verifies a plaintext PIN against a stored bcrypt hash string."""
    try:
        return bcrypt.checkpw(pin.encode('utf-8'), hashed_pin.encode('utf-8'))
    except Exception:
        return False

def login_user(account_number: str, pin: str):
    """
    Validates user credentials against the database.
    Returns the user record dict (without PIN hash) if successful, else None.
    """
    try:
        user = db.fetch_one(
            "SELECT user_id, full_name, account_number, pin_hash, role FROM users WHERE account_number = %s",
            (account_number,)
        )
        if user and verify_pin(pin, user['pin_hash']):
            return {
                "user_id": user['user_id'],
                "full_name": user['full_name'],
                "account_number": user['account_number'],
                "role": user['role']
            }
        return None
    except Exception as e:
        raise RuntimeError(f"Login database verification failed: {e}")

def change_owner_pin(user_id: int, current_pin: str, new_pin: str, confirm_pin: str):
    """
    Allows the owner to change their own PIN.
    Verifies the current PIN, checks that the new PIN matches confirm PIN,
    hashes the new PIN, and updates the database.
    """
    if not current_pin or not new_pin or not confirm_pin:
        return False, "All fields are required."
    
    if new_pin != confirm_pin:
        return False, "New PIN and Confirm PIN do not match."
        
    try:
        # Fetch current owner pin hash
        owner = db.fetch_one(
            "SELECT pin_hash FROM users WHERE user_id = %s AND role = 'owner'",
            (user_id,)
        )
        if not owner:
            return False, "Owner account not found."
            
        if not verify_pin(current_pin, owner['pin_hash']):
            return False, "Current PIN is incorrect."
            
        # Update database with new hashed PIN
        hashed_new_pin = hash_pin(new_pin)
        rows_updated = db.execute_query(
            "UPDATE users SET pin_hash = %s WHERE user_id = %s AND role = 'owner'",
            (hashed_new_pin, user_id)
        )
        if rows_updated > 0:
            return True, "PIN updated successfully. Please log in again."
        else:
            return False, "PIN update failed. No changes made."
    except Exception as e:
        return False, f"Database error during PIN change: {e}"

def reset_customer_pin(account_number: str, new_pin: str):
    """
    Allows the owner to reset any customer's PIN by their account number.
    Hashes the new PIN and updates the database.
    """
    if not account_number or not new_pin:
        return False, "Account number and new PIN are required."
        
    try:
        # Verify account exists and is a customer
        user = db.fetch_one(
            "SELECT user_id FROM users WHERE account_number = %s AND role = 'customer'",
            (account_number,)
        )
        if not user:
            return False, f"Customer account '{account_number}' not found."
            
        # Update hashed PIN
        hashed_new_pin = hash_pin(new_pin)
        db.execute_query(
            "UPDATE users SET pin_hash = %s WHERE account_number = %s AND role = 'customer'",
            (hashed_new_pin, account_number)
        )
        return True, f"PIN for account '{account_number}' has been reset successfully."
    except Exception as e:
        return False, f"Database error during customer PIN reset: {e}"
