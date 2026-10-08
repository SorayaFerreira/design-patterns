# 🎯 Specification pattern for complex business rules
from abc import ABC, abstractmethod
from typing import Any, List

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'AndSpecification':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'OrSpecification':
        return OrSpecification(self, other)
    
    def not_(self) -> 'NotSpecification':
        return NotSpecification(self)

# 🔗 Composite specifications
class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

class OrSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

class NotSpecification(Specification):
    def __init__(self, spec: Specification):
        self.spec = spec
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)

# 🛍️ Business rule specifications
class PremiumCustomerSpec(Specification):
    def is_satisfied_by(self, customer: Dict[str, Any]) -> bool:
        return customer.get('tier') == 'premium'

class HighValueOrderSpec(Specification):
    def __init__(self, threshold: float):
        self.threshold = threshold
    
    def is_satisfied_by(self, order: Dict[str, Any]) -> bool:
        return order.get('total', 0) >= self.threshold

class RecentCustomerSpec(Specification):
    def __init__(self, days: int):
        self.days = days
    
    def is_satisfied_by(self, customer: Dict[str, Any]) -> bool:
        # Simplified: check if registered within days
        return customer.get('days_since_registration', float('inf')) <= self.days

# 🎨 Using specifications
premium_spec = PremiumCustomerSpec()
high_value_spec = HighValueOrderSpec(100.0)
recent_spec = RecentCustomerSpec(30)

# Complex business rule: Premium OR (High value AND Recent)
eligible_for_discount = premium_spec.or_(high_value_spec.and_(recent_spec))

# Test customers
customers = [
    {"name": "Alice", "tier": "premium", "order_total": 50, "days_since_registration": 60},
    {"name": "Bob", "tier": "regular", "order_total": 150, "days_since_registration": 15},
    {"name": "Charlie", "tier": "regular", "order_total": 30, "days_since_registration": 5},
]

for customer in customers:
    order = {"total": customer["order_total"]}
    if eligible_for_discount.is_satisfied_by(customer) and high_value_spec.is_satisfied_by(order):
        print(f"✅ {customer['name']} is eligible for discount! 🎉")
    else:
        print(f"❌ {customer['name']} is not eligible")