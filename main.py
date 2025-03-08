from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, select

app = FastAPI()

# Your PostgreSQL Database URL from Render
DATABASE_URL = "postgresql+asyncpg://ecommerce_db_xzrk_user:YvjlbHojbsR6trH87Jmi83XWT68KeOdy@dpg-cv5rt7btq21c73dbfkg0-a/ecommerce_db_xzrk"

# Set up SQLAlchemy engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Define the Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    category = Column(String)

# Initialize the database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

# Dependency to get the database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Fetch all products from the database
@app.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return {"products": [p.__dict__ for p in products]}
