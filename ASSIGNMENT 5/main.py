from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# -----------------------
# DATA
# -----------------------

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
order_counter = 1


# -----------------------
# MODELS
# -----------------------

class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


class NewOrder(BaseModel):
    customer_name: str
    product_id: int


# -----------------------
# HELPER
# -----------------------

def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)


# =====================================================
# DAY 6 ENDPOINTS (ADD ABOVE /products/{product_id})
# =====================================================

# -----------------------
# Q1 - SEARCH PRODUCTS
# -----------------------

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# -----------------------
# Q2 - SORT PRODUCTS
# -----------------------

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# -----------------------
# Q3 - PAGINATION
# -----------------------

@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):
    total = len(products)
    start = (page - 1) * limit
    paged = products[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": -(-total // limit),
        "products": paged
    }


# -----------------------
# Q4 - SEARCH ORDERS
# -----------------------

@app.post("/orders")
def create_order(new_order: NewOrder):
    global order_counter

    product = find_product(new_order.product_id)
    if not product:
        return {"error": "Product not found"}

    order = {
        "order_id": order_counter,
        "customer_name": new_order.customer_name,
        "product_id": new_order.product_id,
        "product_name": product["name"]
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order placed", "order": order}


@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# -----------------------
# Q5 - SORT BY CATEGORY THEN PRICE
# -----------------------

@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "products": result,
        "total": len(result)
    }


# -----------------------
# Q6 - SEARCH + SORT + PAGINATE
# -----------------------

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20),
):

    result = products

    # Search
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # Sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    result = sorted(
        result,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    # Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }


# -----------------------
# BONUS - ORDERS PAGINATION
# -----------------------

@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    total = len(orders)
    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": -(-total // limit),
        "orders": orders[start:start + limit]
    }


# =====================================================
# EXISTING CRUD (KEEP BELOW)
# =====================================================

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    return product


@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}