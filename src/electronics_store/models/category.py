from dataclasses import dataclass, field

from electronics_store.models import Product


@dataclass
class Category:
    category_id: int
    name: str
    description: str = ""
    products: list = field(default_factory=list)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Category name can't be empty")
        self.name = self.name.strip()

    def add_product(self, product: Product) -> None:
        if product not in self.products:
            self.products.append(product)

    def remove_product(self, product: Product) -> bool:
        if product in self.products:
            self.products.remove(product)
            return True
        return False

    @property
    def product_count(self) -> int:
        return len(self.products)

    def to_dict(self) -> dict:
        return {
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "product_count": self.product_count,
            "products": [p.to_dict() for p in self.products]
        }