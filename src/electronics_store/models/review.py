from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Review:
    review_id: int
    product_id: int
    customer_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime = datetime.now()

    def __post_init__(self):
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "product_id": self.product_id,
            "customer_id": self.customer_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat()
        }