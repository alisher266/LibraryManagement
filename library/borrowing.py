class BorrowingManager:
    def __init__(self, db):
        self.db = db

    def borrow_book(self, email, book_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        # Find user by email
        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user:
            print(f"❌ No user found with email {email}")
            conn.close()
            return

        # Find book by ID
        cursor.execute("SELECT title, available FROM books WHERE book_id=%s", (book_id,))
        book = cursor.fetchone()
        if not book:
            print(f"❌ No book found with ID {book_id}")
            conn.close()
            return

        if book["available"] == 0:
            print(f"❌ Book '{book['title']}' is already borrowed.")
            conn.close()
            return

        # Borrow the book
        cursor.execute(
            "INSERT INTO borrowing (user_id, book_id, borrow_date) VALUES (%s, %s, CURDATE())",
            (user["user_id"], book_id)
        )
        cursor.execute("UPDATE books SET available=0 WHERE book_id=%s", (book_id,))
        conn.commit()
        conn.close()
        print(f"✅ {email} borrowed '{book['title']}' successfully!")
    def return_book(self, email):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)

        # Step 1: Find user by email
        cursor.execute("SELECT user_id, name FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user:
            print(f"❌ No user found with email {email}")
            conn.close()
            return

        # Step 2: Find all active borrowings for this user
        cursor.execute("""
            SELECT b.borrow_id, bk.title
            FROM borrowing b
            JOIN books bk ON b.book_id = bk.book_id
            WHERE b.user_id=%s AND b.return_date IS NULL
        """, (user["user_id"],))
        records = cursor.fetchall()

        if not records:
            print(f"❌ {user['name']} ({email}) has no active borrowings.")
            conn.close()
            return

        # Step 3: Show borrowed books with sequential numbers
        print(f"Books currently borrowed by {user['name']} ({email}):")
        for i, r in enumerate(records, start=1):
            print(f"{i}. {r['title']}")

        # Step 4: Ask which one to return (sequential number)
        choice = input("Enter the number of the book to return: ")
        try:
            choice = int(choice)
            if choice < 1 or choice > len(records):
                print("❌ Invalid choice.")
                conn.close()
                return
        except ValueError:
            print("❌ Please enter a valid number.")
            conn.close()
            return

        # Map sequential number back to borrow_id
        borrow_id = records[choice - 1]["borrow_id"]
        book_title = records[choice - 1]["title"]

        # Step 5: Mark as returned
        cursor.execute("UPDATE borrowing SET return_date=CURDATE() WHERE borrow_id=%s", (borrow_id,))
        cursor.execute("UPDATE books SET available=1 WHERE book_id=(SELECT book_id FROM borrowing WHERE borrow_id=%s)", (borrow_id,))
        conn.commit()
        conn.close()
        print(f"✅ {user['name']} ({email}) returned '{book_title}' successfully!")



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
