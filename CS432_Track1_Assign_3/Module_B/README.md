# StayEase Hostel Management System
**Custom B+ Tree Database Engine & Flask Web API Integration**

This repository contains the complete implementation of the StayEase Hostel Management System for CS-432 (Databases). The project is divided into two major architectural modules: a custom ACID-compliant B+ Tree database engine built from scratch, and a production-grade Flask REST API backed by MySQL that handles multi-user concurrency.

## Project Overview

### Module A: The Database Engine
We built a custom transactional database engine in Python that guarantees all four ACID properties.
* **Storage:** Data is stored and indexed entirely using a custom **B+ Tree** data structure (`bplustree.py`) with logarithmic $O(\log n)$ performance.
* **Transaction Management:** Features a strict `begin()`, `commit()`, and `rollback()` lifecycle using threading locks to ensure **Isolation**.
* **Crash Recovery:** Implements **Write-Ahead Logging (WAL)** (`stayease_wal.log`) and Checkpointing. Capable of performing full `REDO` and `UNDO` operations to recover committed data after a simulated hard crash.

### Module B: The Web API & Concurrency
We transitioned the core logic into a networked, multi-user web environment to test concurrency defenses.
* **API Framework:** A RESTful web API built with **Flask** to handle administrative tasks like member registration and room allocation.
* **Security:** Endpoints are secured using JSON Web Tokens (JWT) via the `@token_required` decorator.
* **Race Condition Defense:** Implements **Pessimistic Locking** (`SELECT ... FOR UPDATE`) at the MySQL InnoDB level to strictly prevent room overbooking during high-traffic spikes.





## File Structure
* **`app.py in Module_B/web/app `**: The main Flask API application handling web requests and MySQL concurrency locks.
* **`db_manager.py` & `transaction_manager.py`**: The core transaction logic, logging, and crash recovery systems for the custom engine.
* **`bplustree.py`**: The underlying B+ Tree data structure acting as the storage engine.
* **`setup_db.py`**: Database connection setup, configuration, and initialization scripts.
* **`stress_test.py`**: A custom multi-threaded Python script simulating 100 concurrent requests and random network failures to test database locks and rollback capabilities.
* **`locustfile.py`**: Configuration for Locust to simulate a swarm of 100 concurrent administrative users hitting the API.
* **`demo.ipynb in Module_A`**: An interactive Jupyter Notebook demonstrating Atomicity, Consistency, Isolation, and Durability (ACID) validations for Module A.

## ⚙️ Setup & Installation

**1. Clone the repository:**
```bash
git clone <https://github.com/nachiketpatil0105/stay_ease>
cd stay_ease
```
**2. Open CS432_Track1_Assgn_3 in vs code**

**3. Install Dependencies:**
Ensure you have Python 3 installed, then install the required libraries:
```bash
pip install requirements.txt
```

**4. MySQL Database Setup (For Module B):**
Ensure your local MySQL server is running. Update your database credentials (username, password, host) inside `app.py` and `setup_db.py`.

## Running the System

### Starting the Flask API
To start the web server for Module B, run:
```bash
python app.py
```
The API will be available at `http://localhost:5000`.

### Running the Custom Engine Demo
To see the B+ Tree, WAL, and crash recovery in action (Module A), open the Jupyter Notebook:
```bash
jupyter notebook demo.ipynb
```

## Concurrency & Stress Testing

This project includes rigorous load testing to prove the absence of race conditions and the enforcement of the Isolation property.

### 1. Custom Stress Test (Race Condition Defense)
Fires 100 concurrent threads at a single room and simulates mid-transaction crashes.
```bash
python stress_test.py
```
> **Evaluator Note regarding Room Capacity:** > In the original schema design for Module A, Room 101 has a maximum capacity of 2. To properly demonstrate a large-scale race condition and allow multiple threads to successfully book beds before triggering the lock rejections, the `stress_test.py` setup phase dynamically updates the B+ Tree to increase Room 101's capacity to exactly **5**.

```text
============================================================
MODULE B: STRESS TEST & RACE CONDITION DEFENSE
============================================================
[START] Room 101 capacity set to 5.
[START] Unleashing 100 concurrent booking requests...

============================================================
STRESS TEST RESULTS
============================================================
Successful Bookings   : 5 (Expected: 5)
Room Full Rejections  : 90 (Expected: 90)
Simulated Crashes     : 5 (Expected: 5)
Unexpected Errors     : 0 (Expected: 0)

[FINAL] Room 101 Capacity Remaining: 0 (Expected: 0)

MODULE B CONCURRENCY TEST PASSED PERFECTLY!
```

### 2. Locust Load Testing
To test the API under sustained network traffic:
1. Start the Flask server (`python app.py`).
2. Open a new terminal and start Locust: `locust -f locustfile.py`.
3. Open your browser to `http://localhost:8089`.
4. Set the number of users to **100** with a spawn rate of **10** and click **Start Swarming**.