# 🛠️ StayEase: Internal Architecture & Developer Notes

This document outlines the backend architecture, database design principles, and security protocols implemented in the StayEase Hostel Management System. It serves as a technical reference for developers and project evaluators (CS 432).

## 🗄️ 1. Database Schema & Normalization
The MySQL database (`stayease`) was designed with strict adherence to relational database rules, achieving the **3rd Normal Form (3NF)**.

### Key Design Decisions:
* **Separation of Credentials:** To avoid data anomalies and improve security, user authentication data (`Password_Hash`) is isolated in the `user_credentials` table, which references the main `members` table via a Foreign Key (`Member_ID`).
* **Lookup Tables for Data Integrity:** Complaint categories and subcategories are not stored as plain text. They are normalized into a `complaint_types` table. The `complaints` table strictly uses `Complaint_Type_ID` as a Foreign Key, preventing orphaned data (e.g., Error 1452 handling).

### Database Constraints Used:
* **Primary/Foreign Keys:** Enforced across all relational boundaries (e.g., linking payments to specific fee structures and members).
* **CHECK Constraints:** Implemented strict business logic directly at the database level. 
  * *Example:* `chk_resolution_logic` enforces that if a complaint's `Status` is updated to 'Resolved', the `Resolved_Date` must not be `NULL`. This prevents wardens from marking issues as resolved without a valid timestamp.

## 🔐 2. Security & Authentication Model
The system uses a completely stateless, Role-Based Access Control (RBAC) architecture.

* **Password Hashing:** Plain text passwords are **never** stored. The `Werkzeug.security` library is used to hash all passwords using the robust `scrypt` algorithm before database insertion.
* **JWT (JSON Web Tokens):** Upon successful login, the Flask backend issues a JWT containing the user's `Member_ID` and `Role`. The frontend stores this token in `localStorage` and includes it in the Authorization header for all subsequent API requests.
* **State Management:** To prevent "Ghost Data" (data leakage between sessions on shared devices), the frontend utilizes hard reloads (`window.location.reload()`) upon logout to instantly clear the DOM and memory state.

## 🚀 3. Backend API Logic
The Flask application is designed to be lightweight, utilizing complex SQL `JOIN` operations to minimize the number of queries required per page load.

* **The Portfolio Route (`/portfolio/<id>`):** This single endpoint aggregates a user's entire dashboard. It executes multiple parameterized `SELECT` queries utilizing `JOIN`s to fetch member details, active complaints (joining `complaints` and `complaint_types`), and payment history (joining `payments` and `fee_structures`) simultaneously.
* **Prepared Statements:** All MySQL queries use parameterized inputs (e.g., `WHERE Member_ID = %s`) provided by `mysql-connector-python` to absolutely prevent SQL Injection attacks.

## 🧰 4. Utility Scripts
Inside the `utils/` directory, you will find `seed_users.py`. 
* **Purpose:** This script programmatically generates the `scrypt` hashes and seeds the initial "Golden Dataset" of users into the `user_credentials` table using an `INSERT IGNORE` methodology.
* **Usage:** It is kept for documentation and future environment setups. The main `stayease.sql` dump already contains the output of this script for immediate testing.