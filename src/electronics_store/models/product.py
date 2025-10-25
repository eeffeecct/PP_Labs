from dataclasses import dataclass, field
from typing import Dict, List, Optional, ClassVar
from datetime import datetime
from abc import ABC


@dataclass
class Product(ABC):
    """Abstract class for all products"""
    product_id: int
    name: str
    brand: str
    price: float
    stock: int = 0
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now, init=False)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Product name can't be empty")
        if self.price < 0:
            raise ValueError("Price can't be negative")
        if self.stock < 0:
            raise ValueError("Stock can't be negative")

        self.name = self.name.strip()


    def increase_stock(self, quantity: int) -> None:
        """Increase the quantity of goods in stock"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock += quantity

    def decrease_stock(self, quantity: int) -> None:
        """Decrease the quantity of goods in stock"""
        if quantity > self.stock:
            raise ValueError("Inadequate stock")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock -= quantity

    def to_dict(self) -> Dict:  # Serialization
        """Convert an object to a dictionary"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "type": self.__class__.__name__
        }


@dataclass
class ElectronicProduct(Product):
    warranty_months: int = 12
    specifications: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        if not self.brand.strip():
            raise ValueError("Brand can't be empty")
        if self.warranty_months < 0:
            raise ValueError("Warranty cannot be negative")

    def add_specification(self, key: str, value: str) -> None:
        self.specifications[key] = value

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "brand": self.brand,
            "warranty_months": self.warranty_months,
            "specifications": self.specifications
        })
        return data


@dataclass
class Smartphone(ElectronicProduct):
    storage: str = "128GB"
    screen_size: float = 6.1
    os: Optional[str] = None

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "storage": self.storage,
            "screen_size": self.screen_size,
            "os": self.os
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Smartphone': # Fabric method
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            price=data["price"],
            brand=data["brand"],
            storage=data.get("storage", "128GB"),
            screen_size=data.get("screen_size", 6.1),
            stock=data.get("stock", 0),
            description=data.get("description", ""),
            warranty_months=data.get("warranty_months", 12),
            os=data.get("os"),
            specifications=data.get("specifications", {})
        )


@dataclass
class Laptop(ElectronicProduct):
    processor: str = "Intel i5"
    ram: str = "16GB"
    storage_type: Optional[str] = None

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "processor": self.processor,
            "ram": self.ram,
            "storage_type": self.storage_type
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Laptop':
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            price=data["price"],
            brand=data["brand"],
            processor=data.get("processor", "Intel i5"),
            ram=data.get("ram", "16GB"),
            stock=data.get("stock", 0),
            description=data.get("description", ""),
            warranty_months=data.get("warranty_months", 12),
            storage_type=data.get("storage_type"),
            specifications=data.get("specifications", {})
        )