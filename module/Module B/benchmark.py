import mysql.connector
import time

def run_benchmark():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',          # Replace with your MySQL username
        password='Niraj@1607',  # Replace with your MySQL password
        database='stayease'
    )
    cursor = conn.cursor()
    
    query = "SELECT * FROM complaints WHERE Status = 'Pending';"
    
    # We run the query 1,000 times to make the time difference obvious
    iterations = 1000
    
    start_time = time.time()
    for _ in range(iterations):
        cursor.execute(query)
        cursor.fetchall() # Fetch the results
    end_time = time.time()
    
    total_time = end_time - start_time
    print(f"Total time for {iterations} queries: {total_time:.4f} seconds")
    print(f"Average time per query: {(total_time / iterations) * 1000:.4f} ms")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    run_benchmark()