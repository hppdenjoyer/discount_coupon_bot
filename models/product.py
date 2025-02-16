from typing import Dict, List, Any

class Product:
    def __init__(self, id: str, name: str, price: float, description: str, category: str):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.category = category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category
        }

def get_products_by_category(category: str) -> List[Product]:
    """Get products for a specific category."""
    import json
    
    try:
        with open('data/products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
    return [Product(**product) for product in products_data.get(category, [])]
