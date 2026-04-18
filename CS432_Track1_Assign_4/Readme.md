# StayEase - Distributed Database Architecture

This repository contains the implementation for **Assignment 4: Database Sharding & Scalability** for the CS 432 Databases course at the Indian Institute of Technology, Gandhinagar.

The project demonstrates the migration of the StayEase hostel management system from a single monolithic MySQL database to a horizontally scaled, 3-node distributed database cluster.


## System Architecture

To achieve horizontal scalability, fault tolerance, and high availability, the database was split across three independent MySQL nodes (Ports: `3307`, `3308`, `3309`).

### 1. Hash-Based Partitioning (Sharded Data)
Heavy, fast-growing transactional tables are sharded using a Modulo hash algorithm on the `Member_ID` key (`Member_ID % 3`). This ensures that a specific user's entire dataset is strictly co-located on a single physical node, optimizing query speeds.
* **Sharded Tables:** `members`, `room_allocations`, `complaints`

### 2. Reference Data Replication
Because MySQL cannot natively execute `JOIN` queries across different physical servers, small static infrastructure tables are designated as "Reference Data" and identically replicated to all three nodes. This allows complex joins to execute safely and locally.
* **Replicated Tables:** `rooms`, `hostels`, `roles`, `complaint_types`

### 3. Application-Level Query Routing
The Flask backend has been rewritten to act as a dynamic, distributed query router:
* **Direct Routing:** Single-key lookups and inserts (e.g., viewing a specific portfolio or raising a complaint) are mathematically routed directly to the specific shard holding the data.
* **Scatter-Gather:** Range queries and global dashboard views (e.g., viewing the Admin Member Directory) open concurrent connections to all three nodes, execute the query, and merge/sort the results in Python memory before returning a unified JSON response.

## Prerequisites
* Python 3.8+
* MySQL Server (Local for source DB, plus 3 active ports for the cluster nodes)
* Flask and dependencies (`pip install -r requirements.txt`)

## Installation & Setup

1. **Start the Cluster Nodes:**
   Ensure your three MySQL shard instances are running on ports `3307`, `3308`, and `3309`.

2. **Run the Migration Script:**
   The automated Python script extracts data from the local monolith, applies the routing logic, and distributes the data across the cluster.
   ```bash
   python migrate_to_cluster.py

Note: This script automatically handles both hashing the transactional tables and cloning the reference tables

3. **Start the Flask Application:**
    ```bash
    python app.py

## Key Files
* migrate_to_cluster.py: The data migration and replication engine.

* utils.py: Contains the get_shard_connection(member_id) router, the Scatter-Gather port list, and JWT security wrappers.

* routes_admin.py: Implements Scatter-Gather routing for admin directories and cross-cluster statistics.

* routes_portfolio.py: Implements Direct Routing for user-specific lookups, updates, and inserts.

* QueryCraft_report.pdf: The complete scalability, consistency, and trade-offs analysis report.

