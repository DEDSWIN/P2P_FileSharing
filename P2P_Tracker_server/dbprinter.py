import sqlite3

# Specify the database path
DB_PATH = 'instance/tracker.db'  # Replace with the actual name/path of your database if different

def print_table_contents():
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch and print data from the 'users' table
    print("\n-- Users Table --")
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Peer Address: {user[2]}")
    else:
        print("No users found.")

    # Fetch and print data from the 'files' table
    print("\n-- Files Table --")
    cursor.execute("SELECT * FROM File")
    files = cursor.fetchall()

    if files:
        for file in files:
            print(f"ID: {file[0]}, Filename: {file[1]}, Filetype: {file[2]}, Size: {file[3]} bytes, Peer: {file[4]}, Comments: {file[5]}")
    else:
        print("No files found.")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    print_table_contents()
