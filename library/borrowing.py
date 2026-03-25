class BorrowingManager:
    def __init__(self, db):
        self.db = db

    def borrow_book(self, user_id, book_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            cursor.execute("SELECT available FROM books WHERE book_id=%s FOR UPDATE", (book_id,))
            book = cursor.fetchone()
            if not book or book["available"] == 0:
                print("Book not available!")
                conn.rollback()
                return
            cursor.execute("INSERT INTO borrowing (user_id, book_id, borrow_date) VALUES (%s, %s, CURDATE())",
                           (user_id, book_id))
            cursor.execute("UPDATE books SET available=0 WHERE book_id=%s", (book_id,))
            conn.commit()
            print("Book borrowed successfully!")
        except Exception as e:
            conn.rollback()
            print("Error:", e)
        finally:
            conn.close()

    def return_book(self, borrow_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT book_id FROM borrowing WHERE borrow_id=%s AND return_date IS NULL", (borrow_id,))
        record = cursor.fetchone()
        if not record:
            print("Invalid or already returned!")
            conn.close()
            return
        cursor.execute("UPDATE borrowing SET return_date=CURDATE() WHERE borrow_id=%s", (borrow_id,))
        cursor.execute("UPDATE books SET available=1 WHERE book_id=%s", (record["book_id"],))
        conn.commit()
        conn.close()
        print("Book returned successfully!")
