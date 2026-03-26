class BorrowingManager:
    def __init__(self, db):
        self.db = db

    def borrow_book(self, email, book_title):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        # Find user by email
        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user:
            print(f"No user found with email {email}")
            conn.close()
            return

        # Find book by title
        cursor.execute("SELECT book_id, available FROM books WHERE title=%s", (book_title,))
        book = cursor.fetchone()
        if not book:
            print(f"No book found with title '{book_title}'")
            conn.close()
            return

        if book["available"] == 0:
            print(f"Book '{book_title}' is already borrowed.")
            conn.close()
            return

        # Borrow the book
        cursor.execute(
            "INSERT INTO borrowing (user_id, book_id, borrow_date) VALUES (%s, %s, CURDATE())",
            (user["user_id"], book["book_id"])
        )
        cursor.execute("UPDATE books SET available=0 WHERE book_id=%s", (book["book_id"],))
        conn.commit()
        conn.close()
        print(f"{email} borrowed '{book_title}' successfully!")

    def return_book(self, borrow_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT book_id FROM borrowing WHERE borrow_id=%s AND return_date IS NULL", (borrow_id,))
        record = cursor.fetchone()
        if not record:
            print("Invalid borrow ID or already returned.")
            conn.close()
            return

        cursor.execute("UPDATE borrowing SET return_date=CURDATE() WHERE borrow_id=%s", (borrow_id,))
        cursor.execute("UPDATE books SET available=1 WHERE book_id=%s", (record["book_id"],))
        conn.commit()
        conn.close()
        print("Book returned successfully!")
    def view_borrowings(self):
        conn = self.db.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)

        # Join users + books for readable output
        cursor.execute("""
            SELECT b.borrow_id, u.name AS user_name, u.email, bk.title AS book_title,
                   b.borrow_date, b.return_date
            FROM borrowing b
            JOIN users u ON b.user_id = u.user_id
            JOIN books bk ON b.book_id = bk.book_id
        """)
        results = cursor.fetchall()
        conn.close()

        borrowings = []
        for r in results:
            status = f"Returned on {r['return_date']}" if r["return_date"] else "Currently borrowed"
            borrowings.append(
                f"[{r['borrow_id']}] {r['user_name']} ({r['email']}) borrowed '{r['book_title']}' on {r['borrow_date']} - {status}"
            )
        return borrowings
