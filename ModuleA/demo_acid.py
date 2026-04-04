# demo_acid.py
"""
CS 432 — Module A: ACID Demonstration
Covers all four properties with concrete pass/fail assertions.
"""

import threading
import time
import os
from db_manager import DatabaseManager
from transaction_manager import TransactionManager

# ------------------------------------------------------------------ #
#  SETUP                                                               #
# ------------------------------------------------------------------ #

def setup_database():
    """Create a fresh database with three tables as required by the assignment."""
    # Clean up old files for a fresh demo
    for f in ["wal.log", "db_snapshot.pkl", "db_snapshot.pkl.bak"]:
        if os.path.exists(f):
            os.remove(f)
    
    db = DatabaseManager()
    db.create_database("shop")
    
    # Table 1: Users
    db.create_table("shop", "users", 
                    schema={"user_id": int, "name": str, "balance": int, "city": str},
                    order=4, search_key="user_id")
    
    # Table 2: Products
    db.create_table("shop", "products",
                    schema={"product_id": int, "name": str, "stock": int, "price": int},
                    order=4, search_key="product_id")
    
    # Table 3: Orders
    db.create_table("shop", "orders",
                    schema={"order_id": int, "user_id": int, "amount": int, "time": str},
                    order=4, search_key="order_id")
    
    tm = TransactionManager(db, "shop", log_file="wal.log")
    
    # Seed initial data using a transaction
    txn = tm.begin_transaction()
    tm.insert(txn, "users",    1, {"user_id": 1, "name": "Alice", "balance": 1000, "city": "Delhi"})
    tm.insert(txn, "users",    2, {"user_id": 2, "name": "Bob",   "balance": 500,  "city": "Mumbai"})
    tm.insert(txn, "products", 10, {"product_id": 10, "name": "Laptop", "stock": 5, "price": 800})
    tm.insert(txn, "products", 11, {"product_id": 11, "name": "Phone",  "stock": 0, "price": 300})
    tm.commit(txn) # save_to_disk() is called inside commit()
    
    return db, tm

# ------------------------------------------------------------------ #
#  TEST 1: ATOMICITY                                                   #
# ------------------------------------------------------------------ #

def test_atomicity(db, tm):
    print("\n" + "="*60)
    print("TEST 1: ATOMICITY")
    print("Scenario: Purchase transaction crashes mid-way.")
    print("Expected: ALL changes are rolled back. No partial state.")
    print("="*60)
    
    # Check state before
    user_before    = tm.search("users", 1)
    product_before = tm.search("products", 10)
    print(f"\nBEFORE — User 1 balance: {user_before['balance']}, "
          f"Product 10 stock: {product_before['stock']}")
    
    txn = tm.begin_transaction()
    try:
        # Step 1: Deduct balance
        tm.update(txn, "users", 1, 
                  {**user_before, "balance": user_before["balance"] - 200})
        
        # Step 2: Reduce stock
        tm.update(txn, "products", 10,
                  {**product_before, "stock": product_before["stock"] - 1})
        
        # Step 3: SIMULATED CRASH — raise an exception before inserting order
        raise RuntimeError("💥 Simulated crash during order insertion!")
        
        # This line is never reached
        tm.insert(txn, "orders", 1001,
                  {"order_id": 1001, "user_id": 1, "amount": 200, "time": "2026-04-01"})
        tm.commit(txn)
        
    except RuntimeError as e:
        print(f"\n{e}")
        tm.rollback(txn)
    
    # Check state after — should be identical to before
    user_after    = tm.search("users", 1)
    product_after = tm.search("products", 10)
    order_after   = tm.search("orders", 1001)
    
    print(f"\nAFTER  — User 1 balance: {user_after['balance']}, "
          f"Product 10 stock: {product_after['stock']}, "
          f"Order 1001: {order_after}")
    
    assert user_after["balance"]    == user_before["balance"],    "❌ Balance was not restored!"
    assert product_after["stock"]   == product_before["stock"],   "❌ Stock was not restored!"
    assert order_after              is None,                       "❌ Order should not exist!"
    print("\n✅ ATOMICITY PASSED — No partial state after crash")

# ------------------------------------------------------------------ #
#  TEST 2: CONSISTENCY                                                 #
# ------------------------------------------------------------------ #

