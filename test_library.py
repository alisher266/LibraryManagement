import unittest
import mysql.connector
from library import DatabaseConnection, BookManager, UserManager, BorrowingManager

class TestLibraryManagementSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize a fresh test database
        cls.db = DatabaseConnection(database="library_db_test")
        cls.db.initialize(reset=True)  # reset ensures clean tables
        cls.books = BookManager(cls.db)
        cls.users = UserManager(cls.db)
        cls.borrowing = BorrowingManager(cls.db)

    def test_add_and_view_book(self):
        self.books.add_book("Test Book", "Test Author", 2026)
        books_list = self.books.view_books()
        titles = [b.title for b in books_list]
        self.assertIn("Test Book", titles)

    def test_add_and_view_user(self):
        self.users.add_user("Test User", "testuser@example.com")
        users_list = self.users.view_users()
        emails = [u.email for u in users_list]
        self.assertIn("testuser@example.com", emails)

    def test_borrow_and_return_book(self):
        self.users.add_user("Borrower", "borrower@example.com")
        self.books.add_book("Borrowable Book", "Author", 2026)

        books_list = self.books.view_books()
        book_id = [b.book_id for b in books_list if b.title == "Borrowable Book"][0]

        self.borrowing.borrow_book("borrower@example.com", book_id)
        borrowings = self.borrowing.view_borrowings()
        self.assertTrue(any("Borrowable Book" in br for br in borrowings))

        self.borrowing.return_book("borrower@example.com")
        borrowings_after = self.borrowing.view_borrowings()
        self.assertTrue(any("Returned" in br for br in borrowings_after))

    def test_search_books(self):
        self.books.add_book("Python Testing", "QA Author", 2026)
        results = self.books.search_books("Python")
        self.assertTrue(any("Python Testing" in b["title"] for b in results))

    def test_update_book(self):
        self.books.add_book("Old Title", "Old Author", 2000)
        books_list = self.books.view_books()
        book_id = [b.book_id for b in books_list if b.title == "Old Title"][0]
        self.books.update_book(book_id, "New Title", "New Author", 2026)
        updated_books = self.books.view_books()
        titles = [b.title for b in updated_books]
        self.assertIn("New Title", titles)

    def test_delete_user(self):
        self.users.add_user("Delete Me", "deleteme@example.com")
        users_list = self.users.view_users()
        user_id = [u.user_id for u in users_list if u.email == "deleteme@example.com"][0]
        self.users.delete_user(user_id)
        updated_users = self.users.view_users()
        emails = [u.email for u in updated_users]
        self.assertNotIn("deleteme@example.com", emails)
    
    ##more test to check

    def test_borrow_unavailable_book(self):
        self.users.add_user("Unavailable Borrower", "unavail@example.com")
        self.books.add_book("Unavailable Book", "Author", 2026)
        book_id = [b.book_id for b in self.books.view_books() if b.title == "Unavailable Book"][0]
        # Borrow once
        self.borrowing.borrow_book("unavail@example.com", book_id)
        # Try borrowing again (should fail gracefully)
        self.borrowing.borrow_book("unavail@example.com", book_id)
        borrowings = self.borrowing.view_borrowings()
        count = sum("Unavailable Book" in br for br in borrowings)
        self.assertEqual(count, 1)  # only one borrowing record should exist

    def test_add_duplicate_user_email(self):
        self.users.add_user("Dup User", "dup@example.com")
        # Try adding same email again
        try:
            self.users.add_user("Dup User Again", "dup@example.com")
            duplicate_added = True
        except Exception:
            duplicate_added = False
        self.assertFalse(duplicate_added)  # should not allow duplicate email

    def test_delete_book(self):
        self.books.add_book("Delete Book", "Author", 2026)
        books_list = self.books.view_books()
        book_id = [b.book_id for b in books_list if b.title == "Delete Book"][0]
        self.books.delete_book(book_id)
        updated_books = self.books.view_books()
        titles = [b.title for b in updated_books]
        self.assertNotIn("Delete Book", titles)

    def test_search_nonexistent_book(self):
        results = self.books.search_books("NonexistentKeyword")
        self.assertEqual(len(results), 0)  # should return empty list

if __name__ == "__main__":
    unittest.main()
