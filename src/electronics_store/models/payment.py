from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Payment:
    payment_id: str
    order_id: str
    amount: float
    payment_method: str
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = datetime.now()
    processed_at: datetime = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")

    def complete_payment(self) -> None:
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.now()

    def fail_payment(self) -> None:
        self.status = PaymentStatus.FAILED
        self.processed_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }