from dataclasses import dataclass, field

from electronics_store.models import Product


@dataclass
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    @property
    def total_price(self) -> float:
        return self.product.price * self.quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product.product_id,
            "product_name": self.product.name,
            "quantity": self.quantity,
            "unit_price": self.product.price,
            "total_price": self.total_price
        }


@dataclass
class ShoppingCart:
    cart_id: str
    customer_id: int
    items: list = field(default_factory=list)

    @property
    def total_amount(self) -> float:
        return sum(item.total_price for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def add_item(self, product: Product, quantity: int = 1) -> None:
        for item in self.items:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity))

    def remove_item(self, product_id: int) -> None:
        self.items = [item for item in self.items if item.product.product_id != product_id]

    def clear(self) -> None:
        self.items.clear()

    def to_dict(self) -> dict:
        return {
            "cart_id": self.cart_id,
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items],
            "total_amount": self.total_amount,
            "item_count": self.item_count
        }
