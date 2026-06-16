CREATE DATABASE IF NOT EXISTS atm_db;
USE atm_db;

-- Drop tables if they exist to allow clean reseeding
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS users;

-- 1. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,
    role ENUM('owner', 'customer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Accounts Table (Customers only)
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    account_type VARCHAR(50) NOT NULL DEFAULT 'Savings',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Transactions Table
CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    txn_type ENUM('deposit', 'withdraw', 'transfer_in', 'transfer_out') NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note VARCHAR(255),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================
-- Seed Data (with bcrypt-hashed PINs)
-- ==========================================

-- Seed Owner (Admin) - Account 0000, PIN 0000
INSERT INTO users (user_id, full_name, account_number, pin_hash, role)
VALUES (1, 'Admin Owner', '0000', '$2b$12$Mhqwb7omeYcjJIICFXpsMOhvh.ytrAQPTqIzWd5Hw8SisdtU3pU5m', 'owner');

-- Seed Alice Johnson - Account 1001, PIN 1234, Balance $5000
INSERT INTO users (user_id, full_name, account_number, pin_hash, role)
VALUES (2, 'Alice Johnson', '1001', '$2b$12$dax82U5/V0yWBSvRSbaxJuXZ7fXzTxyGPQ3o8ratqXiWSK3/S12Tq', 'customer');

INSERT INTO accounts (account_id, user_id, balance, account_type)
VALUES (1, 2, 5000.00, 'Savings');

-- Seed Bob Smith - Account 1002, PIN 5678, Balance $3000
INSERT INTO users (user_id, full_name, account_number, pin_hash, role)
VALUES (3, 'Bob Smith', '1002', '$2b$12$ULz2iSwK4FWhNh4YM.E2h.7VRR/ogBX.lqYvHEgzbhhoraOvvp/XS', 'customer');

INSERT INTO accounts (account_id, user_id, balance, account_type)
VALUES (2, 3, 3000.00, 'Savings');
