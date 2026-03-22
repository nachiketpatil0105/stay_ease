# StayEase Database SQL Files

This directory contains the database export files required to run the StayEase Management System. To accommodate different testing preferences, the database is provided in both a unified, optimized format and a modular, pre-optimized format.

##  Quick Start

To instantly set up the fully optimized database with all dummy data, users, and performance indexes required for **SubTask 4 & 5**, please import the following file:

* **`stayease.sql`**
  * **Description:** The final, self-contained production dump.
  * **Contents:** Contains the complete Data Definition Language (DDL), the seeded Data Manipulation Language (DML) "Golden Dataset," all User/Role setups, and the **Performance Optimization Indexes** (Composite B-Trees).
  * **How to use:** Import this single file via MySQL Workbench (Server > Data Import) or run `source stayease.sql` in the MySQL CLI.

---

##  Modular Architecture

If you prefer to review the database architecture step-by-step , the initial database state has been split into three distinct files based on separation of concerns in the database folder of this directory:

1. **`stayease_ddl.sql` (Structure)**
   * Contains the raw schema definitions, tables, primary keys, and foreign key constraints.
2. **`stayease_dml.sql` (Data)**
   * Contains the `INSERT` statements for the "Golden Dataset" (dummy users, rooms, complaints, and payments).
3. **`security_setup.sql` (Security)**
   * Contains the creation of the MySQL user roles (`StayEaseAdmin`, `StayEaseUser`) and their respective grant privileges.

*Note: If building from the modular files, they must be executed in the exact order listed above to satisfy foreign key constraints.*

##  Default Login Credentials
Once the database is imported, you can log into the Flask application using the seeded Admin account:
* **Username:** `admin`
* **Password:** `admin123`