from dataclasses import dataclass, field
from datetime import datetime
from .customer import Customer
from .product import Product


@dataclass
class OrderItem:
    product: Product
    quantity: int
    unit_price: float = field(init=False)

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.unit_price = self.product.price

    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product.product_id,
            "product_name": self.product.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price
        }


@dataclass
class Order:
    order_id: str
    customer: Customer
    items: list = field(default_factory=list)
    order_date: datetime = field(default_factory=datetime.now, init=False)
    status: str = "pending"

    def __post_init__(self):
        if not self.items:
            raise ValueError("Order must have at least one item")

    @property
    def total_amount(self) -> float:
        return sum(item.total_price for item in self.items)

    def add_item(self, product: Product, quantity: int) -> None:
        self.items.append(OrderItem(product, quantity))

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer.customer_id,
            "customer_name": self.customer.name,
            "items": [item.to_dict() for item in self.items],
            "total_amount": self.total_amount,
            "order_date": self.order_date.isoformat(),
            "status": self.status
        }
