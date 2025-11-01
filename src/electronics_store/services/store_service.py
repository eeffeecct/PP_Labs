from electronics_store.models.product import Smartphone, Laptop
from electronics_store.models.customer import Customer
from electronics_store.models.order import Order, OrderItem
from electronics_store.exceptions.custom_exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    CustomerNotFoundError,
    OrderProcessingError,
)
from electronics_store.data_handlers.json_handler import JSONHandler
from electronics_store.data_handlers.xml_handler import XMLHandler

from dataclasses import dataclass, field
from typing import List
import uuid
from datetime import datetime


@dataclass
class StoreService:
    products: dict = field(default_factory=dict)
    customers: dict = field(default_factory=dict)
    orders: dict = field(default_factory=dict)
    next_product_id: int = 1
    next_customer_id: int = 1

    def create_product(self, product_data: dict):
        try:
            product_type = product_data.get("type", "Smartphone")
            product_class = Smartphone if product_type == "Smartphone" else Laptop
            product = product_class.from_dict(product_data)

            if product.product_id is None:
                product.product_id = self.next_product_id
                self.next_product_id += 1

            self.products[product.product_id] = product
            return product
        except Exception as e:
            raise OrderProcessingError(f"Failed to create product: {e}")

    def get_product(self, product_id: int):
        if product_id not in self.products:
            raise ProductNotFoundError(product_id)
        return self.products[product_id]

    def get_all_products(self) -> List[Smartphone | Laptop]:
        return list(self.products.values())

    def get_all_customers(self) -> List[Customer]:
        return list(self.customers.values())

    def get_all_orders(self) -> List[Order]:
        return list(self.orders.values())

    def create_customer(self, name: str, email: str, **kwargs):
        customer_id = self.next_customer_id
        self.next_customer_id += 1
        customer = Customer(customer_id=customer_id, name=name, email=email, **kwargs)
        self.customers[customer_id] = customer
        return customer

    def get_customer(self, customer_id: int):
        if customer_id not in self.customers:
            raise CustomerNotFoundError(customer_id)
        return self.customers[customer_id]

    def create_order(self, customer_id: int, items: list):
        customer = self.get_customer(customer_id)
        if not items:
            raise OrderProcessingError("Order must contain items")

        order_items = []
        for item in items:
            product = self.get_product(item['product_id'])
            if product.stock < item['quantity']:
                raise InsufficientStockError(product.name, item['quantity'], product.stock)

            order_items.append(OrderItem(product, item['quantity']))
            product.decrease_stock(item['quantity'])

        # Order ID Generation
        order = Order(order_id=str(uuid.uuid4()), customer=customer, items=order_items)
        self.orders[order.order_id] = order
        return order

    def search_products(self, query: str):
        query = query.lower()
        return [p for p in self.products.values() if query in p.name.lower()]

    def export_to_json(self, file_path: str):
        data = {
            "products": [p.to_dict() for p in self.products.values()],
            "customers": [c.to_dict() for c in self.customers.values()],
            "orders": [o.to_dict() for o in self.orders.values()],
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_products": len(self.products),
                "total_customers": len(self.customers),
                "next_product_id": self.next_product_id,
                "next_customer_id": self.next_customer_id
            }
        }
        JSONHandler.write_file(data, file_path)

    def import_from_json(self, file_path: str):
        data = JSONHandler.read_file(file_path)

        for product_data in data.get("products", []):
            self.create_product(product_data)

        for customer_data in data.get("customers", []):
            self.create_customer(**{k: v for k, v in customer_data.items() if k != 'customer_id'})

        metadata = data.get("metadata", {})
        self.next_product_id = metadata.get("next_product_id", self.next_product_id)
        self.next_customer_id = metadata.get("next_customer_id", self.next_customer_id)

    def export_to_xml(self, file_path: str):
        data = {
            "products": [p.to_dict() for p in self.products.values()],
            "customers": [c.to_dict() for c in self.customers.values()],
            "metadata": {
                "total_products": len(self.products),
                "total_customers": len(self.customers),
                "export_date": datetime.now().isoformat()
            }
        }
        root = XMLHandler.dict_to_xml_element("store", data)
        XMLHandler.write_file(root, file_path)

    def import_from_xml(self, file_path: str):
        data = XMLHandler.xml_element_to_dict(XMLHandler.read_file(file_path))

        products_data = data.get("products", [])
        if isinstance(products_data, dict):
            products_data = [products_data]
        for product_data in products_data:
            self.create_product(product_data)

        customers_data = data.get("customers", [])
        if isinstance(customers_data, dict):
            customers_data = [customers_data]
        for customer_data in customers_data:
            self.create_customer(**{k: v for k, v in customer_data.items() if k != 'customer_id'})

    def get_store_stats(self) -> dict:
        total_products = len(self.products)
        total_customers = len(self.customers)
        total_orders = len(self.orders)
        total_inventory = sum(product.stock for product in self.products.values())
        total_value = sum(product.price * product.stock for product in self.products.values())

        return {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_inventory_value": round(total_value, 2),
            "total_inventory_units": total_inventory,
            "low_stock_products": len([p for p in self.products.values() if p.stock <= 5])
        }