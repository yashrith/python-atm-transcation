# 🏦 MySQL & Streamlit ATM Simulation Web Application

A fully functional ATM (Automated Teller Machine) simulator built as a modern full-stack web application using **Python (Streamlit)** and **MySQL**. It features custom dark-themed CSS interfaces (cyberpunk retro terminal aesthetic), secure password/PIN handling via **bcrypt**, parameterized query statements to prevent SQL injections, and dedicated dashboards for both Owner (Admin) and Customer roles.

---

## 🔑 Demo Login Credentials (Quick Testing)

| Role | Account Number | Password / PIN | Starting Balance | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Owner (Admin)** | `0000` | `0000` | *N/A* | Admin panel to register/delete customers, view logs, and reset customer PINs. |
| **Customer 1** | `1001` | `1234` | `$5,000.00` | Standard customer (Check balance, deposit, withdraw, transfer). |
| **Customer 2** | `1002` | `5678` | `$3,000.00` | Standard customer (Check balance, deposit, withdraw, transfer). |

---

## 📁 Repository Structure

```
python-atm-transcation/
├── atm_app/
│   ├── app.py              # Main Streamlit entry point & UI
│   ├── db.py               # MySQL Connection Pool and Query Helper Methods
│   ├── auth.py             # bcrypt Hashing and PIN Verification Logic
│   ├── transactions.py     # Deposit, Withdrawal, and Peer-to-Peer Transfer operations
│   ├── schema.sql          # Database schema tables and seed data
│   ├── requirements.txt    # Python library dependencies
│   ├── .env                # Configured credentials file
│   ├── .env.example        # Database configuration environment template
│   └── README.md           # Local application instructions
├── .gitignore              # Files to ignore (e.g. credentials, cache)
└── README.md               # Main repository documentation (this file)
```

---

## 🛠️ Setup & Running Instructions

You can set up and run the application in two ways: using Docker Compose (Recommended) or manual installation.

### Option 1: Quick Start via Docker (Recommended)
This method spins up both the MySQL database and the Streamlit app automatically, runs the schema creation, and seeds the database with zero configuration.

1. Ensure **Docker Desktop** is installed and running on your system.
2. Build and start the services from the project root:
   ```bash
   docker compose up --build
   ```
3. Once the logs show both services are healthy and running, open **[http://localhost:8501](http://localhost:8501)** in your web browser.
4. To shut down the containers and clean up resources:
   ```bash
   docker compose down
   ```

---

### Option 2: Manual Setup (Local Python & MySQL)

If you prefer to run the components directly on your host machine:

#### 1. Database Setup
Ensure that your local MySQL server is running locally on port `3306`.
Import the `schema.sql` file to create the `atm_db` database and seed it with demo records:
```bash
mysql -u root -p < atm_app/schema.sql
```
*(Enter your MySQL root password when prompted)*

#### 2. Configure Environment variables
Copy the `.env.example` file to `.env` inside the `atm_app/` folder:
```bash
cp atm_app/.env.example atm_app/.env
```
Open the `atm_app/.env` file and input your local MySQL root password:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=atm_db
```

#### 3. Install Python Dependencies
Install the required packages in your python environment:
```bash
pip install -r atm_app/requirements.txt
```

#### 4. Launch the Web Application
Start the Streamlit server from the `atm_app/` directory:
```bash
cd atm_app
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## 🔒 Security Features
- **One-Way PIN Hashing:** Plaintext passwords/PINs are never stored in the database. They are hashed using `bcrypt` (with 12 salt rounds) and verified in memory.
- **SQL Injection Prevention:** All queries use parameterized inputs to ensure database protection.
- **Transaction Rollback:** Transfer actions utilize database transactions so that a ledger debit only succeeds if the corresponding credit also succeeds.
