import mysql.connector
from werkzeug.security import generate_password_hash

def setup_test_users():
    print("Connecting to database...")
    try:
        # Update these credentials if your MySQL uses a different user/password
        conn = mysql.connector.connect(
            host='localhost',
            user='root',          
            password='password',  
            database='stayease'
        )
        cursor = conn.cursor()

        # 1. Generate secure hashes for our test passwords
        print("Generating secure password hashes...")
        admin_hash = generate_password_hash("admin123")
        student_hash = generate_password_hash("student123")

        # 2. Insert or Update the users
        # We use ON DUPLICATE KEY UPDATE so it doesn't crash if they already exist
        sql = """
            INSERT INTO user_credentials (Member_ID, Username, Password_Hash) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Password_Hash = VALUES(Password_Hash);
        """

        # Insert Member 1 (Ensure Member_ID 1 actually exists in your `members` table!)
        cursor.execute(sql, (1, 'admin', admin_hash))
        
        # Insert Member 2 (Ensure Member_ID 2 actually exists in your `members` table!)
        cursor.execute(sql, (2, 'student', student_hash))

        conn.commit()
        print("\n✅ Test users created successfully!")
        print("-" * 40)
        print("👉 You can now log in at http://127.0.0.1:5000/dashboard with:")
        print("   👤 Admin   -> Username: admin   | Password: admin123")
        print("   🎓 Student -> Username: student | Password: student123")
        print("-" * 40)

    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        print("Make sure your MySQL server is running and the credentials are correct!")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

if __name__ == '__main__':
    setup_test_users()