def test_consistency(db, tm):
    print("\n" + "="*60)
    print("TEST 2: CONSISTENCY")
    print("Scenario: Try to sell a product that is out of stock.")
    print("Expected: Transaction is rejected, balance and orders unchanged.")
    print("="*60)
    
    # Passing None for txn here because we are outside a transaction
    user_before    = tm.search("users", 1, None)
    product_before = tm.search("products", 11, None)  # Stock = 0!
    
    print(f"\nBEFORE — User 1 balance: {user_before['balance']}, "
          f"Product 11 stock: {product_before['stock']}")
    
    txn = tm.begin_transaction()
    try:
        # Table 1: Update user balance
        tm.update(txn, "users", 1,
                  {**user_before, "balance": user_before["balance"] - 300})
                  
        # Table 2: Insert a pending order
        tm.insert(txn, "orders", 1002, 
                  {"order_id": 1002, "user_id": 1, "amount": 300, "time": "2026-04-01"})
        
        # Table 3: Check business rule for products BEFORE modifying
        if product_before["stock"] <= 0:
            raise ValueError("  Consistency violation: Product is out of stock!")
            
        tm.update(txn, "products", 11,
                  {**product_before, "stock": product_before["stock"] - 1})
        tm.commit(txn)
        
    except ValueError as e:
        print(f"\n{e}")
        tm.rollback(txn)
    
    # Verify everything rolled back
    user_after    = tm.search("users", 1, None)
    product_after = tm.search("products", 11, None)
    order_after   = tm.search("orders", 1002, None)
    
    print(f"\nAFTER  — User 1 balance: {user_after['balance']}, "
          f"Product 11 stock: {product_after['stock']}, "
          f"Order 1002: {order_after}")
    
    assert user_after["balance"] == user_before["balance"], " Balance changed illegally!"
    assert product_after["stock"] == 0,                     " Stock should still be 0!"
    assert order_after is None,                             " Order was not rolled back!"
    print("\n CONSISTENCY PASSED — Invalid transaction was rejected cleanly across 3 tables")

# ------------------------------------------------------------------ #
#  TEST 3: ISOLATION                                                   #
# ------------------------------------------------------------------ #

def test_isolation(db, tm):
    print("\n" + "="*60)
    print("TEST 3: ISOLATION")
    print("Scenario: Two threads try to buy the last unit simultaneously.")
    print("Expected: Only one succeeds. No double-spending.")
    print("="*60)
    
    # Reset product stock to exactly 1 so only one purchase can succeed
    setup_txn = tm.begin_transaction()
    current_product = tm.search("products", 10)
    tm.update(setup_txn, "products", 10, {**current_product, "stock": 1})
    tm.commit(setup_txn)
    
    results = []   # Collect outcomes from both threads
    
    def purchase_attempt(thread_id, user_id, delay):
        """Each thread tries to buy the last product."""
        time.sleep(delay)  # Stagger the starts slightly
        txn = tm.begin_transaction()
        try:
            # Pass the txn object to secure the locks BEFORE reading
            user    = tm.search("users",    user_id, txn)
            product = tm.search("products", 10, txn)
            
            if product["stock"] <= 0:
                raise ValueError(f"Thread {thread_id}: Out of stock!")
            
            tm.update(txn, "users", user_id,
                      {**user, "balance": user["balance"] - 800})
            
            # Small sleep INSIDE the transaction to force overlap
            time.sleep(0.05)
            
            tm.update(txn, "products", 10,
                      {**product, "stock": product["stock"] - 1})
            
            tm.insert(txn, "orders", 2000 + thread_id,
                      {"order_id": 2000 + thread_id, "user_id": user_id,
                       "amount": 800, "time": "2026-04-01"})
            
            tm.commit(txn)
            results.append((thread_id, "SUCCESS"))
            print(f"  Thread {thread_id}: Purchase SUCCEEDED")
            
        except Exception as e:
            tm.rollback(txn)
            results.append((thread_id, f"FAILED: {e}"))
            print(f"  Thread {thread_id}: Purchase FAILED — {e}")
    
    # Launch both threads at nearly the same time
    t1 = threading.Thread(target=purchase_attempt, args=(1, 1, 0.0))
    t2 = threading.Thread(target=purchase_attempt, args=(2, 2, 0.01))
    t1.start(); t2.start()
    t1.join();  t2.join()
    
    final_stock = tm.search("products", 10)["stock"]
    successes   = [r for r in results if r[1] == "SUCCESS"]
    
    print(f"\nFinal stock: {final_stock}")
    print(f"Successful purchases: {len(successes)}")
    
    assert final_stock >= 0,       "❌ Stock went negative — isolation failed!"
    assert len(successes) <= 1,    "❌ Both threads succeeded — double-spending occurred!"
    print("\n✅ ISOLATION PASSED — Table-level locking prevented race condition")

