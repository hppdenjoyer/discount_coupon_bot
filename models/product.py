from typing import List, Dict, Any
import json
from dataclasses import dataclass


@dataclass
class Product:
    """Модель купона/товара."""
    id: str
    name: str
    price: float
    description: str
    category: str


def get_products_by_category(category: str) -> List[Product]:
    """Получение списка товаров по категории."""
    try:
        with open('data/products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return [Product(**product) for product in products_data.get(category, [])]


def save_product(product: Product) -> bool:
    """Сохранение нового товара в базу."""
    try:
        with open('data/products.json', 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        if product.category not in products_data:
            products_data[product.category] = []

        # Преобразование объекта Product в словарь
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category": product.category
        }

        products_data[product.category].append(product_dict)

        with open('data/products.json', 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=4)

        return True
    except Exception:
        return False
