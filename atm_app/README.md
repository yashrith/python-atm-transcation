# 🏦 Secure ATM Simulation Web Application

A fully functional, dark-themed ATM machine simulation web application built using **Python (Streamlit)** and **MySQL** database integration. It supports bcrypt-hashed PIN verification, transaction journaling, and two roles (Owner/Admin and Demo Customers).

---

## 🔑 Login Credentials for Quick Testing

| Role | Name | Account Number | PIN | Initial Balance | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Owner (Admin)** | Admin Owner | `0000` | `0000` | N/A | Admin panel to manage customers and reset PINs. |
| **Customer 1** | Alice Johnson | `1001` | `1234` | `$5,000.00` | Standard checking/savings ATM customer. |
| **Customer 2** | Bob Smith | `1002` | `5678` | `$3,000.00` | Standard checking/savings ATM customer. |

---

## 🛠️ Step 1: Install MySQL and Create the Database

### macOS Installation (via Homebrew)
1. Install Homebrew if not already installed, then run:
   ```bash
   brew install mysql
   ```
2. Start the MySQL service:
   ```bash
   brew services start mysql
   ```
3. Run the secure installation script to set a root password:
   ```bash
   mysql_secure_installation
   ```

### Windows/Linux Installation
- **Windows:** Download the MySQL Installer from the [MySQL Downloads](https://dev.mysql.com/downloads/installer/) page. Choose Developer Default and follow the GUI wizard to set a root password.
- **Ubuntu/Debian:** Run `sudo apt update && sudo apt install mysql-server` and secure using `sudo mysql_secure_installation`.

---

## 🗄️ Step 2: Seed the Database Schema and Demo Data

1. Open your terminal and log into your MySQL server as root (or another administrative user):
   ```bash
   mysql -u root -p
   ```
2. Enter your password.
3. Import and execute the `schema.sql` file. From the `atm_app` directory, run:
   ```bash
   mysql -u root -p < schema.sql
   ```
   *(Alternatively, copy and paste the contents of `schema.sql` into MySQL Workbench or phpMyAdmin and execute it).*

---

## 🔑 Step 3: Configure Environment Variables

1. Inside the `atm_app` folder, copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_root_password
   DB_NAME=atm_db
   ```

---

## 📦 Step 4: Install Dependencies

Using `pip`, install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## 🚀 Step 5: Launch the Application

Navigate to the `atm_app/` directory and start the Streamlit web server:
```bash
streamlit run app.py
```

Streamlit will automatically launch the application in your default web browser (usually at `http://localhost:8501`).

---

## 📋 Features Overview

### 📟 Owner (Admin) Panel (Account `0000`)
- **Dashboard:** Live overview of total active customers, total deposits held, and a table list of accounts.
- **Create Account:** Instantly register new customer cards (validates account number uniqueness and hashes their PIN with bcrypt).
- **Delete Account:** Remove customer accounts (cascades automatically to delete account and transaction log).
- **Reset Customer PIN:** Reset any customer's password by account number.
- **View All Transactions:** Monitor a global history of deposits, withdrawals, and transfers across the entire bank.
- **Change Own Password:** Securely change the Owner PIN (requires current PIN confirmation, hashes new PIN, and logs you out to force re-login).

### 💳 Customer Panel (Accounts `1001` or `1002`)
- **Check Balance:** Display available funds in a retro metric card.
- **Deposit Cash:** Make instant deposits with optional transaction memos.
- **Withdraw Cash:** Safe withdrawals that validate sufficient funds before dispensing.
- **Transfer Funds:** P2P transfers using target account verification and instant double-entry logging (`transfer_out` for sender, `transfer_in` for recipient).
- **Transaction History:** Displays a detailed list of the last 10 transactions.
