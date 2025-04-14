from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, select
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime,timedelta

app = FastAPI()

# ✅ Corrected PostgreSQL Database URL from Render
DATABASE_URL = "postgresql+asyncpg://ecommerce_db_xzrk_user:YvjlbHojbsR6trH87Jmi83XWT68KeOdy@dpg-cv5rt7btq21c73dbfkg0-a.oregon-postgres.render.com/ecommerce_db_xzrk"

# ✅ Set up SQLAlchemy engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ✅ Define the Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    category = Column(String)

# ✅ Initialize the database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

# ✅ Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# ✅ Fetch all products from the database
@app.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id))
    products = result.scalars().all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price, "category": p.category} for p in products]}

# ✅ Search for products by category
@app.get("/products/search")
async def search_products(category: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.category == category))
    products = result.scalars().all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price, "category": p.category} for p in products]}

# ✅ Model for Adding Products
class ProductCreate(BaseModel):
    name: str
    price: float
    category: str

# ✅ Secure Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ JWT Token Setup
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Fake User Database (Replace with PostgreSQL Users Table)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("password123"),
    }
}

# ✅ Model for User Login
class UserLogin(BaseModel):
    username: str
    password: str

# ✅ Authenticate User
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and pwd_context.verify(password, user["hashed_password"]):
        return user
    return None

# ✅ Login Endpoint (Generates Token)
@app.post("/login")
async def login(user: UserLogin):
    user_data = authenticate_user(user.username, user.password)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Add a new product (Requires Token)
@app.post("/products/add")
async def add_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    new_product = Product(name=product.name, price=product.price, category=product.category)
    db.add(new_product)
    await db.commit()
    return {"message": "Product added successfully", "product": product}

# ✅ Root endpoint to prevent 404 errors
@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce Recommendation API"}
