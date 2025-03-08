from fastapi import FastAPI

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce Recommendation API"}

# Mock product data
products = [
    {"id": 1, "name": "Wireless Headphones", "price": 50.99, "category": "Electronics"},
    {"id": 2, "name": "Mechanical Keyboard", "price": 80.00, "category": "Accessories"},
    {"id": 3, "name": "Gaming Mouse", "price": 35.50, "category": "Accessories"},
    {"id": 4, "name": "Smartphone Stand", "price": 15.99, "category": "Gadgets"},
]

@app.get("/products")
def get_products():
    return {"products": products}
