from datetime import datetime
from lib.db import session, init_db
from lib.models import User, Category, Transaction
from sqlalchemy import func

# --- Helper Functions ---
def get_date_input():
    while True:
        date_str = input("Enter date (YYYY-MM-DD): ")
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")

# --- Core Features ---

def create_user():
    print("\n--- Create New User ---")
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    if session.query(User).filter_by(email=email).first():
        print("Error: Email already exists!")
        return
    
    new_user = User(name=name, email=email)
    session.add(new_user)
    session.commit()
    print(f"User {name} created successfully!")

def manage_categories():
    print("\n--- Manage Categories ---")
    name = input("Enter Category Name (e.g., Food, Rent, Salary): ")
    desc = input("Enter Description (optional): ")
    
    if session.query(Category).filter_by(name=name).first():
        print("Category already exists.")
        return

    new_cat = Category(name=name, description=desc)
    session.add(new_cat)
    session.commit()
    print(f"Category '{name}' added.")

def add_transaction():
    print("\n--- Add Transaction ---")
    # Select User
    users = session.query(User).all()
    if not users: 
        print("No users found. Create a user first.")
        return
    
    for u in users: print(f"{u.id}. {u.name}")
    user_id = int(input("Select User ID: "))

    # Select Category
    cats = session.query(Category).all()
    if not cats:
        print("No categories found. Create one first.")
        return
    
    for c in cats: print(f"{c.id}. {c.name}")
    cat_id = int(input("Select Category ID: "))

    amount = float(input("Enter Amount (positive for income, negative for expense): "))
    desc = input("Description: ")
    date = get_date_input()

    new_trans = Transaction(amount=amount, date=date, description=desc, user_id=user_id, category_id=cat_id)
    session.add(new_trans)
    session.commit()
    print("Transaction recorded!")

def view_summary():
    print("\n--- Spending Summary & Analytics ---")
    users = session.query(User).all()
    for u in users: print(f"{u.id}. {u.name}")
    user_id = input("Select User ID to view (or press Enter for all): ")

    query = session.query(
        Category.name, 
        func.sum(Transaction.amount)
    ).join(Transaction).group_by(Category.name)

    if user_id:
        query = query.filter(Transaction.user_id == int(user_id))
    
    results = query.all()
    
    print(f"\n{'Category':<20} | {'Total':<10}")
    print("-" * 35)
    for cat_name, total in results:
        print(f"{cat_name:<20} | ${total:.2f}")

def list_transactions():
    print("\n--- List Transactions ---")
    keyword = input("Search keyword (optional): ")
    
    query = session.query(Transaction)
    if keyword:
        query = query.filter(Transaction.description.ilike(f"%{keyword}%"))
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    print(f"\n{'Date':<12} | {'User':<10} | {'Category':<10} | {'Amount':<10} | {'Desc'}")
    print("-" * 60)
    for t in transactions:
        print(f"{t.date} | {t.user.name:<10} | {t.category.name:<10} | ${t.amount:<9} | {t.description}")

# --- Main Menu ---
def main_menu():
    init_db() # Ensure DB exists
    while True:
        print("\n=== PennyPilote CLI ===")
        print("1. Create User")
        print("2. Manage Categories")
        print("3. Add Transaction")
        print("4. View Summary Reports")
        print("5. List/Search Transactions")
        print("6. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1': create_user()
        elif choice == '2': manage_categories()
        elif choice == '3': add_transaction()
        elif choice == '4': view_summary()
        elif choice == '5': list_transactions()
        elif choice == '6': 
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()