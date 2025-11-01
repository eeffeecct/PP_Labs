from services.store_service import StoreService
from models.product import Smartphone, Laptop


class StoreApp:
    def __init__(self):
        self.store = StoreService()
        self.load_data()

    def load_data(self):
        try:
            self.store.import_from_json("data/store_data.json")
            print("Data loaded from file")
        except:
            print("No file found, starting fresh")

    def save_data(self):
        try:
            self.store.export_to_json("data/store_data.json")
            self.store.export_to_xml("data/store_data.xml")
            print("Data saved successfully")
        except Exception as e:
            print(f"Save error: {e}")

    def show_menu(self):
        print("\n" + "="*40)
        print("ELECTRONICS STORE MANAGEMENT SYSTEM")
        print("="*40)
        print("1. Manage Products")
        print("2. Manage Customers")
        print("3. Manage Orders")
        print("4. Search Products")
        print("5. Save Data")
        print("6. Store Statistics")
        print("0. Exit")
        print("="*40)

    def products_menu(self):
        while True:
            print("\n" + "="*25)
            print("PRODUCTS MANAGEMENT")
            print("="*25)
            print("1. Add Smartphone")
            print("2. Add Laptop")
            print("3. Show All Products")
            print("4. Back")

            choice = input("Select option: ")

            if choice == "1":
                self.add_smartphone()
            elif choice == "2":
                self.add_laptop()
            elif choice == "3":
                self.show_products()
            elif choice == "4":
                break
            else:
                print("Invalid selection")

    def add_smartphone(self):
        try:
            print("\nADD SMARTPHONE")
            name = input("Name: ")
            price = float(input("Price: "))
            brand = input("Brand: ")
            storage = input("Storage (default 128GB): ") or "128GB"
            screen_size = float(input("Screen size (default 6.1): ") or 6.1)
            stock = int(input("Stock quantity: ") or 0)
            os = input("OS (optional): ") or None

            phone = Smartphone(
                product_id=0,  # ID will be assigned automatically
                name=name,
                price=price,
                brand=brand,
                storage=storage,
                screen_size=screen_size,
                stock=stock,
                os=os
            )

            self.store.create_product(phone.to_dict())
            print("Smartphone added successfully")

        except ValueError as e:
            print(f"Input error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def add_laptop(self):
        try:
            print("\nADD LAPTOP")
            name = input("Name: ")
            price = float(input("Price: "))
            brand = input("Brand: ")
            processor = input("Processor (default Intel i5): ") or "Intel i5"
            ram = input("RAM (default 16GB): ") or "16GB"
            stock = int(input("Stock quantity: ") or 0)
            storage_type = input("Storage type (optional): ") or None

            laptop = Laptop(
                product_id=0,
                name=name,
                price=price,
                brand=brand,
                processor=processor,
                ram=ram,
                stock=stock,
                storage_type=storage_type
            )

            self.store.create_product(laptop.to_dict())
            print("Laptop added successfully")

        except ValueError as e:
            print(f"Input error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def show_products(self):
        products = self.store.get_all_products()
        if not products:
            print("No products available")
            return

        print(f"\nALL PRODUCTS ({len(products)}):")
        for product in products:
            print(f"ID {product.product_id}: {product.name}")
            print(f"   Price: ${product.price} | Stock: {product.stock} | Brand: {product.brand}")
            if isinstance(product, Smartphone):
                print(f"   Storage: {product.storage} | Screen: {product.screen_size}\"")
            elif isinstance(product, Laptop):
                print(f"   Processor: {product.processor} | RAM: {product.ram}")

    def customers_menu(self):
        while True:
            print("\n" + "="*25)
            print("CUSTOMERS MANAGEMENT")
            print("="*25)
            print("1. Add Customer")
            print("2. Show All Customers")
            print("3. Back")

            choice = input("Select option: ")

            if choice == "1":
                self.add_customer()
            elif choice == "2":
                self.show_customers()
            elif choice == "3":
                break
            else:
                print("Invalid selection")

    def add_customer(self):
        try:
            print("\nADD CUSTOMER")
            name = input("Name: ")
            email = input("Email: ")
            phone = input("Phone (optional): ") or None
            address = input("Address (optional): ") or None

            customer = self.store.create_customer(name, email, phone=phone, address=address)
            print(f"Customer {customer.name} added. ID: {customer.customer_id}")

        except Exception as e:
            print(f"Error: {e}")

    def show_customers(self):
        customers = self.store.get_all_customers()
        if not customers:
            print("No customers available")
            return

        print(f"\nALL CUSTOMERS ({len(customers)}):")
        for customer in customers:
            print(f"ID {customer.customer_id}: {customer.name}")
            print(f"   Email: {customer.email}")
            if customer.phone:
                print(f"   Phone: {customer.phone}")

    def orders_menu(self):
        while True:
            print("\n" + "="*25)
            print("ORDERS MANAGEMENT")
            print("="*25)
            print("1. Create Order")
            print("2. Show All Orders")
            print("3. Back")

            choice = input("Select option: ")

            if choice == "1":
                self.create_order_interactive()
            elif choice == "2":
                self.show_orders()
            elif choice == "3":
                break
            else:
                print("Invalid selection")

    def create_order_interactive(self):
        try:
            print("\nCREATE ORDER")

            # Show available customers
            customers = self.store.get_all_customers()
            if not customers:
                print("No customers available for order")
                return

            print("Available customers:")
            for customer in customers:
                print(f"   ID {customer.customer_id}: {customer.name}")

            customer_id = int(input("\nCustomer ID: "))

            # Show available products
            products = self.store.get_all_products()
            if not products:
                print("No products available for order")
                return

            print("\nAvailable products:")
            for product in products:
                print(f"   ID {product.product_id}: {product.name} - ${product.price} (stock: {product.stock})")

            # Collect order items
            items = []
            while True:
                product_id = input("\nProduct ID (or 'done' to finish): ")
                if product_id.lower() == 'done':
                    break

                quantity = int(input("Quantity: "))
                items.append({"product_id": int(product_id), "quantity": quantity})

                add_more = input("Add more products? (yes/no): ")
                if add_more.lower() != 'yes':
                    break

            if not items:
                print("Order must contain products")
                return

            order = self.store.create_order(customer_id, items)
            print(f"Order created! ID: {order.order_id}")
            print(f"   Total amount: ${order.total_amount}")

        except Exception as e:
            print(f"Order creation error: {e}")

    def show_orders(self):
        orders = self.store.get_all_orders()
        if not orders:
            print("No orders available")
            return

        print(f"\nALL ORDERS ({len(orders)}):")
        for order in orders:
            print(f"ID {order.order_id}")
            print(f"   Customer: {order.customer.name}")
            print(f"   Total: ${order.total_amount}")
            print(f"   Date: {order.order_date.strftime('%d.%m.%Y %H:%M')}")
            print(f"   Items: {len(order.items)}")

    def search_products_menu(self):
        query = input("\nEnter search query: ")
        results = self.store.search_products(query)

        if not results:
            print("No products found")
            return

        print(f"\nSEARCH RESULTS ({len(results)}):")
        for product in results:
            print(f"ID {product.product_id}: {product.name} - ${product.price} | Brand: {product.brand}")

    def show_stats(self):
        stats = self.store.get_store_stats()
        print("\nSTORE STATISTICS:")
        print(f"   Products: {stats['total_products']}")
        print(f"   Customers: {stats['total_customers']}")
        print(f"   Orders: {stats['total_orders']}")
        print(f"   Inventory value: ${stats['total_inventory_value']}")
        print(f"   Low stock products: {stats['low_stock_products']}")

    def run(self):
        print("Starting Electronics Store Management System...")

        while True:
            self.show_menu()
            choice = input("Select option: ")

            if choice == "1":
                self.products_menu()
            elif choice == "2":
                self.customers_menu()
            elif choice == "3":
                self.orders_menu()
            elif choice == "4":
                self.search_products_menu()
            elif choice == "5":
                self.save_data()
            elif choice == "6":
                self.show_stats()
            elif choice == "0":
                self.save_data()
                print("Goodbye!")
                break
            else:
                print("Invalid selection")


def main():
    app = StoreApp()
    app.run()


if __name__ == "__main__":
    main()