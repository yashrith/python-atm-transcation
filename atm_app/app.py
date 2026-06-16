import streamlit as st
import pandas as pd
from datetime import datetime
import db
import auth
import transactions

# Page configuration
st.set_page_config(
    page_title="Secure ATM Terminal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark ATM CSS styling
def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Main page background */
        .stApp {
            background-color: #0b0e14;
            color: #d1d5db;
        }

        /* Monospace Retro ATM Typography */
        h1, h2, h3, h4, h5, h6, .stSubheader {
            font-family: 'Courier New', Courier, monospace;
            color: #00ff66 !important;
            text-shadow: 0 0 8px rgba(0, 255, 102, 0.3);
            font-weight: bold;
        }

        /* Metric Balance Box styling */
        [data-testid="stMetricValue"] {
            font-family: 'Courier New', Courier, monospace;
            font-size: 2.8rem !important;
            color: #00ff66 !important;
            text-shadow: 0 0 15px rgba(0, 255, 102, 0.5);
            background-color: #111827;
            padding: 15px 25px;
            border-radius: 10px;
            border: 2px solid #00ff66;
            display: inline-block;
            box-shadow: inset 0 0 10px rgba(0, 255, 102, 0.2);
        }
        
        [data-testid="stMetricLabel"] {
            color: #9ca3af !important;
            font-size: 1rem !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important;
            border-right: 2px solid #00ff66;
        }
        
        [data-testid="stSidebar"] h3 {
            color: #00ff66;
            text-shadow: 0 0 5px rgba(0, 255, 102, 0.3);
        }

        /* ATM-Style Panels / Containers */
        .atm-card {
            background-color: #111827;
            border: 1px solid rgba(0, 255, 102, 0.25);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 255, 102, 0.05);
            margin-bottom: 25px;
        }

        .atm-card-header {
            color: #00ff66;
            font-size: 1.35rem;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(0, 255, 102, 0.15);
            padding-bottom: 10px;
            font-family: 'Courier New', Courier, monospace;
            text-transform: uppercase;
        }

        /* Customized Form Fields */
        div[data-baseweb="input"] {
            background-color: #1f2937 !important;
            border: 1px solid rgba(0, 255, 102, 0.3) !important;
            border-radius: 6px !important;
        }
        
        div[data-baseweb="input"]:focus-within {
            border: 1px solid #00ff66 !important;
            box-shadow: 0 0 8px rgba(0, 255, 102, 0.3) !important;
        }
        
        input {
            color: #00ff66 !important;
            font-family: 'Courier New', Courier, monospace !important;
        }

        /* Select boxes and number inputs */
        div[data-baseweb="select"] {
            background-color: #1f2937 !important;
            border: 1px solid rgba(0, 255, 102, 0.3) !important;
        }

        /* Button elements */
        .stButton>button {
            background-color: #1f2937 !important;
            color: #00ff66 !important;
            border: 1px solid #00ff66 !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-weight: bold !important;
            font-family: 'Courier New', Courier, monospace;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }

        .stButton>button:hover {
            background-color: #00ff66 !important;
            color: #0b0e14 !important;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.6) !important;
            border-color: #00ff66 !important;
        }

        /* Centered login wrapper */
        .login-wrapper {
            max-width: 500px;
            margin: 60px auto;
            background: #111827;
            border: 2px solid #00ff66;
            border-radius: 16px;
            padding: 35px;
            box-shadow: 0 0 25px rgba(0, 255, 102, 0.15), 0 20px 40px rgba(0, 0, 0, 0.6);
            text-align: center;
        }
        
        /* Table enhancements */
        .dataframe {
            background-color: #111827 !important;
            border: 1px solid rgba(0, 255, 102, 0.2) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Handle DB Connection Verification
db_error = None
try:
    db.init_pool()
except Exception as e:
    db_error = str(e)

# Render Database Connection Error Screen
if db_error:
    inject_custom_css()
    st.title("🏦 Secure ATM Initialization Error")
    st.error(f"Failed to connect to the MySQL database: {db_error}")
    st.markdown(
        """
        ### Action Required:
        1. **Create the Database:** Verify your MySQL Server is running and create the database `atm_db`.
        2. **Configure Credentials:** Verify there is a `.env` file in the `atm_app/` folder (or workspace root) based on `.env.example` with valid credentials:
           ```env
           DB_HOST=localhost
           DB_PORT=3306
           DB_USER=root
           DB_PASSWORD=your_password
           DB_NAME=atm_db
           ```
        3. **Seed Database Tables:** Run the `schema.sql` file using the terminal or MySQL workbench:
           ```bash
           mysql -u root -p < schema.sql
           ```
        4. **Refresh/Rerun** this Streamlit application once resolved.
        """
    )
    st.stop()

# Initialize Login Session States
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    inject_custom_css()
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.title("🏦 SECURE ATM")
    st.subheader("INSERT CARD / LOGIN")
    
    account_number = st.text_input(
        "Account Number", 
        placeholder="Enter Account Number (e.g. 1001)",
        max_chars=20
    )
    pin = st.text_input(
        "PIN", 
        type="password", 
        placeholder="Enter 4-Digit PIN",
        max_chars=10
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Authenticate", use_container_width=True):
        if not account_number or not pin:
            st.error("Both Account Number and PIN are required.")
        else:
            with st.spinner("Processing Card..."):
                user = auth.login_user(account_number, pin)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"Access Granted! Welcome, {user['full_name']}.")
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Account Number or PIN.")
                    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATED ATM WORKSPACES
# ==========================================
else:
    inject_custom_css()
    user = st.session_state.user
    role = user['role']
    
    # Sidebar Session Info
    st.sidebar.markdown("### 🏦 CARD STATUS")
    st.sidebar.success("🔒 Secured Connection")
    st.sidebar.markdown(f"**Customer:** {user['full_name']}")
    st.sidebar.markdown(f"**Account:** {user['account_number']}")
    st.sidebar.markdown(f"**Access Role:** {role.upper()}")
    st.sidebar.markdown("---")
    
    # Navigation Sidebar
    st.sidebar.markdown("### 🛠️ MENU SELECT")
    
    if role == 'owner':
        menu = st.sidebar.radio(
            "Select Operation",
            [
                "Dashboard", 
                "Create Account", 
                "Delete Account", 
                "Reset Customer PIN", 
                "View All Transactions", 
                "Change Own Password"
            ]
        )
    else:  # Customer Role
        menu = st.sidebar.radio(
            "Select Operation",
            [
                "Check Balance", 
                "Deposit Cash", 
                "Withdraw Cash", 
                "Transfer Funds", 
                "Transaction History"
            ]
        )
        
    st.sidebar.markdown("---")
    if st.sidebar.button("Eject Card / Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Card Ejected. Have a nice day!")
        st.rerun()

    # ==========================================
    # OWNER (ADMIN) VIEWS
    # ==========================================
    if role == 'owner':
        
        # 1. OWNER DASHBOARD
        if menu == "Dashboard":
            st.title("📟 Owner (Admin) Dashboard")
            st.markdown("---")
            try:
                accounts = transactions.get_all_accounts_dashboard()
                total_customers = len(accounts)
                total_deposits = sum(float(acc['balance']) for acc in accounts)
                
                # Metric display
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Customer Accounts", total_customers)
                with col2:
                    st.metric("Total Bank Deposits", f"${total_deposits:,.2f}")
                
                st.markdown("<br><h3>📋 Active Customer Accounts</h3>", unsafe_allow_html=True)
                if total_customers > 0:
                    df = pd.DataFrame(accounts)
                    # Formatting values for presentation
                    df_display = df.copy()
                    df_display['balance'] = df_display['balance'].apply(lambda x: f"${float(x):,.2f}")
                    df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_display.columns = ["Full Name", "Account Number", "Balance", "Account Type", "Registered At"]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.warning("No registered customer accounts exist.")
            except Exception as e:
                st.error(f"Failed to load dashboard data: {e}")

        # 2. CREATE ACCOUNT
        elif menu == "Create Account":
            st.title("➕ Create Customer Account")
            st.markdown("---")
            
            with st.form("create_account_form"):
                st.markdown('<div class="atm-card">', unsafe_allow_html=True)
                st.markdown('<div class="atm-card-header">New Account Details</div>', unsafe_allow_html=True)
                
                full_name = st.text_input("Full Name", placeholder="e.g. Alice Johnson")
                account_number = st.text_input("Account Number (Unique)", placeholder="e.g. 1003")
                starting_balance = st.number_input("Starting Balance ($)", min_value=0.0, step=100.0, value=0.0)
                account_type = st.selectbox("Account Type", ["Savings", "Checking"])
                new_pin = st.text_input("Temporary PIN (Numeric)", type="password", placeholder="e.g. 1234", max_chars=10)
                
                st.markdown("</div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Register Customer")
                
                if submit:
                    if not full_name or not account_number or not new_pin:
                        st.error("All fields are required.")
                    elif not new_pin.isdigit():
                        st.error("PIN must contain only numbers.")
                    else:
                        success, message = transactions.create_customer_account(
                            full_name, account_number, starting_balance, new_pin, account_type
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

        # 3. DELETE ACCOUNT
        elif menu == "Delete Account":
            st.title("❌ Delete Customer Account")
            st.markdown("---")
            
            try:
                accounts = transactions.get_all_accounts_dashboard()
                if not accounts:
                    st.warning("No accounts available to delete.")
                else:
                    account_options = [f"{acc['account_number']} - {acc['full_name']}" for acc in accounts]
                    
                    st.markdown('<div class="atm-card">', unsafe_allow_html=True)
                    st.markdown('<div class="atm-card-header">Select Target Account</div>', unsafe_allow_html=True)
                    
                    selected_option = st.selectbox("Select Account", account_options)
                    selected_acct_num = selected_option.split(" - ")[0]
                    
                    st.warning("⚠️ WARNING: Deleting an account will permanently remove all transaction histories associated with it.")
                    confirm = st.checkbox("I confirm that I want to delete this customer account permanently.")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.button("Delete Account"):
                        if not confirm:
                            st.error("Please confirm account deletion by checking the confirmation box.")
                        else:
                            success, message = transactions.delete_customer_account(selected_acct_num)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
            except Exception as e:
                st.error(f"Failed to fetch account list: {e}")

        # 4. RESET CUSTOMER PIN
        elif menu == "Reset Customer PIN":
            st.title("🔑 Reset Customer PIN")
            st.markdown("---")
            
            try:
                accounts = transactions.get_all_accounts_dashboard()
                if not accounts:
                    st.warning("No customer accounts available.")
                else:
                    account_options = [f"{acc['account_number']} - {acc['full_name']}" for acc in accounts]
                    
                    st.markdown('<div class="atm-card">', unsafe_allow_html=True)
                    st.markdown('<div class="atm-card-header">Select Customer Account</div>', unsafe_allow_html=True)
                    
                    selected_option = st.selectbox("Select Account", account_options)
                    selected_acct_num = selected_option.split(" - ")[0]
                    
                    new_pin = st.text_input("New PIN (Numeric)", type="password", placeholder="Enter New PIN", max_chars=10)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.button("Reset Customer PIN"):
                        if not new_pin:
                            st.error("New PIN is required.")
                        elif not new_pin.isdigit():
                            st.error("PIN must contain only numbers.")
                        else:
                            success, message = auth.reset_customer_pin(selected_acct_num, new_pin)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
            except Exception as e:
                st.error(f"Failed to fetch customer list: {e}")

        # 5. VIEW ALL TRANSACTIONS
        elif menu == "View All Transactions":
            st.title("📜 Global Transaction Log")
            st.markdown("---")
            
            try:
                all_txns = transactions.get_all_transactions_dashboard()
                if all_txns:
                    df = pd.DataFrame(all_txns)
                    df_display = df.copy()
                    df_display['amount'] = df_display['amount'].apply(lambda x: f"${float(x):,.2f}")
                    df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_display['txn_type'] = df_display['txn_type'].str.replace('_', ' ').str.upper()
                    df_display.columns = ["Txn ID", "Full Name", "Account Number", "Type", "Amount", "Timestamp", "Note"]
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("No transactions recorded in the bank database yet.")
            except Exception as e:
                st.error(f"Failed to retrieve transactions: {e}")

        # 6. CHANGE OWNER PASSWORD (PIN)
        elif menu == "Change Own Password":
            st.title("🔐 Change Owner PIN")
            st.markdown("---")
            
            st.markdown('<div class="atm-card">', unsafe_allow_html=True)
            st.markdown('<div class="atm-card-header">Security Verification</div>', unsafe_allow_html=True)
            
            curr_pin = st.text_input("Current PIN", type="password", placeholder="Enter Current PIN")
            new_pin = st.text_input("New PIN", type="password", placeholder="Enter New PIN")
            conf_pin = st.text_input("Confirm New PIN", type="password", placeholder="Confirm New PIN")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Update Owner PIN"):
                success, message = auth.change_owner_pin(user['user_id'], curr_pin, new_pin, conf_pin)
                if success:
                    st.success(message)
                    # Clear session state and force re-login
                    st.session_state.logged_in = False
                    st.session_state.user = None
                    st.info("Session expired due to credentials change. Redirecting to login...")
                    # Small wait to let them see success message, then rerun
                    import time
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(message)

    # ==========================================
    # CUSTOMER VIEWS
    # ==========================================
    else:
        # Fetch current balance
        try:
            balance = transactions.get_balance(user['account_number'])
        except Exception as e:
            st.error(f"Error reading account balance: {e}")
            balance = 0.0

        # 1. CHECK BALANCE
        if menu == "Check Balance":
            st.title("💰 Check Account Balance")
            st.markdown("---")
            
            st.markdown('<div class="atm-card">', unsafe_allow_html=True)
            st.markdown('<div class="atm-card-header">Available Funds</div>', unsafe_allow_html=True)
            
            st.metric("Total Ledger Balance", f"${float(balance):,.2f}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick instructions card
            st.info("💡 Deposit cash to increase your balance, or use Transfer to send funds to Alice or Bob.")

        # 2. DEPOSIT CASH
        elif menu == "Deposit Cash":
            st.title("📥 Deposit Cash")
            st.markdown("---")
            
            st.markdown('<div class="atm-card">', unsafe_allow_html=True)
            st.markdown('<div class="atm-card-header">Deposit Window</div>', unsafe_allow_html=True)
            
            deposit_amt = st.number_input("Amount to Deposit ($)", min_value=0.0, step=50.0, format="%.2f")
            deposit_note = st.text_input("Description / Memo", placeholder="e.g. Weekly Savings", max_chars=100)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Complete Deposit"):
                if deposit_amt <= 0:
                    st.error("Please enter a deposit amount greater than zero.")
                else:
                    success, message = transactions.deposit(user['account_number'], deposit_amt, deposit_note)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # 3. WITHDRAW CASH
        elif menu == "Withdraw Cash":
            st.title("📤 Withdraw Cash")
            st.markdown("---")
            
            st.markdown('<div class="atm-card">', unsafe_allow_html=True)
            st.markdown('<div class="atm-card-header">Withdrawal Window</div>', unsafe_allow_html=True)
            
            withdraw_amt = st.number_input("Amount to Withdraw ($)", min_value=0.0, step=20.0, format="%.2f")
            withdraw_note = st.text_input("Description / Memo", placeholder="e.g. Groceries", max_chars=100)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Dispense Cash"):
                if withdraw_amt <= 0:
                    st.error("Please enter an amount greater than zero.")
                elif withdraw_amt > float(balance):
                    st.error("Insufficient funds in your account.")
                else:
                    success, message = transactions.withdraw(user['account_number'], withdraw_amt, withdraw_note)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # 4. TRANSFER FUNDS
        elif menu == "Transfer Funds":
            st.title("💸 Peer-to-Peer Transfer")
            st.markdown("---")
            
            st.markdown('<div class="atm-card">', unsafe_allow_html=True)
            st.markdown('<div class="atm-card-header">Transfer Form</div>', unsafe_allow_html=True)
            
            to_acct = st.text_input("Destination Account Number", placeholder="Enter recipient account (e.g. 1002)")
            transfer_amt = st.number_input("Amount to Transfer ($)", min_value=0.0, step=50.0, format="%.2f")
            transfer_note = st.text_input("Description / Memo", placeholder="e.g. Split Dinner Bill", max_chars=100)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Execute Transfer"):
                if not to_acct:
                    st.error("Recipient account number is required.")
                elif to_acct == user['account_number']:
                    st.error("You cannot transfer money to your own account.")
                elif transfer_amt <= 0:
                    st.error("Please enter an amount greater than zero.")
                elif transfer_amt > float(balance):
                    st.error("Insufficient funds for this transfer.")
                else:
                    success, message = transactions.transfer(user['account_number'], to_acct, transfer_amt, transfer_note)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

        # 5. TRANSACTION HISTORY
        elif menu == "Transaction History":
            st.title("📜 Transaction History")
            st.markdown("---")
            
            try:
                txns = transactions.get_transaction_history(user['account_number'], limit=10)
                
                st.markdown('<div class="atm-card">', unsafe_allow_html=True)
                st.markdown('<div class="atm-card-header">Last 10 Transactions</div>', unsafe_allow_html=True)
                
                if txns:
                    df = pd.DataFrame(txns)
                    df_display = df.copy()
                    
                    # Highlight amounts/types nicely
                    df_display['amount'] = df_display.apply(
                        lambda row: f"-${float(row['amount']):,.2f}" if row['txn_type'] in ['withdraw', 'transfer_out'] else f"+${float(row['amount']):,.2f}", 
                        axis=1
                    )
                    df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_display['txn_type'] = df_display['txn_type'].str.replace('_', ' ').str.upper()
                    df_display.columns = ["Txn ID", "Transaction Type", "Amount", "Timestamp", "Description/Memo"]
                    
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("No transaction records found for this card.")
                    
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to retrieve transaction records: {e}")
