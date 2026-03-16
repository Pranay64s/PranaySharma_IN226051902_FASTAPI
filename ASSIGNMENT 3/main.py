from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 150, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Gaming Chair", "price": 15999, "category": "Furniture", "in_stock": False},
    {"id": 4, "name": "LED Bulb", "price": 299, "category": "Electronics", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

orders = []
feedback = []

# DAY 4 CRUD ENDPOINTS


class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)


@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(new_product: NewProduct, response: Response):

    if any(p["name"].lower() == new_product.name.lower() for p in products):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    product_dict = {
        "id": next_id,
        **new_product.dict()
    }

    products.append(product_dict)

    return {
        "message": "Product added",
        "product": product_dict
    }

@app.put("/products/discount")
def bulk_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):
    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated),
        "updated_products": updated,
    }


@app.get("/products/audit")
def product_audit():
    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]
    stock_value = sum(p["price"] * 10 for p in in_stock_list)
    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: int = None,
    in_stock: bool = None,
    response: Response = None
):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return product


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}