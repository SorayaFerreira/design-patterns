# 🚀 Saga pattern for distributed transactions
from enum import Enum
from typing import List, Callable, Any, Optional
import uuid

class SagaStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"

class SagaStep:
    def __init__(self, name: str, action: Callable, compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.status = SagaStatus.PENDING
        self.result = None
        self.error = None
        self.emoji = "📝"
    
    def execute(self) -> bool:
        try:
            print(f"▶️ Executing: {self.name}")
            self.status = SagaStatus.RUNNING
            self.result = self.action()
            self.status = SagaStatus.COMPLETED
            print(f"✅ Completed: {self.name}")
            return True
        except Exception as e:
            self.status = SagaStatus.FAILED
            self.error = str(e)
            print(f"❌ Failed: {self.name} - {e}")
            return False
    
    def compensate(self) -> bool:
        if self.status != SagaStatus.COMPLETED:
            return True  # Nothing to compensate
        
        try:
            print(f"↩️ Compensating: {self.name}")
            self.status = SagaStatus.COMPENSATING
            self.compensation(self.result)
            print(f"✅ Compensated: {self.name}")
            return True
        except Exception as e:
            print(f"⚠️ Compensation failed: {self.name} - {e}")
            return False

class Saga:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING
        print(f"📋 Saga '{name}' created with ID: {self.id}")
    
    def add_step(self, step: SagaStep):
        self.steps.append(step)
        print(f"➕ Added step: {step.name}")
    
    def execute(self):
        print(f"\n🚀 Starting saga: {self.name}")
        self.status = SagaStatus.RUNNING
        
        completed_steps = []
        
        for step in self.steps:
            if step.execute():
                completed_steps.append(step)
            else:
                # Step failed, compensate completed steps
                print(f"\n⚠️ Saga failed at step: {step.name}")
                self.status = SagaStatus.COMPENSATING
                
                # Compensate in reverse order
                for completed_step in reversed(completed_steps):
                    completed_step.compensate()
                
                self.status = SagaStatus.FAILED
                print(f"❌ Saga '{self.name}' failed and compensated")
                return False
        
        self.status = SagaStatus.COMPLETED
        print(f"\n🎉 Saga '{self.name}' completed successfully!")
        return True

# 🛒 Example: Order processing saga
class OrderService:
    def __init__(self):
        self.orders = {}
    
    def create_order(self, order_id: str, items: List[str]) -> str:
        self.orders[order_id] = {"id": order_id, "items": items, "status": "created"}
        print(f"  📦 Order {order_id} created")
        return order_id
    
    def cancel_order(self, order_id: str):
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            print(f"  🗑️ Order {order_id} cancelled")

class PaymentService:
    def __init__(self):
        self.payments = {}
        self.balance = 1000  # Starting balance
    
    def process_payment(self, payment_id: str, amount: float) -> str:
        if amount > self.balance:
            raise Exception("Insufficient funds! 💸")
        
        self.balance -= amount
        self.payments[payment_id] = {"id": payment_id, "amount": amount, "status": "processed"}
        print(f"  💳 Payment {payment_id} processed: ${amount}")
        return payment_id
    
    def refund_payment(self, payment_id: str):
        if payment_id in self.payments:
            amount = self.payments[payment_id]["amount"]
            self.balance += amount
            self.payments[payment_id]["status"] = "refunded"
            print(f"  💰 Payment {payment_id} refunded: ${amount}")

class InventoryService:
    def __init__(self):
        self.inventory = {"item1": 10, "item2": 5, "item3": 0}
    
    def reserve_items(self, reservation_id: str, items: List[str]) -> str:
        for item in items:
            if self.inventory.get(item, 0) <= 0:
                raise Exception(f"Item {item} out of stock! 📦")
            
            self.inventory[item] -= 1
        
        print(f"  📋 Items reserved: {items}")
        return reservation_id
    
    def release_items(self, reservation_id: str):
        # Simplified: just add items back
        print(f"  📤 Items released for reservation {reservation_id}")

# 🎮 Create and execute saga
order_service = OrderService()
payment_service = PaymentService()
inventory_service = InventoryService()

# Create order processing saga
saga = Saga("Process Online Order")

# Add saga steps
saga.add_step(SagaStep(
    "Create Order",
    lambda: order_service.create_order("order-123", ["item1", "item2"]),
    lambda order_id: order_service.cancel_order(order_id)
))

saga.add_step(SagaStep(
    "Reserve Inventory",
    lambda: inventory_service.reserve_items("reservation-123", ["item1", "item2"]),
    lambda reservation_id: inventory_service.release_items(reservation_id)
))

saga.add_step(SagaStep(
    "Process Payment",
    lambda: payment_service.process_payment("payment-123", 99.99),
    lambda payment_id: payment_service.refund_payment(payment_id)
))

# Execute the saga
saga.execute()

# Try a failing saga
print("\n" + "="*50 + "\n")

failing_saga = Saga("Process Large Order")

failing_saga.add_step(SagaStep(
    "Create Large Order",
    lambda: order_service.create_order("order-456", ["item3"]),  # Out of stock!
    lambda order_id: order_service.cancel_order(order_id)
))

failing_saga.add_step(SagaStep(
    "Reserve Out-of-Stock Items",
    lambda: inventory_service.reserve_items("reservation-456", ["item3"]),  # Will fail!
    lambda reservation_id: inventory_service.release_items(reservation_id)
))

failing_saga.add_step(SagaStep(
    "Process Large Payment",
    lambda: payment_service.process_payment("payment-456", 5000),  # Too expensive!
    lambda payment_id: payment_service.refund_payment(payment_id)
))

failing_saga.execute()