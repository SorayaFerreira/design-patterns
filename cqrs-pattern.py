# Let’s build a CQRS (Command Query Responsibility Segregation) system:

# 🛍️ CQRS Pattern - Separate read and write models
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import uuid

# 📝 Commands (write operations)
@dataclass
class Command:
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class CreateOrderCommand(Command):
    customer_id: str
    items: List[Dict[str, Any]]
    emoji: str = "🛒"

@dataclass
class UpdateOrderStatusCommand(Command):
    order_id: str
    status: str
    emoji: str = "📦"

@dataclass
class CancelOrderCommand(Command):
    order_id: str
    emoji: str = "❌"

# 🔍 Queries (read operations)
@dataclass
class Query:
    pass

@dataclass
class GetOrderByIdQuery(Query):
    order_id: str

@dataclass
class GetOrdersByCustomerQuery(Query):
    customer_id: str

# 🎯 Command handlers
class CommandHandler:
    def __init__(self):
        self.events = []  # Event store
        print("⚡ Command handler ready!")
    
    def handle(self, command: Command):
        if isinstance(command, CreateOrderCommand):
            order_id = str(uuid.uuid4())
            event = {
                'type': 'OrderCreated',
                'order_id': order_id,
                'customer_id': command.customer_id,
                'items': command.items,
                'timestamp': command.timestamp,
                'emoji': command.emoji
            }
            self.events.append(event)
            print(f"{command.emoji} Order {order_id} created!")
            return order_id
        
        elif isinstance(command, UpdateOrderStatusCommand):
            event = {
                'type': 'OrderStatusUpdated',
                'order_id': command.order_id,
                'status': command.status,
                'timestamp': command.timestamp,
                'emoji': command.emoji
            }
            self.events.append(event)
            print(f"{command.emoji} Order {command.order_id} status: {command.status}")

        elif isinstance(command, CancelOrderCommand):
            order_id = command.order_id
            event = {
                'type': 'OrderCancelled',
                'order_id': order_id,
                'timestamp': command.timestamp,
                'emoji': command.emoji
            }
            self.events.append(event)
            print(f"{command.emoji} Order {order_id} cancelled!")
            return order_id

# 📊 Query handlers with read model
class QueryHandler:
    def __init__(self, events):
        self.events = events
        self._orders = {}  # Read model
        self._rebuild_read_model()
        print("🔍 Query handler ready!")
    
    def _rebuild_read_model(self):
        # Rebuild read model from events
        for event in self.events:
            if event['type'] == 'OrderCreated':
                self._orders[event['order_id']] = {
                    'id': event['order_id'],
                    'customer_id': event['customer_id'],
                    'items': event['items'],
                    'status': 'created',
                    'created_at': event['timestamp']
                }
            elif event['type'] == 'OrderStatusUpdated':
                if event['order_id'] in self._orders:
                    self._orders[event['order_id']]['status'] = event['status']
    
    def handle(self, query: Query):
        if isinstance(query, GetOrderByIdQuery):
            return self._orders.get(query.order_id)
        
        elif isinstance(query, GetOrdersByCustomerQuery):
            return [
                order for order in self._orders.values()
                if order['customer_id'] == query.customer_id
            ]

# 🎮 Let's use CQRS!
command_handler = CommandHandler()
query_handler = QueryHandler(command_handler.events)

# Create an order
create_cmd = CreateOrderCommand(
    customer_id="cust-123",
    items=[
        {"name": "Python Book", "price": 29.99, "emoji": "📘"},
        {"name": "Coffee", "price": 4.99, "emoji": "☕"}
    ]
)
order_id = command_handler.handle(create_cmd)

# Update order status
update_cmd = UpdateOrderStatusCommand(order_id=order_id, status="shipped")
command_handler.handle(update_cmd)

# Cancel the order
cancel_cmd = CancelOrderCommand(order_id=order_id)
command_handler.handle(cancel_cmd)

# Query the order
query_handler = QueryHandler(command_handler.events)  # Rebuild read model
order = query_handler.handle(GetOrderByIdQuery(order_id=order_id))
print(f"📋 Order details: {order}")

# 🎯 Try it yourself: Add a cancel order command and implement event replay functionality!