import mysql.connector
import sys
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, host="localhost", port=3306, user="root", password="1234", database="library_db"):
        self.database_name = database
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }

    def connect(self):
        """Connect to the database (assumes it already exists)."""
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Database connection error: {e}")
            return None

    def initialize(self, reset=False):
        """Create database, tables, and optionally reseed sample data."""
        try:
            # Step 1: Create database if missing
            temp_conn = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"]
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
            temp_conn.close()

            # Step 2: Connect to the actual database
            conn = self.connect()
            if not conn: return
            cursor = conn.cursor()

            # Step 3: Create tables if missing
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INT,
                available BOOLEAN DEFAULT TRUE
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowing (
                borrow_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                borrow_date DATE NOT NULL,
                return_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (book_id) REFERENCES books(book_id)
            )
            """)

            # Step 4: Truncating tables
            if reset:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("TRUNCATE TABLE borrowing")
                cursor.execute("TRUNCATE TABLE users")
                cursor.execute("TRUNCATE TABLE books")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                print("Tables truncated before reseeding.")

            # Step 5: Insertinto values into tables
            cursor.execute("SELECT COUNT(*) FROM books")
            if cursor.fetchone()[0] == 0:
                books = [
                    ("The Great Gatsby", "F. Scott Fitzgerald", 1925, True),
                    ("1984", "George Orwell", 1949, True),
                    ("To Kill a Mockingbird", "Harper Lee", 1960, True),
                    ("Pride and Prejudice", "Jane Austen", 1813, True),
                    ("Moby-Dick", "Herman Melville", 1851, True),
                    ("The Catcher in the Rye", "J.D. Salinger", 1951, True),
                    ("Brave New World", "Aldous Huxley", 1932, True),
                    ("The Hobbit", "J.R.R. Tolkien", 1937, True),
                    ("Crime and Punishment", "Fyodor Dostoevsky", 1866, True),
                    ("Beloved", "Toni Morrison", 1987, True)
                ]

                cursor.executemany(
                    "INSERT INTO books (title, author, year, available) VALUES (%s, %s, %s, %s)",
                    books
                )

            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                users = [
                    ("Alice Johnson", "alice@example.com"),
                    ("Bob Smith", "bob@example.com"),
                    ("Charlie Brown", "charlie@example.com"),
                    ("Diana Prince", "diana@example.com"),
                    ("Ethan Hunt", "ethan@example.com"),
                    ("Fiona Gallagher", "fiona@example.com")
                ]

                cursor.executemany(
                    "INSERT INTO users (name, email) VALUES (%s, %s)",
                    users
                )

            conn.commit()
            conn.close()
            print("Database, tables, and sample data initialized successfully!")

        except Error as e:
            print(f"Initialization error: {e}")
            sys.exit(1)
