# 🏗️ Unit of Work pattern for transaction management
class UnitOfWork:
    def __init__(self):
        self._products = ProductRepository()
        self._new: List[Product] = []
        self._dirty: List[Product] = []
        self._removed: List[str] = []
        print("💼 Unit of Work initialized!")
    
    # 🎨 Track new entities
    def register_new(self, product: Product):
        self._new.append(product)
        print(f"📝 Registered new: {product.emoji} {product.name}")
    
    # 🔄 Track modified entities
    def register_dirty(self, product: Product):
        if product not in self._dirty:
            self._dirty.append(product)
            print(f"✏️ Registered dirty: {product.emoji} {product.name}")
    
    # 🗑️ Track removed entities
    def register_removed(self, id: str):
        self._removed.append(id)
        print(f"🗑️ Registered for removal: {id}")
    
    # 💾 Commit all changes
    def commit(self):
        print("🚀 Committing changes...")
        
        # Add new products
        for product in self._new:
            self._products.add(product)
        
        # Update modified products
        for product in self._dirty:
            self._products.update(product)
        
        # Remove deleted products
        for id in self._removed:
            self._products.delete(id)
        
        # Clear tracking lists
        self._new.clear()
        self._dirty.clear()
        self._removed.clear()
        
        print("✅ All changes committed!")
    
    # 🔄 Rollback changes
    def rollback(self):
        self._new.clear()
        self._dirty.clear()
        self._removed.clear()
        print("↩️ Changes rolled back!")