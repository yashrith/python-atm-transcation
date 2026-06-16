import db

def get_balance(account_number: str):
    """Fetches the balance of the given account number."""
    try:
        res = db.fetch_one(
            "SELECT balance FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.account_number = %s",
            (account_number,)
        )
        if res:
            return res['balance']
        return None
    except Exception as e:
        raise RuntimeError(f"Error fetching balance: {e}")

def deposit(account_number: str, amount: float, note: str = None):
    """
    Deposits an amount to the customer's account.
    Increments the balance and inserts a transaction log.
    """
    if amount <= 0:
        return False, "Deposit amount must be greater than zero."
    
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch account details
        cursor.execute(
            "SELECT a.account_id FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.account_number = %s",
            (account_number,)
        )
        account = cursor.fetchone()
        if not account:
            return False, "Account not found."
            
        account_id = account['account_id']
        
        # Update account balance
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, account_id)
        )
        
        # Insert transaction record
        cursor.execute(
            "INSERT INTO transactions (account_id, txn_type, amount, note) VALUES (%s, 'deposit', %s, %s)",
            (account_id, amount, note or "ATM Deposit")
        )
        
        conn.commit()
        return True, f"Successfully deposited ${amount:,.2f}."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Deposit transaction failed: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def withdraw(account_number: str, amount: float, note: str = None):
    """
    Withdraws an amount from the customer's account, validating sufficient funds.
    Decrements the balance and inserts a transaction log.
    """
    if amount <= 0:
        return False, "Withdrawal amount must be greater than zero."
        
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch account details and current balance
        cursor.execute(
            "SELECT a.account_id, a.balance FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.account_number = %s",
            (account_number,)
        )
        account = cursor.fetchone()
        if not account:
            return False, "Account not found."
            
        account_id = account['account_id']
        balance = account['balance']
        
        if balance < amount:
            return False, f"Insufficient funds. Current balance: ${balance:,.2f}."
            
        # Update account balance
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, account_id)
        )
        
        # Insert transaction record
        cursor.execute(
            "INSERT INTO transactions (account_id, txn_type, amount, note) VALUES (%s, 'withdraw', %s, %s)",
            (account_id, amount, note or "ATM Withdrawal")
        )
        
        conn.commit()
        return True, f"Successfully withdrew ${amount:,.2f}."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Withdrawal transaction failed: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def transfer(from_account_number: str, to_account_number: str, amount: float, note: str = None):
    """
    Transfers money from one customer account to another.
    Performs debit on sender, credit on recipient, and registers two transaction logs.
    """
    if amount <= 0:
        return False, "Transfer amount must be greater than zero."
    if from_account_number == to_account_number:
        return False, "Cannot transfer money to the same account."
        
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Fetch sender details
        cursor.execute(
            "SELECT a.account_id, a.balance, u.full_name FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.account_number = %s",
            (from_account_number,)
        )
        sender = cursor.fetchone()
        if not sender:
            return False, "Sender account not found."
            
        sender_id = sender['account_id']
        sender_balance = sender['balance']
        
        if sender_balance < amount:
            return False, f"Insufficient funds. Available balance: ${sender_balance:,.2f}."
            
        # 2. Fetch recipient details (must be customer role)
        cursor.execute(
            "SELECT a.account_id, u.full_name FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.account_number = %s AND u.role = 'customer'",
            (to_account_number,)
        )
        recipient = cursor.fetchone()
        if not recipient:
            return False, f"Recipient account '{to_account_number}' not found or is not a customer account."
            
        recipient_id = recipient['account_id']
        recipient_name = recipient['full_name']
        
        # 3. Deduct from sender
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, sender_id)
        )
        
        # 4. Add to recipient
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, recipient_id)
        )
        
        # 5. Insert transaction log for sender (transfer_out)
        sender_note = f"To {recipient_name} ({to_account_number})"
        if note:
            sender_note += f" - {note}"
        cursor.execute(
            "INSERT INTO transactions (account_id, txn_type, amount, note) VALUES (%s, 'transfer_out', %s, %s)",
            (sender_id, amount, sender_note)
        )
        
        # 6. Insert transaction log for recipient (transfer_in)
        recipient_note = f"From {sender['full_name']} ({from_account_number})"
        if note:
            recipient_note += f" - {note}"
        cursor.execute(
            "INSERT INTO transactions (account_id, txn_type, amount, note) VALUES (%s, 'transfer_in', %s, %s)",
            (recipient_id, amount, recipient_note)
        )
        
        conn.commit()
        return True, f"Successfully transferred ${amount:,.2f} to {recipient_name} ({to_account_number})."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Transfer transaction failed: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_transaction_history(account_number: str, limit: int = 10):
    """Retrieves the last N transactions for a specific customer account."""
    try:
        return db.fetch_all(
            """
            SELECT t.txn_id, t.txn_type, t.amount, t.timestamp, t.note 
            FROM transactions t 
            JOIN accounts a ON t.account_id = a.account_id 
            JOIN users u ON a.user_id = u.user_id 
            WHERE u.account_number = %s 
            ORDER BY t.timestamp DESC 
            LIMIT %s
            """,
            (account_number, limit)
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching transaction history: {e}")

# ==========================================
# Owner (Admin) Dashboard Helpers
# ==========================================

def get_all_accounts_dashboard():
    """Retrieves list of all customer accounts and balances (for Admin)."""
    try:
        return db.fetch_all(
            """
            SELECT u.full_name, u.account_number, a.balance, a.account_type, u.created_at 
            FROM users u 
            JOIN accounts a ON u.user_id = a.user_id 
            WHERE u.role = 'customer'
            ORDER BY u.account_number ASC
            """
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching dashboard accounts: {e}")

def get_all_transactions_dashboard():
    """Retrieves list of all transactions across all accounts (for Admin)."""
    try:
        return db.fetch_all(
            """
            SELECT t.txn_id, u.full_name, u.account_number, t.txn_type, t.amount, t.timestamp, t.note 
            FROM transactions t 
            JOIN accounts a ON t.account_id = a.account_id 
            JOIN users u ON a.user_id = u.user_id 
            ORDER BY t.timestamp DESC
            """
        )
    except Exception as e:
        raise RuntimeError(f"Error fetching dashboard transactions: {e}")

def create_customer_account(full_name: str, account_number: str, starting_balance: float, pin: str, account_type: str = 'Savings'):
    """
    Creates a new user and account in a single transaction.
    Hashes PIN with bcrypt first.
    """
    if not full_name or not account_number or not pin:
        return False, "Full Name, Account Number, and PIN are required."
    if starting_balance < 0:
        return False, "Starting balance cannot be negative."
        
    import auth  # Deferred import to prevent circular dependency issues
    
    conn = None
    cursor = None
    try:
        conn = db.get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor()
        
        # Verify account number uniqueness
        cursor.execute("SELECT user_id FROM users WHERE account_number = %s", (account_number,))
        if cursor.fetchone():
            return False, f"Account number '{account_number}' already exists."
            
        # Hash customer PIN
        hashed_pin = auth.hash_pin(pin)
        
        # Insert into users
        cursor.execute(
            "INSERT INTO users (full_name, account_number, pin_hash, role) VALUES (%s, %s, %s, 'customer')",
            (full_name, account_number, hashed_pin)
        )
        user_id = cursor.lastrowid
        
        # Insert into accounts
        cursor.execute(
            "INSERT INTO accounts (user_id, balance, account_type) VALUES (%s, %s, %s)",
            (user_id, starting_balance, account_type)
        )
        
        conn.commit()
        return True, f"Account '{account_number}' for {full_name} created successfully with a starting balance of ${starting_balance:,.2f}."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Failed to create account: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_customer_account(account_number: str):
    """
    Deletes a customer account by account number.
    On Delete Cascade ensures accounts and transactions records are deleted automatically.
    """
    if not account_number:
        return False, "Account number is required."
    if account_number == '0000':
        return False, "Cannot delete owner account."
        
    try:
        # Check if customer exists and is customer role
        user = db.fetch_one(
            "SELECT user_id, full_name FROM users WHERE account_number = %s AND role = 'customer'",
            (account_number,)
        )
        if not user:
            return False, f"Customer account '{account_number}' not found."
            
        # Delete user
        rows_deleted = db.execute_query(
            "DELETE FROM users WHERE account_number = %s AND role = 'customer'",
            (account_number,)
        )
        if rows_deleted > 0:
            return True, f"Account '{account_number}' ({user['full_name']}) was deleted successfully."
        else:
            return False, "Failed to delete account. No changes made."
    except Exception as e:
        return False, f"Error deleting customer account: {e}"
