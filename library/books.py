class Book:
    def __init__(self, book_id, title, author, year, available=True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.available = available

    def __str__(self):
        status = "Available" if self.available else "Borrowed"
        return f"[{self.book_id}] {self.title} by {self.author} ({self.year}) - {status}"
class BookManager:
    def __init__(self, db):
        self.db = db

    def add_book(self, title, author, year):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, year, available) VALUES (%s, %s, %s, %s)", 
                       (title, author, year, True))
        conn.commit()
        conn.close()
        print("Book added successfully!")

    def view_books(self):
        conn = self.db.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books")
        results = cursor.fetchall()
        conn.close()

        # Convert dictionaries into Book objects
        books = [Book(r["book_id"], r["title"], r["author"], r["year"], r["available"]) for r in results]
        return books


    def search_books(self, keywords):
        conn = self.db.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        words = keywords.split()[:3]
        conditions, params = [], []
        for word in words:
            conditions.append("(title LIKE %s OR author LIKE %s)")
            params.extend([f"%{word}%", f"%{word}%"])
        query = "SELECT * FROM books WHERE " + " OR ".join(conditions)
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def update_book(self, book_id, title, author, year):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET title=%s, author=%s, year=%s WHERE book_id=%s",
                       (title, author, year, book_id))
        conn.commit()
        conn.close()
        print("Book updated successfully!")

    def delete_book(self, book_id):
        conn = self.db.connect()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM borrowing WHERE book_id=%s AND return_date IS NULL", (book_id,))
        if cursor.fetchone():
            print("Cannot delete: Book is currently borrowed.")
            conn.close()
            return
        cursor.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
        conn.commit()
        conn.close()
        print("Book deleted successfully!")

