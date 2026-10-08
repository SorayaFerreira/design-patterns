# 👋 Hello, Repository Pattern!
"""
💡 Explanation: The Repository pattern abstracts data access, 
making it easy to switch between different storage mechanisms 
(database, file, memory) without changing your business logic!
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import json

# 🎨 Define our domain model
class Product:
    def __init__(self, id: str, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.emoji = "📦"  # Every product needs an emoji! 
    
    def __repr__(self):
        return f"{self.emoji} Product({self.name}, ${self.price})"

# 🛡️ Abstract repository interface
class Repository(ABC):
    @abstractmethod
    def add(self, entity: Any) -> None:
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> None:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> None:
        pass

# 🚀 Concrete implementation
class ProductRepository(Repository):
    def __init__(self):
        self._storage: Dict[str, Product] = {}
        print("🏪 Product repository initialized!")
    
    def add(self, product: Product) -> None:
        self._storage[product.id] = product
        print(f"✅ Added {product.emoji} {product.name} to repository!")
    
    def get(self, id: str) -> Optional[Product]:
        return self._storage.get(id)
    
    def get_all(self) -> List[Product]:
        return list(self._storage.values())
    
    def update(self, product: Product) -> None:
        if product.id in self._storage:
            self._storage[product.id] = product
            print(f"📝 Updated {product.emoji} {product.name}")
    
    def delete(self, id: str) -> None:
        if id in self._storage:
            product = self._storage.pop(id)
            print(f"🗑️ Deleted {product.emoji} {product.name}")


# Pra ver funcionando...
if __name__ == "__main__":
    repo = ProductRepository()
    repo.add(Product("1", "Notebook", 3500.0, 10))
    print(repo.get_all())
