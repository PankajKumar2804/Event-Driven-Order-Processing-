"""
Database models for order processing system
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class OrderModel:
    """Order database model"""
    def __init__(self, order_id: str, customer_id: str, items: list):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus.PENDING
        self.payment_status = PaymentStatus.PENDING
        self.total_amount = sum(item['price'] * item['quantity'] for item in items)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.shipped_at: Optional[datetime] = None
        self.delivered_at: Optional[datetime] = None
        self.notes = ""
    
    def update_status(self, status: OrderStatus):
        """Update order status"""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def update_payment(self, status: PaymentStatus):
        """Update payment status"""
        self.payment_status = status
        self.updated_at = datetime.utcnow()
    
    def add_note(self, note: str):
        """Add note to order"""
        self.notes += f"\n[{datetime.utcnow()}] {note}"
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'items': self.items,
            'status': self.status.value,
            'payment_status': self.payment_status.value,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }


class CustomerModel:
    """Customer database model"""
    def __init__(self, customer_id: str, name: str, email: str, phone: str = ""):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = datetime.utcnow()
        self.orders_count = 0
        self.total_spent = 0.0
        self.is_active = True
    
    def add_order(self, amount: float):
        """Update customer after order"""
        self.orders_count += 1
        self.total_spent += amount
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'orders_count': self.orders_count,
            'total_spent': self.total_spent,
            'is_active': self.is_active
        }


class InventoryModel:
    """Inventory/Product model"""
    def __init__(self, product_id: str, name: str, price: float, quantity: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.sku = ""
        self.created_at = datetime.utcnow()
        self.last_restocked = None
    
    def decrease_stock(self, amount: int) -> bool:
        """Decrease stock"""
        if self.quantity >= amount:
            self.quantity -= amount
            return True
        return False
    
    def increase_stock(self, amount: int):
        """Increase stock"""
        self.quantity += amount
        self.last_restocked = datetime.utcnow()
    
    def is_in_stock(self, amount: int = 1) -> bool:
        """Check if product is in stock"""
        return self.quantity >= amount
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'sku': self.sku,
            'in_stock': self.is_in_stock()
        }


if __name__ == "__main__":
    # Example usage
    order = OrderModel("ORD-001", "CUST-001", [
        {'price': 99.99, 'quantity': 1}
    ])
    print(order.to_dict())
