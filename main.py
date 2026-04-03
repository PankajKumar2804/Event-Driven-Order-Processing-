"""
Order Processing API with event-driven architecture
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Order Processing API", version="1.0.0")

# Models
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None

# In-memory store (replace with database)
orders_db = {}
order_counter = 0

@app.get("/")
async def root():
    return {"message": "Order Processing API", "version": "1.0.0"}

@app.post("/orders")
async def create_order(order: Order):
    """Create a new order"""
    global order_counter
    order_counter += 1
    order_id = f"ORD-{order_counter}"
    
    order.created_at = datetime.now()
    order.updated_at = datetime.now()
    
    orders_db[order_id] = order
    
    # Emit event
    await emit_order_event(order_id, "order.created", order)
    
    return {"order_id": order_id, "order": order}

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order by ID"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]

@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: OrderStatus):
    """Update order status"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    old_status = order.status
    order.status = status
    order.updated_at = datetime.now()
    
    # Emit event
    await emit_order_event(order_id, f"order.{status}", order)
    
    return {"order_id": order_id, "old_status": old_status, "new_status": status}

@app.get("/orders")
async def list_orders(status: Optional[OrderStatus] = None):
    """List all orders, optionally filtered by status"""
    if status:
        return [o for o in orders_db.values() if o.status == status]
    return list(orders_db.values())

async def emit_order_event(order_id: str, event_type: str, data):
    """Emit order event (integrate with message queue like RabbitMQ/Kafka)"""
    event = {
        "order_id": order_id,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data.dict()
    }
    # TODO: Publish to message queue
    print(f"Event emitted: {event}")
    return event

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
