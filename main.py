users = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"}
}

products = []
sales = []

def login():
    print("=== Business Inventory and Sales Management System ===")
    username = input("Username: ")
    password = input("Password: ")
    if username in users and users[username]["password"] == password:
        role = users[username]["role"]
        print(f"\n✅ Login successful! Welcome, {username.capitalize()} ({role.upper()})\n")
        main_menu(role)
    else:
        print("\n❌ Invalid credentials.\n")
        login()

def main_menu(role):
    while True:
        print("========= MAIN MENU =========")
        if role == "admin":
            print("1. Manage Products")
            print("2. Record Sale")
            print("3. View Reports")
            print("4. Manage Users")
            print("5. Logout")
        else:
            print("1. Record Sale")
            print("2. Logout")
        choice = input("Select option: ")
        if role == "admin":
            if choice == "1": manage_products()
            elif choice == "2": record_sale()
            elif choice == "3": view_reports()
            elif choice == "4": manage_users()
            elif choice == "5": print("Logged out.\n"); break
            else: print("❌ Invalid choice.\n")
        else:
            if choice == "1": record_sale()
            elif choice == "2": print("Logged out.\n"); break
            else: print("❌ Invalid choice.\n")

def manage_products():
    while True:
        print("\n=== Manage Products ===")
        print("1. View Products")
        print("2. Add Product")
        print("3. Remove Product")
        print("4. Back")
        choice = input("Choose: ")
        if choice == "1":
            if not products: print("No products.\n")
            else:
                for i, p in enumerate(products, 1):
                    print(f"{i}. {p}")
        elif choice == "2":
            name = input("Enter product name: ")
            products.append(name)
            print(f"Added: {name}")
        elif choice == "3":
            if not products: print("No products to remove.\n")
            else:
                for i, p in enumerate(products, 1): print(f"{i}. {p}")
                try:
                    idx = int(input("Enter product number: "))
                    removed = products.pop(idx - 1)
                    print(f"Removed: {removed}")
                except: print("Invalid input.")
        elif choice == "4": break
        else: print("❌ Invalid choice.\n")

def record_sale():
    if not products:
        print("No products available.\n")
        return
    print("\n=== Record Sale ===")
    for i, p in enumerate(products, 1):
        print(f"{i}. {p}")
    try:
        idx = int(input("Select product: "))
        qty = int(input("Enter quantity: "))
        sales.append({"product": products[idx - 1], "quantity": qty})
        print(f"Sale recorded: {qty} x {products[idx - 1]}\n")
    except: print("Invalid input.\n")

def view_reports():
    print("\n=== Sales Report ===")
    if not sales:
        print("No sales yet.\n")
    else:
        for i, s in enumerate(sales, 1):
            print(f"{i}. {s['product']} - {s['quantity']} pcs")
    print()

def manage_users():
    print("\n=== Manage Users ===")
    for name, data in users.items():
        print(f"{name} ({data['role']})")
    print()

if __name__ == "__main__":
    login()
