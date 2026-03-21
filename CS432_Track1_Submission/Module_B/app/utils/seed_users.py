import mysql.connector
from werkzeug.security import generate_password_hash

def seed_first_time_users():
    print("Connecting to StayEase database...")
    try:
        # Update your password if needed
        conn = mysql.connector.connect(
            host='localhost',
            user='root',          
            password='password',  # Write your MySQL password here
            database='stayease'
        )
        cursor = conn.cursor()

        print("Generating secure password hashes...")
        
        # Define the exact users (Member_ID, First_Name, Plain_Password)
        # IMPORTANT: These Member_IDs (1, 2, 3, 4, 5) MUST already exist in your `members` table!
        users_to_create = [
            (100, 'admin', 'admin123'), # Admin (Usually best to keep this as 'admin')
            (102, 'riya', 'warden123'), # Warden 1 First Name
            (106, 'rakesh', 'warden123'),# Warden 2 First Name
            (110, 'priya', 'student123'),# Student 1 First Name
            (114, 'amit', 'student123'), # Student 2 First Name
            (116, 'neha', 'student123')  #Student 3 FIrst Name
        ]

        sql = """
            INSERT IGNORE INTO user_credentials (Member_ID, Username, Password_Hash) 
            VALUES (%s, %s, %s);
        """

        success_count = 0
        for member_id, first_name, plain_text_pass in users_to_create:
            hashed_pass = generate_password_hash(plain_text_pass)
            
            username = first_name.strip().lower()
            
            cursor.execute(sql, (member_id, username, hashed_pass))
            
            if cursor.rowcount == 1:
                print(f"  [+] Created credentials for: {username}")
                success_count += 1
            else:
                print(f"  [-] Skipped {username} (Already exists)")

        conn.commit()
        
        print("\n Database Seeding Complete!")
        print("-" * 50)
        print(f"Successfully inserted {success_count} new login accounts.")
        print("-" * 50)
        print("You can now test your RBAC dashboard with:")
        print("Admin   -> Username: admin | Password: admin123")
        print("Warden  -> Username: riya  | Password: warden123")
        print("Student -> Username: priya  | Password: student123")
        print("-" * 50)

    except mysql.connector.Error as err:
        print(f"\n Database Error: {err}")
        print("Hint: Make sure Member IDs which you are using to create passwords actually exist in your 'members' table first!")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals() and conn.is_connected(): conn.close()

if __name__ == '__main__':
    seed_first_time_users()