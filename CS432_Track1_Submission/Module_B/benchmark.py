import time
import mysql.connector
import statistics

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',  # <- Replace this with your active MySQL password
        database='stayease'
    )

QUERIES = {
    "Portfolio - Room Allocation": (
        """SELECT m.First_Name, m.Last_Name, m.Email, m.Contact_Number,
                  r.Room_Number, h.Hostel_Name
           FROM members m
           LEFT JOIN room_allocations ra 
               ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
           LEFT JOIN rooms r ON ra.Room_ID = r.Room_ID
           LEFT JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
           WHERE m.Member_ID = %s""",
        (1,)
    ),
    "Portfolio - Complaints": (
        """SELECT c.Description, c.Submission_Date, c.Status, ct.Type_Name
           FROM complaints c
           JOIN complaint_types ct 
               ON c.Complaint_Type_ID = ct.Complaint_Type_ID
           WHERE c.Member_ID = %s
           ORDER BY c.Submission_Date DESC""",
        (1,)
    ),
    "Portfolio - Payments": (
        """SELECT p.Amount_Paid, p.Payment_Date, p.Payment_Status, f.Fee_Name
           FROM payments p
           JOIN fee_structures f ON p.Fee_Type_ID = f.Fee_Type_ID
           WHERE p.Member_ID = %s
           ORDER BY p.Payment_Date DESC""",
        (1,)
    ),
}

def benchmark_query(cursor, label, query, params, runs=100):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        cursor.execute(query, params)
        cursor.fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)
    avg  = statistics.mean(times)
    mini = min(times)
    maxi = max(times)
    print(f"  {label}:")
    print(f"    Avg: {avg:.4f} ms | Min: {mini:.4f} ms | Max: {maxi:.4f} ms")
    return avg, mini, maxi

def run_explain(cursor, label, query, params):
    cursor.execute("EXPLAIN " + query, params)
    rows = cursor.fetchall()
    print(f"\n  EXPLAIN for '{label}':")
    for row in rows:
        print(f"    table={row[2]}, type={row[3]}, "
              f"key={row[5]}, rows={row[8]}, Extra={row[9]}")

def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("  StayEase — Query Benchmark")
    print("=" * 60)

    print("\n>>> EXPLAIN Plans:")
    for label, (query, params) in QUERIES.items():
        run_explain(cursor, label, query, params)

    print("\n>>> Timing (100 runs each):")
    results = {}
    for label, (query, params) in QUERIES.items():
        results[label] = benchmark_query(cursor, label, query, params)

    print("\n>>> Summary:")
    print(f"  {'Query':<35} {'Avg (ms)':>10} {'Min (ms)':>10} {'Max (ms)':>10}")
    print("  " + "-" * 68)
    for label, (avg, mini, maxi) in results.items():
        print(f"  {label:<35} {avg:>10.4f} {mini:>10.4f} {maxi:>10.4f}")

    cursor.close()
    conn.close()
    print("\nDone.")

if __name__ == '__main__':
    main()

