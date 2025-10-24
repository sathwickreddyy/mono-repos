"""Order model for order processing system."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    """Order model representing a customer order."""
    
    order_id: str = Field(..., description="Unique order identifier")
    customer_id: str = Field(..., description="Customer identifier")
    product_id: str = Field(..., description="Product identifier")
    quantity: int = Field(..., gt=0, description="Order quantity")
    price: float = Field(..., gt=0, description="Product price")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Order creation timestamp")
    
    @field_validator('order_id', 'customer_id', 'product_id')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @property
    def total_amount(self) -> float:
        """Calculate total order amount."""
        return self.quantity * self.price
    
    def to_dict(self) -> dict:
        """Convert order to dictionary for Kafka serialization."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_amount": self.total_amount
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Create Order instance from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "order_id": "ORD-001",
                "customer_id": "CUST-123",
                "product_id": "PROD-456",
                "quantity": 2,
                "price": 29.99,
                "status": "pending"
            }
        }
