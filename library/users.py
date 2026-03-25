class UserManager:
    def __init__(self, db):
        self.db = db

    def add_user(self, name, email):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        conn.close()
        print("User added successfully!")

    def view_users(self):
        conn = self.db.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        conn.close()
        return results

    def update_user(self, user_id, name, email):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name=%s, email=%s WHERE user_id=%s", (name, email, user_id))
        conn.commit()
        conn.close()
        print("User updated!")

    def delete_user(self, user_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM borrowing WHERE user_id=%s AND return_date IS NULL", (user_id,))
        if cursor.fetchone():
            print("Cannot delete: user has borrowed books.")
            conn.close()
            return
        cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        conn.close()
        print("User deleted!")
