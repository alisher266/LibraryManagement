import mysql.connector
import sys
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, host="localhost", port=3306, user="root", password="1234", database="library_db"):
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
    def initialize(self):
        try:
            # Step 1: Create database if missing (use config value)
            temp_conn = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"]
            )
            temp_conn.autocommit = True
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            temp_cursor.close()
            temp_conn.close()

            # Step 2: Connect to the actual database
            conn = self.connect()
            if not conn:
                return
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

            conn.commit()
            cursor.close()
            conn.close()
            print("Database and tables initialized successfully!")

        except Error as e:
            print(f"Initialization error: {e}")
            sys.exit(1)
