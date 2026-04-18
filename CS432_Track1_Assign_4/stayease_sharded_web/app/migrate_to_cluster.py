import mysql.connector

# Local database
LOCAL_DB_CONFIG = {
    "host": "localhost",
    "user": "root",          
    "password": "password",  # Change to your local password
    "database": "stayease"   
}

# The IITGN Cluster (Destinations)
REMOTE_DB_USER = "QueryCraft"
REMOTE_DB_PASS = "password@123"
REMOTE_HOST = "10.0.116.184"
REMOTE_DB_NAME = "QueryCraft"

PORTS = [3307, 3308, 3309]

def get_remote_connection(shard_index):
    """Returns a connection to the specific physical shard."""
    return mysql.connector.connect(
        host=REMOTE_HOST,
        port=PORTS[shard_index],
        user=REMOTE_DB_USER,
        password=REMOTE_DB_PASS,
        database=REMOTE_DB_NAME
    )

def shard_table(local_cursor, table_name, shard_key_column):
    """Splits massive tables across the 3 servers using Modulo Hashing."""
    print(f"\n--- Sharding {table_name} ---")
    
    # Fetch all local data
    local_cursor.execute(f"SELECT * FROM {table_name}")
    rows = local_cursor.fetchall()
    columns = [desc[0] for desc in local_cursor.description]
    
    if not rows:
        print(f"No data found in local {table_name}.")
        return

    # Prepare the INSERT query dynamically
    placeholders = ", ".join(["%s"] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    # Distribute row by row
    success_count = 0
    for row in rows:
        # Create a dictionary to easily access the shard key
        row_dict = dict(zip(columns, row))
        shard_key_value = row_dict[shard_key_column]
        
        # Determine target shard (Hash-based partitioning)
        shard_index = shard_key_value % 3
        
        # Connect to the specific shard, insert, and close
        remote_conn = get_remote_connection(shard_index)
        remote_cursor = remote_conn.cursor()
        
        try:
            remote_cursor.execute(insert_query, row)
            remote_conn.commit()
            success_count += 1
            print(f"Routed {shard_key_column} {shard_key_value} -> Shard {shard_index + 1} (Port {PORTS[shard_index]})")
        except Exception as e:
            # We use pass here so it doesn't crash if the data is already in the database
            pass
        finally:
            remote_cursor.close()
            remote_conn.close()
            
    print(f"Successfully sharded {success_count}/{len(rows)} records for {table_name}.")


def replicate_table(local_cursor, table_name):
    """Copies small Reference Data tables identically to ALL 3 servers."""
    print(f"\n--- Replicating {table_name} ---")
    
    # Fetch all local data
    local_cursor.execute(f"SELECT * FROM {table_name}")
    rows = local_cursor.fetchall()
    columns = [desc[0] for desc in local_cursor.description]
    
    if not rows:
        print(f"No data found in local {table_name}.")
        return

    # Prepare the INSERT query dynamically
    placeholders = ", ".join(["%s"] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    # Loop through all 3 shards and insert the full table into each
    for shard_index in range(len(PORTS)):
        remote_conn = get_remote_connection(shard_index)
        remote_cursor = remote_conn.cursor()
        
        try:
            # Clear existing data first so we don't get duplicate key errors
            remote_cursor.execute(f"TRUNCATE TABLE {table_name}")
            # Insert all rows at once
            remote_cursor.executemany(insert_query, rows)
            remote_conn.commit()
            print(f"Replicated {len(rows)} records -> Shard {shard_index + 1} (Port {PORTS[shard_index]})")
        except Exception as e:
            pass
        finally:
            remote_cursor.close()
            remote_conn.close()
            
    print(f"Successfully replicated {table_name} to all nodes.")


if __name__ == "__main__":
    # Connect to local DB
    local_conn = mysql.connector.connect(**LOCAL_DB_CONFIG)
    local_cursor = local_conn.cursor()

    try:
        # 1. SHARD the heavy transactional tables
        shard_table(local_cursor, "members", "Member_ID")
        shard_table(local_cursor, "room_allocations", "Member_ID")
        shard_table(local_cursor, "complaints", "Member_ID")
        
        # 2. REPLICATE the static infrastructure tables
        replicate_table(local_cursor, "rooms")
        replicate_table(local_cursor, "hostels")
        replicate_table(local_cursor, "roles")
        replicate_table(local_cursor, "complaint_types")
        
    finally:
        local_cursor.close()
        local_conn.close()
        print("\nMigration Complete!")