# ------------------------------------------------------------------ #
#  TEST 4: DURABILITY                                                  #
# ------------------------------------------------------------------ #

def test_durability(db, tm):
    print("\n" + "="*60)
    print("TEST 4: DURABILITY")
    print("Scenario: Commit data across 3 tables, simulate restart, verify data survived.")
    print("="*60)
    
    # Insert records into all 3 tables and commit
    txn = tm.begin_transaction()
    
    # Table 1: users
    tm.insert(txn, "users", 99,
              {"user_id": 99, "name": "Durable Dave", "balance": 777, "city": "Chennai"})
    # Table 2: products
    tm.insert(txn, "products", 99, 
              {"product_id": 99, "name": "Titanium Shield", "stock": 50, "price": 100})
    # Table 3: orders
    tm.insert(txn, "orders", 9999, 
              {"order_id": 9999, "user_id": 99, "amount": 100, "time": "2026-04-03"})
              
    tm.commit(txn)
    
    print("\nData committed and saved to disk.")
    
    # Simulate a restart — create a brand new DatabaseManager and load from disk
    print("Simulating system restart...")
    new_db = DatabaseManager()
    new_db.load_from_disk()
    
    # The new_db needs its own TransactionManager (pointing at the loaded state)
    new_tm = TransactionManager(new_db, "shop", log_file="wal.log")
    
    user_rec  = new_tm.search("users", 99, None)
    prod_rec  = new_tm.search("products", 99, None)
    order_rec = new_tm.search("orders", 9999, None)
    
    print(f"\nAfter restart — User 99: {user_rec}")
    print(f"After restart — Product 99: {prod_rec}")
    print(f"After restart — Order 9999: {order_rec}")
    
    assert user_rec is not None,  " User record lost!"
    assert prod_rec is not None,  " Product record lost!"
    assert order_rec is not None, " Order record lost!"
    assert user_rec["name"] == "Durable Dave", " Record corrupted after restart!"
    
    print("\n DURABILITY PASSED — Committed data for 3 tables survived simulated restart")

# ------------------------------------------------------------------ #
#  TEST 5: CRASH RECOVERY ON RESTART                                 #
# ------------------------------------------------------------------ #

def test_crash_recovery(db, tm):
    print("\n" + "="*60)
    print("TEST 5: CRASH RECOVERY ON RESTART")
    print("Scenario: Process crashes mid-transaction. System restarts.")
    print("Expected: Incomplete transaction is found in WAL and undone.")
    print("="*60)
    
    # 1. Start a transaction and make multi-table changes
    txn = tm.begin_transaction()
    user_before = tm.search("users", 1)
    tm.update(txn, "users", 1, {**user_before, "balance": 0})
    tm.insert(txn, "orders", 999, {"order_id": 999, "user_id": 1, "amount": 1000, "time": "2026-04-01"})
    
    print("\n[CRASH] Power pulled! System died before COMMIT or ROLLBACK.")
    # We deliberately DO NOT commit or rollback here. 
    # The WAL has BEGIN and WRITE entries, but no COMMIT.
    
    # 2. Simulate startup
    print("\nSimulating system restart...")
    new_db = DatabaseManager()
    new_db.load_from_disk() # Loads the last clean snapshot
    
    # 3. Initializing TransactionManager triggers self._recover()
    # This will read the WAL, see the incomplete txn, and undo it!
    new_tm = TransactionManager(new_db, "shop", log_file="wal.log")
    
    # 4. Verify the dirty data was cleaned up
    user_after = new_tm.search("users", 1)
    order_after = new_tm.search("orders", 999)
    
    assert user_after["balance"] == user_before["balance"], "Balance was not recovered!"
    assert order_after is None, "Incomplete order was not removed!"
    print("\n CRASH RECOVERY PASSED — Incomplete data undone from WAL on restart")

# ------------------------------------------------------------------ #
#  MAIN                                                                #
# ------------------------------------------------------------------ #

print("╔══════════════════════════════════════════════════════════╗")
print("║         CS 432 — Module A: ACID Validation Demo          ║")
print("╚══════════════════════════════════════════════════════════╝")

db, tm = setup_database()

test_atomicity(db, tm)
test_consistency(db, tm)
test_isolation(db, tm)
test_durability(db, tm)

print("\n" + "="*60)
print("ALL ACID TESTS PASSED ✅")
print("="*60)