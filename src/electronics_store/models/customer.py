from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Customer:
    customer_id: int
    name: str
    email: str
    phone: str = None
    address: str = None
    registration_date: datetime = field(default_factory=datetime.now, init=False)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Customer name cannot be empty")
        if "@" not in self.email:
            raise ValueError("Invalid email format")
        self.name = self.name.strip()

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "registration_date": self.registration_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            address=data.get("address")
        )
