from library import DatabaseConnection, BookManager, UserManager, BorrowingManager, validate_int

def get_db_info():
    print("\n--- Database Configuration ---")
    host = input("Enter host (default: localhost): ") or "localhost"
    port = input("Enter port (default: 3306): ") or "3306"
    user = input("Enter user (default: root): ") or "root"
    password = input("Enter password (default: 1234): ") or "1234"
    database = input("Enter database name (default: library_db): ") or "library_db"
    return DatabaseConnection(host=host, port=int(port), user=user, password=password, database=database)

def menu():
    db = get_db_info()
    db.initialize()   
    books = BookManager(db)
    users = UserManager(db)
    borrowing = BorrowingManager(db)

    while True:
        print("\n--- Library Management System ---")
        print("1. Add Book")
        print("2. View Books")
        print("3. Search Books")
        print("4. Add User")
        print("5. View Users")
        print("6. Borrow Book")
        print("7. Return Book")
        print("8. Update Book")
        print("9. Delete Book")
        print("10. Update User")
        print("11. Delete User")
        print("12. Borrowing records")
        print("13. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            title = input("Enter title: ")
            author = input("Enter author: ")
            year = input("Enter year: ")
            books.add_book(title, author, year)
        elif choice == "2":
            print("="*60)
            print(" LIBRARY BOOKS ".center(60))
            print("="*60)
            books_list = books.view_books()
            for b in books_list:
                print(b)
        elif choice == "3":
            keyword = input("Enter keyword: ")
            for r in books.search_books(keyword):
                print(r)
        elif choice == "4":
            name = input("Enter name: ")
            email = input("Enter email: ")
            users.add_user(name, email)
        elif choice == "5":
            users_list = users.view_users()
            for u in users_list:
                print(u)
        elif choice == "6":
            print("="*60)
            print(" LIBRARY BOOKS ".center(60))
            print("="*60)
            books_list = books.view_books()
            for b in books_list:
                print(b)
            print("="*60) 
            email = input("Enter user email: ")
            book_id = input("Enter book ID: ")
            borrowing.borrow_book(email, book_id)

        elif choice == "7":
            email = input("Enter user email: ")
            borrowing.return_book(email)
        elif choice == "8":
            book_id = validate_int(input("Book ID: "), "Book ID")
            title = input("New title: ")
            author = input("New author: ")
            year = input("New year: ")
            books.update_book(book_id, title, author, year)
        elif choice == "9":
            book_id = validate_int(input("Enter Book ID to delete: "), "Book ID")
            if book_id:
                books.delete_book(book_id)
        elif choice == "10":
            user_id = validate_int(input("Enter User ID to update: "), "User ID")
            if user_id:
                name = input("Enter new name: ").strip()
                email = input("Enter new email: ").strip()
                if not name or not email:
                    print("Name and email cannot be empty!")
                else:
                    users.update_user(user_id, name, email)
        elif choice == "11":
            user_id = validate_int(input("Enter User ID to delete: "), "User ID")
            if user_id:
                users.delete_user(user_id)
        elif choice == "12":
            borrowings_list = borrowing.view_borrowings()
            if not borrowings_list:
                print("No borrowings found.")
            else:
                for br in borrowings_list:
                    print(br)
        elif choice == "13":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    menu()

