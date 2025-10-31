from services.store_service import StoreService
from models.product import Smartphone, Laptop


def main():
    store = StoreService()
    
    try:
        phone = Smartphone(
            product_id=1,
            name="iPhone 15",
            price=999,
            brand="Apple",
            storage="128GB",
            stock=10
        )
        
        laptop = Laptop(
            product_id=2, 
            name="MacBook Pro",
            price=2000,
            brand="Apple", 
            processor="M2",
            ram="16GB",
            stock=5
        )
        
        store.products[1] = phone
        store.products[2] = laptop
        
        customer = store.create_customer(
            name="Tim Ter",
            email="timter@gmail.com",
            phone="+71234567890"
        )
        
        order = store.create_order(
            customer_id=1,
            items=[{"product_id": 1, "quantity": 2}]
        )
        
        print("Store setup completed!")
        print(f"Products: {len(store.products)}")
        print(f"Customers: {len(store.customers)}")
        print(f"Orders: {len(store.orders)}")
        
        store.export_to_json("data/data.json")
        store.export_to_xml("data/jsonXML.xml")

        print("Data exported to JSON!")
        print("Data exported to XML!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()